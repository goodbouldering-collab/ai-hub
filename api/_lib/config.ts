/**
 * 環境変数の解決を一元化。各 endpoint からはこのモジュールを通して参照する。
 * これによりデフォルト値・名前変更を1箇所で管理できる。
 */

import { ConfigError } from "./http.js";

// 2026-05-07: OAuth アプリ ai-hub-admin が 1064 にアクセスできないため、
// 1086 を本番扱いに切り替え。preview は環境変数で別テンプレを指定したい時用。
// デフォルトは preview = live = 1086（同テンプレへの書き込みになる）。
export const COLORME_PREVIEW_TEMPLATE_ID = (): number =>
  Number(process.env.COLORME_PREVIEW_TEMPLATE_ID || 1086);

export const COLORME_LIVE_TEMPLATE_ID = (): number =>
  Number(process.env.COLORME_LIVE_TEMPLATE_ID || 1086);

export function templateIdFor(target: "preview" | "live"): number {
  return target === "live" ? COLORME_LIVE_TEMPLATE_ID() : COLORME_PREVIEW_TEMPLATE_ID();
}

export function requireEnv(name: string): string {
  const v = process.env[name];
  if (!v) throw new ConfigError(`${name} is not set`);
  return v;
}

export const claudeModel = (): string =>
  process.env.AI_HUB_CLAUDE_MODEL || "claude-sonnet-4-6";
