export type Units = "imperial" | "metric";

export interface Place {
  label: string;
  lat: number;
  lon: number;
}

export interface Weather {
  temperature_c: number;
  apparent_c: number | null;
  humidity: number | null;
  wind_kmh: number | null;
  weather_code: number | null;
  is_day: boolean | null;
  description: string;
  as_of: string | null;
}

export interface Commute {
  origin_label: string;
  dest_label: string;
  distance_m: number | null;
  duration_s: number | null;
  duration_traffic_s: number | null;
  as_of: string | null;
  status: "ok" | "needs_key" | "error" | "pending";
  map_embed_url: string | null;
}

export interface Person {
  id: string;
  name: string;
  color: string;
  is_home: boolean | null;
  place_label: string | null;
  distance_home_m: number | null;
  lat: number | null;
  lon: number | null;
  battery: number | null;
  velocity_kmh: number | null;
  last_seen: string | null;
  status: "home" | "away" | "unknown";
}

export interface Sensor {
  sensor: string;
  metric: string;
  value: number;
  unit: string | null;
  as_of: string;
}

export interface ChecklistItem {
  id: number;
  text: string;
  done: boolean;
  position: number;
  assignee: string | null;
}

export interface Dashboard {
  units: Units;
  overlay: string | null;
  home: Place;
  work: Place;
  weather: Weather | null;
  commute: Commute | null;
  people: Person[];
  sensors: Sensor[];
  checklist: ChecklistItem[];
  server_time: string;
}
