import { useEffect, useState } from "react";
import { api } from "../api";
import { Check } from "../icons";
import type { ChecklistItem } from "../types";

// Phone-friendly control surface: the TV is read-only, so checking things off
// and adding tasks happens here. Big tap targets, no fiddly UI.
export default function Control() {
  const [items, setItems] = useState<ChecklistItem[]>([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);

  const load = () => api.checklist().then(setItems).catch(() => {});
  useEffect(() => {
    load();
    const onFocus = () => load();
    window.addEventListener("focus", onFocus);
    return () => window.removeEventListener("focus", onFocus);
  }, []);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    const t = text.trim();
    if (!t || busy) return;
    setBusy(true);
    try {
      const item = await api.addItem(t);
      setItems((xs) => [...xs, item]);
      setText("");
    } finally {
      setBusy(false);
    }
  }

  async function toggle(id: number) {
    setItems((xs) => xs.map((i) => (i.id === id ? { ...i, done: !i.done } : i))); // optimistic
    try {
      await api.toggle(id);
    } catch {
      load();
    }
  }

  async function remove(id: number) {
    setItems((xs) => xs.filter((i) => i.id !== id));
    try {
      await api.remove(id);
    } catch {
      load();
    }
  }

  return (
    <div className="control">
      <header>
        <h1>COMPEETAH</h1>
        <span>checklist</span>
      </header>

      <form className="addform" onSubmit={add}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Add a task…"
          enterKeyHint="done"
        />
        <button className="btn" type="submit" disabled={busy}>Add</button>
      </form>

      {items.length === 0 ? (
        <div className="ctl-empty">Nothing here yet — add your first task above.</div>
      ) : (
        <ul className="ctl-list">
          {items.map((i) => (
            <li key={i.id} className={`ctl-item ${i.done ? "done" : ""}`}>
              <button className="toggle" onClick={() => toggle(i.id)} aria-label="toggle">
                {i.done && <Check size={22} />}
              </button>
              <span className="label">{i.text}</span>
              <button className="del" onClick={() => remove(i.id)} aria-label="delete">×</button>
            </li>
          ))}
        </ul>
      )}

      <a className="backlink" href="/">← back to the dashboard</a>
    </div>
  );
}
