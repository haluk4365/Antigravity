import os, sys, asyncio, requests, base64, httpx
sys.path.append('.')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image

# 1. Gorseli kucult (max 2000px)
src = r'C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM\lara_hlk_rklm.01\hlk_LARA025.02.JPG'
dst = r'C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM\lara_hlk_rklm.01\hlk_LARA025_SIRT_sm.jpg'

img = Image.open(src)
print(f'Orijinal boyut: {img.size}')
img.thumbnail((2000, 2000), Image.LANCZOS)
img.save(dst, 'JPEG', quality=90)
print(f'Kucultuldu: {img.size}')

# 2. ImgBB ye yukle
imgbb_key = os.environ.get('IMGBB_API_KEY')
with open(dst, 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

resp = httpx.post(
    'https://api.imgbb.com/1/upload',
    data={'key': imgbb_key, 'name': 'hlk_LARA025_SIRT_sm', 'image': img_b64},
    timeout=30
)
data = resp.json()
if data.get('success'):
    url = data['data']['url']
    print(f'ImgBB URL: {url}')
else:
    print(f'Hata: {data}')
