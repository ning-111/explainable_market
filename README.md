# Explainable Market

A demo web app that connects **news events to price moves** — see *why* a
symbol moved, not just that it did. English UI, Flask + SQLite, fully offline:
no live feeds or external services are contacted.

## Run

```bash
cd explainable_market
./run.sh                 # uses the venv in ../venv
# or: ../venv/bin/python app.py
```

Open http://127.0.0.1:5050

## Test account

The login page shows the built-in test account; use it to sign in directly:

| Username | Password  |
|----------|-----------|
| `demo`   | `demo123` |

(Shortcut: the "Fill demo credentials" button on the login page prefills the form.)

## Features

- **Login** — session-based auth with a pre-seeded test account.
- **Watchlist** — add/remove symbols per user; dashboard shows last price,
  day change and a 30-day sparkline for each.
- **News feed** — sample headlines with source, date and sentiment
  (positive / neutral / negative), plus a "Collect news now" button that
  simulates a collection pass by generating a few fresh sample headlines
  (no live data; everything stays offline).
- **Explainable market** — every seeded price series has news-driven shocks
  engineered into it, so:
  - the symbol chart shows news markers on the exact days moves happened;
  - the **News impact analysis** table shows each event's day move, the
    following 3-session move, and whether the reaction was consistent with
    the sentiment;
  - the dashboard pairs top watchlist movers with their most likely
    headline ("Explained" / "No related news").

## Stack & layout

Flask 3 + SQLite (stdlib `sqlite3`), server-side SVG charts (no CDN/JS deps).
Seed data is deterministic — 12 symbols, 120 trading days, ~20 news events.

```
app.py         routes: auth, dashboard, watchlist, symbol detail, news
db.py          schema + helpers (auto-creates and seeds data/market.db)
seed.py        deterministic sample data with engineered news-price shocks
charts.py      SVG sparkline & price chart with news markers
collector.py   simulated news collection (offline sample generator)
templates/     Jinja2 pages (English UI)
static/        stylesheet
```

To reset all data, delete `data/market.db` and restart.
