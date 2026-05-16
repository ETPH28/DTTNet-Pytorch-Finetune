#!/usr/bin/env python3
"""Generate spectrogram images for audio tracks in a directory.

Label mapping:
- other -> source
- paper -> paper
- verb  -> ours
"""

from __future__ import annotations

import argparse
from pathlib import Path

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np


LABEL_MAP = {
    "other": "source",
    "paper": "paper",
    "verb": "ours",
}


def make_spectrogram(audio_path: Path, output_dir: Path, sr: int, n_fft: int, hop_length: int) -> Path:
    """Generate and save one spectrogram for an audio file."""
    audio, sample_rate = librosa.load(audio_path, sr=sr, mono=True)
    stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
    spectrogram_db = librosa.amplitude_to_db(np.abs(stft), ref=np.max)

    stem = audio_path.stem.lower()
    label = LABEL_MAP.get(stem, stem)

    fig, ax = plt.subplots(figsize=(12, 4))
    img = librosa.display.specshow(
        spectrogram_db,
        sr=sample_rate,
        hop_length=hop_length,
        x_axis="time",
        y_axis="log",
        ax=ax,
        cmap="magma",
    )
    ax.set_title(label)
    fig.colorbar(img, ax=ax, format="%+2.0f dB")
    fig.tight_layout()

    output_path = output_dir / f"{label}_spectrogram.png"
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate spectrograms for each .wav track in a directory.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory containing audio tracks (default: this script's directory).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "output",
        help="Directory for generated spectrogram images (default: Spectrogram/output).",
    )
    parser.add_argument("--sr", type=int, default=None, help="Target sample rate. Default keeps original sample rate.")
    parser.add_argument("--n-fft", type=int, default=2048, help="FFT window size.")
    parser.add_argument("--hop-length", type=int, default=512, help="Hop length between FFT frames.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    wav_files = sorted(input_dir.glob("*.wav"))
    if not wav_files:
        raise SystemExit(f"No .wav files found in {input_dir}")

    for audio_path in wav_files:
        out = make_spectrogram(
            audio_path=audio_path,
            output_dir=output_dir,
            sr=args.sr,
            n_fft=args.n_fft,
            hop_length=args.hop_length,
        )
        print(f"Saved: {out}")


if __name__ == "__main__":
    main()
