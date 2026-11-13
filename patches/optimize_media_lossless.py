#!/usr/bin/env python3
"""Conservatively recompress raster images and videos without changing decoded pixels/frames.

PNG and WebP files are replaced only when a smaller candidate decodes to exactly
the same pixel data. Video files are encoded with lossless H.264 (QP 0, no scaling,
no frame-rate conversion, and unchanged pixel format). A video candidate is used
only when it is smaller; otherwise an MP4 source is copied unchanged.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

from PIL import Image
from PIL.PngImagePlugin import PngInfo


def image_pixels(image: Image.Image) -> tuple[str, tuple[int, int], bytes]:
    image.load()
    return image.mode, image.size, image.tobytes()


def png_metadata(image: Image.Image) -> dict:
    info = image.info
    kwargs: dict = {}
    for key in ("icc_profile", "exif", "dpi", "transparency"):
        if key in info:
            kwargs[key] = info[key]

    pnginfo = PngInfo()
    for key, value in info.items():
        if key in {"icc_profile", "exif", "dpi", "transparency"}:
            continue
        if key in {"gamma", "chromaticity", "srgb", "background"}:
            try:
                if key == "gamma":
                    pnginfo.add(b"gAMA", struct.pack(">I", round(float(value) * 100000)))
                elif key == "chromaticity":
                    pnginfo.add(b"cHRM", struct.pack(">8I", *(round(float(v) * 100000) for v in value)))
                elif key == "srgb":
                    pnginfo.add(b"sRGB", bytes([int(value)]))
                elif key == "background":
                    if image.mode == "P":
                        payload = bytes([int(value)])
                    elif image.mode in {"1", "L"}:
                        payload = struct.pack(">H", int(value))
                    else:
                        payload = struct.pack(">3H", *(int(v) for v in value))
                    pnginfo.add(b"bKGD", payload)
            except (TypeError, ValueError, struct.error):
                # An unhandled metadata value is safer to preserve by skipping
                # this image than to silently discard it.
                raise ValueError(f"cannot safely preserve PNG metadata field {key!r}")
        elif isinstance(value, str):
            pnginfo.add_text(key, value)
        elif isinstance(value, bytes) and len(key) == 4 and key.isascii():
            pnginfo.add(key.encode("ascii"), value)

    if pnginfo.chunks:
        kwargs["pnginfo"] = pnginfo
    return kwargs


def optimize_image(path: Path) -> tuple[bool, int]:
    try:
        with Image.open(path) as original:
            if getattr(original, "n_frames", 1) != 1:
                return False, 0
            before = image_pixels(original)
            fmt = (original.format or path.suffix.lstrip(".")).upper()
            suffix = path.suffix.lower()
            fd, temp_name = tempfile.mkstemp(prefix=f".{path.stem}.lossless-", suffix=suffix, dir=path.parent)
            os.close(fd)
            temp = Path(temp_name)
            try:
                if fmt == "PNG" or suffix == ".png":
                    kwargs = png_metadata(original)
                    original.save(temp, format="PNG", optimize=True, compress_level=9, **kwargs)
                elif fmt == "WEBP" or suffix == ".webp":
                    # WebP lossless keeps the exact decoded RGB/RGBA values.
                    if original.mode not in {"RGB", "RGBA"}:
                        return False, 0
                    kwargs = {}
                    for key in ("icc_profile", "exif", "xmp"):
                        if key in original.info:
                            kwargs[key] = original.info[key]
                    original.save(temp, format="WEBP", lossless=True, quality=100, method=6, exact=True, **kwargs)
                else:
                    return False, 0

                with Image.open(temp) as encoded:
                    after = image_pixels(encoded)
                if before != after:
                    return False, 0

                old_size = path.stat().st_size
                new_size = temp.stat().st_size
                if new_size >= old_size:
                    return False, 0
                os.replace(temp, path)
                return True, old_size - new_size
            finally:
                temp.unlink(missing_ok=True)
    except Exception as exc:
        print(f"SKIP image {path}: {exc}")
        return False, 0


def optimize_images(root: Path) -> None:
    if not root.is_dir():
        raise SystemExit(f"Image root does not exist: {root}")
    candidates = sorted(
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in {".png", ".webp"}
    )
    optimized = 0
    saved = 0
    for path in candidates:
        changed, amount = optimize_image(path)
        if changed:
            optimized += 1
            saved += amount
            print(f"LOSSLESS IMAGE {path}: saved {amount:,} bytes")
    print(
        f"Lossless image pass complete: {optimized}/{len(candidates)} files reduced; "
        f"{saved:,} bytes saved. Pixel data was verified before replacement."
    )


def run_ffmpeg(command: list[str]) -> bool:
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()
        print("FFmpeg lossless attempt unavailable: " + (detail[-1] if detail else "unknown error"))
        return False
    return True


def optimize_video(source: Path, destination: Path, audio: str) -> None:
    if not source.is_file():
        raise SystemExit(f"Video source is missing: {source}")
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is required for lossless video processing.")
    destination.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{destination.stem}.lossless-",
        suffix=".mp4",
        dir=destination.parent,
    )
    os.close(fd)
    candidate = Path(temp_name)
    candidate.unlink(missing_ok=True)

    base = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(source), "-map", "0:v:0",
    ]
    if audio == "copy":
        base += ["-map", "0:a?", "-c:a", "copy"]
    else:
        base += ["-an"]

    # QP 0 is lossless H.264. '+' prevents FFmpeg from silently changing the
    # source pixel format; no scale, crop, or frame-rate filter is applied.
    video_args = [
        "-c:v", "libx264", "-preset", "veryslow", "-qp", "0",
        "-pix_fmt", "+", "-fps_mode", "passthrough",
        "-map_metadata", "0", "-map_chapters", "0",
        "-movflags", "+faststart", str(candidate),
    ]

    try:
        succeeded = run_ffmpeg(base + video_args)
        if not succeeded and audio == "copy":
            # Some source audio codecs cannot be muxed into MP4. ALAC is
            # lossless and keeps the audio stream intact at the decoded level.
            retry = [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(source), "-map", "0:v:0", "-map", "0:a?",
                "-c:a", "alac",
            ] + video_args
            succeeded = run_ffmpeg(retry)

        if not succeeded or not candidate.is_file() or candidate.stat().st_size == 0:
            if source.suffix.lower() == ".mp4":
                shutil.copy2(source, destination)
                print(f"KEPT ORIGINAL VIDEO {source}: lossless encoder unavailable.")
                return
            raise SystemExit(f"Could not create a quality-preserving MP4 from {source}")

        source_size = source.stat().st_size
        candidate_size = candidate.stat().st_size
        if candidate_size < source_size:
            os.replace(candidate, destination)
            print(
                f"LOSSLESS VIDEO {destination}: "
                f"{source_size:,} -> {candidate_size:,} bytes"
            )
        elif source.suffix.lower() == ".mp4":
            shutil.copy2(source, destination)
            print(
                f"KEPT ORIGINAL VIDEO {source}: lossless candidate was larger "
                f"({candidate_size:,} vs {source_size:,} bytes)."
            )
        else:
            # The page expects MP4. Keep the lossless transcode for non-MP4
            # inputs rather than copying a different container under an MP4 name.
            os.replace(candidate, destination)
            print(
                f"LOSSLESS VIDEO {destination}: kept MP4 compatibility; "
                f"size changed {source_size:,} -> {candidate_size:,} bytes."
            )
    finally:
        candidate.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, help="Recursively losslessly recompress PNG and WebP images in this folder.")
    parser.add_argument("--video", nargs=2, metavar=("SOURCE", "DESTINATION"), help="Create a lossless H.264 MP4, keeping the smaller source/candidate when possible.")
    parser.add_argument("--audio", choices=("copy", "none"), default="none", help="Copy the audio bitstream losslessly or omit audio (default: none).")
    args = parser.parse_args()

    if bool(args.images) == bool(args.video):
        parser.error("choose exactly one mode: --images ROOT or --video SOURCE DESTINATION")
    if args.images:
        optimize_images(args.images)
    else:
        optimize_video(Path(args.video[0]), Path(args.video[1]), args.audio)


if __name__ == "__main__":
    main()
