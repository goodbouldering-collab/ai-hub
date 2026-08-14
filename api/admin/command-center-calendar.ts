import { withAdmin } from "../_lib/http.js";

const ACCOUNT = "goodbouldering@gmail.com";
const ACCOUNT_LABEL = "グッぼるクライミングCafe";
const DEFAULT_ICS_URL = "https://calendar.google.com/calendar/ical/goodbouldering%40gmail.com/public/basic.ics";
const DATE_KEY = /^\d{4}-\d{2}-\d{2}$/;
const MAX_RANGE_DAYS = 62;

type BusyDay = { date: string; busyCount: number; allDayCount: number };
type Occurrence = { start: Date; end: Date; allDay: boolean };

function validDate(value: unknown): value is string {
  if (typeof value !== "string" || !DATE_KEY.test(value)) return false;
  const parsed = new Date(`${value}T00:00:00Z`);
  return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
}
function rangeFromRequest(req: { url?: string }) {
  const url = new URL(req.url || "/api/admin/command-center/calendar", "https://aiclimb.vercel.app");
  const from = url.searchParams.get("from");
  const to = url.searchParams.get("to");
  if (!validDate(from) || !validDate(to)) return null;
  const span = Math.floor((Date.parse(`${to}T00:00:00Z`) - Date.parse(`${from}T00:00:00Z`)) / 86_400_000) + 1;
  return span >= 1 && span <= MAX_RANGE_DAYS ? { from, to } : null;
}
function unfold(ics: string): string[] { return ics.replace(/\r\n[ \t]/g, "").replace(/\n[ \t]/g, "").split(/\r?\n/); }
function property(lines: string[], name: string): { value: string; allDay: boolean } | null {
  const line = lines.find((entry) => entry.toUpperCase().startsWith(`${name};`) || entry.toUpperCase().startsWith(`${name}:`));
  if (!line) return null;
  const separator = line.indexOf(":");
  const left = separator >= 0 ? line.slice(0, separator) : line;
  const value = separator >= 0 ? line.slice(separator + 1).trim() : "";
  return { value, allDay: /VALUE=DATE/i.test(left) || /^\d{8}$/.test(value) };
}
function parseDate(raw: string, allDay: boolean): Date | null {
  if (/^\d{8}$/.test(raw)) return new Date(`${raw.slice(0, 4)}-${raw.slice(4, 6)}-${raw.slice(6, 8)}T00:00:00+09:00`);
  const basic = raw.match(/^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})(Z?)$/);
  if (basic) return new Date(`${basic[1]}-${basic[2]}-${basic[3]}T${basic[4]}:${basic[5]}:${basic[6]}${basic[7] ? "Z" : "+09:00"}`);
  const parsed = new Date(raw);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}
function addDays(value: Date, days: number): Date { const next = new Date(value); next.setUTCDate(next.getUTCDate() + days); return next; }
function dateKeys(from: string, to: string): string[] { const keys: string[] = []; for (let cursor = new Date(`${from}T00:00:00Z`), last = new Date(`${to}T00:00:00Z`); cursor <= last; cursor = addDays(cursor, 1)) keys.push(cursor.toISOString().slice(0, 10)); return keys; }
function occurrences(lines: string[], rangeStart: Date, rangeEnd: Date): Occurrence[] {
  const startProp = property(lines, "DTSTART");
  if (!startProp) return [];
  const start = parseDate(startProp.value, startProp.allDay);
  if (!start) return [];
  const endProp = property(lines, "DTEND");
  const end = endProp ? parseDate(endProp.value, endProp.allDay) : addDays(start, startProp.allDay ? 1 : 0);
  const actualEnd = end && end > start ? end : new Date(start.getTime() + 3_600_000);
  const cancelled = lines.some((line) => /^STATUS\s*:\s*CANCELLED$/i.test(line.trim())) || lines.some((line) => /^TRANSP\s*:\s*TRANSPARENT$/i.test(line.trim()));
  if (cancelled) return [];
  const rule = property(lines, "RRULE")?.value || "";
  const parts = Object.fromEntries(rule.split(";").map((part) => part.split("=")).filter((pair) => pair.length === 2));
  const frequency = String(parts.FREQ || "").toUpperCase();
  const interval = Math.max(1, Number(parts.INTERVAL || 1));
  const countLimit = Math.min(5_000, Math.max(1, Number(parts.COUNT || 5_000)));
  const until = parts.UNTIL ? parseDate(String(parts.UNTIL), false) : null;
  const output: Occurrence[] = [];
  let cursor = new Date(start);
  for (let index = 0; index < countLimit; index += 1) {
    const occurrenceEnd = new Date(cursor.getTime() + (actualEnd.getTime() - start.getTime()));
    if (until && cursor > until) break;
    if (cursor >= rangeEnd) break;
    if (occurrenceEnd > rangeStart) output.push({ start: cursor, end: occurrenceEnd, allDay: startProp.allDay });
    if (!frequency) break;
    cursor = frequency === "WEEKLY" ? addDays(cursor, 7 * interval) : frequency === "MONTHLY" ? new Date(cursor.setUTCMonth(cursor.getUTCMonth() + interval)) : addDays(cursor, interval);
  }
  return output;
}
function parseBusyDays(ics: string, from: string, to: string): BusyDay[] {
  const keys = dateKeys(from, to);
  const days = new Map<string, BusyDay>(keys.map((key) => [key, { date: key, busyCount: 0, allDayCount: 0 }]));
  const events = ics.split(/BEGIN:VEVENT/i).slice(1).map((block) => block.split(/END:VEVENT/i)[0]);
  const rangeStart = new Date(`${from}T00:00:00+09:00`);
  const rangeEnd = addDays(new Date(`${to}T00:00:00+09:00`), 1);
  for (const block of events) for (const occurrence of occurrences(unfold(block), rangeStart, rangeEnd)) for (const day of days.values()) {
    const dayStart = new Date(`${day.date}T00:00:00+09:00`);
    const dayEnd = addDays(dayStart, 1);
    if (occurrence.start < dayEnd && occurrence.end > dayStart) { day.busyCount += 1; if (occurrence.allDay) day.allDayCount += 1; }
  }
  return [...days.values()];
}

export default withAdmin({ method: "GET" }, async ({ req, res }) => {
  const range = rangeFromRequest(req);
  if (!range) { res.status(400).json({ error: "invalid_range" }); return; }
  try {
    const response = await fetch(process.env.GOOGLE_CALENDAR_ICS_URL || DEFAULT_ICS_URL, { headers: { accept: "text/calendar" }, signal: AbortSignal.timeout(10_000), cache: "no-store" });
    if (!response.ok) throw new Error("calendar_fetch_failed");
    res.setHeader("Cache-Control", "private, no-store, max-age=0");
    res.status(200).json({ account: ACCOUNT, accountLabel: ACCOUNT_LABEL, status: "connected", privacy: "busy_only", syncedAt: new Date().toISOString(), range, days: parseBusyDays(await response.text(), range.from, range.to) });
  } catch {
    res.setHeader("Cache-Control", "private, no-store, max-age=0");
    res.status(200).json({ account: ACCOUNT, accountLabel: ACCOUNT_LABEL, status: "unavailable", privacy: "busy_only", syncedAt: null, range, days: [] });
  }
});
