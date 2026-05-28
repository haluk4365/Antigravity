"""
v4 deneme — tek sahne (kızıl, havuz) yeni stratejiyle:
- Reference olarak SADECE PINK-b2 (üst) verilir; alt parça prompt'tan tarif edilir.
- Amaç: üst bağcığın ucunda 'sarı krochet çiçek' çıkmasını önlemek
  (Seedance'in alt'ın sarı çiçeklerini üstün bağcığına kopyalamasını engelle).
- Tek sahne, ~200 kredi maliyet; çıktı v4_test_redhead.mp4
"""

import asyncio
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.imgbb_service import ImgBBService
from services.kie_api import KieAIService
from logger import get_logger

log = get_logger("test_v4_top_only")

PINK_B2 = r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM\PINK-b2.jpg"
OUTPUT = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM\v4_test_redhead.mp4")

PROMPT = (
    "Product — TOP piece: the EXACT triangle halter top from the reference image — "
    "vivid hot-pink crochet, densely covered with multicolor crochet flowers "
    "(orange, royal blue, yellow, light gray, cream, turquoise, green) on the "
    "cups. The halter's pink crochet straps (neck strap and back-tie strap) "
    "terminate with TINY TRANSLUCENT PINK GLASS BEADS only — like small round "
    "pink crystal pendants, exactly as shown in the reference image. "
    "ABSOLUTELY NO flower charms on the top straps. NO yellow flowers, NO "
    "turquoise flowers, NO crochet motifs anywhere on the top strings. "
    "Product — BOTTOM piece (NOT in the reference; build it from this "
    "description): matching hot-pink crochet side-tied briefs in the SAME "
    "vivid hot-pink color and crochet texture as the top. The bottom is "
    "side-tied with thin pink crochet straps; from the TWO BOTTOM SIDE-TIE "
    "ENDS (left hip and right hip) hang small crochet flower charms — one "
    "yellow and one turquoise flower per side. Flower charms exist ONLY on "
    "the bottom hip ties. "
    "NO brand labels, NO clothing tags, NO 'LARA ARI' woven label, NO white "
    "rectangular labels, NO logos, NO printed text anywhere on the bikini. "
    "Model: a 23-year-old red-haired Mediterranean woman, approximately 170 cm "
    "tall, slim athletic build, long wavy bright copper-red hair, fair skin "
    "with light freckles, fresh natural makeup, calm confident expression, "
    "wearing the bikini described above. "
    "Setting: a modern rooftop infinity pool at bright midday, sea or city "
    "horizon behind, saturated turquoise water, polarized clean light, "
    "professional fashion-film lighting; the fuchsia bikini contrasts the "
    "blue pool. "
    "Action: she sits on the pool edge, dipping her feet into the water, "
    "in side-profile to camera. Smooth slow lateral dolly from right to left "
    "clearly showing both the bikini top and bottom details. Subtle slow motion. "
    "9:16 vertical, professional cinematic photography, sharp focus on the "
    "bikini details, color-graded, no on-screen text, no captions, no brand "
    "labels, no logos. Completely silent — no music, no dialogue, no "
    "voice-over, no narration."
)


async def main() -> None:
    load_dotenv()
    imgbb = ImgBBService(os.environ["IMGBB_API_KEY"])
    kie = KieAIService(os.environ["KIE_API_KEY"])

    bal = kie.get_credit_balance().get("data", 0)
    log.info(f"Bakiye: {bal} kredi")

    with open(PINK_B2, "rb") as fh:
        res = imgbb.upload_image_bytes(fh.read(), name="PINK-b2")
    top_url = res["url"]
    log.info(f"PINK-b2 → {top_url}")

    task_id = await asyncio.to_thread(
        kie.create_video,
        prompt=PROMPT,
        duration=5,
        aspect_ratio="9:16",
        generate_audio=False,
        reference_images=[top_url],
    )
    log.info(f"Task: {task_id} — bekleniyor")
    result = await kie.async_poll_task(task_id)
    if result.get("status") != "success":
        raise RuntimeError(f"Render başarısız: {result.get('error')}")
    video_url = result["urls"][0]
    if isinstance(video_url, dict):
        video_url = video_url["url"]
    log.info(f"Video URL: {video_url}")

    log.info("İndiriliyor…")
    r = requests.get(video_url, timeout=180)
    r.raise_for_status()
    OUTPUT.write_bytes(r.content)
    log.info(f"✅ Kaydedildi: {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")

    bal_after = kie.get_credit_balance().get("data", 0)
    log.info(f"Sonrası bakiye: {bal_after} (yakım: {bal - bal_after})")


if __name__ == "__main__":
    asyncio.run(main())
