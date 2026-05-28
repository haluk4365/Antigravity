"""
merge_lara_sunset.py — Mevcut 3 sahneyi Sunset Light Leak geçişleri, ses patlama koruması ve dalga efekti ile birleştir
"""

import sys
import os
import shutil
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from logger import get_logger

log = get_logger("merge_lara_sunset")

HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
SUNSET_DIR = HLK / "LARA_Sunset_230526"

SCENE1_FILE = SUNSET_DIR / "TEST_SCENE1_BRASIL_HOOK.mp4"
SCENE2_FILE = SUNSET_DIR / "SCENE2_TURKISH_DELIGHT.mp4"
SCENE3_FILE = SUNSET_DIR / "SCENE3_FINAL_MOMENT.mp4"
FINAL_FILE = SUNSET_DIR / "FINAL_REKLAM_LARA_SUNSET.mp4"
AMBIENT_FILE = SUNSET_DIR / "ocean_waves_ambient.mp3"

log.info("=" * 70)
log.info("Sahneler geçiş ses patlama korumalı ve %12 dalga sesiyle birleştiriliyor...")
log.info("=" * 70)

# Dosya kontrol
for label, path in [("Sahne 1", SCENE1_FILE), ("Sahne 2", SCENE2_FILE), ("Sahne 3", SCENE3_FILE)]:
    if not path.exists():
        log.error(f"  ❌ {label} bulunamadı: {path}")
        sys.exit(1)
    size_mb = path.stat().st_size / (1024*1024)
    log.info(f"  ✅ {label}: {size_mb:.1f} MB")

# Arka plan ses dosyası kontrolü ve kopyalama
if not AMBIENT_FILE.exists():
    source_ambient = HLK / "LARA_Bikini_230526" / "2026 yaz_HANDMADE_BİKİNİ" / "_rescue_turuncu" / "option_1_calm.mp3"
    if source_ambient.exists():
        log.info(f"  Deniz dalgası ses dosyası kopyalanıyor -> {AMBIENT_FILE.name}")
        shutil.copy(source_ambient, AMBIENT_FILE)
    else:
        log.warning(f"  ⚠️ Kaynak deniz dalgası sesi bulunamadı: {source_ambient}")

