import { useEffect, useState } from "react";

export function Header({ connected }: { connected: boolean }) {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const time = now.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  const date = now.toLocaleDateString([], { weekday: "long", month: "long", day: "numeric" });

  return (
    <header className="topbar">
      <div className="brand">
        <h1>COMPEETAH</h1>
        <span className="tag">home base</span>
      </div>
      <div className="statusline">
        <div className="conn">
          <span className={`dot ${connected ? "live" : "down"}`} />
          {connected ? "live" : "reconnecting"}
        </div>
        <div className="clock">
          {time}
          <span className="date">{date}</span>
        </div>
      </div>
    </header>
  );
}
