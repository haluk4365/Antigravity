"""
produce_pink_ad.py — Lara Arı pembe bikini reklam filmi.

3 sahne, 3 farklı manken (sarışın / kızıl / kumral), 3 bağlantılı mekan,
toplam 15 sn, tam sessiz video. Pipeline'ın karakter-sabitleme mantığını
atlamak için Kie API'yı doğrudan çağırır:
  - Her sahnede sadece ÜRÜN görselleri reference olarak verilir
  - Manken tarifi prompt'a gömülüdür (her sahnede farklı)
  - generate_audio=False → sessiz video
3 sahne paralel render → moviepy concat → tek mp4.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.imgbb_service import ImgBBService
from services.kie_api import KieAIService
from logger import get_logger

log = get_logger("produce_pink_ad")

PINK_B2 = r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM\PINK-b2.jpg"
OUTPUT_DIR = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
OUTPUT_FILE = OUTPUT_DIR / "FINAL_REKLAM_LARA_ARI_PINK_v4.mp4"

PRODUCT_DESC = (
    "Product — TOP piece: the EXACT triangle halter top from the reference "
    "image — vivid hot-pink crochet, densely covered with multicolor crochet "
    "flowers (orange, royal blue, yellow, light gray, cream, turquoise, green) "
    "on the cups. The top is a HALTER style — it MUST have two CLEARLY VISIBLE "
    "thin pink crochet straps: (1) a HALTER NECK STRAP rising from the inner "
    "top of each cup, crossing up and around behind the neck and tying at the "
    "nape; (2) a BACK-TIE STRAP running from the outer side of each cup around "
    "the upper back and tying behind. The top is NEVER strapless or bandeau — "
    "the straps must be visible in every shot. Both strap ends terminate ONLY "
    "with TINY TRANSLUCENT PINK GLASS BEADS — like small round pink crystal "
    "pendants, exactly as shown in the reference. "
    "ABSOLUTELY NO flower charms on the top straps; NO yellow flowers, NO "
    "turquoise flowers, NO crochet motifs anywhere on the top strings. "
    "Product — BOTTOM piece (NOT in the reference; build it from this "
    "description): matching hot-pink crochet side-tied briefs in the SAME "
    "vivid hot-pink color and crochet texture as the top. Thin pink crochet "
    "side-tie straps; from each of the TWO BOTTOM SIDE-TIE ENDS (left hip "
    "and right hip) hang small crochet flower charms — one yellow and one "
    "turquoise per side. Crochet flower charms exist ONLY on the bottom hip "
    "ties — never on the top. "
    "CRITICAL — NO brand labels, NO clothing tags, NO 'LARA ARI' woven label, "
    "NO white rectangular labels, NO logos, NO printed text anywhere on the "
    "bikini. The bikini surface must be completely clean."
)

FORMAT_SPEC = (
    "9:16 vertical, professional cinematic photography, sharp focus on the bikini "
    "details, color-graded, no on-screen text, no captions, no brand labels, "
    "no logos, no clothing tags. Completely silent — no music, no dialogue, "
    "no voice-over, no narration."
)

SCENES = [
    {
        "name": "scene1_blonde_balcony",
        "duration": 5,
        "model": (
            "A 22-year-old natural blonde Mediterranean woman, approximately "
            "170 cm tall, slim athletic build, long softly-waved natural blonde "
            "hair, light skin with subtle warm undertone, fresh natural makeup, "
            "soft confident smile, editorial natural beauty"
        ),
        "scene": (
            "Setting: an elegant seaside hotel / villa balcony in early morning, "
            "Aegean / Mediterranean sea visible behind a white railing, pastel "
            "soft sun, gentle warm fill, neutral white-balance, professional "
            "fashion-film lighting."
        ),
        "action": (
            "She steps out onto the balcony wearing the bikini, gently stretches "
            "her arms while looking toward the sea, calm natural smile. Slow "
            "stabilized handheld camera, subtle parallax."
        ),
    },
    {
        "name": "scene2_redhead_pool",
        "duration": 5,
        "model": (
            "A different woman: a 23-year-old red-haired Mediterranean woman, "
            "approximately 170 cm tall, slim athletic build, long wavy bright "
            "copper-red hair, fair skin with light freckles, fresh natural "
            "makeup, calm confident expression"
        ),
        "scene": (
            "Setting: a modern rooftop infinity pool at bright midday, sea or "
            "city horizon behind, saturated turquoise water, polarized clean "
            "light, professional fashion-film lighting; the fuchsia bikini "
            "contrasts the blue pool."
        ),
        "action": (
            "She sits on the pool edge, dipping her feet into the water, in "
            "side-profile to camera. Smooth slow lateral dolly from right to "
            "left clearly showing both the bikini top and bottom details. "
            "Subtle slow motion."
        ),
    },
    {
        "name": "scene3_auburn_beach",
        "duration": 5,
        "model": (
            "A different woman: a 24-year-old auburn (warm chestnut) Turkish / "
            "Mediterranean woman, approximately 170 cm tall, slim athletic "
            "build, long natural auburn wavy hair, lightly sun-kissed skin, "
            "soft warm natural makeup, warm confident smile"
        ),
        "scene": (
            "Setting: a golden-hour Mediterranean sandy beach with soft waves, "
            "warm amber backlight, rim light glowing on her hair, shallow depth "
            "of field, cinematic fashion-film color grading."
        ),
        "action": (
            "She walks along the wet sand toward the sea, then turns her head "
            "over her shoulder back to the camera and smiles, waves breaking "
            "softly behind her. The pink crochet halter neck strap behind her "
            "neck and the back-tie strap across her upper back are CLEARLY "
            "VISIBLE throughout the shot; the tiny pink glass beads at the "
            "strap tips are visible. Smooth handheld follow, then subtle "
            "slow motion on the smile."
        ),
    },
]


def build_prompt(scene_def: dict) -> str:
    return (
        f"Product: {PRODUCT_DESC} "
        f"Model: {scene_def['model']}, wearing the bikini described above. "
        f"{scene_def['scene']} "
        f"Action: {scene_def['action']} "
        f"{FORMAT_SPEC}"
    )


def upload_product_images(imgbb: ImgBBService) -> list[str]:
    log.info(f"ImgBB upload: {Path(PINK_B2).name} (only top — bottom is described in prompt)")
    with open(PINK_B2, "rb") as fh:
        data = fh.read()
    result = imgbb.upload_image_bytes(data, name=Path(PINK_B2).stem)
    log.info(f"  → {result['url']}")
    return [result["url"]]


async def render_scene(
    kie: KieAIService, idx: int, scene_def: dict, ref_urls: list[str]
) -> str:
    prompt = build_prompt(scene_def)
    log.info(f"[Sahne {idx + 1}/3] {scene_def['name']} — görev oluşturuluyor")
    task_id = await asyncio.to_thread(
        kie.create_video,
        prompt=prompt,
        duration=scene_def["duration"],
        aspect_ratio="9:16",
        generate_audio=False,
        reference_images=ref_urls,
    )
    log.info(f"[Sahne {idx + 1}/3] task={task_id} — bekleniyor…")
    result = await kie.async_poll_task(task_id)
    if result.get("status") != "success":
        raise RuntimeError(
            f"Sahne {idx + 1} başarısız: {result.get('error', 'unknown')}"
        )
    urls = result.get("urls") or []
    if not urls:
        raise RuntimeError(f"Sahne {idx + 1}: video URL alınamadı: {result}")
    video_url = urls[0]
    if isinstance(video_url, dict):
        video_url = video_url.get("url") or ""
    log.info(f"[Sahne {idx + 1}/3] hazır: {video_url[:90]}…")
    return video_url


def download(url: str, dst: Path) -> None:
    log.info(f"İndiriliyor → {dst.name}")
    response = requests.get(url, timeout=180)
    response.raise_for_status()
    dst.write_bytes(response.content)
    log.info(f"  {dst.stat().st_size:,} bytes")


def concat(parts: list[Path], output: Path) -> None:
    log.info(f"3 sahne moviepy ile birleştiriliyor → {output.name}")
    from moviepy import VideoFileClip, concatenate_videoclips

    clips = [VideoFileClip(str(p)) for p in parts]
    final = concatenate_videoclips(clips, method="compose")
    output.parent.mkdir(parents=True, exist_ok=True)
    fps = clips[0].fps or 24
    final.write_videofile(
        str(output),
        codec="libx264",
        audio=False,
        fps=fps,
        preset="medium",
        threads=4,
    )
    for clip in clips:
        clip.close()
    final.close()
    log.info(f"✅ Final: {output}")


async def main() -> None:
    load_dotenv()
    imgbb_key = os.environ.get("IMGBB_API_KEY")
    kie_key = os.environ.get("KIE_API_KEY")
    if not imgbb_key or not kie_key:
        raise SystemExit("IMGBB_API_KEY veya KIE_API_KEY .env'de eksik")

    imgbb = ImgBBService(imgbb_key)
    kie = KieAIService(kie_key)

    try:
        bal = kie.get_credit_balance()
        bal_val = bal.get("data", 0) if isinstance(bal, dict) else 0
        log.info(f"Kie AI bakiye: {bal_val} kredi (ihtiyaç ≈ 375)")
    except Exception as exc:
        log.warning(f"Bakiye okunamadı: {exc}")

    ref_urls = upload_product_images(imgbb)

    log.info("3 sahne paralel render başlıyor — Seedance ~3-5 dk per sahne")
    tasks = [render_scene(kie, i, s, ref_urls) for i, s in enumerate(SCENES)]
    scene_urls = await asyncio.gather(*tasks)

    with tempfile.TemporaryDirectory(prefix="pink_ad_") as tmp:
        tmp_dir = Path(tmp)
        parts: list[Path] = []
        for i, url in enumerate(scene_urls):
            part = tmp_dir / f"scene{i + 1}.mp4"
            download(url, part)
            parts.append(part)
        concat(parts, OUTPUT_FILE)

    log.info(f"🎬 Reklam hazır: {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
