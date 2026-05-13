import os
import json
import random
import numpy as np
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from pedalboard import Pedalboard, Reverb, Compressor
from pedalboard.io import AudioFile

# Set a seed for reproducibility in your research
random.seed(42)

def process_song(song_path, output_root, stem_names=['vocals', 'drums', 'bass', 'other']):
    song_name = song_path.name
    out_song_dir = output_root / song_name
    
    # Checkpointing: Skip if already processed
    if (out_song_dir / "augmentation_metadata.json").exists():
        return f"Skipped {song_name} (already processed)"
        
    out_song_dir.mkdir(parents=True, exist_ok=True)

    augmented_stems = []
    metadata = {"song": song_name, "augmentations": {}}
    samplerate = 44100

    for stem in stem_names:
        input_file = song_path / f"{stem}.wav"
        if not input_file.exists():
            continue

        with AudioFile(str(input_file)) as f:
            audio = f.read(f.frames)
            samplerate = f.samplerate

        # Generate Random Parameters
        params = {
            "comp_threshold": random.uniform(-25.0, -10.0),
            "comp_ratio": random.uniform(2.0, 5.0),
            "rev_room_size": random.uniform(0.2, 0.6),
            "rev_wet_level": random.uniform(0.1, 0.3)
        }
        metadata["augmentations"][stem] = params

        # Define Effects Chain
        board = Pedalboard([
            Compressor(threshold_db=params["comp_threshold"], ratio=params["comp_ratio"]),
            Reverb(room_size=params["rev_room_size"], wet_level=params["rev_wet_level"], dry_level=0.7)
        ])

        # Process and Save Stem
        effected_audio = board(audio, samplerate)
        output_stem_path = out_song_dir / f"{stem}.wav"
        
        with AudioFile(str(output_stem_path), 'w', samplerate, effected_audio.shape[0]) as f:
            f.write(effected_audio)
        
        augmented_stems.append(effected_audio)

    if not augmented_stems:
        return f"Skipped {song_name} (no stems found)"

    # --- Automated Mixdown ---
    mixed_audio = np.sum(augmented_stems, axis=0)

    # Peak Normalization to -0.5 dB to prevent clipping
    max_val = np.max(np.abs(mixed_audio))
    if max_val > 0:
        mixed_audio = (mixed_audio / max_val) * 0.94 # ~ -0.5dB

    mix_path = out_song_dir / "mixture.wav"
    with AudioFile(str(mix_path), 'w', samplerate, mixed_audio.shape[0]) as f:
        f.write(mixed_audio)

    # Save Metadata for reproducibility
    with open(out_song_dir / "augmentation_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)
        
    return f"Successfully processed: {song_name}"

def run_pipeline_parallel(source_dir, output_dir, max_workers=None):
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    all_tasks = []
    for subset in ['train', 'test']:
        subset_dir = source_path / subset
        if subset_dir.exists():
            songs = [d for d in subset_dir.iterdir() if d.is_dir()]
            for song in songs:
                all_tasks.append((song, output_path / subset))

    if not all_tasks:
        print("No songs found. Please check your source directory.")
        return

    print(f"Launching parallel processing for {len(all_tasks)} songs...")
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_song, task[0], task[1]) for task in all_tasks]
        
        completed = 0
        for future in futures:
            try:
                result = future.result()
                completed += 1
                if completed % 10 == 0 or completed == len(all_tasks):
                    print(f"Progress: {completed}/{len(all_tasks)} songs finished.")
            except Exception as e:
                print(f"Error processing song: {e}")

if __name__ == '__main__':
    # Update these paths to match your cloud environment
    SOURCE_MUSDB = './musdb18hq'
    OUTPUT_AUGMENTED = './musdb18hq_augmented'
    
    print(f"Starting data augmentation pipeline...")
    print(f"Source: {SOURCE_MUSDB}")
    print(f"Output: {OUTPUT_AUGMENTED}")
    
    run_pipeline_parallel(SOURCE_MUSDB, OUTPUT_AUGMENTED)
