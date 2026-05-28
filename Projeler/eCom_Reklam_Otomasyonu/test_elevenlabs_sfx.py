"""
test_elevenlabs_sfx.py — ElevenLabs Sound Effects API'sini test eder.

3 farklı beach ambient prompt'u dener, .mp3 olarak kaydeder.
Sonuç: _rescue_turuncu klasöründe option_1.mp3, option_2.mp3, option_3.mp3
"""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from logger import get_logger

log = get_logger("test_elevenlabs_sfx")

OUT_DIR = Path(
    r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM"
    r"\2026 yaz_HANDMADE_BİKİNİ\_rescue_turuncu"
)

PROMPTS = {
    "option_1_calm.mp3": (
        "Calm tropical beach atmosphere with gentle ocean waves softly "
        "rolling in, light warm sea breeze, distant faint seagulls. "
        "No music, no human voices, no chatter — pure natural ambience."
    ),
    "option_2_lively.mp3": (
        "Sunny beach club ambience with rhythmic ocean waves crashing, "
        "warm breeze through palm leaves rustling, very faint distant "
        "background beach chatter. No music, no clear voices."
    ),
    "option_3_minimal.mp3": (
        "Pure ocean wave sounds, gentle rhythmic waves washing onto sand, "
        "soft wind. No music, no voices, no birds — minimal natural beach."
    ),
}


def generate_sfx(api_key: str, prompt: str, duration: float = 16.0) -> bytes:
    url = "https://api.elevenlabs.io/v1/sound-generation"
    r = requests.post(
        url,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
        },
        json={
            "text": prompt,
            "duration_seconds": duration,
            "prompt_influence": 0.4,
        },
        timeout=180,
    )
    if not r.ok:
        log.error(
            f"HTTP {r.status_code} — body: {r.text[:400]}"
        )
        r.raise_for_status()
    return r.content


def main() -> None:
    load_dotenv()
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise SystemExit("ELEVENLABS_API_KEY .env'de eksik")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for filename, prompt in PROMPTS.items():
        log.info(f"Üretiliyor: {filename}")
        log.info(f"  Prompt: {prompt[:80]}…")
        try:
            audio = generate_sfx(api_key, prompt)
        except requests.HTTPError as e:
            log.error(f"FAIL: {filename} — {e}")
            log.error("ElevenLabs Sound Effects abonelik kapsamı dışı olabilir.")
            log.error("Fallback: Freesound API key gerek.")
            sys.exit(1)
        out = OUT_DIR / filename
        out.write_bytes(audio)
        log.info(f"  ✓ {out.name} ({len(audio):,} bytes)")

    log.info("3 ambient seçeneği hazır — dinle ve birini seç.")


if __name__ == "__main__":
    main()
