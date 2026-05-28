import os
import glob
from PIL import Image
import imageio
import numpy as np

folder = r"c:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\P-308"
images = glob.glob(os.path.join(folder, "*.jpeg")) + glob.glob(os.path.join(folder, "*.jpg"))

if not images:
    print("No images found!")
    exit(1)

print(f"Found {len(images)} images.")

FPS = 30
DURATION_PER_IMG = 3.0  # seconds
TRANSITION_DURATION = 0.5  # seconds
TARGET_SIZE = (1920, 1080)

frames_per_img = int(DURATION_PER_IMG * FPS)
trans_frames = int(TRANSITION_DURATION * FPS)

def get_crop_box(img_size, target_size, zoom_factor=1.0):
    iw, ih = img_size
    tw, th = target_size
    
    target_aspect = tw / th
    img_aspect = iw / ih
    
    if img_aspect > target_aspect:
        new_w = int(ih * target_aspect)
        new_h = ih
    else:
        new_w = iw
        new_h = int(iw / target_aspect)
        
    new_w = int(new_w / zoom_factor)
    new_h = int(new_h / zoom_factor)
    
    left = (iw - new_w) / 2
    top = (ih - new_h) / 2
    right = left + new_w
    bottom = top + new_h
    
    return (left, top, right, bottom)

def generate_frames():
    previous_img_frames = []
    
    for i, img_path in enumerate(images):
        print(f"Processing image {i+1}/{len(images)}: {os.path.basename(img_path)}")
        img = Image.open(img_path).convert("RGB")
        
        current_img_frames = []
        for f in range(frames_per_img):
            # Zoom from 1.0 to 1.15
            zoom = 1.0 + (0.15 * (f / frames_per_img))
            box = get_crop_box(img.size, TARGET_SIZE, zoom)
            
            frame_img = img.resize(TARGET_SIZE, box=box, resample=Image.Resampling.LANCZOS)
            current_img_frames.append(frame_img)
        
        if previous_img_frames:
            # Yield non-overlapping part of previous image
            for frame in previous_img_frames[:-trans_frames]:
                yield frame
                
            # Crossfade
            for j in range(trans_frames):
                alpha = (j + 1) / trans_frames
                f1 = previous_img_frames[-trans_frames + j]
                f2 = current_img_frames[j]
                blended = Image.blend(f1, f2, alpha)
                yield blended
                
            previous_img_frames = current_img_frames[trans_frames:]
        else:
            previous_img_frames = current_img_frames
            
    # Yield remaining frames of the last image
    for frame in previous_img_frames:
        yield frame

output_path = os.path.join(folder, "Professional_Slideshow.mp4")
writer = imageio.get_writer(output_path, fps=FPS, macro_block_size=None, quality=8)

for frame_idx, frame in enumerate(generate_frames()):
    if frame_idx % 30 == 0:
        print(f"Writing frame {frame_idx}...")
    writer.append_data(np.array(frame))

writer.close()
print(f"Video saved to {output_path}")
