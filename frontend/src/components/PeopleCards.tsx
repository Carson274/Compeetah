import { Home, Pin, Battery } from "../icons";
import { distance, speed, ago } from "../format";
import type { Person, Units } from "../types";

function PersonCard({ p, units }: { p: Person; units: Units }) {
  const moving = (p.velocity_kmh ?? 0) > 3;
  return (
    <div className={`card person ${p.status}`}>
      <div className="row">
        <div className="who">
          <span className="swatch" style={{ background: p.color }} />
          {p.name}
        </div>
        <span className={`statepill ${p.status}`}>
          {p.status === "home" ? <Home size={14} /> : <Pin size={14} />}
          {p.status === "unknown" ? "no signal" : p.status}
        </span>
      </div>

      {p.status === "home" && <div className="state">HOME</div>}
      {p.status === "away" && <div className="state">AWAY</div>}
      {p.status === "unknown" && <div className="state">Waiting for first location…</div>}

      {p.status === "away" && p.distance_home_m != null && (
        <div className="detail">{distance(p.distance_home_m, units)} from home{moving ? ` · ${speed(p.velocity_kmh, units)}` : ""}</div>
      )}
      {p.status === "home" && <div className="detail">at {p.place_label ?? "home"}</div>}
      {p.status === "unknown" && <div className="detail">set up OwnTracks on this phone</div>}

      <div className="foot">
        {p.battery != null && (
          <span className="chip"><Battery size={15} /> {p.battery}%</span>
        )}
        {p.last_seen && <span className="chip muted">seen {ago(p.last_seen)}</span>}
      </div>
    </div>
  );
}

export function PeopleCards({ people, units }: { people: Person[]; units: Units }) {
  return (
    <section className="area-people">
      {people.map((p) => (
        <PersonCard key={p.id} p={p} units={units} />
      ))}
    </section>
  );
}
