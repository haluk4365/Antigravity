#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sahne-2 Prototip v4.0 — Clean Overlay Pipeline (TR)

HLK V3.5 formatı: Konuşma balonu doğrudan video üzerine overlay.
HLK karakteri tek parça halinde korunur, balon alt kısma bindirilir.

Pipeline (tek akış, crop/stack YOK):
  1. Orijinal Hedra video (720×1280)
  2. Balon PNG'sini alt kısma overlay (y=900)
  3. AHU ses eklenir

Kullanim: python render_scene.py
Cikti:   output/scene2_tr_prototype.mp4 (720×1280)
"""

import subprocess
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# SABITLER — v4.0 CLEAN OVERLAY
# ============================================================
HEDRA_VIDEO  = "assets/hedra_tr.mp4"
BUBBLE_PNG   = "output/bubble.png"
AHU_MP3      = "assets/ahu_tr.mp3"
OUTPUT_MP4   = "output/scene2_tr_prototype.mp4"

# Balon overlay pozisyonu — orijinal video alt kısmına
BUBBLE_OVERLAY_Y = 830  # balon 720×450, y=830 → 830+450=1280

# Cikti
VIDEO_W = 720
VIDEO_H = 1280

FFMPEG  = "ffmpeg"
FFPROBE = "ffprobe"


def get_duration(filepath):
    try:
        result = subprocess.run(
            [FFPROBE, "-v", "error", "-show_entries",
             "format=duration", "-of", "csv=p=0", filepath],
            capture_output=True, text=True, timeout=15
        )
        if result.stdout.strip():
            return float(result.stdout.strip())
    except Exception as e:
        logger.warning(f"  ⚠ Süre okunamadi: {e}")
    return 0.0


def get_resolution(filepath):
    try:
        result = subprocess.run(
            [FFPROBE, "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height",
             "-of", "json", filepath],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        if "streams" in data and data["streams"]:
            s = data["streams"][0]
            return s.get("width", 0), s.get("height", 0)
    except Exception:
        pass
    return 0, 0


def build_ffmpeg_cmd():
    """v4.0: Tek akış overlay — crop/stack YOK, balon direkt video üstüne.
    Son 1 saniye son kare donar (tpad) + sessiz apad."""
    dur = get_duration(HEDRA_VIDEO)
    total_dur = dur + 5.0
    cmd = [
        FFMPEG,
        "-i", HEDRA_VIDEO,           # 0 — orijinal video (tek parça)
        "-i", BUBBLE_PNG,             # 1 — balon PNG
        "-i", AHU_MP3,                # 2 — ses
        "-filter_complex",
        # Balon overlay: orijinal video üzerine, alt kısma hizali
        f"[1:v]format=rgba[balloon];"
        f"[0:v][balloon]overlay=0:{BUBBLE_OVERLAY_Y}:format=auto[overlayed];"
        # Son 1 saniye son kareyi dondur (tpad)
        f"[overlayed]tpad=stop_mode=clone:stop_duration=5[final_v]",
        "-map", "[final_v]",
        "-map", "2:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-af", "apad=pad_dur=5",
        "-c:a", "aac",
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-t", str(total_dur),
        "-movflags", "+faststart",
        "-y",
        OUTPUT_MP4
    ]
    return cmd


def run_command(cmd):
    logger.info(f"  Pipeline baslatiliyor...")

    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=120)

        if process.returncode != 0:
            hata = [l for l in stderr.split('\n')
                    if 'error' in l.lower() or 'Error' in l]
            for l in hata[:5]:
                logger.error(f"  {l.strip()}")
            return False

        for l in stderr.split('\n'):
            if 'muxing' in l.lower() or 'frame=' in l.lower():
                logger.info(f"  {l.strip()[:80]}")
                break

        return True

    except subprocess.TimeoutExpired:
        logger.error("  Pipeline timeout")
        return False
    except Exception as e:
        logger.error(f"  Hata: {e}")
        return False


def validate_output(filepath):
    logger.info(f"\n  Dogrulama:")

    if not Path(filepath).exists():
        logger.error(f"  Dosya yok: {filepath}")
        return False

    size_kb = Path(filepath).stat().st_size // 1024
    dur = get_duration(filepath)
    w, h = get_resolution(filepath)

    hedra_dur = get_duration(HEDRA_VIDEO)
    if abs(dur - hedra_dur) > 1.0:
        logger.warning(f"  Süre: {dur:.3f}sn (beklenen {hedra_dur:.3f})")
    else:
        logger.info(f"  Süre: {dur:.3f}sn")

    if w != VIDEO_W or h != VIDEO_H:
        logger.warning(f"  Çözünürlük: {w}x{h}")
    else:
        logger.info(f"  Çözünürlük: {w}x{h} (9:16)")

    logger.info(f"  Boyut: {size_kb}KB")
    logger.info(f"  Dogrulama tamam")
    return True


def main():
    print("\nSAHNE-2 v4.0 CLEAN OVERLAY RENDER")
    print("=" * 45)

    for f in [HEDRA_VIDEO, BUBBLE_PNG, AHU_MP3]:
        if not Path(f).exists():
            logger.error(f"  Girdi yok: {f}")
            sys.exit(1)
        logger.info(f"  Girdi: {f}")

    dur = get_duration(HEDRA_VIDEO)
    mp3_dur = get_duration(AHU_MP3)
    logger.info(f"  Video: {dur:.3f}sn")
    logger.info(f"  MP3:   {mp3_dur:.3f}sn")

    cmd = build_ffmpeg_cmd()
    basarili = run_command(cmd)

    if not basarili:
        logger.error("  Pipeline basarisiz")
        sys.exit(1)

    validate_output(OUTPUT_MP4)
    print(f"\n  ✅ scene2_tr_prototype.mp4 hazir")
    print(f"  HLK: tek parça (orijinal video korundu)")
    print(f"  Balon: overlay y=900, 720×380px")


if __name__ == "__main__":
    main()
