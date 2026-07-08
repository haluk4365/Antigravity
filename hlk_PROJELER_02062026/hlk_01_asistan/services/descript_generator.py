"""
Descript Platform API — Ses ve video üretim servisi.

Overdub TTS (text-to-speech), proje yönetimi, AI Agent düzenleme
ve compositon publish işlemleri için Descript REST API entegrasyonu.

Endpoints:
    GET  /overdub/voices         — Kullanılabilir sesleri listele
    POST /overdub/generate_async — Overdub (TTS) üretimini başlat
    GET  /jobs/{job_id}          — Job durumunu kontrol et
    DELETE /jobs/{job_id}        — Job'ı iptal et
    POST /jobs/agent             — AI Agent ile doğal dilden düzenleme
    POST /jobs/publish           — Composition yayınla
    GET  /projects               — Projeleri listele
    POST /jobs/import/project_media — Medya içe aktar

Not: Overdub API yalnızca Descript Enterprise müşterilerine açıktır.
"""

import logging
import os
import time
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://descriptapi.com/v1"
REQUEST_TIMEOUT = 60
POLL_INTERVAL = 2  # saniye


class DescriptGenerator:
    """Descript API ile Overdub TTS ve proje yönetimi.

    Kullanım:
        dg = DescriptGenerator()
        voices = dg.list_voices()
        job_id = dg.generate_tts("Merhaba", voice_id="...")
        result = dg.wait_for_completion(job_id)
    """

    def __init__(self):
        raw_key = os.getenv("DESCRIPT_API_KEY", "")
        if not raw_key:
            raise ValueError("❌ DESCRIPT_API_KEY .env içinde bulunamadı")
        self._api_key = raw_key
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        })

    # ──────────────────────────────────────────────────────────────────
    # 1. SES (Overdub TTS)
    # ──────────────────────────────────────────────────────────────────

    def list_voices(self) -> list[dict]:
        """Kullanılabilir Overdub seslerini ve stil ID'lerini listeler.

        Returns:
            Ses listesi (her biri voice_id, name, style_id vb. içerir).
            Hata durumunda boş liste döner.
        """
        url = f"{BASE_URL}/overdub/voices"
        try:
            resp = self._session.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                voices = data if isinstance(data, list) else data.get("voices", data.get("data", []))
                logger.info(f"🔊 Descript: {len(voices)} ses bulundu")
                return voices
            logger.warning(f"⚠️ Descript ses listeleme: {resp.status_code} — {resp.text[:200]}")
        except requests.RequestException as e:
            logger.error(f"❌ Descript ses listeleme hatası: {e}")
        return []

    def generate_tts(
        self,
        text: str,
        voice_id: str,
        voice_style_id: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> Optional[str]:
        """Overdub TTS üretimini başlat (asenkron).

        Args:
            text: Seslendirilecek metin.
            voice_id: Descript voice ID (list_voices() ile alınır).
            voice_style_id: Opsiyonel stil ID (varsayılan stil kullanılır).
            callback_url: Opsiyonel webhook URL (job tamamlanınca POST gönderilir).

        Returns:
            job_id (polling için) veya None.
        """
        url = f"{BASE_URL}/overdub/generate_async"
        payload = {
            "voice_id": voice_id,
            "text": text,
        }
        if voice_style_id:
            payload["voice_style_id"] = voice_style_id
        if callback_url:
            payload["callback_url"] = callback_url

        try:
            resp = self._session.post(
                url,
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            if resp.status_code in (200, 201, 202):
                data = resp.json()
                job_id = data.get("id") or data.get("job_id")
                if job_id:
                    logger.info(
                        f"🔊 Descript TTS başlatıldı: job={job_id}, "
                        f"voice={voice_id}, text_len={len(text)}"
                    )
                    return job_id
                logger.error(f"❌ Descript: job_id alınamadı — {data}")
            else:
                logger.error(
                    f"❌ Descript TTS hatası ({resp.status_code}): {resp.text[:300]}"
                )
        except requests.RequestException as e:
            logger.error(f"❌ Descript TTS istek hatası: {e}")
        return None

    def get_job(self, job_id: str) -> Optional[dict]:
        """Job durumunu kontrol et.

        Args:
            job_id: generate_tts() veya diğer async işlemlerden dönen ID.

        Returns:
            Job durum dict'i veya None.
        """
        url = f"{BASE_URL}/jobs/{job_id}"
        try:
            resp = self._session.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
            logger.warning(f"⚠️ Descript job sorgu: {resp.status_code} — {resp.text[:200]}")
        except requests.RequestException as e:
            logger.error(f"❌ Descript job sorgu hatası: {e}")
        return None

    def cancel_job(self, job_id: str) -> bool:
        """Çalışan bir job'ı iptal et.

        Returns:
            Başarılı ise True.
        """
        url = f"{BASE_URL}/jobs/{job_id}"
        try:
            resp = self._session.delete(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 204:
                logger.info(f"🗑️ Descript job iptal edildi: {job_id}")
                return True
            logger.warning(f"⚠️ Descript job iptal: {resp.status_code} — {resp.text[:200]}")
        except requests.RequestException as e:
            logger.error(f"❌ Descript job iptal hatası: {e}")
        return False

    def wait_for_completion(
        self,
        job_id: str,
        max_wait: int = 120,
        success_states: tuple = ("completed", "succeeded", "done"),
        failure_states: tuple = ("failed", "error"),
    ) -> Optional[dict]:
        """Job tamamlanana kadar polling yap.

        Args:
            job_id: İzlenecek job ID.
            max_wait: Maksimum bekleme süresi (saniye).
            success_states: Başarılı kabul edilen state değerleri.
            failure_states: Başarısız kabul edilen state değerleri.

        Returns:
            Başarılıysa job result dict'i, başarısızsa None.
        """
        start = time.time()
        while time.time() - start < max_wait:
            result = self.get_job(job_id)
            if result is None:
                time.sleep(POLL_INTERVAL)
                continue

            status = (
                result.get("status")
                or result.get("state")
                or result.get("job_status", "")
            ).lower()

            elapsed = time.time() - start
            logger.info(f"⏳ Descript job [{job_id}]: {status} ({elapsed:.0f}s)")

            if status in success_states:
                logger.info(f"✅ Descript job tamamlandı: {job_id} ({elapsed:.1f}s)")
                return result
            if status in failure_states:
                error_msg = result.get("error") or result.get("message", "bilinmeyen hata")
                logger.error(f"❌ Descript job başarısız: {job_id} — {error_msg}")
                return None

            time.sleep(POLL_INTERVAL)

        logger.error(f"⏰ Descript job timeout: {job_id} ({max_wait}s)")
        return None

    def download_audio(self, job_result: dict, output_path: str) -> Optional[str]:
        """Job sonucundan audio URL'sini al ve indir.

        Job result içinde audio_url / output_url / url alanları aranır.
        Dosya MP3 olarak kaydedilir.

        Args:
            job_result: wait_for_completion() veya get_job() sonucu.
            output_path: Kaydedilecek dosya yolu.

        Returns:
            output_path (başarılı) veya None.
        """
        audio_url = (
            job_result.get("audio_url")
            or job_result.get("output_url")
            or job_result.get("url")
            or (job_result.get("output") or {}).get("audio_url")
            or (job_result.get("result") or {}).get("url")
        )
        if not audio_url:
            # Job result'ın içini dene
            for key in ("output", "result", "data", "payload"):
                nested = job_result.get(key)
                if isinstance(nested, dict):
                    audio_url = (
                        nested.get("audio_url")
                        or nested.get("output_url")
                        or nested.get("url")
                    )
                    if audio_url:
                        break
        if not audio_url:
            logger.error(f"❌ Descript: audio URL bulunamadı — job keys: {list(job_result.keys())}")
            return None

        try:
            resp = requests.get(audio_url, timeout=120)
            if resp.status_code == 200:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                size_kb = len(resp.content) / 1024
                logger.info(f"✅ Descript audio indirildi: {output_path} ({size_kb:.1f} KB)")
                return output_path
            logger.error(f"❌ Descript audio indirme: {resp.status_code}")
        except requests.RequestException as e:
            logger.error(f"❌ Descript audio indirme hatası: {e}")
        return None

    # ──────────────────────────────────────────────────────────────────
    # 2. TAM PİPELİNE: generate → wait → download
    # ──────────────────────────────────────────────────────────────────

    def generate_and_wait(
        self,
        text: str,
        voice_id: str,
        output_path: str,
        voice_style_id: Optional[str] = None,
        max_wait: int = 120,
    ) -> Optional[str]:
        """Overdub TTS pipeline: metin → ses dosyası.

        Args:
            text: Seslendirilecek metin.
            voice_id: Descript voice ID.
            output_path: Kaydedilecek MP3 dosya yolu.
            voice_style_id: Opsiyonel stil ID.
            max_wait: Maksimum bekleme süresi.

        Returns:
            output_path (başarılı) veya None.
        """
        logger.info(f"🔊 Descript pipeline başlıyor: text_len={len(text)}, voice={voice_id}")

        job_id = self.generate_tts(
            text=text,
            voice_id=voice_id,
            voice_style_id=voice_style_id,
        )
        if not job_id:
            return None

        result = self.wait_for_completion(job_id, max_wait=max_wait)
        if not result:
            return None

        return self.download_audio(result, output_path)

    # ──────────────────────────────────────────────────────────────────
    # 3. PROJE YÖNETİMİ
    # ──────────────────────────────────────────────────────────────────

    def list_projects(self, **params) -> list[dict]:
        """Drive'daki projeleri listele.

        Args:
            **params: Filtreleme parametreleri (name, folder_path, creator, sort vb.)

        Returns:
            Proje listesi veya boş liste.
        """
        url = f"{BASE_URL}/projects"
        try:
            resp = self._session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                projects = data if isinstance(data, list) else data.get("projects", data.get("data", []))
                return projects
            logger.warning(f"⚠️ Descript proje listeleme: {resp.status_code}")
        except requests.RequestException as e:
            logger.error(f"❌ Descript proje listeleme hatası: {e}")
        return []

    def get_project(self, project_id: str) -> Optional[dict]:
        """Proje detaylarını getir (medya + composition listesi)."""
        url = f"{BASE_URL}/projects/{project_id}"
        try:
            resp = self._session.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
            logger.warning(f"⚠️ Descript proje detay: {resp.status_code}")
        except requests.RequestException as e:
            logger.error(f"❌ Descript proje detay hatası: {e}")
        return None

    # ──────────────────────────────────────────────────────────────────
    # 4. AI AGENT (Doğal Dilden Düzenleme)
    # ──────────────────────────────────────────────────────────────────

    def run_agent(
        self,
        prompt: str,
        project_id: Optional[str] = None,
        composition_id: Optional[str] = None,
        project_name: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> Optional[str]:
        """AI Agent ile doğal dil kullanarak proje düzenle.

        Agent Studio Sound, caption, filler-word removal, translation,
        dubbing ve rough-cut işlemlerini yapabilir.

        Args:
            prompt: Yapılacak işlemi tanımlayan doğal dil komutu.
            project_id: Varolan bir projede çalışmak için.
            composition_id: Belirli bir composition'da çalışmak için.
            project_name: Yeni proje oluşturmak için.
            callback_url: Opsiyonel webhook.

        Returns:
            job_id veya None.
        """
        url = f"{BASE_URL}/jobs/agent"
        payload = {"prompt": prompt}
        if project_id:
            payload["project_id"] = project_id
        if composition_id:
            payload["composition_id"] = composition_id
        if project_name:
            payload["project_name"] = project_name
        if callback_url:
            payload["callback_url"] = callback_url

        try:
            resp = self._session.post(url, json=payload, timeout=REQUEST_TIMEOUT)
            if resp.status_code in (200, 201, 202):
                data = resp.json()
                job_id = data.get("id") or data.get("job_id")
                if job_id:
                    logger.info(f"🤖 Descript Agent başlatıldı: job={job_id}, prompt={prompt[:60]}...")
                    return job_id
            logger.error(f"❌ Descript Agent hatası ({resp.status_code}): {resp.text[:300]}")
        except requests.RequestException as e:
            logger.error(f"❌ Descript Agent istek hatası: {e}")
        return None

    # ──────────────────────────────────────────────────────────────────
    # 5. PUBLISH / EXPORT
    # ──────────────────────────────────────────────────────────────────

    def publish_composition(
        self,
        composition_id: str,
        project_id: str,
        resolution: str = "1080p",
        output_format: str = "video",
        callback_url: Optional[str] = None,
    ) -> Optional[str]:
        """Composition'ı yayınla (export et).

        Args:
            composition_id: Yayınlanacak composition ID.
            project_id: Proje ID.
            resolution: 480p, 720p, 1080p, 1440p, 2160p (4K).
            output_format: "video" veya "audio".
            callback_url: Opsiyonel webhook.

        Returns:
            job_id veya None.
        """
        url = f"{BASE_URL}/jobs/publish"
        payload = {
            "composition_id": composition_id,
            "project_id": project_id,
            "resolution": resolution,
            "format": output_format,
        }
        if callback_url:
            payload["callback_url"] = callback_url

        try:
            resp = self._session.post(url, json=payload, timeout=REQUEST_TIMEOUT)
            if resp.status_code in (200, 201, 202):
                data = resp.json()
                job_id = data.get("id") or data.get("job_id")
                if job_id:
                    logger.info(f"📤 Descript publish başlatıldı: job={job_id}")
                    return job_id
            logger.error(f"❌ Descript publish hatası ({resp.status_code}): {resp.text[:300]}")
        except requests.RequestException as e:
            logger.error(f"❌ Descript publish istek hatası: {e}")
        return None

    def check_status(self) -> dict:
        """API durumunu ve token geçerliliğini kontrol et.

        Returns:
            {"ok": True/False, "detail": str}
        """
        url = f"{BASE_URL}/status"
        try:
            resp = self._session.get(url, timeout=10)
            if resp.status_code == 200:
                return {"ok": True, "detail": "API erişilebilir"}
            return {"ok": False, "detail": f"HTTP {resp.status_code}"}
        except requests.RequestException as e:
            return {"ok": False, "detail": str(e)}


# Global singleton — voice_generator.py ve hedra_generator.py ile tutarlı
descript_generator = DescriptGenerator()
