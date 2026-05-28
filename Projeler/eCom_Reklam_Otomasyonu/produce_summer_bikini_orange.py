"""
produce_summer_bikini_orange.py — Lara Arı 2026 Yaz Koleksiyonu / Turuncu Motif.

Mont reklamı tarzında UGC:
  - Karakter SABİT — 'turk kiz.png' referans imaj olarak besleniyor
  - 4 sahne (Hook 4s + Detail 4s + Build 4s + Payoff 4s), toplam 16 sn
  - 9:16 dikey, iPhone selfie hissi
  - ElevenLabs 'Nisa' sesi (genç, Z kuşağı) ile Türkçe voiceover
  - Handmade vurgusu (her motif elde örülmüş + macro detay close-up)

Üretim akışı:
  1. ImgBB'ye 4 referans yüklenir: karakter + üst + alt + etek
  2. KIE / Seedance ile 4 sahne paralel render (~3-5 dk per sahne)
  3. ElevenLabs her sahne için ayrı voiceover üretir
  4. moviepy ile sahneler + ses birleştirilir

Çıktı: hlk-REKLAM\\FINAL_REKLAM_LARA_ARI_TURUNCU.mp4
Maliyet: ~$2.10 (Seedance 375 cr ≈ $1.88 + ElevenLabs ~$0.05 + ImgBB ücretsiz)
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
from services.elevenlabs_service import ElevenLabsService
from logger import get_logger

log = get_logger("produce_summer_bikini_orange")

# ============================================================================
# DOSYA YOLLARI
# ============================================================================
HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
COLLECTION = HLK / "2026 yaz_HANDMADE_BİKİNİ"

CHARACTER_REF = COLLECTION / "turk kiz.png"
PRODUCT_TOP = COLLECTION / "MOTİFTURUNCU-SIZE-36-SUMMERMARKET.jpg"
PRODUCT_BOTTOM = COLLECTION / "MOTİFTURUNCU-SIZE-36-BOTTOM-SUMMERMARKET.jpg"
PRODUCT_SKIRT = COLLECTION / "MOTİFTURUNCU-SIZE-SKIRT-36-SUMMERMARKET.jpg"

OUTPUT_FILE = HLK / "FINAL_REKLAM_LARA_ARI_TURUNCU.mp4"

# ============================================================================
# KARAKTER (mont reklamındaki kız — turk kiz.png ile sabit)
# ============================================================================
CHARACTER_DESC = (
    "The EXACT same young Turkish Gen-Z woman from the reference image — "
    "approximately 20 years old, balayage-blonde hair in a messy top bun "
    "with a few loose face-framing strands, dewy fresh natural makeup with "
    "subtle peachy lip, naturally sun-kissed glowing skin, bright warm "
    "eyes, soft confident playful smile. Same face, same hair, same body "
    "as the reference image — DO NOT generate a different person."
)

# ============================================================================
# ÜRÜN AÇIKLAMASI — GERÇEK RENKLER (handmade vurgusu)
# ============================================================================
PRODUCT_DESC = (
    "Product — TOP piece: hand-crocheted triangle halter bikini top with "
    "vivid fuchsia-pink crochet edging around two diamond granny-square "
    "panels filled with multicolor crochet motifs (fuchsia, orange, "
    "lilac, soft pink, turquoise, mint green, ivory). LONG ORANGE BEADED "
    "FRINGE hanging from the bottom edge of each triangle panel — densely "
    "strung small bright-orange seed beads that sparkle and sway with "
    "movement. Long thin fuchsia-pink braided cord halter neck strap and "
    "back-tie strap, both ending in small multicolor glass beads. "
    "Product — BOTTOM piece (matching set, NOT orange): hand-crocheted "
    "Brazilian-cut brief in DEEP TURQUOISE TEAL color with visible crochet "
    "texture, fuchsia-pink braided cord side-tie straps knotted into bows, "
    "ends terminating in small multicolor glass beads. "
    "Accessory — SKIRT: hand-crocheted granny-square waistband in DEEP "
    "TURQUOISE TEAL with three diamond multicolor motifs (fuchsia, orange, "
    "lilac, mint green) edged in vivid fuchsia-pink trim; the skirt body "
    "is a sheer flowing NEON LIME-GREEN CHIFFON that catches the sunlight, "
    "knee-to-calf length, semi-transparent, with a soft front opening. "
    # ─── FIDELITY ZORLAMASI — renk ve doku bozulmasın ─────────────────────
    "PRODUCT FIDELITY (HIGHEST PRIORITY): preserve the EXACT colors, "
    "EXACT crochet stitch pattern, and EXACT handmade texture from the "
    "reference images — do NOT smooth, blur, simplify, stylize, or "
    "re-invent the crochet. Every individual crochet stitch and granny-"
    "square cell must be visible and sharp. Colors must match the "
    "reference 1:1 — do NOT shift fuchsia toward red/coral, do NOT shift "
    "turquoise toward navy/green, do NOT shift lime-green chiffon toward "
    "yellow or mint. The orange beaded fringe must remain bright orange, "
    "not amber or rust. All pieces CLEARLY artisan handmade — visible "
    "crochet stitches, hand-tied bead strands, slight artisan "
    "irregularities preserved. "
    # ─── ETİKET / LOGO GİZLEME — referansta görünse bile ASLA gösterme ───
    "CRITICAL LABEL REMOVAL (ABSOLUTE — even if visible in the bottom "
    "reference image, you MUST hide it): there must be NO 'LARA ARI' "
    "woven label, NO LARA logo, NO bee logo, NO white rectangular fabric "
    "tag on the inside or outside of the bikini bottom, NO size tag, NO "
    "care label, NO printed text, NO embroidered text, NO letters, NO "
    "numbers anywhere on any garment. If a tag is present in the "
    "reference image, REMOVE IT — render the crochet surface completely "
    "clean and uninterrupted where the tag would be."
)

# ============================================================================
# UGC FORMAT TANIMI
# ============================================================================
FORMAT_SPEC = (
    "9:16 vertical UGC creator footage, handheld iPhone 15 Pro selfie "
    "aesthetic, real skin texture, natural sensor grain, candid imperfect "
    "framing, subtle camera shake — NOT cinematic fashion film. "
    "Enable ambient and environmental sounds (waves, breeze, light beach "
    "chatter). No on-screen text, no captions, no brand watermark, no "
    "dialogue lip-sync, no character speech."
)

# ============================================================================
# 3 SAHNE — Hook → Build → Payoff (mont reklamı yapısı)
# ============================================================================
SCENES = [
    {
        "name": "scene1_hook",
        "duration": 4,
        "voiceover": "Kızlar — Lara Arı'dan yaz koleksiyonu geldi, hepsi el yapımı!",
        "setting": (
            "Setting: sunny beach club terrace at late morning, wooden "
            "deck, palm shadows, blurred turquoise sea in the background, "
            "vibrant joyful summer mood."
        ),
        "action": (
            "She holds up the orange-fringed crochet bikini top close to "
            "the camera in one hand, smiling excitedly with a 'look at "
            "this!' expression, gently shaking it so the long orange "
            "beaded fringe sways and sparkles in the sunlight. Handheld "
            "iPhone front-camera selfie angle, slight wobble, real skin, "
            "phone sensor grain."
        ),
    },
    {
        "name": "scene2_detail",
        "duration": 4,
        "voiceover": "Şu boncuklu püsküllerdeki detaya bakın — tamamen el yapımı!",
        "setting": (
            "Sudden jump cut. Setting: same beach club, sun-lit wooden "
            "table surface or her lap, soft natural sunlight, shallow "
            "depth of field with a warm bokeh background."
        ),
        "action": (
            "EXTREME MACRO CLOSE-UP of the orange-fringed crochet bikini "
            "top — her fingertips gently touch and brush across the "
            "multicolor crochet granny-square panels and lift a strand "
            "of the LONG ORANGE BEADED FRINGE so it sways and the tiny "
            "orange seed beads glint in the sunlight. Each individual "
            "crochet stitch and each bead is SHARP AND CLEARLY VISIBLE. "
            "Camera slowly pans down the fringe. No face in frame — "
            "only hands and the bikini top. Vertical 9:16, handheld "
            "iPhone macro feel, warm afternoon light."
        ),
    },
    {
        "name": "scene3_build",
        "duration": 4,
        "voiceover": "Her motif tek tek örülmüş, bu ürünler aşırı güzel!",
        "setting": (
            "Sudden jump cut. Setting: sandy beach path with sea behind, "
            "warm golden afternoon light, light breeze moving her hair "
            "and the sheer lime-green chiffon skirt."
        ),
        "action": (
            "Now wearing the FULL look — orange-fringed crochet bikini "
            "top, turquoise crochet brief, and the neon lime-green sheer "
            "chiffon skirt with the turquoise multicolor crochet "
            "waistband. She turns slowly in place to reveal the back — "
            "fuchsia-pink back-tie strap of the bikini and the granny-"
            "square crochet waistband of the skirt CLEARLY VISIBLE — then "
            "looks back over her shoulder smiling. Handheld iPhone back-"
            "camera vertical 9:16, gentle motion, fringe and chiffon "
            "moving naturally."
        ),
    },
    {
        "name": "scene4_payoff",
        "duration": 4,
        "voiceover": "Bu yazın favorisi resmen bende!",
        "setting": (
            "Sudden jump cut back to selfie angle. Same beach, warm "
            "late-afternoon light, soft sun flare behind her."
        ),
        "action": (
            "Tight selfie close-up, she throws a peace sign with one "
            "hand and laughs brightly into the camera, the orange beaded "
            "fringe of the bikini top and a hint of the lime chiffon "
            "skirt visible at the bottom of the frame. Front camera, "
            "candid joyful smile, natural movement."
        ),
    },
]


# ============================================================================
# PROMPT BUILDER
# ============================================================================
def build_prompt(scene_def: dict) -> str:
    return (
        f"Character: {CHARACTER_DESC} "
        f"{PRODUCT_DESC} "
        f"{scene_def['setting']} "
        f"Action: {scene_def['action']} "
        f"{FORMAT_SPEC}"
    )


# ============================================================================
# REFERANS GÖRSEL YÜKLEME
# ============================================================================
def upload_reference_images(imgbb: ImgBBService) -> list[str]:
    """Karakter + 3 ürün görselini ImgBB'ye yükler."""
    refs = [CHARACTER_REF, PRODUCT_TOP, PRODUCT_BOTTOM, PRODUCT_SKIRT]
    urls: list[str] = []
    for ref in refs:
        if not ref.exists():
            raise SystemExit(f"Referans görsel yok: {ref}")
        log.info(f"ImgBB upload: {ref.name}")
        with open(ref, "rb") as fh:
            data = fh.read()
        result = imgbb.upload_image_bytes(data, name=ref.stem.replace(" ", "_"))
        log.info(f"  → {result['url']}")
        urls.append(result["url"])
    return urls


