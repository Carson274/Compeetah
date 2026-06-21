# 🟥 Compeetah

A wall-mounted **whiteboard dashboard** for a Raspberry Pi + TV, with a subtle
Netflix streak. It shows, at a glance:

- 🌡️ **Outside weather** for home (free, no key — [Open-Meteo](https://open-meteo.com))
- 🚗 **Live drive time to Netflix** with traffic, refreshed every 5 minutes ([Google Maps](https://developers.google.com/maps/documentation/distance-matrix))
- 📍 **Where you and your roommate are** — `HOME` or how far away — via [OwnTracks](https://owntracks.org)
- ✅ A **to-do checklist** you tick off from your phone (the TV stays read-only)
- 📡 A **sensors** panel ready for whatever you wire into the Pi later

Everything is logged to a local **SQLite** database so you can mine the history
later (commute trends, time-at-home, sensor charts…).

```
┌─ COMPEETAH ──────────────────────────────── 5:52 PM · Sat Jun 20 ─┐
│  Outside        Drive to Netflix     Carson          ✅ To-do      │
│   71°F            15 MIN              HOME             ☐ …          │
│   Clear          10.2 mi · traffic   @ SJ Airport     ☐ …          │
│  Sensors                             Roommate                      │
│   48%  22.6°C                         AWAY  4.5 mi                 │
└────────────────────────────────────────────────────────────────────┘
```

---

## Architecture

```
            phones (OwnTracks)             phone/browser (/control)
                   │  HTTP location              │  checklist edits
                   ▼                             ▼
        ┌──────────────────────── FastAPI (backend/) ───────────────────────┐
        │  routers: owntracks · checklist · sensors · dashboard + /ws        │
        │  providers: weather (Open-Meteo) · drivetime (Google) · location   │
        │  scheduler: every 5 min → fetch weather + drive time → store + push │
        │  SQLite (data/compeetah.sqlite3)  ← all readings, append-only       │
        └─────────────────────────────────┬─────────────────────────────────┘
                                           │ websocket push
                                           ▼
                            React dashboard (frontend/) on the TV
```

- **Backend** — FastAPI + SQLAlchemy + APScheduler. Polls weather & drive time,
  ingests OwnTracks pushes, serves a REST API and a `/ws` websocket that pushes a
  fresh snapshot to every screen whenever anything changes.
- **Frontend** — React + Vite. Two views from one bundle: the **TV dashboard**
  (`/`) and the phone-friendly **control** (`/control`).
- **Location** lives behind a small `LocationProvider` seam
  (`backend/app/providers/location.py`) so OwnTracks can later be swapped for a
  Find My bridge, a GPS sensor, etc. without touching the rest of the app.

---

## Quick start (development, on your laptop)

**1. Backend**

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then add your Google Maps key (see below)
uvicorn app.main:app --reload --port 8000
```

**2. Frontend** (second terminal)

```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173  (proxies /api + /ws → :8000)
```

Open **http://localhost:5173** for the dashboard and
**http://localhost:5173/control** for the phone checklist.

Weather shows up immediately. Drive time needs a Google key; locations need
OwnTracks (both below).

---

## Configuration

Two files, clearly split:

| File | Holds | Tracked in git? |
| --- | --- | --- |
| [`config.yaml`](config.yaml) | home/work coordinates, your names, units, poll interval, home radius | ✅ yes (no secrets) |
| `backend/.env` | API keys & tokens | ❌ no — gitignored |

Edit `config.yaml` to set your real home (it ships pointed at San José Airport),
confirm the Netflix office, set `units` (`imperial`/`metric`), and name the two
people. `drive_origin: home` measures the commute from home; `live` measures it
from whoever's most recent location.

### Google Maps key (drive time)

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project
   and **enable the “Distance Matrix API”**.
2. Create an API key, then put it in `backend/.env`:
   ```
   GOOGLE_MAPS_API_KEY=your_key_here
   ```

Until that's set, the commute card simply shows an “add a key” note — nothing
breaks. **Never commit a real key** — it belongs only in `backend/.env`.

---

## Locations with OwnTracks

OwnTracks is a free, open-source location app that reports to *your* server (no
third party). One-time setup per phone:

1. Install **OwnTracks** ([iOS](https://apps.apple.com/app/owntracks/id692424691) /
   [Android](https://play.google.com/store/apps/details?id=org.owntracks.android)).
2. In the app: **Settings → Connection**
   - **Mode:** `HTTP`
   - **URL:** `http://<pi-host>:8000/api/owntracks?user=carson`
     (use `?user=roommate` on the other phone — the ids come from `config.yaml`)
   - **Device ID / Tracker ID (TID):** anything; or match `owntracks_tid` in config.
   - If you set `OWNTRACKS_TOKEN` in `.env`, put it in the app's **Password**
     field (and set any username) so strangers can't POST fake locations.
3. Hit the ▶︎/“publish” button once to send the first fix. The person card flips
   from *“waiting”* to `HOME` / `AWAY`.

**“Home” detection** is done server-side: anything within `home.radius_m` of the
home point counts as home. No geofence config needed on the phone (though
OwnTracks regions work too).

### Reaching the Pi when you're away from home

To get location updates *while commuting* (the interesting part!), the phones
need to reach the Pi from outside your home network. The clean, safe option is
**[Tailscale](https://tailscale.com)** (a private mesh VPN, free for personal
use):

1. Install Tailscale on the Pi and both phones, signed into the same account.
2. Point the OwnTracks URL at the Pi's Tailscale name, e.g.
   `http://compeetah-pi:8000/api/owntracks?user=carson`.

No ports exposed to the public internet. (A Cloudflare Tunnel works too if you
prefer a public hostname — set `OWNTRACKS_TOKEN` if you do.)

---

## Running on the Raspberry Pi (kiosk)

**1. Build the frontend once** (the backend then serves it on a single port):

```bash
cd frontend && npm install && npm run build
```

**2. Run the backend** (serves API, websocket, *and* the built dashboard):

```bash
cd backend && source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Now `http://<pi>:8000` is the dashboard and `http://<pi>:8000/control` is the
phone view.

**3. Auto-start the server** — drop this in `/etc/systemd/system/compeetah.service`
(adjust paths/user), then `sudo systemctl enable --now compeetah`:

```ini
[Unit]
Description=Compeetah dashboard
After=network-online.target

[Service]
User=pi
WorkingDirectory=/home/pi/Compeetah/backend
ExecStart=/home/pi/Compeetah/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**4. Launch Chromium in kiosk mode** pointed at the dashboard. Add to the Pi's
autostart (e.g. `~/.config/lxsession/LXDE-pi/autostart` or a `.desktop` entry):

```
chromium-browser --kiosk --noerrdialogs --disable-infobars \
  --incognito http://localhost:8000
```

Tip: `xset s off -dpms` keeps the TV from sleeping; `unclutter` hides the cursor.

---

## Adding sensors later

Any script on the Pi can push readings — they show up on the dashboard and are
stored for history:

```bash
curl -X POST http://localhost:8000/api/sensors \
  -H 'content-type: application/json' \
  -d '{"sensor":"living_room","metric":"temperature","value":22.4,"unit":"C"}'
```

or a batch: `{"readings": [ {…}, {…} ]}`. A tiny `while True: read; post; sleep`
loop reading a BME280/DHT22 over GPIO is all you need.

---

## Data & statistics

Everything lands in `data/compeetah.sqlite3` (SQLite), append-only:

| Table | What |
| --- | --- |
| `location_readings` | every OwnTracks fix + computed `is_home`, `distance_home_m` |
| `weather_readings` | weather every poll |
| `drivetime_readings` | commute duration/distance every poll |
| `sensor_readings` | generic `(sensor, metric, value, unit)` rows |
| `checklist_items` | the to-do list |

Point any SQLite tool at it (`sqlite3 data/compeetah.sqlite3`) for ad-hoc stats,
or build charts on top later.

---

## Roadmap

- 📱 A dedicated **phone app** (the repo is structured to add a `mobile/` later;
  the API + `/control` already work from any phone browser as a PWA-style start).
- 🗺️ Reverse-geocode “away” locations to show a place name + a mini map.
- 📈 A stats/history view over the SQLite data.
- 🔌 Real Pi sensors (temp/humidity/air quality) on the sensors panel.

---

## Project layout

```
config.yaml            # editable settings (home/work/users/units)
backend/
  app/
    main.py            # FastAPI app, lifespan, serves built frontend
    config.py db.py    # settings + SQLite
    models.py schemas.py
    scheduler.py       # 5-min weather + drive-time poll
    ws.py services.py  # websocket hub + snapshot builder
    providers/         # weather · drivetime · location (pluggable)
    routers/           # owntracks · checklist · sensors · dashboard
frontend/
  src/
    App.tsx            # the TV dashboard
    control/Control.tsx# the phone checklist
    components/ hooks/ icons.tsx styles.css
```
