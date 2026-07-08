"""
Hedra AI — Lip-sync video üretim servisi.
"""

import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.hedra.com"


class HedraGenerator:
    """Hedra API ile lip-sync video üretir."""

    def __init__(self):
        self._api_key = os.getenv("HEDRA_API_KEY", "")
        if not self._api_key:
            raise ValueError("HEDRA_API_KEY gereklidir")

    def _headers(self) -> dict:
        return {
            "X-API-Key": self._api_key,
            "Accept": "application/json",
        }

    def upload_image(self, image_path: str) -> str | None:
        """Görsel yükle, URL döndür."""
        try:
            with open(image_path, "rb") as f:
                resp = requests.post(
                    f"{BASE_URL}/web-app/v1/images",
                    headers=self._headers(),
                    files={"file": f},
                    timeout=60,
                )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("url") or data.get("image_url")
            logger.error("Hedra image upload %s: %s", resp.status_code, resp.text[:200])
        except Exception as e:
            logger.error("Hedra image upload hata: %s", e)
        return None

    def upload_audio(self, audio_path: str) -> str | None:
        """Ses yükle, URL döndür."""
        try:
            with open(audio_path, "rb") as f:
                resp = requests.post(
                    f"{BASE_URL}/web-app/v1/audios",
                    headers=self._headers(),
                    files={"file": f},
                    timeout=60,
                )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("url") or data.get("audio_url")
            logger.error("Hedra audio upload %s: %s", resp.status_code, resp.text[:200])
        except Exception as e:
            logger.error("Hedra audio upload hata: %s", e)
        return None

    def generate(self, image_url: str, audio_url: str, model_id: str = "omnia") -> str | None:
        """Video üretim isteği gönder, job_id döndür."""
        payload = {
            "image_url": image_url,
            "audio_url": audio_url,
            "model_id": model_id,
            "aspect_ratio": "9:16",
            "resolution": "720p",
        }
        headers = self._headers()
        headers["Content-Type"] = "application/json"
        try:
            resp = requests.post(
                f"{BASE_URL}/web-app/v1/videos/generate",
                headers=headers,
                json=payload,
                timeout=120,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("job_id") or data.get("video_id")
            logger.error("Hedra generate %s: %s", resp.status_code, resp.text[:200])
        except Exception as e:
            logger.error("Hedra generate hata: %s", e)
        return None

    def wait_for_completion(self, job_id: str, max_wait: int = 300) -> str | None:
        """Video hazır olana kadar polling yap, video_url döndür."""
        start = time.time()
        while time.time() - start < max_wait:
            try:
                resp = requests.get(
                    f"{BASE_URL}/web-app/v1/jobs/{job_id}",
                    headers=self._headers(),
                    timeout=30,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    status = data.get("status") or data.get("state", "")
                    if status == "completed":
                        return data.get("video_url") or data.get("output_url")
                    elif status == "failed":
                        logger.error("Hedra job başarısız: %s", data.get("error", ""))
                        return None
                elif resp.status_code == 404:
                    logger.error("Hedra job bulunamadı: %s", job_id)
                    return None
            except Exception as e:
                logger.error("Hedra status kontrol hata: %s", e)
            time.sleep(5)
        logger.error("Hedra timeout — %ss içinde tamamlanamadı", max_wait)
        return None

    def download_video(self, video_url: str, output_path: str) -> bool:
        """Video indir, diske kaydet."""
        try:
            resp = requests.get(video_url, timeout=120)
            if resp.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                size_mb = len(resp.content) / (1024 * 1024)
                logger.info("Hedra video kaydedildi: %s (%.1f MB)", output_path, size_mb)
                return True
            logger.error("Hedra video indirme hata: %s", resp.status_code)
        except Exception as e:
            logger.error("Hedra video indirme hata: %s", e)
        return False

    def create_lipsync_video(
        self, image_path: str, audio_path: str, output_path: str, model_id: str = "omnia"
    ) -> bool:
        """Tam pipeline: görsel + ses → lip-sync video. True/False döndür."""
        logger.info("Hedra lip-sync başlıyor...")
        image_url = self.upload_image(image_path)
        if not image_url:
            return False
        audio_url = self.upload_audio(audio_path)
        if not audio_url:
            return False
        job_id = self.generate(image_url, audio_url, model_id)
        if not job_id:
            return False
        logger.info("Hedra job_id: %s — bekleniyor...", job_id)
        video_url = self.wait_for_completion(job_id)
        if not video_url:
            return False
        return self.download_video(video_url, output_path)
