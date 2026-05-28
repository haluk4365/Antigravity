import os, sys, asyncio, requests
sys.path.append('.')
from dotenv import load_dotenv; load_dotenv()
from services.kie_api import KieAIService

BACK_URL = 'https://i.ibb.co/DDYvvLP2/hlk-LARA025-SIRT-sm.jpg'
OUTPUT = r'c:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM\scene2_sirt.mp4'
PROMPT = (
    "Sudden jump cut from previous angle. The EXACT same person from the reference image "
    "(do not generate a different person - same face, hair, outfit, build): UGC creator footage, "
    "vertical 9:16, handheld iPhone 15 Pro back camera. Setting: urban street with graffiti or brick wall. "
    "Action: girl turns around slowly to face away from camera, clearly showing the BACK of the jacket - "
    "the beige faux fur back panel, cream sleeves, brown leather lower section, and black studded cuffs - "
    "exactly as in the back-view reference image. Then she confidently walks away. "
    "Behavior detail: slight motion blur, real skin texture, phone sensor grain. "
    "No character dialogue, no lip movement. Enable ambient and environmental sounds."
)

async def run():
    kie = KieAIService(os.environ.get('KIE_API_KEY'))
    print('Gorev olusturuluyor...')
    task_id = kie.create_video(
        prompt=PROMPT,
        duration=6,
        aspect_ratio='9:16',
        reference_images=[BACK_URL]
    )
    print(f'Task ID: {task_id}')
    print('Tamamlanmasi bekleniyor (3-5 dk)...')
    result = await kie.async_poll_task(task_id)
    status = result.get('status', '')
    print(f'Durum: {status}')
    outputs = result.get('outputs') or []
    if outputs:
        url = outputs[0].get('url') or outputs[0]
        print(f'Video URL: {url}')
        r = requests.get(url)
        r.raise_for_status()
        with open(OUTPUT, 'wb') as f:
            f.write(r.content)
        print(f'Kaydedildi: {OUTPUT}')
    else:
        print('Cikti bulunamadi:')
        print(result)

asyncio.run(run())
