# PKS Bridge — Spotify → PKS

The `pks_bridge.py` script populates the PKS DuckDB Spotify tables
(`spotify_plays_agg`, `spotify_top_artists`, `spotify_top_tracks`,
`spotify_listening_stats`) from the consolidated `spotify.db` produced by
`src/ingest_spotify.py`.

This makes Spotify listening history a first-class peer of Facebook posts,
emails, and contact data inside the Personal Knowledge System — searchable,
joinable, and topic-modelable alongside other personal archives.

## Schema mapping

| signal-noise-system (`spotify.db`) | PKS DuckDB table           | Aggregation level              |
|------------------------------------|----------------------------|--------------------------------|
| `events` (audio, ms_played ≥ 30s)  | `spotify_plays_agg`        | per-day × track × platform     |
| `events` (audio, ms_played ≥ 30s)  | `spotify_top_artists`      | per-year top-50 artists        |
| `events` (audio, ms_played ≥ 30s)  | `spotify_top_tracks`       | per-year top-50 tracks         |
| `events` (audio, ms_played ≥ 30s)  | `spotify_listening_stats`  | per-year × month + top plays   |

## Run

```bash
PYTHONPATH=/root/pks /usr/bin/python3 /root/repos/signal-noise-system/src/pks_bridge.py
```

Idempotent: wipes target tables on each run before re-inserting.

## Last run (2026-06-08)

| Table                   | Rows inserted |
|-------------------------|---------------|
| `spotify_plays_agg`     | 158,116       |
| `spotify_top_artists`   | 607           |
| `spotify_top_tracks`    | 650           |
| `spotify_listening_stats` | 125         |

## Privacy

No raw `ts` timestamps or `ms_played` values are stored in PKS — only the
aggregations defined by `pks.db.schema`. The granular `spotify_plays_agg`
table keeps day-of-month and hour-of-day but loses the sub-minute resolution.
`spotify_track_uri` is preserved as the canonical Spotify identifier.
