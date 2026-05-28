"""
OpenRouter Service — GLM-4.7-Flash Chat
=========================================
OpenRouter üzerinden Google GLM-4.7-Flash modelini kullanır.
"""

import openai
from logger import get_logger

log = get_logger("openrouter_service")


class OpenRouterService:
    """GLM-4.7-Flash tabanlı chat servisi."""

    def __init__(self, api_key: str, model: str = "google/gemini-2.0-flash-lite", base_url: str = "https://openrouter.ai/api/v1"):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def chat(self, messages: list[dict], temperature: float = 1.0, max_tokens: int = 2000) -> str:
        """
        OpenRouter chat completion çağrısı.

        Args:
            messages: OpenAI format mesaj listesi
            temperature: Yaratıcılık seviyesi
            max_tokens: Maximum yanıt uzunluğu

        Returns:
            str: Modelin yanıtı
        """
        try:
            effective_max_tokens = max(max_tokens, 100)
            create_kwargs = {
                "model": self.model,
                "messages": messages,
                "max_tokens": effective_max_tokens,
            }

            content = ""
            for attempt in range(3):
                response = self.client.chat.completions.create(**create_kwargs)
                content = response.choices[0].message.content or ""
                if content.strip():
                    break
                log.warning(f"OpenRouter boş content döndürdü (deneme {attempt+1}/3)")
                if attempt < 2:
                    import time
                    time.sleep(0.5)

            if not content.strip():
                log.error("OpenRouter 3 denemede de boş content döndürdü")
                raise RuntimeError("OpenRouter API 3 denemede de boş yanıt döndürdü.")

            log.info(f"OpenRouter chat yanıt alındı — {len(content)} karakter")
            return content

        except openai.RateLimitError:
            log.error("OpenRouter rate limit aşıldı!", exc_info=True)
            raise
        except openai.APIError as e:
            log.error(f"OpenRouter API hatası: {e}", exc_info=True)
            raise
