"""
merge_orange_with_voice.py — 4 yerel sahne + ElevenLabs Nisa voiceover.

Yeni KIE render YOK. Yerel _rescue_turuncu klasöründeki 4 mp4'ü kullanır,
ElevenLabs ile 4 voiceover üretir, moviepy ile birleştirir.

Çıktı: hlk-REKLAM\\FINAL_REKLAM_LARA_ARI_TURUNCU.mp4
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.elevenlabs_service import ElevenLabsService
from logger import get_logger

from produce_summer_bikini_orange import (
    SCENES,
    OUTPUT_FILE,
    concat_with_audio,
)

AMBIENT_PATH = Path(
    r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM"
    r"\2026 yaz_HANDMADE_BİKİNİ\_rescue_turuncu\option_3_minimal.mp3"
)


def concat_with_voice_and_ambient(
    parts: list[Path],
    audio_paths: list[Path],
    ambient_path: Path,
    output: Path,
    ambient_volume: float = 0.22,
) -> None:
    """4 sahne + 4 voiceover + ambient track → final mp4."""
    from moviepy import (
        AudioFileClip,
        CompositeAudioClip,
        VideoFileClip,
        concatenate_videoclips,
    )

    log.info(f"Sahneler birleştiriliyor + voiceover + ambient (%{int(ambient_volume*100)}) → {output.name}")

    clips = []
    voice_clips = []
    for video_path, audio_path in zip(parts, audio_paths):
        vid = VideoFileClip(str(video_path))
        voice = AudioFileClip(str(audio_path))
        if voice.duration > vid.duration:
            voice = voice.with_duration(vid.duration)
        vid = vid.with_audio(voice)
        clips.append(vid)
        voice_clips.append(voice)

    final_video = concatenate_videoclips(clips, method="compose")
    total = final_video.duration
    log.info(f"  Toplam video süresi: {total:.2f} sn")

    ambient = AudioFileClip(str(ambient_path)).with_volume_scaled(ambient_volume)
    if ambient.duration > total:
        ambient = ambient.with_duration(total)
    log.info(f"  Ambient: {ambient.duration:.2f} sn @ %{int(ambient_volume*100)} ses")

    # Voiceover (zaten her sahnenin audio'sunda) + ambient karıştır
    composite = CompositeAudioClip([ambient, final_video.audio])
    final_video = final_video.with_audio(composite)

    output.parent.mkdir(parents=True, exist_ok=True)
    fps = clips[0].fps or 24
    final_video.write_videofile(
        str(output),
        codec="libx264",
        audio_codec="aac",
        fps=fps,
        preset="medium",
        threads=4,
    )

    for c in clips:
        c.close()
    for v in voice_clips:
        v.close()
    ambient.close()
    final_video.close()
    log.info(f"✅ Final (ambient'lı): {output}")


# ── Yerel voiceover üretici ────────────────────────────────────────────────
# Önceki Nisa + eleven_v3 + style=0.75 kombinasyonu aksanlı/kalitesiz çıktı.
# Şimdi: Ahu (conversational, samimi UGC) + multilingual_v2 + daha doğal
# parametreler. Marka adı için noktalı virgül koyup nefes alma izni veriyoruz.
def generate_voiceovers_v2(eleven: "ElevenLabsService", tmp_dir: Path) -> list[Path]:
    audio_paths: list[Path] = []
    for i, scene in enumerate(SCENES):
        text = scene["voiceover"]
        log.info(f"[Ses {i + 1}/4] {scene['name']}: \"{text}\"")
        audio_bytes = eleven.generate_speech(
            text=text,
            voice_name="Ahu",
            stability=0.55,
            similarity_boost=0.80,
            style=0.40,
        )
        path = tmp_dir / f"voice_scene{i + 1}.mp3"
        path.write_bytes(audio_bytes)
        dur = ElevenLabsService.measure_audio_duration(audio_bytes)
        log.info(f"  → {path.name} ({path.stat().st_size:,} bytes, {dur:.1f}s)")
        audio_paths.append(path)
    return audio_paths

log = get_logger("merge_orange_with_voice")

RESCUE_DIR = Path(
    r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM"
    r"\2026 yaz_HANDMADE_BİKİNİ\_rescue_turuncu"
)
LOCAL_SCENES = [
    RESCUE_DIR / "scene1_hook.mp4",
    RESCUE_DIR / "scene2_detail.mp4",
    RESCUE_DIR / "scene3_build.mp4",
    RESCUE_DIR / "scene4_payoff.mp4",
]


def main() -> None:
    load_dotenv()
    if not os.environ.get("ELEVENLABS_API_KEY"):
        raise SystemExit("ELEVENLABS_API_KEY .env'de eksik")

    for p in LOCAL_SCENES:
        if not p.exists():
            raise SystemExit(f"Yerel sahne yok: {p}")

    eleven = ElevenLabsService(
        os.environ["ELEVENLABS_API_KEY"],
        model_id="eleven_multilingual_v2",
    )

    with tempfile.TemporaryDirectory(prefix="orange_voice_") as tmp:
        tmp_dir = Path(tmp)

        log.info("ADIM 1/3 — Yerel 4 sahneyi geçici klasöre kopyala")
        parts: list[Path] = []
        for i, src in enumerate(LOCAL_SCENES):
            dst = tmp_dir / f"scene{i + 1}.mp4"
            shutil.copy(src, dst)
            parts.append(dst)

        log.info("ADIM 2/3 — ElevenLabs Ahu (multilingual_v2) ile 4 voiceover üret")
        audio_paths = generate_voiceovers_v2(eleven, tmp_dir)

        log.info("ADIM 3/3 — Sahneler + voiceover + ambient mix")
        if not AMBIENT_PATH.exists():
            raise SystemExit(f"Ambient ses yok: {AMBIENT_PATH}")
        concat_with_voice_and_ambient(parts, audio_paths, AMBIENT_PATH, OUTPUT_FILE, ambient_volume=0.20)

    log.info(f"🎬 Sesli final reklam hazır: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
