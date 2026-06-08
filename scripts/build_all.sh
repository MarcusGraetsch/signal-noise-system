#!/usr/bin/env bash
# build_all.sh — One-shot reproduction of all derived artifacts.
# Run from repo root: ./scripts/build_all.sh
#
# Reads from:
#   - /root/.openclaw/Schleuse/spotify/my_spotify_data.zip     (Spotify GDPR "Account Data" export)
#   - /root/.openclaw/Schleuse/spotify/my_spotify_data2.zip    (Spotify GDPR "Extended Streaming History" export)
#   - ~/.hermes/data/marcus_email_corpus.db                    (Gmail corpus, 62k+ sent)
#
# Writes to:
#   - data/processed/spotify.db         (events + aggregates)
#   - data/processed/music_profile.json
#   - data/processed/hidden_gems.json
#   - data/processed/monthly_correlation.csv
#   - data/processed/correlation_chart.txt
#   - data/processed/life_phases_overlay.csv
#   - reports/correlation_report.md
#   - reports/music_profile.md
#   - reports/hidden_gems.md
#   - reports/playlists.md
#   - playlists/*.csv                   (Spotify-importable)
#   - playlists/by_year/year_*.csv

set -euo pipefail
cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-/usr/bin/python3}"

echo "==> Ingesting Spotify exports"
$PYTHON src/ingest_spotify.py

echo "==> Building music profile"
$PYTHON src/build_music_profile.py

echo "==> Correlating listening with email volume"
$PYTHON src/correlate.py

echo "==> Finding hidden gems, recurring patterns, diversity"
$PYTHON src/hidden_gems.py

echo "==> Generating playlists"
$PYTHON src/playlists.py

echo "==> Bridging into PKS (Personal Knowledge System)"
PYTHONPATH=/root/pks $PYTHON src/pks_bridge.py

echo "==> Computing track embeddings (one-time, ~3 min)"
$PYTHON src/compute_track_embeddings.py

echo "==> Topic modeling (BERTopic)"
$PYTHON src/topic_model.py

echo "==> Labeling topics with Marcus-style heuristics"
$PYTHON src/label_topics.py

echo
echo "Done. See reports/ and playlists/ for outputs."
