import os
import json
import numpy as np
from pathlib import Path
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
from pedalboard import Reverb, Compressor
from pedalboard.io import AudioFile

def parse_float_list(value):
    return [float(v.strip()) for v in value.split(",") if v.strip()]


def make_effect_param_matrix(comp_thresholds, comp_ratios, rev_room_sizes):
    matrix = []
    for comp_threshold in comp_thresholds:
        for comp_ratio in comp_ratios:
            for rev_room_size in rev_room_sizes:
                matrix.append((comp_threshold, comp_ratio, rev_room_size))
    return matrix


def add_wet_source(dry_audio, wet_audio, alpha):
    return dry_audio + (alpha * wet_audio)


def process_song(
    song_path,
    output_root,
    reverb_alpha,
    compression_alpha,
    comp_threshold,
    comp_ratio,
    rev_room_size,
    stem_names=['vocals', 'drums', 'bass', 'other'],
):
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

        # Use discrete parameter values from the configured matrix.
        params = {
            "comp_threshold": comp_threshold,
            "comp_ratio": comp_ratio,
            "rev_room_size": rev_room_size,
            "reverb_alpha": reverb_alpha,
            "compression_alpha": compression_alpha,
        }
        metadata["augmentations"][stem] = params

        # Build fully wet sources, then add them into the dry source with alpha.
        compression = Compressor(
            threshold_db=params["comp_threshold"],
            ratio=params["comp_ratio"],
        )
        reverb = Reverb(
            room_size=params["rev_room_size"],
            wet_level=1.0,
            dry_level=0.0,
        )
        wet_compression = compression(audio, samplerate)
        wet_reverb = reverb(audio, samplerate)

        effected_audio = add_wet_source(audio, wet_compression, compression_alpha)
        effected_audio = add_wet_source(effected_audio, wet_reverb, reverb_alpha)
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

def run_pipeline_parallel(
    source_dir,
    output_dir,
    effect_param_matrix,
    reverb_alpha,
    compression_alpha,
    max_workers=None,
):
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    all_tasks = []
    for subset in ['train', 'test']:
        subset_dir = source_path / subset
        if subset_dir.exists():
            songs = [d for d in subset_dir.iterdir() if d.is_dir()]
            for comp_threshold, comp_ratio, rev_room_size in effect_param_matrix:
                variant_dir = (
                    output_path
                    / (
                        f"rev_alpha={reverb_alpha:.3f}_comp_alpha={compression_alpha:.3f}"
                        f"_thr={comp_threshold:.2f}_ratio={comp_ratio:.2f}_room={rev_room_size:.3f}"
                    )
                    / subset
                )
                for song in songs:
                    all_tasks.append(
                        (
                            song,
                            variant_dir,
                            reverb_alpha,
                            compression_alpha,
                            comp_threshold,
                            comp_ratio,
                            rev_room_size,
                        )
                    )

    if not all_tasks:
        print("No songs found. Please check your source directory.")
        return

    print(f"Launching parallel processing for {len(all_tasks)} songs...")
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                process_song,
                task[0],
                task[1],
                task[2],
                task[3],
                task[4],
                task[5],
                task[6],
            )
            for task in all_tasks
        ]
        
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
    parser = ArgumentParser()
    parser.add_argument("--source-dir", type=str, default="./musdb18hq")
    parser.add_argument("--output-dir", type=str, default="./custom_aug")
    parser.add_argument("--reverb-alpha", type=float, default=0.2)
    parser.add_argument("--compression-alpha", type=float, default=0.7)
    parser.add_argument("--comp-thresholds", type=str, default="-30,-24")
    parser.add_argument("--comp-ratios", type=str, default="8.0,12.0")
    parser.add_argument("--rev-room-sizes", type=str, default="0.25,0.55")
    parser.add_argument("--max-workers", type=int, default=None)
    args = parser.parse_args()

    reverb_alpha = args.reverb_alpha
    compression_alpha = args.compression_alpha
    comp_thresholds = parse_float_list(args.comp_thresholds)
    comp_ratios = parse_float_list(args.comp_ratios)
    rev_room_sizes = parse_float_list(args.rev_room_sizes)
    effect_param_matrix = make_effect_param_matrix(
        comp_thresholds,
        comp_ratios,
        rev_room_sizes,
    )

    if not effect_param_matrix:
        raise ValueError("Effect parameter matrix is empty.")
    if reverb_alpha == 0.0 and compression_alpha == 0.0:
        raise ValueError("At least one of reverb_alpha or compression_alpha must be non-zero.")
    if len(comp_thresholds) != 2 or len(comp_ratios) != 2 or len(rev_room_sizes) != 2:
        raise ValueError("Use exactly 2 thresholds, 2 ratios, and 2 room sizes for 2x2x2 (8 variants).")

    print("Starting data augmentation pipeline...")
    print(f"Source: {args.source_dir}")
    print(f"Output: {args.output_dir}")
    print(f"Reverb alpha: {reverb_alpha}")
    print(f"Compression alpha: {compression_alpha}")
    print(f"Compressor thresholds: {comp_thresholds}")
    print(f"Compressor ratios: {comp_ratios}")
    print(f"Reverb room sizes: {rev_room_sizes}")
    print(f"Total matrix variants: {len(effect_param_matrix)}")

    run_pipeline_parallel(
        args.source_dir,
        args.output_dir,
        effect_param_matrix,
        reverb_alpha,
        compression_alpha,
        max_workers=args.max_workers,
    )
