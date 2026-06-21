import type { Units } from "./types";

export const cToF = (c: number) => (c * 9) / 5 + 32;

/** Temperature with degree sign, rounded, in the active unit system. */
export function temp(c: number | null | undefined, units: Units): string {
  if (c == null) return "—";
  const v = units === "imperial" ? cToF(c) : c;
  return `${Math.round(v)}°`;
}

export function tempUnit(units: Units): string {
  return units === "imperial" ? "F" : "C";
}

/** Distance from meters, in mi or km. */
export function distance(m: number | null | undefined, units: Units): string {
  if (m == null) return "—";
  if (units === "imperial") {
    const mi = m / 1609.34;
    return mi < 0.1 ? `${Math.round(m * 3.281)} ft` : `${mi.toFixed(1)} mi`;
  }
  return m < 100 ? `${Math.round(m)} m` : `${(m / 1000).toFixed(1)} km`;
}

export function speed(kmh: number | null | undefined, units: Units): string {
  if (kmh == null) return "—";
  return units === "imperial"
    ? `${Math.round(kmh / 1.609)} mph`
    : `${Math.round(kmh)} km/h`;
}

/** Seconds -> "23 min" / "1 hr 5 min". */
export function duration(seconds: number | null | undefined): string {
  if (seconds == null) return "—";
  const mins = Math.round(seconds / 60);
  if (mins < 60) return `${mins}`;
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  return m ? `${h}h ${m}` : `${h}h`;
}

export function durationUnit(seconds: number | null | undefined): string {
  if (seconds == null) return "";
  return seconds < 3600 ? "min" : "";
}

/** Relative time like "just now", "4 min ago", "2 hr ago". */
export function ago(iso: string | null | undefined): string {
  if (!iso) return "never";
  const then = new Date(iso).getTime();
  const secs = Math.max(0, (Date.now() - then) / 1000);
  if (secs < 45) return "just now";
  const mins = Math.round(secs / 60);
  if (mins < 60) return `${mins} min ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs} hr ago`;
  const days = Math.round(hrs / 24);
  return `${days} d ago`;
}

const TITLE: Record<string, string> = { temperature: "Temp", humidity: "Humidity" };
export function metricLabel(metric: string): string {
  return TITLE[metric] ?? metric.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
