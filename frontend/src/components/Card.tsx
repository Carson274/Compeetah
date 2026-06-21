import type { ReactNode } from "react";

interface Props {
  title: string;
  icon?: ReactNode;
  area: string; // e.g. "area-weather"
  extra?: string; // extra class on the inner .card (e.g. "weather")
  children: ReactNode;
}

export function Card({ title, icon, area, extra, children }: Props) {
  return (
    <section className={area}>
      <div className={`card ${extra ?? ""}`}>
        <h2>
          {icon && <span className="ic">{icon}</span>}
          {title}
        </h2>
        <div className="hrule" />
        <div className="body">{children}</div>
      </div>
    </section>
  );
}
