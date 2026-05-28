import { anthropic, MODEL } from "../lib/anthropic.js";
import { hashIdea, Idea } from "../notion/ideaStore.js";
import { log, warn } from "../lib/logger.js";

const PROMPT = `Sen bir YouTube içerik strategist'isin. Kanal sahibi Türkiye'de KOBİ ve bireysel girişimcilere yönelik AI otomasyon eğitimi içeriği üretiyor (YouTube kanalı + eğitim topluluğu).

Görevin: Web search kullanarak bugün/bu hafta Türkiye'de KOBİ'lerin ve girişimcilerin yaşadığı somut sorunları araştır. Şu kaynaklara öncelik ver:
- ŞikayetVar (sikayetvar.com) — son şikayetler, özellikle e-ticaret/finans/telekom
- Google Trends Türkiye — son rising search'ler
- Reddit r/Turkey — son popüler tartışmalar
- Twitter Türkiye trending topics

Bulduğun sinyaller içinden, Claude Code / Antigravity / n8n ile otomasyona dönüştürülebilir VE kanalın YouTube kitlesine ilgi çekecek olanları seç.

Her fikir için JSON formatında döndür:
{
  "problem": "1 cümle, sinyalden gelen somut sorun",
  "otomasyon": "1 cümle, somut otomasyon fikri",
  "hedef_kitle": "KOBİ | bireysel girişimci | her ikisi",
  "hook": "YouTube videosunun açılış cümlesi olabilecek hook fikri",
  "skor": 1-10 arası ilgi tahmini,
  "kaynak": "hangi araştırmadan/site'den çıktı, kısa açıklama"
}

Sadece skoru 7+ olan, maksimum 5 fikir döndür. Çıktı SADECE JSON array, başka metin yok.

ÖNEMLİ: Politik trendleri, magazin/celebrity haberlerini, sektör-bağımsız genel sorunları (trafik, hava durumu vs) filtrele. Sadece otomasyonla çözülebilir, niş, somut sorunlar.`;

export async function runIdeaEngine(excludeHashes: Set<string>): Promise<Idea[]> {
  try {
    const resp = await anthropic.messages.create({
      model: MODEL,
      max_tokens: 4096,
      tools: [{ type: "web_search_20250305", name: "web_search", max_uses: 8 } as any],
      messages: [{ role: "user", content: PROMPT }],
    });

    const textBlock = resp.content.filter((c: any) => c.type === "text").map((c: any) => c.text).join("\n");
    const m = textBlock.match(/\[[\s\S]*\]/);
    if (!m) {
      warn("idea engine: no JSON array in response");
      return [];
    }
    const arr: Idea[] = JSON.parse(m[0]);
    const fresh = arr.filter((i) => !excludeHashes.has(hashIdea(i))).filter((i) => i.skor >= 7);
    log(`ideas: ${arr.length} returned, ${fresh.length} fresh`);
    return fresh.slice(0, 5);
  } catch (e: any) {
    warn(`idea engine error: ${e.message}`);
    return [];
  }
}
