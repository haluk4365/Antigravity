"""
produce_summer_bikini_purple.py — Lara Arı 2026 Yaz / Mor Motif.

Turuncu script'inin mor versiyonu. Aynı karakter (turk kiz.png), aynı
voiceover metinleri, aynı 4-sahne yapısı (4+4+4+4 = 16s, 9:16 UGC).
Farklı: ürün dosyaları, renk paleti, gün batımı atmosferi.

Çıktı: hlk-REKLAM\\FINAL_REKLAM_LARA_ARI_MOR.mp4
Maliyet: ~$2.25 (KIE 450 cr + ElevenLabs abonelikte)
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

log = get_logger("produce_summer_bikini_purple")

HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
COLLECTION = HLK / "2026 yaz_HANDMADE_BİKİNİ"

CHARACTER_REF = COLLECTION / "turk kiz.png"
PRODUCT_TOP = COLLECTION / "MOTİFMOR-SIZE-36-SUMMERMARKET.jpg"
PRODUCT_BOTTOM = COLLECTION / "MOTİFMOR-SIZE-36-BOTTOM-SUMMERMARKET.jpg"
PRODUCT_SKIRT = COLLECTION / "MOTİFMOR-SIZE-36-SKIRT-SUMMERMARKET.jpg"

RESCUE_DIR = COLLECTION / "_rescue_mor"
AMBIENT_PATH = COLLECTION / "_rescue_turuncu" / "option_3_minimal.mp3"  # aynı ambient
OUTPUT_FILE = HLK / "FINAL_REKLAM_LARA_ARI_MOR.mp4"

CHARACTER_DESC = (
    "The EXACT same young Turkish Gen-Z woman from the reference image — "
    "approximately 20 years old, balayage-blonde hair in a messy top bun "
    "with a few loose face-framing strands, dewy fresh natural makeup with "
    "subtle peachy lip, naturally sun-kissed glowing skin, bright warm "
    "eyes, soft confident playful smile. Same face, same hair, same body "
    "as the reference image — DO NOT generate a different person."
)

PRODUCT_DESC = (
    "Product — TOP piece: hand-crocheted triangle halter bikini top with "
    "BLACK crochet edging around two diamond granny-square panels filled "
    "with multicolor crochet motifs (deep PURPLE/LILAC, olive-green, white, "
    "magenta pink, black). LONG MULTICOLOR BEADED FRINGE hanging from the "
    "bottom edge of each triangle panel — densely strung small seed beads in "
    "PURPLE, LILAC, LIME-GREEN, MAGENTA-PINK, and CLEAR-SILVER mix that "
    "sparkle and sway with movement. Long thin BLACK braided cord halter "
    "neck strap and back-tie strap, both ending in small multicolor glass "
    "beads (purple, pink, green). "
    "Product — BOTTOM piece (matching set): hand-crocheted Brazilian-cut "
    "brief in solid LIGHT LILAC / LAVENDER PURPLE color with visible "
    "crochet texture. BLACK braided cord side-tie straps knotted into "
    "bows, ends terminating in small multicolor glass beads (purple, "
    "green, pink). "
    "Accessory — SKIRT: hand-crocheted granny-square waistband in DEEP "
    "BLACK crochet with three diamond multicolor motifs (purple, olive-"
    "green, magenta-pink, white) edged in vivid LILAC PURPLE trim; the "
    "skirt body is a sheer flowing BUBBLEGUM PINK CHIFFON (NOT hot pink, "
    "NOT magenta — soft warm bubblegum pink) that catches the sunlight, "
    "knee-to-calf length, semi-transparent, with a soft front opening. "
    "PRODUCT FIDELITY (HIGHEST PRIORITY): preserve EXACT colors, EXACT "
    "crochet stitch pattern, EXACT handmade texture from the reference "
    "images. Do NOT smooth, blur, simplify, stylize, or re-invent the "
    "crochet. Every individual crochet stitch and granny-square cell must "
    "be visible and sharp. Colors must match the reference 1:1 — do NOT "
    "shift lilac toward navy/grey, do NOT shift bubblegum pink toward red "
    "or magenta, do NOT shift the black edging toward dark brown. "
    "CRITICAL LABEL REMOVAL (ABSOLUTE — even if visible in the bottom "
    "reference, you MUST hide it): there must be NO 'LARA ARI' woven "
    "label, NO LARA logo, NO bee logo, NO white rectangular fabric tag, "
    "NO size tag, NO care label, NO printed text, NO letters, NO numbers "
    "anywhere on any garment. Render the crochet surface completely "
    "clean and uninterrupted where the tag would be."
)

FORMAT_SPEC = (
    "9:16 vertical UGC creator footage, handheld iPhone 15 Pro selfie "
    "aesthetic, real skin texture, natural sensor grain, candid imperfect "
    "framing, subtle camera shake — NOT cinematic fashion film. "
    "Enable ambient and environmental sounds. No on-screen text, no "
    "captions, no brand watermark, no dialogue lip-sync, no character speech."
)

# Sahne ortamı: gün batımı / altın saat (turuncudaki öğlen plaj kulübünden farklı)
SCENES = [
    {
        "name": "scene1_hook",
        "duration": 4,
        "voiceover": "Kızlar — Lara Arı'dan yaz koleksiyonu geldi, hepsi el yapımı!",
        "setting": (
            "Setting: sunset golden-hour seaside terrace, warm amber light, "
            "deep blue ocean and rocky coastline visible behind, vibrant "
            "evening summer mood."
        ),
        "action": (
            "She holds up the multicolor-fringed black-edged crochet bikini "
            "top close to the camera in one hand, smiling excitedly with a "
            "'look at this!' expression, gently shaking it so the long "
            "multicolor beaded fringe sways and sparkles in the warm "
            "sunset light. Handheld iPhone front-camera selfie angle, "
            "slight wobble, real skin, phone sensor grain."
        ),
    },
    {
        "name": "scene2_detail",
        "duration": 4,
        "voiceover": "Şu boncuklu püsküllerdeki detaya bakın — tamamen el yapımı!",
        "setting": (
            "Sudden jump cut. Setting: warm golden hour close-up, sun-lit "
            "wooden surface or her lap, soft natural sunset light, shallow "
            "depth of field with warm pink-amber bokeh background."
        ),
        "action": (
            "EXTREME MACRO CLOSE-UP of the multicolor-fringed crochet "
            "bikini top — her fingertips gently touch and brush across "
            "the multicolor crochet granny-square panels and lift a "
            "strand of the LONG MULTICOLOR BEADED FRINGE so it sways "
            "and the tiny purple/pink/green seed beads glint in the "
            "sunset light. Each individual crochet stitch and each bead "
            "is SHARP AND CLEARLY VISIBLE. Camera slowly pans down the "
            "fringe. No face in frame — only hands and the bikini top. "
            "Vertical 9:16, handheld iPhone macro feel, warm sunset light."
        ),
    },
    {
        "name": "scene3_build",
        "duration": 4,
        "voiceover": "Her motif tek tek örülmüş, bu ürünler aşırı güzel!",
        "setting": (
            "Sudden jump cut. Setting: rocky coastal cliff path at sunset, "
            "warm pink and amber sky, ocean below, light breeze moving her "
            "hair and the sheer bubblegum pink chiffon skirt."
        ),
        "action": (
            "Now wearing the FULL look — multicolor-fringed black-edged "
            "crochet bikini top, lilac crochet brief, and the bubblegum "
            "pink sheer chiffon skirt with the black multicolor crochet "
            "granny-square waistband. She turns slowly in place to "
            "reveal the back — the black back-tie strap of the bikini "
            "and the black granny-square crochet waistband of the skirt "
            "CLEARLY VISIBLE — then looks back over her shoulder smiling. "
            "Handheld iPhone back-camera vertical 9:16, gentle motion, "
            "fringe and chiffon moving naturally in the breeze."
        ),
    },
    {
        "name": "scene4_payoff",
        "duration": 4,
        "voiceover": "Bu yazın favorisi resmen bende!",
        "setting": (
            "Sudden jump cut back to selfie angle. Same coastal sunset "
            "setting, warm late-golden light, soft sun flare behind her."
        ),
        "action": (
            "Tight selfie close-up, she throws a peace sign with one "
            "hand and laughs brightly into the camera, the multicolor "
            "beaded fringe of the bikini top and a hint of the bubblegum "
            "pink chiffon skirt visible at the bottom of the frame. "
            "Front camera, candid joyful smile, natural movement."
        ),
    },
]


def build_prompt(scene_def: dict) -> str:
    return (
        f"Character: {CHARACTER_DESC} "
        f"{PRODUCT_DESC} "
        f"{scene_def['setting']} "
        f"Action: {scene_def['action']} "
        f"{FORMAT_SPEC}"
    )


def upload_reference_images(imgbb: ImgBBService) -> list[str]:
    refs = [CHARACTER_REF, PRODUCT_TOP, PRODUCT_BOTTOM, PRODUCT_SKIRT]
    urls: list[str] = []
    for ref in refs:
        if not ref.exists():
            raise SystemExit(f"Referans yok: {ref}")
        log.info(f"ImgBB upload: {ref.name}")
        with open(ref, "rb") as fh:
            data = fh.read()
        result = imgbb.upload_image_bytes(data, name=ref.stem.replace(" ", "_"))
        urls.append(result["url"])
    return urls


async def render_scene(
    kie: KieAIService, idx: int, scene_def: dict, ref_urls: list[str]
) -> str:
    prompt = build_prompt(scene_def)
    log.info(f"[Sahne {idx + 1}/4] {scene_def['name']} — task oluştur")
    task_id = await asyncio.to_thread(
        kie.create_video,
        prompt=prompt,
        duration=scene_def["duration"],
        aspect_ratio="9:16",
        generate_audio=False,
        reference_images=ref_urls,
    )
    result = await kie.async_poll_task(task_id)
    if result.get("status") != "success":
        raise RuntimeError(f"Sahne {idx + 1} fail: {result.get('error', '?')}")
    urls = result.get("urls") or []
    if not urls:
        raise RuntimeError(f"Sahne {idx + 1} URL boş")
    video_url = urls[0]
    if isinstance(video_url, dict):
        video_url = video_url.get("url") or ""
    log.info(f"[Sahne {idx + 1}/4] hazır")
    return video_url


def download(url: str, dst: Path) -> None:
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    dst.write_bytes(r.content)


def generate_voiceovers(eleven: ElevenLabsService, tmp_dir: Path) -> list[Path]:
    paths = []
    for i, scene in enumerate(SCENES):
        audio = eleven.generate_speech(
            text=scene["voiceover"],
            voice_name="Ahu",
            stability=0.55,
            similarity_boost=0.80,
            style=0.40,
        )
        p = tmp_dir / f"voice_scene{i + 1}.mp3"
        p.write_bytes(audio)
        paths.append(p)
    return paths


def concat_with_voice_and_ambient(
    parts: list[Path],
    audio_paths: list[Path],
    ambient_path: Path,
    output: Path,
    ambient_volume: float = 0.20,
) -> None:
    from moviepy import (
        AudioFileClip,
        CompositeAudioClip,
        VideoFileClip,
        concatenate_videoclips,
    )

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

    final = concatenate_videoclips(clips, method="compose")
    ambient = AudioFileClip(str(ambient_path)).with_volume_scaled(ambient_volume)
    if ambient.duration > final.duration:
        ambient = ambient.with_duration(final.duration)
    composite = CompositeAudioClip([ambient, final.audio])
    final = final.with_audio(composite)
    output.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(
        str(output),
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


async def main() -> None:
    load_dotenv()
    for key in ("IMGBB_API_KEY", "KIE_API_KEY", "ELEVENLABS_API_KEY"):
        if not os.environ.get(key):
            raise SystemExit(f"{key} eksik")
    if not AMBIENT_PATH.exists():
        raise SystemExit(f"Ambient yok: {AMBIENT_PATH}")

    imgbb = ImgBBService(os.environ["IMGBB_API_KEY"])
    kie = KieAIService(os.environ["KIE_API_KEY"])
    eleven = ElevenLabsService(
        os.environ["ELEVENLABS_API_KEY"],
        model_id="eleven_multilingual_v2",
    )

    bal = kie.get_credit_balance()
    bal_val = bal.get("data", 0) if isinstance(bal, dict) else 0
    log.info(f"KIE bakiye: {bal_val} kredi")

    ref_urls = upload_reference_images(imgbb)
    log.info("4 sahne paralel render")
    tasks = [render_scene(kie, i, s, ref_urls) for i, s in enumerate(SCENES)]
    scene_urls = await asyncio.gather(*tasks)

    # Sahneleri kalıcı _rescue_mor klasörüne kaydet (önceki turuncu deneyiminden öğrendik)
    RESCUE_DIR.mkdir(parents=True, exist_ok=True)
    rescue_paths = []
    for i, url in enumerate(scene_urls):
        p = RESCUE_DIR / f"scene{i + 1}.mp4"
        download(url, p)
        rescue_paths.append(p)
        log.info(f"Kurtarıldı: {p.name}")

    with tempfile.TemporaryDirectory(prefix="purple_") as tmp:
        tmp_dir = Path(tmp)
        audio_paths = generate_voiceovers(eleven, tmp_dir)
        concat_with_voice_and_ambient(
            rescue_paths, audio_paths, AMBIENT_PATH, OUTPUT_FILE
        )
    log.info(f"✅ {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
