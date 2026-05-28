"""
remix_red_energetic.py — Kırmızı reklamın sesini daha enerjik yeniden mixle.

Render YOK. Mevcut _rescue_kirmizi sahnelerini kullanır.
Ahu stability=0.35 + style=0.70 (daha canlı/enerjik).

Çıktı: FINAL_REKLAM_LARA_ARI_KIRMIZI_v2.mp4
"""

import os
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.elevenlabs_service import ElevenLabsService
from logger import get_logger

log = get_logger("remix_red_energetic")

HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
COLLECTION = HLK / "LARA_Bikini_230526" / "2026 yaz_HANDMADE_BİKİNİ"
RESCUE_DIR = COLLECTION / "_rescue_kirmizi"
AMBIENT_PATH = COLLECTION / "_rescue_turuncu" / "option_3_minimal.mp3"
OUTPUT = HLK / "FINAL_REKLAM_LARA_ARI_KIRMIZI_v2.mp4"

SCENES = [
    "Kızlar — Lara Arı'dan yaz koleksiyonu geldi, hepsi el yapımı!",
    "Şu detaya bakın — tamamen el yapımı!",
    "Her motif tek tek örülmüş, bu ürünler aşırı güzel!",
    "Bu yazın favorisi resmen bende!",
]


def main() -> None:
    load_dotenv()
    eleven = ElevenLabsService(
        os.environ["ELEVENLABS_API_KEY"],
        model_id="eleven_multilingual_v2",
    )

    scene_paths = [RESCUE_DIR / f"scene{i + 1}.mp4" for i in range(4)]
    for p in scene_paths:
        if not p.exists():
            raise SystemExit(f"Sahne yok: {p}")
    if not AMBIENT_PATH.exists():
        raise SystemExit(f"Ambient yok: {AMBIENT_PATH}")

    with tempfile.TemporaryDirectory(prefix="red_v2_") as tmp:
        tmp_dir = Path(tmp)

        log.info("ElevenLabs Ahu (enerjik mod) ile voiceover")
        voice_paths = []
        for i, text in enumerate(SCENES):
            audio = eleven.generate_speech(
                text=text,
                voice_name="Ahu",
                stability=0.35,      # daha az tutarlı → daha canlı dalgalanma
                similarity_boost=0.80,
                style=0.70,          # daha "performans" tonu
            )
            p = tmp_dir / f"v{i + 1}.mp3"
            p.write_bytes(audio)
            voice_paths.append(p)
            log.info(f"  ses {i + 1}: {p.stat().st_size:,} byte")

        log.info("moviepy ile birleştirme")
        from moviepy import (
            AudioFileClip,
            CompositeAudioClip,
            VideoFileClip,
            concatenate_videoclips,
        )

        clips = []
        voice_clips = []
        for vp, ap in zip(scene_paths, voice_paths):
            vid = VideoFileClip(str(vp))
            voice = AudioFileClip(str(ap))
            if voice.duration > vid.duration:
                voice = voice.with_duration(vid.duration)
            vid = vid.with_audio(voice)
            clips.append(vid)
            voice_clips.append(voice)

        final = concatenate_videoclips(clips, method="compose")
        ambient = AudioFileClip(str(AMBIENT_PATH)).with_volume_scaled(0.20)
        if ambient.duration > final.duration:
            ambient = ambient.with_duration(final.duration)
        final = final.with_audio(CompositeAudioClip([ambient, final.audio]))

        final.write_videofile(
            str(OUTPUT),
            codec="libx264",
            audio_codec="aac",
            fps=clips[0].fps or 24,
            preset="medium",
            threads=4,
            logger=None,
        )
        for c in clips: c.close()
        for v in voice_clips: v.close()
        ambient.close()
        final.close()

    log.info(f"✅ {OUTPUT}")


if __name__ == "__main__":
    main()
