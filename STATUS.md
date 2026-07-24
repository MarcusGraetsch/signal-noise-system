# Status: PARKED 🚧

**Parked:** 2026-07-24 by Marcus
**Letzter aktiver Commit:** 2799533 (vor 7 Wochen) — Phase 2 BERTopic

## Warum geparkt?

Marcus macht hier erstmal Pause. Die nächsten Schritte (Phase 3 BERTopic-Auswertung,
Playlisten-Generierung, v3 Topic Labels) sind mit dem aktuellen OpenClaw/MiniMax-Setup
nicht gut machbar — kostet zu viele Tokens für die manuelle Kleinarbeit.

## Geplante Wiederaufnahme

Geplant mit: **Claude Code + Fable** (Marcus' IDE-Setup)
Bedingung: **20€-Plan von Claude** reicht für die Arbeit
Status: offen — kann jederzeit reaktiviert werden

## Was im Repo ist (nicht verlieren)

- Phase 1: Music Profile, Hidden Gems, 21 Playlists — committed
- Phase 2: BERTopic Topic Modeling — committed
- PKS-Bridge: Spotify-Events in DuckDB — committed
- WIP (untracked, in working tree):
  - `data/processed/artist_genres.json` / `artist_genre_overrides.json`
  - `data/processed/marcus_spotify_topic_labels_v02.json/.md`
  - `src/build_artist_genres.py` / `src/label_topics_v2.py`
  - `IDEAS.md`

## Re-Aktivierung

```
cd /root/repos/signal-noise-system
git pull
# Mit Claude Code + Fable die v2-Skripte laufen lassen
python src/build_artist_genres.py
python src/label_topics_v2.py
```