# ============================================================================
# SAHNE RENDER (KIE / Seedance)
# ============================================================================
async def render_scene(
    kie: KieAIService, idx: int, scene_def: dict, ref_urls: list[str]
) -> str:
    prompt = build_prompt(scene_def)
    log.info(f"[Sahne {idx + 1}/4] {scene_def['name']} — görev oluşturuluyor")
    task_id = await asyncio.to_thread(
        kie.create_video,
        prompt=prompt,
        duration=scene_def["duration"],
        aspect_ratio="9:16",
        generate_audio=False,
        reference_images=ref_urls,
    )
    log.info(f"[Sahne {idx + 1}/4] task={task_id} — bekleniyor…")
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
    log.info(f"[Sahne {idx + 1}/4] hazır: {video_url[:90]}…")
    return video_url


def download(url: str, dst: Path) -> None:
    log.info(f"İndiriliyor → {dst.name}")
    response = requests.get(url, timeout=180)
    response.raise_for_status()
    dst.write_bytes(response.content)
    log.info(f"  {dst.stat().st_size:,} bytes")


# ============================================================================
# VOICEOVER (ElevenLabs Nisa — Z kuşağı enerjik kadın)
# ============================================================================
def generate_voiceovers(eleven: ElevenLabsService, tmp_dir: Path) -> list[Path]:
    """Her sahne için ayrı mp3 üretir."""
    audio_paths: list[Path] = []
    for i, scene in enumerate(SCENES):
        log.info(f"[Ses {i + 1}/4] {scene['name']}: \"{scene['voiceover']}\"")
        audio_bytes = eleven.generate_speech(
            text=scene["voiceover"],
            voice_name="Nisa",
            stability=0.35,
            similarity_boost=0.75,
            style=0.75,
        )
        path = tmp_dir / f"voice_scene{i + 1}.mp3"
        path.write_bytes(audio_bytes)
        dur = ElevenLabsService.measure_audio_duration(audio_bytes)
        log.info(f"  → {path.name} ({path.stat().st_size:,} bytes, {dur:.1f}s)")
        audio_paths.append(path)
    return audio_paths


