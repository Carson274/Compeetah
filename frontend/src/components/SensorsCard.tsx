import { Card } from "./Card";
import { Sensor as SensorIcon } from "../icons";
import { metricLabel } from "../format";
import type { Sensor } from "../types";

export function SensorsCard({ sensors }: { sensors: Sensor[] }) {
  return (
    <Card title="Sensors" icon={<SensorIcon />} area="area-sensors" extra="sensors">
      {sensors.length === 0 ? (
        <div className="placeholder">
          <SensorIcon size={40} className="ic" />
          <div>No sensors yet — wire one into the Pi and it shows up here.</div>
        </div>
      ) : (
        <div className="sensorgrid">
          {sensors.map((s) => (
            <div className="sensorcell" key={`${s.sensor}:${s.metric}`}>
              <div className="v">
                {Number.isInteger(s.value) ? s.value : s.value.toFixed(1)}
                <span style={{ fontSize: "0.5em" }}>{s.unit ?? ""}</span>
              </div>
              <div className="k">{metricLabel(s.metric)}</div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
