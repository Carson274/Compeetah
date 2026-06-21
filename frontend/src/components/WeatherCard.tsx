import { Card } from "./Card";
import { Thermo } from "../icons";
import { temp, tempUnit } from "../format";
import type { Units, Weather } from "../types";

export function WeatherCard({ weather, units, place }: { weather: Weather | null; units: Units; place: string }) {
  return (
    <Card title="Outside" icon={<Thermo />} area="area-weather" extra="weather">
      {weather ? (
        <>
          <div className="bignum temp">
            {temp(weather.temperature_c, units)}
            <sup>{tempUnit(units)}</sup>
          </div>
          <div className="desc">{weather.description}</div>
          <div className="meta">
            {weather.apparent_c != null && (
              <span className="chip">Feels {temp(weather.apparent_c, units)}</span>
            )}
            {weather.humidity != null && <span className="chip">{Math.round(weather.humidity)}% humidity</span>}
            <span className="chip">{place}</span>
          </div>
        </>
      ) : (
        <div className="placeholder">Fetching the weather…</div>
      )}
    </Card>
  );
}
