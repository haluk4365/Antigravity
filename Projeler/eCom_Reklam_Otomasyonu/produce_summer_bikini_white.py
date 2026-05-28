"""
produce_summer_bikini_white.py — Lara Arı / İSTİRİDYE (beyaz-krem, sadece üst+alt).

Çıktı: hlk-REKLAM\\FINAL_REKLAM_LARA_ARI_BEYAZ.mp4
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

log = get_logger("produce_summer_bikini_white")

HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
PARENT = HLK / "LARA_Bikini_230526"
HANDMADE = PARENT / "2026 yaz_HANDMADE_BİKİNİ"

CHARACTER_REF = HANDMADE / "turk kiz.png"
PRODUCT_TOP = PARENT / "İSTİRİDYE-TOP-36-SUNSETMARKET.jpg"
PRODUCT_BOTTOM = PARENT / "İSTİRİDYE-36-SUNSETMARKET.jpg"
PRODUCT_PAREO = PARENT / "PINKWHETHER-SIZE-ONESIZE-BACK-PAREO-SUMMERMARKET.jpg"

RESCUE_DIR = PARENT / "_rescue_beyaz"
AMBIENT_PATH = HANDMADE / "_rescue_turuncu" / "option_3_minimal.mp3"
OUTPUT_FILE = HLK / "FINAL_REKLAM_LARA_ARI_BEYAZ.mp4"

CHARACTER_DESC = (
    "The EXACT same young Turkish Gen-Z woman from the reference image — "
    "approximately 20 years old, SAME FACE and same skin/eye features as "
    "the reference, BUT with a DIFFERENT HAIRSTYLE: long natural "
    "balayage-blonde hair worn DOWN in loose soft beach waves cascading "
    "over her shoulders (NOT in a top bun, NOT pulled up). Dewy fresh "
    "natural makeup with subtle peachy lip, naturally sun-kissed glowing "
    "skin, bright warm eyes, soft confident playful smile. DO NOT "
    "generate a different person — only the hairstyle changes. "
    "She wears a MODERN trendy Gen-Z summer streetwear outfit — a fitted "
    "CROPPED short-sleeve white or soft pastel TANK/CROP TOP with a "
    "delicate thin gold chain necklace and tiny minimal hoop earrings. "
    "Contemporary fashion-forward summer style. NO winter coat, NO fur, "
    "NO fall jacket, NO long sleeves."
)

PRODUCT_DESC = (
    "Product — TOP piece: hand-crocheted triangle halter bikini top in "
    "CREAMY OFF-WHITE / IVORY color with a sculptural 3D SEASHELL / "
    "SCALLOP SHELL TEXTURE on each cup — the cups are shaped and stitched "
    "to mimic the ridged fanning pattern of a clam/oyster shell, with "
    "raised crochet ridges radiating outward. Small natural PEARL BEADS "
    "scattered across the cups as accents. Thin off-white braided cord "
    "halter neck strap and back-tie strap, both ending in tiny round "
    "pearl beads. "
    "Product — BOTTOM piece (matching set): hand-crocheted Brazilian-cut "
    "brief in the SAME CREAMY OFF-WHITE / IVORY color with smooth "
    "horizontal crochet ribs. The front top edge has a row of small "
    "natural PEARL BEADS sewn along a scalloped/ruffled crochet trim. "
    "Thin off-white braided cord side-tie straps on each hip, knotted "
    "into bows, ends terminating in tiny pearl beads. "
    "Accessory — PAREO: hand-crocheted SHEER VERY LIGHT OFF-WHITE pareo "
    "(slightly lighter than the reference image — almost cream-white "
    "with a barely-grey undertone, NOT a strong grey) in a wide open "
    "net/mesh crochet pattern with scalloped edges, worn wrapped around "
    "the HIPS and tied at the side; very airy and light, the open net "
    "holes visible. Color tones perfectly with the ivory bikini set. "
    "NEVER worn as a scarf, NEVER over the shoulders. "
    "PRODUCT FIDELITY (HIGHEST PRIORITY): preserve EXACT creamy-ivory "
    "color (NOT pure white, NOT yellow, NOT grey), EXACT 3D seashell "
    "ridge texture on the top, EXACT smooth ribbed crochet on the "
    "bottom. The pearl beads must remain pearly-white round, not flat, "
    "not colored. Romantic, soft, mermaid/seashell aesthetic. "
    "CRITICAL LABEL REMOVAL (ABSOLUTE — even if visible in the bottom "
    "reference, you MUST hide it): NO 'LARA ARI' woven label, NO LARA "
    "logo, NO bee logo, NO white rectangular fabric tag, NO size tag, "
    "NO printed text, NO letters, NO numbers anywhere. Render the "
    "crochet surface completely clean."
)

FORMAT_SPEC = (
    "9:16 vertical UGC creator footage, handheld iPhone 15 Pro selfie "
    "aesthetic, real skin texture, natural sensor grain, candid imperfect "
    "framing, subtle camera shake — NOT cinematic fashion film. "
    "Enable ambient and environmental sounds. No on-screen text, no "
    "captions, no brand watermark, no dialogue lip-sync, no character speech."
)

# Beyaz/krem için: temiz Aegean kıyısı, parlak öğleden sonra ışığı
SCENES = [
    {
        "name": "scene1_hook",
        "duration": 4,
        "voiceover": "Kızlar — Lara Arı'dan yaz koleksiyonu geldi, hepsi el yapımı!",
        "setting": (
            "Setting: LUXURY WHITE YACHT DECK at midday, polished teak "
            "wood floor, glossy white yacht railings and stairs visible "
            "behind, deep open ocean turquoise/sapphire water all around, "
            "no land in sight, soft warm daylight bouncing off the white "
            "yacht surfaces, vibrant luxe summer mood."
        ),
        "action": (
            "She holds up the ivory seashell crochet bikini top with "
            "BOTH HANDS in front of her chest, the bikini top FULLY "
            "CENTERED and ENTIRELY VISIBLE in the frame — both shell-"
            "shaped cups, both straps and the pearl accents ALL clearly "
            "shown, NOT cut off, NOT cropped. Chest-up framing. She "
            "smiles excitedly with a 'look at this!' expression. "
            "Handheld iPhone front-camera selfie, slight wobble, real "
            "skin, phone sensor grain, soft daylight."
        ),
    },
    {
        "name": "scene2_detail",
        "duration": 4,
        "voiceover": "Şu detaya bakın — tamamen el yapımı!",
        "setting": (
            "Sudden jump cut. Setting: same luxury yacht, close-up on "
            "the polished white teak deck surface, soft natural daylight, "
            "shallow depth of field with creamy ocean-blue bokeh."
        ),
        "action": (
            "EXTREME MACRO CLOSE-UP of the ivory seashell crochet "
            "bikini top — her fingertips gently brush across the 3D "
            "SHELL-RIDGE TEXTURE, lifting and tracing the radiating "
            "ridges, each pearl bead SHARP AND CLEARLY VISIBLE. "
            "Camera slowly pans across one shell-shaped cup. No face "
            "in frame — only hands and the bikini top. Vertical 9:16, "
            "handheld iPhone macro feel, soft natural light."
        ),
    },
    {
        "name": "scene3_build",
        "duration": 4,
        "voiceover": "Her motif tek tek örülmüş, bu ürünler aşırı güzel!",
        "setting": (
            "Sudden jump cut. Setting: same luxury yacht, she stands on "
            "the open deck with the deep turquoise ocean and white yacht "
            "railing behind her, soft warm afternoon light, sea breeze "
            "moving her loose balayage waves naturally."
        ),
        "action": (
            "Now wearing the FULL bikini set — ivory seashell-textured "
            "crochet top and matching ivory crochet bottom with pearl-"
            "trim front. She turns slowly in place to reveal the back "
            "— the ivory back-tie strap CLEARLY VISIBLE, the pearl tips "
            "on the strap ends catching the light — then looks back "
            "over her shoulder smiling. Handweld iPhone back-camera "
            "vertical 9:16, gentle motion."
        ),
    },
    {
        "name": "scene4_payoff",
        "duration": 4,
        "voiceover": "Bu yazın favorisi resmen bende!",
        "setting": (
            "Sudden jump cut back to selfie angle. Same luxury yacht "
            "deck, warm afternoon light, soft sun flare and ocean "
            "horizon behind her."
        ),
        "action": (
            "Tight selfie close-up, she throws a peace sign with one "
            "hand and laughs brightly into the camera, the ivory shell "
            "bikini top visible at the bottom of the frame, warm "
            "daylight glowing on her skin. Front camera, candid joyful."
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
    refs = [CHARACTER_REF, PRODUCT_TOP, PRODUCT_BOTTOM, PRODUCT_PAREO]
    urls = []
    for ref in refs:
        if not ref.exists():
            raise SystemExit(f"Referans yok: {ref}")
        log.info(f"Upload: {ref.name}")
        with open(ref, "rb") as fh:
            data = fh.read()
        safe = "".join(c if c.isascii() else "_" for c in ref.stem).replace(" ", "_")
        urls.append(imgbb.upload_image_bytes(data, name=safe)["url"])
    return urls


async def render_scene(kie, idx, scene_def, ref_urls):
    log.info(f"[Sahne {idx + 1}/4]")
    task_id = await asyncio.to_thread(
        kie.create_video,
        prompt=build_prompt(scene_def),
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
    video_url = urls[0] if not isinstance(urls[0], dict) else urls[0].get("url")
    return video_url


def download(url, dst):
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    dst.write_bytes(r.content)


def generate_voiceovers(eleven, tmp_dir):
    paths = []
    for i, scene in enumerate(SCENES):
        audio = eleven.generate_speech(
            text=scene["voiceover"],
            voice_name="Ahu",
            stability=0.35,
            similarity_boost=0.80,
            style=0.70,
        )
        p = tmp_dir / f"v{i + 1}.mp3"
        p.write_bytes(audio)
        paths.append(p)
    return paths


def concat(parts, audio_paths, ambient, output):
    from moviepy import (
        AudioFileClip,
        CompositeAudioClip,
        VideoFileClip,
        concatenate_videoclips,
    )
    clips, voices = [], []
    for vp, ap in zip(parts, audio_paths):
        vid = VideoFileClip(str(vp))
        voice = AudioFileClip(str(ap))
        if voice.duration > vid.duration:
            voice = voice.with_duration(vid.duration)
        vid = vid.with_audio(voice)
        clips.append(vid); voices.append(voice)
    final = concatenate_videoclips(clips, method="compose")
    amb = AudioFileClip(str(ambient)).with_volume_scaled(0.20)
    if amb.duration > final.duration:
        amb = amb.with_duration(final.duration)
    final = final.with_audio(CompositeAudioClip([amb, final.audio]))
    output.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(
        str(output), codec="libx264", audio_codec="aac",
        fps=clips[0].fps or 24, preset="medium", threads=4, logger=None,
    )
    for c in clips: c.close()
    for v in voices: v.close()
    amb.close(); final.close()


async def main():
    load_dotenv()
    for key in ("IMGBB_API_KEY", "KIE_API_KEY", "ELEVENLABS_API_KEY"):
        if not os.environ.get(key):
            raise SystemExit(f"{key} eksik")
    if not AMBIENT_PATH.exists():
        raise SystemExit(f"Ambient yok: {AMBIENT_PATH}")

    imgbb = ImgBBService(os.environ["IMGBB_API_KEY"])
    kie = KieAIService(os.environ["KIE_API_KEY"])
    eleven = ElevenLabsService(
        os.environ["ELEVENLABS_API_KEY"], model_id="eleven_multilingual_v2"
    )
    log.info(f"KIE bakiye: {kie.get_credit_balance().get('data')}")

    ref_urls = upload_reference_images(imgbb)
    tasks = [render_scene(kie, i, s, ref_urls) for i, s in enumerate(SCENES)]
    scene_urls = await asyncio.gather(*tasks)

    RESCUE_DIR.mkdir(parents=True, exist_ok=True)
    rescue = []
    for i, url in enumerate(scene_urls):
        p = RESCUE_DIR / f"scene{i + 1}.mp4"
        download(url, p)
        rescue.append(p)

    with tempfile.TemporaryDirectory(prefix="white_") as tmp:
        tmp_dir = Path(tmp)
        audios = generate_voiceovers(eleven, tmp_dir)
        concat(rescue, audios, AMBIENT_PATH, OUTPUT_FILE)
    log.info(f"✅ {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
