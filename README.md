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

> “What did I listen to in April, five years ago?”

From there, it expands into a broader idea:
listening behavior as a form of personal archive — and possibly as a trace of cultural patterns.

---

## What it does (Phase 1)

- Parses Spotify GDPR export data
- Normalizes listening events
- Stores data in a structured database
- Enables time-based queries

Examples:
- listening activity per month/year
- top artists and tracks over time
- recurring songs and patterns
- temporal “bursts” and gaps in listening

---

## Roadmap

**Phase 1**
- Data ingestion (Spotify export)
- PostgreSQL data model
- Basic queries and reporting

**Phase 2**
- API layer
- Web UI (timeline-based exploration)
- Personal tagging and annotations

**Phase 3**
- Live Spotify API integration
- Public profile / publishing

**Phase 4 (experimental)**
- Comparison with external datasets (charts, regions, radio)
- Exploratory analysis of patterns and “signals”

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

## Tech (initial)

- PostgreSQL
- Node.js or Go (TBD)
- JSON ingestion pipeline
- REST API (planned)

---

## Status

Early-stage build.  
Starting with raw data ingestion and system foundation.

---

## Name

Signal//Noise refers to the distinction between:
- raw data (noise)
- meaningful patterns (signal)

The system explores whether — and how — that distinction can be made in music listening behavior.
