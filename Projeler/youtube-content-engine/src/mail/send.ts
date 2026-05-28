import { Resend } from "resend";
import { log, warn } from "../lib/logger.js";

const resend = new Resend(process.env.RESEND_API_KEY);
const FROM = process.env.RESEND_FROM || "radar@example.com";
const TO = process.env.RESEND_TO || "admin@example.com";

export async function sendMail(subject: string, html: string): Promise<void> {
  const r = await resend.emails.send({ from: FROM, to: TO, subject, html });
  if (r.error) {
    warn(`resend error: ${JSON.stringify(r.error)}`);
    throw new Error(`resend send failed: ${r.error.message}`);
  }
  log(`mail sent → ${TO} (id: ${r.data?.id})`);
}

export async function sendFailureMail(error: string): Promise<void> {
  try {
    await resend.emails.send({
      from: FROM,
      to: TO,
      subject: "⚠️ İçerik Radarı bugün çalışmadı",
      html: `<pre style="font-family:monospace;font-size:12px;color:#333;white-space:pre-wrap;">${error.slice(0, 4000)}</pre>`,
    });
  } catch (e: any) {
    warn(`failure mail also failed: ${e.message}`);
  }
}