try:
    from moviepy import VideoFileClip, CompositeVideoClip, ColorClip, AudioFileClip, CompositeAudioClip
    import moviepy.video.fx as vfx
    import moviepy.audio.fx as afx

    log.info("\nKlipleri yüklüyorum...")
    scene1 = VideoFileClip(str(SCENE1_FILE))
    log.info(f"  Sahne 1: {scene1.duration:.2f}s, Ses: {scene1.audio is not None}")

    scene2 = VideoFileClip(str(SCENE2_FILE))
    log.info(f"  Sahne 2: {scene2.duration:.2f}s, Ses: {scene2.audio is not None}")

    scene3 = VideoFileClip(str(SCENE3_FILE))
    log.info(f"  Sahne 3: {scene3.duration:.2f}s, Ses: {scene3.audio is not None}")

    # Geçiş süresi — 1.0 saniye soft geçiş
    TRANSITION_DURATION = 1.0
    HALF_TRANSITION = TRANSITION_DURATION / 2.0

    # Kompozisyon kliplerini hazırlama
    composite_clips = []
    
    # ── Sahne 1 ──
    # S1 sonunda son kareyi dondur (freeze) ve ses patlamasını önlemek için sesi fadeout yap
    s1_frozen = scene1.with_effects([vfx.Freeze(t=scene1.duration - 0.05, freeze_duration=TRANSITION_DURATION)])
    if s1_frozen.audio is not None:
        # Geçiş süresi boyunca sesi sıfıra indir (pop önleme)
        s1_frozen = s1_frozen.with_audio(s1_frozen.audio.with_effects([afx.AudioFadeOut(TRANSITION_DURATION)]))
    s1_ready = s1_frozen.with_effects([vfx.FadeOut(TRANSITION_DURATION)]).with_start(0.0)
    composite_clips.append(s1_ready)

    # ── Sahne 2 ──
    s2_start = scene1.duration
    # S2 sonunda da geçiş esnasında dondurma uyguluyoruz
    s2_frozen = scene2.with_effects([vfx.Freeze(t=scene2.duration - 0.05, freeze_duration=TRANSITION_DURATION)])
    if s2_frozen.audio is not None:
        # Başlangıçta fadein, bitişte fadeout uygulayarak geçişteki ses sıçramalarını sıfırla
        s2_frozen = s2_frozen.with_audio(s2_frozen.audio.with_effects([
            afx.AudioFadeIn(TRANSITION_DURATION),
            afx.AudioFadeOut(TRANSITION_DURATION)
        ]))
    s2_ready = (s2_frozen
                .with_start(s2_start)
                .with_effects([vfx.FadeIn(TRANSITION_DURATION), vfx.FadeOut(TRANSITION_DURATION)]))
    composite_clips.append(s2_ready)

    # ── Geçiş 1: Soft Light Leak (Sahne 1 -> Sahne 2) ──
    w, h = scene1.size
    leak1 = (ColorClip(size=(w, h), color=(255, 190, 110), duration=TRANSITION_DURATION)
             .with_start(s2_start)
             .with_effects([vfx.FadeIn(HALF_TRANSITION), vfx.FadeOut(HALF_TRANSITION)])
             .with_opacity(0.35))
    composite_clips.append(leak1)

    # ── Sahne 3 ──
    s3_start = s2_start + scene2.duration
    s3_ready = scene3
    if s3_ready.audio is not None:
        # Geçiş başlangıcında sesi yumuşakça yükselt
        s3_ready = s3_ready.with_audio(s3_ready.audio.with_effects([afx.AudioFadeIn(TRANSITION_DURATION)]))
    s3_ready = (s3_ready
                .with_start(s3_start)
                .with_effects([vfx.FadeIn(TRANSITION_DURATION)]))
    composite_clips.append(s3_ready)

    # ── Geçiş 2: Soft Light Leak (Sahne 2 -> Sahne 3) ──
    leak2 = (ColorClip(size=(w, h), color=(255, 190, 110), duration=TRANSITION_DURATION)
             .with_start(s3_start)
             .with_effects([vfx.FadeIn(HALF_TRANSITION), vfx.FadeOut(HALF_TRANSITION)])
             .with_opacity(0.35))
    composite_clips.append(leak2)

    # Toplam Süre
    total_duration = s3_start + scene3.duration
    log.info(f"\nToplam video süresi: {total_duration:.2f}s")

    # Kompozit video oluşturma
    final_video = CompositeVideoClip(composite_clips, size=(w, h)).with_duration(total_duration)

    # ── Sesleri Birleştirme ve Dalga Sesi Ekleme (Audio Mix) ──
    log.info("\nSes parçaları birleştiriliyor ve arka plan dalga sesi ekleniyor...")
    voiceover_audio = final_video.audio
    
    if AMBIENT_FILE.exists() and voiceover_audio is not None:
        # Arka plan dalga sesini yükle
        ambient_audio = AudioFileClip(str(AMBIENT_FILE))
        
        # Süreyi videoya göre ayarla
        ambient_audio = ambient_audio.subclipped(0, total_duration)
        
        # Kullanıcının talebi üzerine dalga sesi düzeyi %12'ye çıkarıldı ( MultiplyVolume: 0.12 )
        ambient_audio = ambient_audio.with_effects([
            afx.MultiplyVolume(0.12),
            afx.AudioFadeIn(0.5),
            afx.AudioFadeOut(0.5)
        ])
        
        # İki ses kanalını birbiri üzerine mix et (Voiceover + Ocean Ambient)
        mixed_audio = CompositeAudioClip([voiceover_audio, ambient_audio])
        final_video = final_video.with_audio(mixed_audio)
        log.info("  ✅ Arka plan deniz dalgası sesi (%12) entegre edildi.")
    else:
        log.warning("  ⚠️ Arka plan dalga sesi bulunamadı veya video ses kanalı boş, orijinal sesle devam ediliyor.")

    FINAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    log.info(f"Video dosyası yazılıyor: {FINAL_FILE.name}")
    
    final_video.write_videofile(
        str(FINAL_FILE),
        fps=24,
        codec="libx264",
        audio=True,
        audio_codec="aac",
        temp_audiofile=str(SUNSET_DIR / "temp_audio.m4a"),
        remove_temp=True
    )

    # Kapatma ve temizlik
    scene1.close()
    scene2.close()
    scene3.close()
    if AMBIENT_FILE.exists() and voiceover_audio is not None:
        ambient_audio.close()
        mixed_audio.close()
    final_video.close()

    size_mb = FINAL_FILE.stat().st_size / (1024*1024)
    log.info(f"\n✅ Başarılı: {FINAL_FILE.name}")
    log.info(f"   Boyut: {size_mb:.1f} MB")
    log.info(f"   Konum: {FINAL_FILE}")
    log.info("\n" + "=" * 70)
    log.info("✅ LARA ARI SUNSET REKLAMI SES DÜZELTMELERİYLE BİRLEŞTİRİLDİ!")
    log.info("=" * 70)

except Exception as e:
    log.error(f"❌ Birleştirme Hatası: {e}", exc_info=True)
    sys.exit(1)
