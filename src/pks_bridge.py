"""
pks_bridge.py — Bridge signal-noise-system → PKS (Personal Knowledge System).

Reads from data/processed/spotify.db (long-format events) and writes aggregated
rows into the PKS DuckDB tables (spotify_plays_agg, spotify_top_artists,
spotify_top_tracks, spotify_listening_stats) defined in pks.db.schema.

Strategy: load events from SQLite into pandas, then INSERT pre-aggregated
DataFrames into DuckDB. Avoids DuckDB's slow sqlite-attachment scanner.

Usage:
  PYTHONPATH=/root/pks /usr/bin/python3 /root/repos/signal-noise-system/src/pks_bridge.py
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

PKS_ROOT = Path("/root/pks")
if str(PKS_ROOT) not in sys.path:
    sys.path.insert(0, str(PKS_ROOT))

ROOT = Path("/root/repos/signal-noise-system")
SRC_DB = ROOT / "data" / "processed" / "spotify.db"
PKS_DUCKDB = Path("/root/.pks/data/pks_analytics.duckdb")


def main() -> int:
    import sqlite3
    import duckdb
    import pandas as pd

    if not SRC_DB.exists():
        print(f"ERROR: source DB not found: {SRC_DB}")
        return 1

    print(f"Reading events from: {SRC_DB}")
    src = sqlite3.connect(str(SRC_DB))
    # Only the columns we need
    df = pd.read_sql("""
        SELECT ts, ms_played, track_name, artist_name, album_name,
               spotify_track_uri, platform, skipped, offline, incognito_mode
        FROM events
        WHERE kind='audio' AND ms_played >= 30000
          AND track_name IS NOT NULL AND artist_name IS NOT NULL
    """, src)
    src.close()
    print(f"  loaded {len(df):,} real-play rows")

    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    df["year"] = df["ts"].dt.year
    df["month"] = df["ts"].dt.month
    df["day"] = df["ts"].dt.day
    df["hour"] = df["ts"].dt.hour
    df["weekday"] = (df["ts"].dt.weekday).astype(int)  # 0=Monday
    df["play_date"] = df["ts"].dt.date
    df["skipped"] = df["skipped"].fillna(False).astype(bool)
    df["offline"] = df["offline"].fillna(False).astype(bool)
    df["incognito_mode"] = df["incognito_mode"].fillna(False).astype(bool)

    print(f"Connecting to PKS DuckDB at: {PKS_DUCKDB}")
    pks = duckdb.connect(str(PKS_DUCKDB))
    # Ensure schema exists (idempotent via IF NOT EXISTS in DDL)
    schema_sql = open("/root/pks/pks/db/schema.py").read()
    schema = schema_sql.split('DUCKDB_SCHEMA = """')[1].split('"""')[0]
    pks.execute(schema)

    # Wipe existing
    print("Wiping existing Spotify tables in PKS...")
    for t in ["spotify_plays_agg", "spotify_top_artists", "spotify_top_tracks", "spotify_listening_stats"]:
        pks.execute(f"DELETE FROM {t}")

    # 1. spotify_plays_agg (per-track-per-day, including platform)
    print("Building spotify_plays_agg ...")
    agg = (df.groupby(["play_date", "year", "month", "day", "hour", "weekday",
                       "track_name", "artist_name", "album_name", "spotify_track_uri", "platform"])
             .agg(play_count=("ms_played", "size"),
                  total_ms=("ms_played", "sum"),
                  skipped_count=("skipped", "sum"),
                  avg_skip_ratio=("skipped", "mean"),
                  is_offline=("offline", "any"),
                  is_incognito=("incognito_mode", "any"))
             .reset_index())
    agg["avg_skip_ratio"] = agg["avg_skip_ratio"].fillna(0.0)
    agg["source"] = "history_export"
    agg = agg.rename(columns={"spotify_track_uri": "spotify_uri"})
    pks.register("df_plays_agg", agg)
    pks.execute("""
        INSERT INTO spotify_plays_agg
        (year, month, day, hour, weekday, artist_name, track_name, album_name,
         spotify_uri, play_count, total_ms, skipped_count, avg_skip_ratio,
         platform, source, is_offline, is_incognito)
        SELECT year, month, day, hour, weekday, artist_name, track_name, album_name,
               spotify_uri, play_count, total_ms, skipped_count, avg_skip_ratio,
               platform, source, is_offline, is_incognito
        FROM df_plays_agg
    """)
    pks.unregister("df_plays_agg")
    n = pks.execute("SELECT COUNT(*) FROM spotify_plays_agg").fetchone()[0]
    print(f"  spotify_plays_agg: {n:,} rows")

    # 2. spotify_top_artists (top 50 per year)
    print("Building spotify_top_artists ...")
    a_agg = (df.groupby(["year", "artist_name"])
              .agg(play_count=("ms_played", "size"), total_ms=("ms_played", "sum"))
              .reset_index())
    a_agg["rank"] = a_agg.groupby("year")["total_ms"].rank(method="first", ascending=False).astype(int)
    a_agg = a_agg[a_agg["rank"] <= 50].copy()
    a_agg["total_hours"] = a_agg["total_ms"] / 3_600_000.0
    pks.register("df_top_artists", a_agg[["year", "rank", "artist_name", "play_count", "total_hours"]])
    pks.execute("""
        INSERT INTO spotify_top_artists (year, rank, artist_name, play_count, total_hours)
        SELECT year, rank, artist_name, play_count, total_hours FROM df_top_artists
    """)
    pks.unregister("df_top_artists")
    n = pks.execute("SELECT COUNT(*) FROM spotify_top_artists").fetchone()[0]
    print(f"  spotify_top_artists: {n:,} rows")

    # 3. spotify_top_tracks (top 50 per year)
    print("Building spotify_top_tracks ...")
    t_agg = (df.groupby(["year", "track_name", "artist_name"])
              .agg(play_count=("ms_played", "size"), total_ms=("ms_played", "sum"))
              .reset_index())
    t_agg["rank"] = t_agg.groupby("year")["total_ms"].rank(method="first", ascending=False).astype(int)
    t_agg = t_agg[t_agg["rank"] <= 50].copy()
    t_agg["total_hours"] = t_agg["total_ms"] / 3_600_000.0
    pks.register("df_top_tracks", t_agg[["year", "rank", "track_name", "artist_name", "play_count", "total_hours"]])
    pks.execute("""
        INSERT INTO spotify_top_tracks (year, rank, track_name, artist_name, play_count, total_hours)
        SELECT year, rank, track_name, artist_name, play_count, total_hours FROM df_top_tracks
    """)
    pks.unregister("df_top_tracks")
    n = pks.execute("SELECT COUNT(*) FROM spotify_top_tracks").fetchone()[0]
    print(f"  spotify_top_tracks: {n:,} rows")

    # 4. spotify_listening_stats (year-month aggregates + top artist/track per month)
    print("Building spotify_listening_stats ...")
    m_agg = (df.groupby(["year", "month"])
              .agg(total_plays=("ms_played", "size"),
                   total_hours=("ms_played", lambda s: s.sum()/3_600_000.0))
              .reset_index())
    m_agg["avg_plays_per_day"] = m_agg["total_plays"] / 30.0
    # Top artist/track per month
    mt = (df.groupby(["year", "month", "artist_name", "track_name"])
            .agg(total_ms=("ms_played", "sum"))
            .reset_index())
    mt["rn"] = mt.groupby(["year", "month"])["total_ms"].rank(method="first", ascending=False).astype(int)
    top = mt[mt["rn"] == 1][["year", "month", "artist_name", "track_name"]].rename(
        columns={"artist_name": "top_artist", "track_name": "top_track"})
    stats = m_agg.merge(top, on=["year", "month"], how="left")
    stats["top_album"] = None
    pks.register("df_listening_stats", stats)
    pks.execute("""
        INSERT INTO spotify_listening_stats
        (year, month, total_plays, total_hours, avg_plays_per_day, top_artist, top_track, top_album)
        SELECT year, month, total_plays, total_hours, avg_plays_per_day, top_artist, top_track, top_album
        FROM df_listening_stats
    """)
    pks.unregister("df_listening_stats")
    n = pks.execute("SELECT COUNT(*) FROM spotify_listening_stats").fetchone()[0]
    print(f"  spotify_listening_stats: {n:,} rows")

    print("\n=== Final PKS Spotify row counts ===")
    for t in ["spotify_plays_agg", "spotify_top_artists", "spotify_top_tracks", "spotify_listening_stats"]:
        n = pks.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {n:,}")

    pks.close()
    print(f"\nDone at {datetime.utcnow().isoformat(timespec='seconds')}Z")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
