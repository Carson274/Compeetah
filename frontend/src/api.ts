import type { ChecklistItem, Dashboard } from "./types";

// Same-origin by default (Vite proxies /api + /ws in dev; FastAPI serves both
// in prod). Override for a separate phone app via VITE_API_BASE.
const BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");

export function wsUrl(): string {
  if (BASE) return BASE.replace(/^http/, "ws") + "/ws";
  const proto = location.protocol === "https:" ? "wss" : "ws";
  return `${proto}://${location.host}/ws`;
}

async function j<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}

export const api = {
  dashboard: () => fetch(`${BASE}/api/dashboard`).then(j<Dashboard>),
  checklist: () => fetch(`${BASE}/api/checklist`).then(j<ChecklistItem[]>),
  addItem: (text: string, assignee?: string | null) =>
    fetch(`${BASE}/api/checklist`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ text, assignee }),
    }).then(j<ChecklistItem>),
  toggle: (id: number) =>
    fetch(`${BASE}/api/checklist/${id}/toggle`, { method: "POST" }).then(j<ChecklistItem>),
  remove: (id: number) =>
    fetch(`${BASE}/api/checklist/${id}`, { method: "DELETE" }).then(j<void>),
};
