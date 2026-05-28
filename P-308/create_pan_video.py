import os
import glob
from PIL import Image, ImageFilter
import imageio
import numpy as np

from moviepy import VideoFileClip, AudioFileClip, afx

folder = os.path.dirname(os.path.abspath(__file__))
images = [img for img in (glob.glob(os.path.join(folder, "*.jpeg")) + glob.glob(os.path.join(folder, "*.jpg")) + glob.glob(os.path.join(folder, "*.png"))) if "peugeot_" not in os.path.basename(img).lower()]

if not images:
    print("No images found!")
    exit(1)

print(f"Found {len(images)} images.")

FPS = 30
DURATION_PER_IMG = 6.0  # seconds
TRANSITION_DURATION = 2.0  # seconds
TARGET_SIZE = (1920, 1080)
ZOOM_FACTOR = 1.15

frames_per_img = int(DURATION_PER_IMG * FPS)
trans_frames = int(TRANSITION_DURATION * FPS)

def create_frame_with_blurred_bg(img, target_size, progress):
    tw, th = target_size
    iw, ih = img.size
    
    bg_aspect = tw / th
    img_aspect = iw / ih
    
    if img_aspect > bg_aspect:
        bg_w = int(ih * bg_aspect)
        bg_h = ih
    else:
        bg_w = iw
        bg_h = int(iw / bg_aspect)
        
    bg_box = ( (iw - bg_w)//2, (ih - bg_h)//2, (iw + bg_w)//2, (ih + bg_h)//2 )
    bg = img.resize(target_size, box=bg_box, resample=Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(30))
    
    if img_aspect > bg_aspect:
        fg_w = tw
        fg_h = int(tw / img_aspect)
    else:
        fg_w = int(th * img_aspect)
        fg_h = th
        
    zoom = 1.0 + 0.1 * progress
    fg_w_zoomed = int(fg_w * zoom)
    fg_h_zoomed = int(fg_h * zoom)
    
    fg = img.resize((fg_w_zoomed, fg_h_zoomed), resample=Image.Resampling.LANCZOS)
    
    bg.paste(fg, ((tw - fg_w_zoomed)//2, (th - fg_h_zoomed)//2))
    return bg

def generate_frames():
    previous_img_frames = []
    
    for i, img_path in enumerate(images):
        print(f"Processing image {i+1}/{len(images)}: {os.path.basename(img_path)}")
        img = Image.open(img_path).convert("RGB")
        
        current_img_frames = []
        for f in range(frames_per_img):
            progress = f / max(1, frames_per_img - 1)
            if i % 2 == 1:
                progress = 1.0 - progress
                
            frame_img = create_frame_with_blurred_bg(img, TARGET_SIZE, progress)
            current_img_frames.append(frame_img)
        
        if previous_img_frames:
            for frame in previous_img_frames[:-trans_frames]:
                yield frame
                
            for j in range(trans_frames):
                alpha = (j + 1) / trans_frames
                f1 = previous_img_frames[-trans_frames + j]
                f2 = current_img_frames[j]
                
                offset_x1 = int(TARGET_SIZE[0] * 0.05 * alpha)
                offset_y1 = int(TARGET_SIZE[1] * 0.05 * alpha)
                
                offset_x2 = int(TARGET_SIZE[0] * 0.05 * (1 - alpha))
                offset_y2 = int(TARGET_SIZE[1] * 0.05 * (1 - alpha))
                
                bg1 = Image.new('RGB', TARGET_SIZE)
                bg1.paste(f1, (-offset_x1, offset_y1))
                
                bg2 = Image.new('RGB', TARGET_SIZE)
                bg2.paste(f2, (offset_x2, -offset_y2))
                
                blended = Image.blend(bg1, bg2, alpha)
                yield blended
                
            previous_img_frames = current_img_frames[trans_frames:]
        else:
            previous_img_frames = current_img_frames
            
    for frame in previous_img_frames:
        yield frame

temp_output_path = os.path.join(folder, "temp_video.mp4")
final_output_path = os.path.join(folder, "M-308 video_06.mp4")
audio_path = os.path.join(folder, "violin_music.mp3")

print("Generating video frames...")
writer = imageio.get_writer(temp_output_path, fps=FPS, macro_block_size=None, quality=8)

for frame_idx, frame in enumerate(generate_frames()):
    if frame_idx % 30 == 0:
        print(f"Writing frame {frame_idx}...")
    writer.append_data(np.array(frame))

writer.close()

print("Adding music...")
try:
    video_clip = VideoFileClip(temp_output_path)
    audio_clip = AudioFileClip(audio_path)
    
    if audio_clip.duration < video_clip.duration:
        audio_clip = audio_clip.with_effects([afx.AudioLoop(duration=video_clip.duration)])
    else:
        audio_clip = audio_clip.subclipped(0, video_clip.duration)
        
    audio_clip = audio_clip.with_effects([afx.AudioFadeOut(2)])
    
    final_clip = video_clip.with_audio(audio_clip)
    final_clip.write_videofile(final_output_path, codec="libx264", audio_codec="aac", fps=FPS)
    
    video_clip.close()
    audio_clip.close()
    final_clip.close()
    os.remove(temp_output_path)
    print(f"Final video saved to {final_output_path}")
except Exception as e:
    print(f"Error adding music: {e}")
