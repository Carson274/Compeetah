import { Card } from "./Card";
import { Car } from "../icons";
import { distance, duration, durationUnit, ago } from "../format";
import type { Commute, Units } from "../types";

export function CommuteCard({ commute, units }: { commute: Commute | null; units: Units }) {
  const secs = commute?.duration_traffic_s ?? commute?.duration_s ?? null;

  return (
    <Card title="Drive to Netflix" icon={<Car />} area="area-commute" extra="commute">
      {!commute || commute.status === "pending" ? (
        <div className="placeholder">Calculating the commute…</div>
      ) : commute.status === "needs_key" ? (
        <div className="notice">
          Add a Google Maps API key to <code>backend/.env</code> to see live drive time.
        </div>
      ) : commute.status === "error" ? (
        <div className="notice">Couldn't reach Google Maps — will retry next cycle.</div>
      ) : (
        <>
          <div className="eta">
            <span className="bignum num">{duration(secs)}</span>
            <span className="unit">{durationUnit(secs)}</span>
          </div>
          <div className="route">
            <b>{commute.origin_label}</b> → <b>{commute.dest_label}</b>
          </div>
          <div className="sub">
            {commute.distance_m != null && <span className="chip">{distance(commute.distance_m, units)}</span>}
            {commute.duration_traffic_s != null && <span className="chip">with traffic</span>}
            <span className="chip muted">updated {ago(commute.as_of)}</span>
          </div>
        </>
      )}
    </Card>
  );
}
