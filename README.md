# Signal//Noise

**Signal//Noise** is a system for turning Spotify listening history into a structured, time-based archive.

It treats music consumption not just as entertainment, but as:
- memory
- repetition
- pattern
- and potential signal within large-scale digital behavior

---

## Why

Spotify is good at recommending music.  
It is not good at helping you remember your own listening history.

This project starts from a simple need:

> "What did I listen to in April, five years ago?"

From there, it expands into a broader idea:
listening behavior as a form of personal archive — and possibly as a trace of cultural patterns.

---

## What it does

- Ingests two Spotify GDPR export ZIPs into a single SQLite database (long-format events table, indexed)
- Builds structured **yearly / monthly / hourly / by-day-of-week** aggregates
- Computes a **music profile** (top artists, tracks, listening modes, long-burn objects)
- **Correlates** monthly listening hours with monthly email-sent volume (from a parallel Gmail corpus) — currently **r = +0.023**, i.e. the two are essentially decoupled at the monthly level
- Identifies **hidden gems** (high-engagement, low-volume artists), **recurring-after-gap** tracks, **forgotten favorites**, and **diversity metrics** (Shannon entropy + Gini coefficient per year)
- Generates **Spotify-importable playlists** (CSV with `spotify:track:` URIs) — 7 curated playlists + one per year (2013–2026)

---

## Quick start

```bash
# One-shot reproduction (reads from /root/.openclaw/Schleuse/spotify/ + ~/.hermes/data/)
./scripts/build_all.sh
```

Outputs land in `reports/`, `data/processed/`, and `playlists/`.

---

## Pipeline

```
[Spotify GDPR ZIPs]                                  [Gmail corpus DB]
        │                                                      │
        ▼                                                      ▼
src/ingest_spotify.py ──► data/processed/spotify.db ◄── src/correlate.py
        │                              │
        │                              ├─► src/build_music_profile.py  → reports/music_profile.md
        │                              │
        │                              ├─► src/hidden_gems.py          → reports/hidden_gems.md
        │                              │
        │                              └─► src/playlists.py            → playlists/*.csv
        │
        └─► reports/correlation_report.md
```

---

## Findings (preliminary, treated as hypothesis)

- **Listening and email-sent volume are uncorrelated** (Pearson r = +0.023 over 125 months). Different drivers.
- **Peak month: 2020-07** (331 hours, ~10.7h/day). Lockdown + relationship crisis overlap.
- **Lowest year (since 2017): 2018** (128h). Coincides with Berlin TXL FUTR HUB project (more in-person work, less headphone time).
- **Shannon entropy** of artist shares doubled from 2017 (7.75) to 2020 (9.86): high-volume years were also the most diverse.
- **Top "comfort objects"** (tracks with > 5h lifetime listening): Hallogallo (NEU!), Jailbreak Live (AC/DC), Maggot Brain (Funkadelic), Politicians In My Eyes (Death) — all > 8h.
- **Top hour-of-day**: 17:00 (789h lifetime). Day-of-week: Saturday dominates.
- **Skim-vs-engage ratio**: 2.5% skipped, 26% shuffle. Deliberate listening, not passive.
- **Genre axis**: tight (Classic Rock, Deutschrock/Krautrock, US Punk-adjacent). No pop, hip-hop, electronica, schlager.

---

## Repository layout

```
.
├── README.md                        (this file)
├── LICENSE
├── .gitignore
├── scripts/
│   └── build_all.sh                 (one-shot reproduction)
├── src/
│   ├── ingest_spotify.py            (ZIP → SQLite, idempotent)
│   ├── build_music_profile.py       (SQLite → JSON + narrative)
│   ├── correlate.py                 (Spotify + email → correlation)
│   ├── hidden_gems.py               (pattern discovery)
│   └── playlists.py                 (CSV generation)
├── data/
│   ├── life_phases.json             (curated life-phase markers)
│   └── processed/                   (gitignored except *.csv, *.txt, life_phases.json)
├── reports/
│   ├── correlation_report.md
│   ├── music_profile.md
│   ├── hidden_gems.md
│   └── playlists.md
└── playlists/
    ├── life_phases.csv              (1 track per year, 2013-2026)
    ├── long_burn.csv                (tracks > 5h lifetime)
    ├── krautrock_drift.csv          (German/Deutschrock)
    ├── hidden_gems.csv              (under-the-radar artists)
    ├── recurring.csv                (tracks that resurface after gaps)
    ├── forgotten_favorites.csv      (heavy past, silent ≥ 2y)
    └── by_year/year_*.csv           (top 30 tracks per year)
```

---

## Roadmap

**Phase 1** ✅
- Data ingestion (Spotify export)
- SQLite data model (long format, indexed)
- Basic queries and reporting

**Phase 2** (next)
- Web UI for timeline-based exploration
- Coach-integration: load `music_profile.json` into `marcus-coach` skill context
- API layer for derived insights

**Phase 3**
- Live Spotify API integration (refresh, no re-export)
- PKS integration (Personal Knowledge System, `spotify/` section)
- Comparison with public charts (Signal/Noise vs. national listening patterns)

**Phase 4 (experimental)**
- Hypothesis-driven analysis with the marcus-coach
- "What did I listen to in 2019-03 vs how was I feeling then?" — multi-source correlation

---

## Methodological note

This project does **not** claim that listening data reveals objective psychological truth or social reality.

Spotify data is:
- partial
- platform-shaped
- context-dependent

Any interpretation is treated as:
- pattern
- hypothesis
- or exploratory signal — not proof.

---

## Status

Phase 1 complete. Data is persisted, queries run, playlists generate, correlations report.
Phase 2: web UI + coach integration — pending.
