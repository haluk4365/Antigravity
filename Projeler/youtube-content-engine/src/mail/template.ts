import { VideoMeta } from "../radar/youtubeApi.js";
import { Buckets, velocity } from "../radar/buckets.js";
import { Idea } from "../notion/ideaStore.js";

const fmtNum = (n: number) =>
  n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M` : n >= 1000 ? `${(n / 1000).toFixed(1)}K` : String(n);

const escape = (s: string | undefined | null) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

function videoCard(v: VideoMeta, meta: string): string {
  return `
    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-bottom:16px;background:#1a1a1a;border-radius:12px;overflow:hidden;">
      <tr>
        <td style="width:140px;vertical-align:top;">
          <a href="${v.url}" style="display:block;"><img src="${v.thumbnailUrl}" width="140" style="display:block;border-radius:0;width:140px;height:auto;" alt=""/></a>
        </td>
        <td style="padding:12px 16px;vertical-align:top;">
          <a href="${v.url}" style="color:#fff;text-decoration:none;font-size:15px;font-weight:600;line-height:1.35;display:block;margin-bottom:6px;">${escape(v.title)}</a>
          <div style="color:#888;font-size:12px;margin-bottom:4px;">${escape(v.channelTitle)}</div>
          <div style="color:#4ade80;font-size:12px;font-weight:600;">${meta}</div>
        </td>
      </tr>
    </table>`;
}

function priorityCard(v: VideoMeta): string {
  const vel = Math.round(velocity(v));
  return `
    <div style="background:linear-gradient(135deg,#dc2626,#ea580c);border-radius:16px;padding:20px;margin-bottom:24px;">
      <div style="color:#fff;font-size:12px;font-weight:700;letter-spacing:1px;margin-bottom:12px;">🎯 BUGÜNÜN PRIORITY VİDEOSU</div>
      <a href="${v.url}" style="display:block;text-decoration:none;">
        <img src="${v.thumbnailUrl}" width="100%" style="display:block;border-radius:8px;margin-bottom:12px;max-width:560px;" alt=""/>
        <div style="color:#fff;font-size:18px;font-weight:700;line-height:1.3;margin-bottom:6px;">${escape(v.title)}</div>
        <div style="color:rgba(255,255,255,0.85);font-size:13px;">${escape(v.channelTitle)} · ${fmtNum(v.viewCount)} view · ${fmtNum(vel)}/saat</div>
      </a>
    </div>`;
}

function ideaCard(i: Idea, index: number): string {
  const idx = String(index).padStart(2, "0");
  return `
    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-bottom:20px;background:#141414;border:1px solid #2a2a2a;border-radius:12px;">
      <tr>
        <td width="60" style="vertical-align:top;padding:22px 0 22px 22px;">
          <div style="color:#4ade80;font-size:30px;font-weight:800;line-height:1;letter-spacing:-1px;">${idx}</div>
        </td>
        <td style="vertical-align:top;padding:22px 22px 22px 10px;">
          <div style="margin-bottom:14px;">
            <span style="color:#fff;font-size:17px;font-weight:600;line-height:1.45;">${escape(i.otomasyon)}</span>
          </div>
          <div style="margin-bottom:14px;">
            <span style="display:inline-block;background:#2a2a2a;color:#fbbf24;font-size:12px;font-weight:600;padding:4px 10px;border-radius:12px;margin-right:6px;">${i.skor}/10</span>
            <span style="display:inline-block;background:#2a2a2a;color:#4ade80;font-size:12px;font-weight:600;padding:4px 10px;border-radius:12px;">${escape(i.hedef_kitle)}</span>
          </div>
          <div style="color:#cfcfcf;font-size:14px;line-height:1.65;margin-bottom:8px;"><span style="color:#888;font-weight:600;">Sorun · </span>${escape(i.problem)}</div>
          <div style="color:#cfcfcf;font-size:14px;line-height:1.65;margin-bottom:12px;"><span style="color:#888;font-weight:600;">Hook · </span>${escape(i.hook)}</div>
          <div style="color:#777;font-size:12px;line-height:1.5;">${escape(i.kaynak)}</div>
        </td>
      </tr>
    </table>`;
}

function section(title: string, body: string): string {
  return `
    <div style="margin-top:28px;margin-bottom:16px;">
      <div style="color:#fff;font-size:14px;font-weight:700;letter-spacing:0.5px;margin-bottom:14px;">${title}</div>
      ${body}
    </div>`;
}

export function buildHtml(buckets: Buckets, ideas: Idea[]): string {
  const dateStr = new Date().toLocaleDateString("tr-TR", { day: "numeric", month: "long", weekday: "long", timeZone: "Europe/Istanbul" });

  const fresh = buckets.fresh.map((v) => videoCard(v, `${fmtNum(v.viewCount)} view · ${fmtNum(Math.round(velocity(v)))}/saat`)).join("") || `<div style="color:#666;font-size:13px;">Bugün taze bir şey çıkmadı.</div>`;
  const matured = buckets.matured.map((v) => videoCard(v, `${fmtNum(v.viewCount)} toplam view`)).join("") || `<div style="color:#666;font-size:13px;">Olgunlaşmış aday yok.</div>`;
  const disc = buckets.discovery.map((v) => videoCard(v, `${fmtNum(v.viewCount)} view · keşif`)).join("") || `<div style="color:#666;font-size:13px;">Keşifte yeni bir şey yok.</div>`;
  const ideaBlock = ideas.length
    ? ideas.map((i, idx) => ideaCard(i, idx + 1)).join("")
    : `<div style="color:#666;font-size:13px;">Bugün filtreyi geçen fikir çıkmadı.</div>`;

  const summary = `${buckets.fresh.length} taze · ${buckets.matured.length} olgunlaşmış · ${buckets.discovery.length} keşif · ${ideas.length} fikir`;

  return `<!DOCTYPE html>
<html><head><meta charset="utf-8"/></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#0a0a0a;">
    <tr><td align="center" style="padding:24px 12px;">
      <table cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width:600px;">
        <tr><td>
          <div style="color:#888;font-size:12px;letter-spacing:1px;margin-bottom:4px;">📡 İÇERİK RADARI</div>
          <div style="color:#fff;font-size:22px;font-weight:700;margin-bottom:24px;">${escape(dateStr)}</div>
          ${buckets.priority ? priorityCard(buckets.priority) : ""}
          ${section("📺 RAKİP RADARI · 🔥 Günlük Taze (son 48 saat)", fresh)}
          ${section("⏰ Olgunlaşmış (1-3 hafta)", matured)}
          ${section("🔍 Keşif", disc)}
          ${section("💡 YEREL FİKİR MOTORU", ideaBlock)}
          <div style="color:#555;font-size:11px;margin-top:32px;padding-top:16px;border-top:1px solid #222;">${summary}</div>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>`;
}

export function buildSubject(): string {
  const d = new Date().toLocaleDateString("tr-TR", { day: "numeric", month: "long", weekday: "long", timeZone: "Europe/Istanbul" });
  return `📡 İçerik Radarı — ${d}`;
}
