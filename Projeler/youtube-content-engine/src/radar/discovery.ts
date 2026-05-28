import { fetchVideosByIds, searchVideos, toVideoMeta, VideoMeta } from "./youtubeApi.js";
import { anthropic, MODEL } from "../lib/anthropic.js";
import { log, warn } from "../lib/logger.js";

export async function pullDiscoveryVideos(excludeChannelTitles: Set<string>): Promise<VideoMeta[]> {
  const since = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
  try {
    const ids = await searchVideos({
      publishedAfter: since,
      order: "viewCount",
      videoCategoryId: "28",
      relevanceLanguage: "en",
      max: 25,
    });
    const raw = await fetchVideosByIds(ids);
    let videos = raw.map((r) => toVideoMeta(r, "discovery"));
    videos = videos.filter((v) => !excludeChannelTitles.has(v.channelTitle));
    if (!videos.length) return [];

    const filtered = await claudeRelevanceFilter(videos);
    log(`discovery: ${videos.length} candidates → ${filtered.length} relevant`);
    return filtered;
  } catch (e: any) {
    warn(`discovery error: ${e.message}`);
    return [];
  }
}

async function claudeRelevanceFilter(videos: VideoMeta[]): Promise<VideoMeta[]> {
  const list = videos.map((v, i) => `${i}. ${v.title} — ${v.channelTitle}`).join("\n");
  const prompt = `Aşağıdaki YouTube videolarından hangileri kanal için relevant?
Kanal odağı: Claude Code, Antigravity, AI otomasyon, KOBİ ve bireysel girişimciler için Türkçe içerik.

Filtrele: politik, oyun, magazin, genel teknoloji haberleri, donanım reviewleri, kripto, generic AI hype.
Tut: AI agent inşası, otomasyon araçları, prompt engineering, dev tooling, indie hacker case study'leri, Claude/GPT/Gemini specific tutoriallar.

Liste:
${list}

Sadece relevant indeksleri JSON array olarak döndür, başka metin yok. Örnek: [0, 3, 7]`;

  try {
    const resp = await anthropic.messages.create({
      model: MODEL,
      max_tokens: 512,
      messages: [{ role: "user", content: prompt }],
    });
    const text = (resp.content.find((c: any) => c.type === "text") as any)?.text ?? "";
    const m = text.match(/\[[\s\d,]*\]/);
    if (!m) return videos;
    const indices: number[] = JSON.parse(m[0]);
    return indices.map((i) => videos[i]).filter(Boolean);
  } catch (e: any) {
    warn(`claude relevance filter error: ${e.message}`);
    return videos;
  }
}
