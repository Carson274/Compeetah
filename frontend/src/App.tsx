import { useDashboard } from "./hooks/useDashboard";
import { Header } from "./components/Header";
import { WeatherCard } from "./components/WeatherCard";
import { CommuteCard } from "./components/CommuteCard";
import { PeopleCards } from "./components/PeopleCards";
import { SensorsCard } from "./components/SensorsCard";
import { ChecklistCard } from "./components/ChecklistCard";

export default function App() {
  const { data, connected } = useDashboard();

  if (!data) {
    return <div className="loading">warming up the whiteboard…</div>;
  }

  const names = Object.fromEntries(data.people.map((p) => [p.id, p.name]));

  return (
    <div className="board">
      <Header connected={connected} />
      <div className="grid">
        <WeatherCard weather={data.weather} units={data.units} place={data.home.label} />
        <CommuteCard commute={data.commute} units={data.units} />
        <PeopleCards people={data.people} units={data.units} />
        <SensorsCard sensors={data.sensors} />
        <ChecklistCard items={data.checklist} names={names} />
      </div>
    </div>
  );
}
