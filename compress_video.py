#!/usr/bin/env python3
"""
Video Compression Script
Compresses a video file to a maximum target size (default: 100 MB)
"""

import subprocess
import os
import sys

def get_video_duration(input_file):
    """Get video duration in seconds using ffprobe"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error getting video duration: {e}")
        sys.exit(1)

def get_file_size_mb(file_path):
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)

def compress_video(input_file, output_file, target_size_mb=100):
    """
    Compress video to target size using ffmpeg

    Args:
        input_file: Path to input video file
        output_file: Path to output video file
        target_size_mb: Target file size in MB (default: 100)
    """

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        sys.exit(1)

    # Get current file size
    current_size_mb = get_file_size_mb(input_file)
    print(f"Current video size: {current_size_mb:.2f} MB")

    if current_size_mb <= target_size_mb:
        print(f"Video is already under {target_size_mb} MB. No compression needed!")
        return

    # Get video duration
    duration = get_video_duration(input_file)
    print(f"Video duration: {duration:.2f} seconds")

    # Calculate target bitrate
    # Formula: (target_size_mb * 8192) / duration - audio_bitrate
    # We'll use 128k for audio bitrate
    audio_bitrate_kbps = 128
    target_size_bits = target_size_mb * 8 * 1024 * 1024
    target_total_bitrate_kbps = (target_size_bits / duration) / 1000
    target_video_bitrate_kbps = target_total_bitrate_kbps - audio_bitrate_kbps

    # Add a safety margin (reduce by 5% to ensure we stay under the limit)
    target_video_bitrate_kbps = int(target_video_bitrate_kbps * 0.95)

    print(f"Target video bitrate: {target_video_bitrate_kbps}k")
    print(f"Target audio bitrate: {audio_bitrate_kbps}k")
    print(f"\nCompressing video...")

    # FFmpeg compression command
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',  # Video codec
        '-b:v', f'{target_video_bitrate_kbps}k',  # Video bitrate
        '-c:a', 'aac',  # Audio codec
        '-b:a', f'{audio_bitrate_kbps}k',  # Audio bitrate
        '-preset', 'medium',  # Encoding speed/quality tradeoff
        '-movflags', '+faststart',  # Enable streaming
        '-y',  # Overwrite output file if exists
        output_file
    ]

    try:
        subprocess.run(cmd, check=True)

        # Get compressed file size
        compressed_size_mb = get_file_size_mb(output_file)
        reduction = ((current_size_mb - compressed_size_mb) / current_size_mb) * 100

        print(f"\n✓ Compression complete!")
        print(f"Original size: {current_size_mb:.2f} MB")
        print(f"Compressed size: {compressed_size_mb:.2f} MB")
        print(f"Size reduction: {reduction:.1f}%")
        print(f"Output file: {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error during compression: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Configuration
    input_video = "asset/DESFRALDE CONSCIENTE VD PROMO 001.mp4"
    output_video = "asset/DESFRALDE CONSCIENTE VD PROMO 001_compressed.mp4"
    target_size = 80  # MB

    print("=" * 60)
    print("VIDEO COMPRESSION SCRIPT")
    print("=" * 60)
    print(f"Input: {input_video}")
    print(f"Output: {output_video}")
    print(f"Target size: {target_size} MB")
    print("=" * 60)
    print()

    compress_video(input_video, output_video, target_size)
