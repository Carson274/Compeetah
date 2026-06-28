// Full-screen quick-reference for Secret Hitler, in the game's propaganda
// palette (cream / charcoal / fascist-red / liberal-blue). Toggled from a phone.

const Mustache = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 120 40" className={className} aria-hidden>
    <path
      d="M60 14c-6-9-16-12-26-9-7 2-12 7-19 7-5 0-9-3-11-7 0 11 8 19 19 19 14 0 22-7 37-7s23 7 37 7c11 0 19-8 19-19-2 4-6 7-11 7-7 0-12-5-19-7-10-3-20 0-26 9z"
      fill="currentColor"
    />
  </svg>
);

export function SecretHitlerRules() {
  return (
    <div className="sh-overlay">
      <header className="sh-header">
        <Mustache className="sh-stache" />
        <div className="sh-title">
          <h1>SECRET HITLER</h1>
          <p>Quick reference — the rules everyone forgets</p>
        </div>
        <Mustache className="sh-stache" />
      </header>

      <div className="sh-grid">
        <section className="sh-panel liberal">
          <h2>Liberals win if…</h2>
          <ul>
            <li>5 <b>Liberal</b> policies are enacted, <i>or</i></li>
            <li><b>Hitler is executed.</b></li>
          </ul>
        </section>

        <section className="sh-panel fascist">
          <h2>Fascists win if…</h2>
          <ul>
            <li>6 <b>Fascist</b> policies are enacted, <i>or</i></li>
            <li><b>Hitler is elected Chancellor</b> after 3 fascist policies.</li>
          </ul>
        </section>

        <section className="sh-panel sh-setup">
          <h2>Who knows whom</h2>
          <table className="sh-table">
            <thead>
              <tr><th>Players</th><th>Lib</th><th>Fasc</th><th>Hitler knows?</th></tr>
            </thead>
            <tbody>
              <tr><td>5</td><td>3</td><td>1</td><td className="yes">yes</td></tr>
              <tr><td>6</td><td>4</td><td>1</td><td className="yes">yes</td></tr>
              <tr><td>7</td><td>4</td><td>2</td><td className="no">blind</td></tr>
              <tr><td>8</td><td>5</td><td>2</td><td className="no">blind</td></tr>
              <tr><td>9</td><td>5</td><td>3</td><td className="no">blind</td></tr>
              <tr><td>10</td><td>6</td><td>3</td><td className="no">blind</td></tr>
            </tbody>
          </table>
          <p className="sh-foot">Fascists always know each other <i>and</i> Hitler. Hitler counts as the extra fascist.</p>
        </section>

        <section className="sh-panel sh-round">
          <h2>The round</h2>
          <ol className="sh-steps">
            <li><b>Election.</b> President nominates a Chancellor → all vote <b>Ja</b>/<b>Nein</b>.</li>
            <li>Majority <b>Ja</b> elects them; a <b>Nein</b> bumps the tracker and passes the presidency left.</li>
            <li><b>Legislative.</b> President draws 3, secretly discards 1, passes 2.</li>
            <li>Chancellor discards 1, <b>enacts</b> the last policy.</li>
            <li>If a fascist policy unlocked a <b>power</b>, the President uses it now.</li>
          </ol>
        </section>

        <section className="sh-panel sh-powers">
          <h2>Presidential powers (by fascist track)</h2>
          <table className="sh-table">
            <thead>
              <tr><th>Players</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th></tr>
            </thead>
            <tbody>
              <tr><td>5–6</td><td>—</td><td>—</td><td>Peek</td><td className="kill">Kill</td><td className="kill">Kill+Veto</td></tr>
              <tr><td>7–8</td><td>—</td><td>Investigate</td><td>Spec. Elect</td><td className="kill">Kill</td><td className="kill">Kill+Veto</td></tr>
              <tr><td>9–10</td><td>Investigate</td><td>Investigate</td><td>Spec. Elect</td><td className="kill">Kill</td><td className="kill">Kill+Veto</td></tr>
            </tbody>
          </table>
          <p className="sh-foot">
            <b>Peek</b> top 3 · <b>Investigate</b> a player's party (not their role) · <b>Spec. Elect</b> pick next President ·
            <b> Kill</b> a player (killing Hitler = Liberals win) · <b>Veto</b> Pres+Chanc scrap both policies (tracker +1).
            Powers fire right after the fascist policy and <b>must</b> be used.
          </p>
        </section>

        <section className="sh-panel sh-forget">
          <h2>★ Don't forget</h2>
          <ul>
            <li><b>Term limits:</b> the just-elected Pres &amp; Chancellor can't be <i>Chancellor</i> next round (5 left → only the last Chancellor).</li>
            <li><b>Chaos:</b> 3 failed elections → <b>top policy auto-enacts</b> (no power); tracker &amp; term limits reset.</li>
            <li><b>After 3 fascist policies, don't elect anyone you can't vouch for</b> — an elected Hitler loses the game.</li>
            <li><b>Talk freely, but never show your cards</b> — claims can be lies.</li>
          </ul>
        </section>
      </div>

      <footer className="sh-bar">tap your phone to hide &nbsp;•&nbsp; trust no one</footer>
    </div>
  );
}
