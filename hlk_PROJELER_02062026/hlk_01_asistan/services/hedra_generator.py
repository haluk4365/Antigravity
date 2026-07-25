"""
Hedra AI — Lip-sync video üretim servisi.
"""

import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.hedra.com/web-app/public"


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

    def _upload_asset(self, file_path: str, mime_type: str) -> str | None:
        """Dosya yükle (iki adimli: asset olustur + upload), asset_id dondur."""
        try:
            headers = self._headers()
            headers["Content-Type"] = "application/json"
            # Adim 1: Asset kaydi olustur
            fname = os.path.basename(file_path)
            resp = requests.post(
                f"{BASE_URL}/assets",
                headers=headers,
                json={"name": fname, "type": mime_type},
                timeout=30,
            )
            if resp.status_code not in (200, 201):
                logger.error("Hedra asset create %s: %s", resp.status_code, resp.text[:200])
                return None
            asset = resp.json()
            asset_id = asset.get("id") or asset.get("asset_id")
            if not asset_id:
                return None
            # Adim 2: Dosyayi yukle
            with open(file_path, "rb") as f:
                up_resp = requests.post(
                    f"{BASE_URL}/assets/{asset_id}/upload",
                    headers={"X-API-Key": self._api_key},
                    files={"file": f},
                    timeout=60,
                )
            if up_resp.status_code in (200, 201, 204):
                logger.info("Hedra asset uploaded: %s", asset_id)
                return asset_id
            logger.error("Hedra asset upload %s: %s", up_resp.status_code, up_resp.text[:200])
        except Exception as e:
            logger.error("Hedra upload hata: %s", e)
        return None

    def upload_image(self, image_path: str) -> str | None:
        """Görsel yükle, asset ID döndür."""
        return self._upload_asset(image_path, "image")

    def upload_audio(self, audio_path: str) -> str | None:
        """Ses yükle, asset ID döndür."""
        return self._upload_asset(audio_path, "audio")

    def generate(self, image_url: str, audio_url: str, model_id: str = "omnia") -> str | None:
        """Video üretim isteği gönder, generation_id döndür."""
        # AR-002_90: Hedra API yeni body yapisi
        # video.generated_video_inputs wrapper zorunlu
        payload = {
            "type": "video",
            "video": {
                "generated_video_inputs": {
                    "type": "generated_video",
                    "model": model_id,
                    "image_asset_id": image_url,
                    "audio_asset_id": audio_url,
                    "aspect_ratio": "9:16",
                    "resolution": "720p",
                }
            }
        }
        headers = self._headers()
        headers["Content-Type"] = "application/json"
        try:
            resp = requests.post(
                f"{BASE_URL}/generations",
                headers=headers,
                json=payload,
                timeout=120,
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                return data.get("id") or data.get("generation_id")
            logger.error("Hedra generate %s: %s", resp.status_code, resp.text[:200])
        except Exception as e:
            logger.error("Hedra generate hata: %s", e)
        return None

    def wait_for_completion(self, generation_id: str, max_wait: int = 300) -> str | None:
        """Video hazır olana kadar polling yap, video_url döndür."""
        start = time.time()
        while time.time() - start < max_wait:
            try:
                resp = requests.get(
                    f"{BASE_URL}/generations/{generation_id}/status",
                    headers=self._headers(),
                    timeout=30,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    status = data.get("status") or data.get("state", "")
                    if status == "completed":
                        return data.get("video_url") or data.get("output_url") or data.get("url")
                    elif status == "failed":
                        logger.error("Hedra generation basarisiz: %s", data.get("error", ""))
                        return None
                elif resp.status_code == 404:
                    logger.error("Hedra generation bulunamadi: %s", generation_id)
                    return None
            except Exception as e:
                logger.error("Hedra status kontrol hata: %s", e)
            time.sleep(5)
        logger.error("Hedra timeout — %ss icinde tamamlanamadi", max_wait)
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
