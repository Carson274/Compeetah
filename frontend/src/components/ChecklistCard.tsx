import { Check } from "../icons";
import type { ChecklistItem } from "../types";

// Read-only on the TV; toggling happens from a phone at /control.
export function ChecklistCard({ items, names }: { items: ChecklistItem[]; names: Record<string, string> }) {
  const done = items.filter((i) => i.done).length;
  const pct = items.length ? (done / items.length) * 100 : 0;

  return (
    <section className="area-checklist">
      <div className="card checklist">
        <h2>
          <span className="ic"><Check /></span>
          To-do
        </h2>
        <div className="hrule" />
        <ul className="items">
          {items.length === 0 && <li className="citem"><span className="label muted">All clear ✨</span></li>}
          {items.map((i) => (
            <li key={i.id} className={`citem ${i.done ? "done" : ""}`}>
              <span className="box">{i.done && <Check size={16} />}</span>
              <span className="label">{i.text}</span>
              {i.assignee && <span className="who">{names[i.assignee] ?? i.assignee}</span>}
            </li>
          ))}
        </ul>
        <div className="foot">
          <div className="progress"><span style={{ width: `${pct}%` }} /></div>
          <div className="hint">{done}/{items.length} · tap on your phone →</div>
        </div>
      </div>
    </section>
  );
}
