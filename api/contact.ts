/**
 * POST /api/contact — AIハブ お問い合わせフォーム送信
 *
 * Resend 経由で 2 通送る:
 *   1) 管理者宛(CONTACT_TO_EMAIL): 問い合わせ内容
 *   2) 送信者宛: 自動返信(控え) ※From が認証済みドメインでないと届かない場合あり
 *
 * 必要 env:
 *   RESEND_API_KEY      — Resend APIキー(未設定なら送信スキップして success を返す)
 *   CONTACT_TO_EMAIL    — 管理者の受信先(既定: climb@goodbouldering.com)
 *   CONTACT_FROM_EMAIL  — 送信元(既定: onboarding@resend.dev / Resendテストドメイン)
 *
 * n-デザインの app/api/contact/route.ts のパターンを Vercel Functions 形式へ移植。
 */
import { readJson, sendError, methodGuard } from "./_lib/http.js";
import type { VercelReq, VercelRes } from "./_lib/auth.js";

const BRAND = "AIハブ";
const SITE_URL = process.env.SITE_URL ?? "https://ai-hub-jp.vercel.app";

function escapeHtml(str: string): string {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function adminEmailHtml(p: { name: string; email: string; type?: string; message: string }) {
  const { name, email, type, message } = p;
  return `
  <div style="font-family:'Hiragino Sans','Yu Gothic',sans-serif;max-width:640px;margin:0 auto;background:#0A0F1C;padding:24px;">
    <div style="background:#0F1626;border:1px solid #1E2A45;border-radius:6px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#2DCBA1,#1E6F5C);padding:24px 28px;color:#06281F;">
        <p style="margin:0 0 6px;font-size:12px;letter-spacing:.12em;opacity:.85;">NEW INQUIRY</p>
        <h2 style="margin:0;font-size:20px;font-weight:800;">${BRAND} お問い合わせ</h2>
      </div>
      <div style="padding:28px;color:#F2F5FB;">
        <table style="width:100%;border-collapse:collapse;font-size:14px;">
          <tr><td style="padding:10px 0;color:#AEB9CE;width:120px;border-bottom:1px solid #1E2A45;">お名前</td><td style="padding:10px 0;font-weight:700;border-bottom:1px solid #1E2A45;">${escapeHtml(name)}</td></tr>
          <tr><td style="padding:10px 0;color:#AEB9CE;border-bottom:1px solid #1E2A45;">メール</td><td style="padding:10px 0;border-bottom:1px solid #1E2A45;"><a href="mailto:${escapeHtml(email)}" style="color:#2DCBA1;text-decoration:none;">${escapeHtml(email)}</a></td></tr>
          ${type ? `<tr><td style="padding:10px 0;color:#AEB9CE;border-bottom:1px solid #1E2A45;">ご相談種別</td><td style="padding:10px 0;border-bottom:1px solid #1E2A45;">${escapeHtml(type)}</td></tr>` : ""}
        </table>
        <p style="color:#AEB9CE;font-size:13px;margin:20px 0 8px;">ご相談内容</p>
        <div style="background:#0A0F1C;padding:16px 18px;border-radius:6px;white-space:pre-wrap;font-size:14px;line-height:1.8;color:#F2F5FB;border:1px solid #1E2A45;">${escapeHtml(message)}</div>
        <a href="mailto:${escapeHtml(email)}" style="display:inline-block;margin-top:20px;background:#2DCBA1;color:#06281F;padding:10px 20px;border-radius:6px;font-weight:700;font-size:13px;text-decoration:none;">返信する</a>
      </div>
    </div>
    <p style="text-align:center;color:#6E7C96;font-size:11px;margin-top:16px;">${BRAND} by 由井辰美 / ${SITE_URL}</p>
  </div>`;
}

function autoReplyHtml(p: { name: string; type?: string; message: string }) {
  const { name, type, message } = p;
  return `
  <div style="font-family:'Hiragino Sans','Yu Gothic',sans-serif;max-width:640px;margin:0 auto;background:#0A0F1C;padding:24px;">
    <div style="background:#0F1626;border:1px solid #1E2A45;border-radius:6px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#2DCBA1,#1E6F5C);padding:28px;color:#06281F;text-align:center;">
        <h2 style="margin:0;font-size:22px;font-weight:800;">お問い合わせありがとうございます</h2>
        <p style="margin:6px 0 0;font-size:13px;opacity:.85;">${BRAND}</p>
      </div>
      <div style="padding:28px;color:#F2F5FB;font-size:14px;line-height:1.9;">
        <p style="margin:0 0 12px;font-weight:700;">${escapeHtml(name)} 様</p>
        <p style="margin:0 0 12px;">この度は${BRAND}へお問い合わせいただき、誠にありがとうございます。</p>
        <p style="margin:0 0 12px;">内容を確認の上、<strong style="color:#2DCBA1;">2営業日以内</strong>にご連絡いたします。</p>
        <p style="margin:0 0 20px;color:#AEB9CE;font-size:13px;">以下は送信いただいた内容の控えです。</p>
        <div style="background:#0A0F1C;border:1px solid #1E2A45;border-radius:6px;padding:16px 18px;font-size:13px;">
          ${type ? `<p style="margin:0 0 8px;"><span style="color:#AEB9CE;">種別：</span>${escapeHtml(type)}</p>` : ""}
          <p style="margin:0;white-space:pre-wrap;color:#AEB9CE;">${escapeHtml(message)}</p>
        </div>
        <hr style="border:none;border-top:1px solid #1E2A45;margin:24px 0;" />
        <p style="color:#6E7C96;font-size:12px;margin:0;line-height:1.7;">
          ${BRAND}（由井辰美）<br />
          <a href="${SITE_URL}" style="color:#2DCBA1;">${SITE_URL}</a>
        </p>
      </div>
    </div>
    <p style="text-align:center;color:#6E7C96;font-size:11px;margin-top:16px;">
      このメールは送信専用アドレスから自動送信されています。
    </p>
  </div>`;
}

export default async function handler(req: VercelReq, res: VercelRes): Promise<void> {
  if (!methodGuard(req, res, "POST")) return;
  try {
    const body = await readJson(req);
    const name = String(body?.name ?? "").trim();
    const email = String(body?.email ?? "").trim();
    const type = body?.type ? String(body.type).trim() : undefined;
    const message = String(body?.message ?? "").trim();

    if (!name || !email || !message) {
      return sendError(res, 400, "必須項目（お名前・メール・内容）が不足しています。");
    }
    // 簡易メール形式チェック
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return sendError(res, 400, "メールアドレスの形式が正しくありません。");
    }
    if (message.length > 4000) {
      return sendError(res, 400, "内容が長すぎます（4000文字以内）。");
    }

    const resendApiKey = process.env.RESEND_API_KEY;
    const toEmail = process.env.CONTACT_TO_EMAIL ?? "climb@goodbouldering.com";
    const fromAddress = process.env.CONTACT_FROM_EMAIL ?? "onboarding@resend.dev";

    if (resendApiKey) {
      // 管理者宛（必須・失敗は500扱い）
      const adminRes = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: { Authorization: `Bearer ${resendApiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          from: `${BRAND} お問い合わせ <${fromAddress}>`,
          to: [toEmail],
          reply_to: email,
          subject: `【${BRAND}】お問い合わせ: ${name} 様`,
          html: adminEmailHtml({ name, email, type, message }),
        }),
      });
      if (!adminRes.ok) {
        const errText = await adminRes.text();
        console.error("Resend (admin) error:", errText);
        return sendError(res, 502, "送信に失敗しました。時間をおいて再度お試しください。");
      }
      // 自動返信（任意・失敗は無視）
      await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: { Authorization: `Bearer ${resendApiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          from: `${BRAND} <${fromAddress}>`,
          to: [email],
          subject: `【${BRAND}】お問い合わせありがとうございます`,
          html: autoReplyHtml({ name, type, message }),
        }),
      }).catch(() => {});
    } else {
      // env 未設定時は送信せず success（フォーム動作確認用・ログに残す）
      console.warn("RESEND_API_KEY 未設定のため送信スキップ:", { name, email, type });
    }

    res.status(200).json({ success: true });
  } catch (err) {
    console.error("Contact API error:", err);
    return sendError(res, 500, "サーバーエラーが発生しました。");
  }
}
