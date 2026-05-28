"""
merge_orange_silent.py — 4 yerel sahneyi sessiz birleştirir (önizleme amaçlı).

Çıktı: hlk-REKLAM\\FINAL_REKLAM_LARA_ARI_TURUNCU_SESSIZ.mp4
"""

import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logger import get_logger

log = get_logger("merge_orange_silent")

RESCUE_DIR = Path(
    r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM"
    r"\2026 yaz_HANDMADE_BİKİNİ\_rescue_turuncu"
)
OUTPUT = Path(
    r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM"
    r"\FINAL_REKLAM_LARA_ARI_TURUNCU_SESSIZ.mp4"
)

SCENE_FILES = [
    RESCUE_DIR / "scene1_hook.mp4",
    RESCUE_DIR / "scene2_detail.mp4",
    RESCUE_DIR / "scene3_build.mp4",
    RESCUE_DIR / "scene4_payoff.mp4",
]


def main() -> None:
    for p in SCENE_FILES:
        if not p.exists():
            raise SystemExit(f"Sahne dosyası yok: {p}")
        log.info(f"OK: {p.name} ({p.stat().st_size:,} bytes)")

    from moviepy import VideoFileClip, concatenate_videoclips

    log.info("4 sahne moviepy ile birleştiriliyor (sessiz)…")
    clips = [VideoFileClip(str(p)) for p in SCENE_FILES]
    final = concatenate_videoclips(clips, method="compose")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fps = clips[0].fps or 24

    final.write_videofile(
        str(OUTPUT),
        codec="libx264",
        audio=False,
        fps=fps,
        preset="medium",
        threads=4,
    )

    for c in clips:
        c.close()
    final.close()

    log.info(f"✅ Sessiz birleştirme tamam: {OUTPUT}")
    log.info(f"  Süre: ~{sum(VideoFileClip(str(p)).duration for p in SCENE_FILES):.1f} sn")


if __name__ == "__main__":
    main()