# ============================================================================
# BİRLEŞTİRME (moviepy)
# ============================================================================
def concat_with_audio(
    parts: list[Path], audio_paths: list[Path], output: Path
) -> None:
    log.info(f"4 sahne + 4 voiceover birleştiriliyor → {output.name}")
    from moviepy import (
        AudioFileClip,
        VideoFileClip,
        concatenate_videoclips,
    )

    clips = []
    audio_clips = []
    for video_path, audio_path in zip(parts, audio_paths):
        vid = VideoFileClip(str(video_path))
        voice = AudioFileClip(str(audio_path))
        if voice.duration > vid.duration:
            voice = voice.with_duration(vid.duration)
        vid = vid.with_audio(voice)
        clips.append(vid)
        audio_clips.append(voice)

    final = concatenate_videoclips(clips, method="compose")
    output.parent.mkdir(parents=True, exist_ok=True)
    fps = clips[0].fps or 24
    final.write_videofile(
        str(output),
        codec="libx264",
        audio_codec="aac",
        fps=fps,
        preset="medium",
        threads=4,
    )
    for clip in clips:
        clip.close()
    for v in audio_clips:
        v.close()
    final.close()
    log.info(f"✅ Final: {output}")


# ============================================================================
# MAIN
# ============================================================================
async def main() -> None:
    load_dotenv()
    for key in ("IMGBB_API_KEY", "KIE_API_KEY", "ELEVENLABS_API_KEY"):
        if not os.environ.get(key):
            raise SystemExit(f"{key} .env'de eksik")

    if not CHARACTER_REF.exists():
        raise SystemExit(
            f"Karakter referansı yok: {CHARACTER_REF}\n"
            f"Mont reklamındaki karakter görselini bu yola kaydet."
        )

    imgbb = ImgBBService(os.environ["IMGBB_API_KEY"])
    kie = KieAIService(os.environ["KIE_API_KEY"])
    eleven = ElevenLabsService(os.environ["ELEVENLABS_API_KEY"])

    try:
        bal = kie.get_credit_balance()
        bal_val = bal.get("data", 0) if isinstance(bal, dict) else 0
        log.info(f"Kie AI bakiye: {bal_val} kredi (ihtiyaç ≈ 375)")
    except Exception as exc:
        log.warning(f"Bakiye okunamadı: {exc}")

    ref_urls = upload_reference_images(imgbb)

    log.info("4 sahne paralel render başlıyor — Seedance ~3-5 dk per sahne")
    tasks = [render_scene(kie, i, s, ref_urls) for i, s in enumerate(SCENES)]
    scene_urls = await asyncio.gather(*tasks)

    with tempfile.TemporaryDirectory(prefix="orange_bikini_") as tmp:
        tmp_dir = Path(tmp)

        parts: list[Path] = []
        for i, url in enumerate(scene_urls):
            part = tmp_dir / f"scene{i + 1}.mp4"
            download(url, part)
            parts.append(part)

        audio_paths = generate_voiceovers(eleven, tmp_dir)
        concat_with_audio(parts, audio_paths, OUTPUT_FILE)

    log.info(f"🎬 Turuncu motif reklamı hazır: {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
