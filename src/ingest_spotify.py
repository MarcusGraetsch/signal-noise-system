"""
ingest_spotify.py — Ingest Marcus's two Spotify GDPR export ZIPs into a single SQLite DB.

Inputs (from local data exchange / VM Schleuse):
  - my_spotify_data.zip     (Account Data: playlists, library, search, identity, wrapped, sound capsule, inferences, marquee, payments, follow, podcast/audiobook stream history)
  - my_spotify_data2.zip    (Extended Streaming History: per-year audio + video JSON, 2013-2026)

Output:
  - data/processed/spotify.db (SQLite, long-format events table + summary tables)

Schema (all times stored as ISO-8601 UTC strings; ms_played for durations):
  events(id, ts, ts_year, ts_month, platform, conn_country, ms_played,
         reason_start, reason_end, shuffle, skipped, offline, episode_show_name,
         spotify_track_uri, spotify_episode_uri, audiobook_uri,
         track_name, artist_name, album_name, source)  -- one row per play

  artists(artist_name, total_ms, total_plays, first_seen, last_seen)
  tracks(uri, track_name, artist_name, album_name, total_ms, total_plays, first_seen, last_seen)
  monthly(year, month, hours, plays, unique_artists, unique_tracks)
  yearly(year, hours, plays, unique_artists, unique_tracks)
  playlists(...) -- from Playlist1.json
  library_items(...) -- from YourLibrary.json
  search_queries(...) -- from SearchQueries.json
  follow(...) -- from Follow.json
  inferences(...) -- from Inferences.json
  wrapped_2025(...) -- key/value pairs from Wrapped2025.json
  sound_capsule_highlights(...) -- milestones
  podcasts(...) -- aggregated from podcast streaming history
  audiobooks(...) -- aggregated from audiobook streaming history

Idempotent: drops & recreates tables.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

SCHLEUSE = Path("/root/.openclaw/Schleuse/spotify")
RAW = Path("/root/repos/signal-noise-system/data/raw")
PROCESSED = Path("/root/repos/signal-noise-system/data/processed")
DB_PATH = PROCESSED / "spotify.db"

ZIP_ACCOUNT = SCHLEUSE / "my_spotify_data.zip"
ZIP_EXTENDED = SCHLEUSE / "my_spotify_data2.zip"

YEAR_RE = re.compile(r"Streaming_History_(Audio|Video)_(\d{4})(?:_\d+)?\.json$")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def open_db() -> sqlite3.Connection:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA foreign_keys=ON")
    return con


def create_schema(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS events;
        DROP TABLE IF EXISTS artists;
        DROP TABLE IF EXISTS tracks;
        DROP TABLE IF EXISTS monthly;
        DROP TABLE IF EXISTS yearly;
        DROP TABLE IF EXISTS playlists;
        DROP TABLE IF EXISTS library_items;
        DROP TABLE IF EXISTS search_queries;
        DROP TABLE IF EXISTS follow;
        DROP TABLE IF EXISTS inferences;
        DROP TABLE IF EXISTS wrapped_2025;
        DROP TABLE IF EXISTS sound_capsule_highlights;
        DROP TABLE IF EXISTS podcasts;
        DROP TABLE IF EXISTS audiobooks;
        DROP TABLE IF EXISTS identity;
        DROP TABLE IF EXISTS user_attributes;
        DROP TABLE IF EXISTS payments;

        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,                    -- ISO-8601 UTC
            ts_year INTEGER,
            ts_month TEXT,                       -- YYYY-MM
            platform TEXT,
            conn_country TEXT,
            ms_played INTEGER NOT NULL DEFAULT 0,
            reason_start TEXT,
            reason_end TEXT,
            shuffle INTEGER,
            skipped INTEGER,
            offline INTEGER,
            incognito_mode INTEGER,
            episode_show_name TEXT,
            spotify_track_uri TEXT,
            spotify_episode_uri TEXT,
            audiobook_uri TEXT,
            audiobook_chapter_uri TEXT,
            audiobook_chapter_title TEXT,
            track_name TEXT,
            artist_name TEXT,
            album_name TEXT,
            source TEXT NOT NULL,                -- 'extended_audio' | 'extended_video' | 'account_audiobook' | 'account_podcast'
            kind TEXT NOT NULL                   -- 'audio' | 'video' | 'audiobook' | 'podcast'
        );
        CREATE INDEX idx_events_ts ON events(ts);
        CREATE INDEX idx_events_year ON events(ts_year);
        CREATE INDEX idx_events_month ON events(ts_month);
        CREATE INDEX idx_events_artist ON events(artist_name);
        CREATE INDEX idx_events_track ON events(track_name, artist_name);
        CREATE INDEX idx_events_source ON events(source);

        CREATE TABLE artists (
            artist_name TEXT PRIMARY KEY,
            total_ms INTEGER NOT NULL DEFAULT 0,
            total_plays INTEGER NOT NULL DEFAULT 0,
            first_seen TEXT,
            last_seen TEXT
        );
        CREATE TABLE tracks (
            track_key TEXT PRIMARY KEY,           -- track_name || '||' || artist_name
            track_name TEXT NOT NULL,
            artist_name TEXT,
            album_name TEXT,
            total_ms INTEGER NOT NULL DEFAULT 0,
            total_plays INTEGER NOT NULL DEFAULT 0,
            first_seen TEXT,
            last_seen TEXT
        );
        CREATE INDEX idx_tracks_artist ON tracks(artist_name);

        CREATE TABLE monthly (
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            ym TEXT NOT NULL,
            hours REAL NOT NULL,
            plays INTEGER NOT NULL,
            unique_artists INTEGER,
            unique_tracks INTEGER,
            PRIMARY KEY (year, month)
        );
        CREATE TABLE yearly (
            year INTEGER PRIMARY KEY,
            hours REAL NOT NULL,
            plays INTEGER NOT NULL,
            unique_artists INTEGER,
            unique_tracks INTEGER
        );

        CREATE TABLE playlists (
            owner_id TEXT,
            playlist_name TEXT,
            playlist_uri TEXT,
            num_tracks INTEGER,
            num_followers INTEGER,
            last_modified TEXT,
            collaborative INTEGER,
            description TEXT,
            is_public INTEGER,
            raw_json TEXT
        );
        CREATE INDEX idx_playlists_name ON playlists(playlist_name);

        CREATE TABLE library_items (
            category TEXT NOT NULL,    -- 'tracks' | 'albums' | 'artists' | 'podcasts' | 'shows' | 'episodes' | 'audiobooks'
            uri TEXT,
            name TEXT,
            description TEXT,
            added_at TEXT,
            artists TEXT,              -- JSON array string
            album TEXT,
            raw_json TEXT
        );
        CREATE INDEX idx_library_cat ON library_items(category);

        CREATE TABLE search_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_time TEXT,
            platform TEXT,
            search_query TEXT,
            interaction_uris TEXT      -- JSON array string
        );
        CREATE INDEX idx_search_time ON search_queries(search_time);
        CREATE INDEX idx_search_query ON search_queries(search_query);

        CREATE TABLE follow (
            direction TEXT NOT NULL,   -- 'following' | 'followed_by' | 'blocking'
            username TEXT NOT NULL
        );
        CREATE INDEX idx_follow_dir ON follow(direction);

        CREATE TABLE inferences (
            inference_id TEXT PRIMARY KEY,
            raw_json TEXT
        );

        CREATE TABLE wrapped_2025 (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE sound_capsule_highlights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            highlight_type TEXT,
            raw_json TEXT
        );

        CREATE TABLE podcasts (
            podcast_name TEXT,
            episode_name TEXT,
            plays INTEGER,
            total_ms INTEGER,
            first_seen TEXT,
            last_seen TEXT,
            PRIMARY KEY (podcast_name, episode_name)
        );

        CREATE TABLE audiobooks (
            audiobook_name TEXT,
            author_name TEXT,
            chapter_name TEXT,
            plays INTEGER,
            total_ms INTEGER,
            PRIMARY KEY (audiobook_name, author_name, chapter_name)
        );

        CREATE TABLE identity (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE user_attributes (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE payments (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """
    )
    con.commit()


def _read_zipped_json(zf: zipfile.ZipFile, member: str) -> object:
    with zf.open(member) as fh:
        return json.load(fh)


def _ingest_extended_streaming(con: sqlite3.Connection, zip_path: Path) -> dict:
    """Long-format events from Streaming_History_Audio_*.json + Video_*.json"""
    cur = con.cursor()
    counts = {"audio_rows": 0, "video_rows": 0, "skipped_missing_ts": 0}
    artist_ms: dict[str, int] = defaultdict(int)
    artist_plays: dict[str, int] = defaultdict(int)
    artist_first: dict[str, str] = {}
    artist_last: dict[str, str] = {}
    track_ms: dict[tuple[str, str], int] = defaultdict(int)
    track_plays: dict[tuple[str, str], int] = defaultdict(int)
    track_album: dict[tuple[str, str], str] = {}
    track_first: dict[tuple[str, str], str] = {}
    track_last: dict[tuple[str, str], str] = {}

    with zipfile.ZipFile(zip_path) as zf:
        members = [n for n in zf.namelist() if YEAR_RE.search(Path(n).name)]
        for member in members:
            m = YEAR_RE.search(Path(member).name)
            kind = "audio" if m.group(1) == "Audio" else "video"
            data = _read_zipped_json(zf, member)
            for r in data:
                ts = r.get("ts")
                if not ts:
                    counts["skipped_missing_ts"] += 1
                    continue
                # ts format: 2013-10-05T21:20:15Z
                ts_year = int(ts[:4])
                ts_month = ts[:7]
                track = r.get("master_metadata_track_name")
                artist = r.get("master_metadata_album_artist_name")
                album = r.get("master_metadata_album_album_name")
                ms = int(r.get("ms_played") or 0)
                cur.execute(
                    """
                    INSERT INTO events
                    (ts, ts_year, ts_month, platform, conn_country, ms_played,
                     reason_start, reason_end, shuffle, skipped, offline, incognito_mode,
                     episode_show_name, spotify_track_uri, spotify_episode_uri,
                     audiobook_uri, audiobook_chapter_uri, audiobook_chapter_title,
                     track_name, artist_name, album_name, source, kind)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        ts, ts_year, ts_month,
                        r.get("platform"), r.get("conn_country"), ms,
                        r.get("reason_start"), r.get("reason_end"),
                        int(bool(r.get("shuffle"))), int(bool(r.get("skipped"))),
                        int(bool(r.get("offline"))), int(bool(r.get("incognito_mode"))),
                        r.get("episode_show_name"),
                        r.get("spotify_track_uri"), r.get("spotify_episode_uri"),
                        r.get("audiobook_uri"), r.get("audiobook_chapter_uri"),
                        r.get("audiobook_chapter_title"),
                        track, artist, album,
                        f"extended_{kind}", kind,
                    ),
                )
                if kind == "audio":
                    counts["audio_rows"] += 1
                    if artist:
                        artist_ms[artist] += ms
                        artist_plays[artist] += 1
                        if artist not in artist_first or ts < artist_first[artist]:
                            artist_first[artist] = ts
                        if artist not in artist_last or ts > artist_last[artist]:
                            artist_last[artist] = ts
                    if track and artist:
                        key = (track, artist)
                        track_ms[key] += ms
                        track_plays[key] += 1
                        if key not in track_album and album:
                            track_album[key] = album
                        if key not in track_first or ts < track_first[key]:
                            track_first[key] = ts
                        if key not in track_last or ts > track_last[key]:
                            track_last[key] = ts
                else:
                    counts["video_rows"] += 1
    con.commit()

    # Build aggregates
    cur.executemany(
        "INSERT INTO artists (artist_name, total_ms, total_plays, first_seen, last_seen) VALUES (?,?,?,?,?)",
        [(a, artist_ms[a], artist_plays[a], artist_first.get(a), artist_last.get(a))
         for a in artist_ms],
    )
    cur.executemany(
        "INSERT INTO tracks (track_key, track_name, artist_name, album_name, total_ms, total_plays, first_seen, last_seen) VALUES (?,?,?,?,?,?,?,?)",
        [(f"{t}||{a}", t, a, track_album.get((t, a)), track_ms[(t, a)], track_plays[(t, a)],
          track_first.get((t, a)), track_last.get((t, a)))
         for (t, a) in track_ms],
    )
    # Monthly + yearly aggregates (audio only, ms_played >= 30000 = "real plays")
    cur.execute(
        """
        INSERT INTO monthly (year, month, ym, hours, plays, unique_artists, unique_tracks)
        SELECT
            ts_year AS year,
            CAST(substr(ts_month,6,2) AS INTEGER) AS month,
            ts_month AS ym,
            ROUND(SUM(ms_played)/3600000.0, 2) AS hours,
            COUNT(*) AS plays,
            COUNT(DISTINCT artist_name) AS unique_artists,
            COUNT(DISTINCT track_name || '||' || COALESCE(artist_name,'')) AS unique_tracks
        FROM events
        WHERE kind='audio' AND ms_played >= 30000
        GROUP BY ts_year, ts_month
        ORDER BY ts_year, ts_month
        """
    )
    cur.execute(
        """
        INSERT INTO yearly (year, hours, plays, unique_artists, unique_tracks)
        SELECT
            ts_year AS year,
            ROUND(SUM(ms_played)/3600000.0, 2) AS hours,
            COUNT(*) AS plays,
            COUNT(DISTINCT artist_name) AS unique_artists,
            COUNT(DISTINCT track_name || '||' || COALESCE(artist_name,'')) AS unique_tracks
        FROM events
        WHERE kind='audio' AND ms_played >= 30000
        GROUP BY ts_year
        ORDER BY ts_year
        """
    )
    con.commit()
    return counts


def _ingest_account_data(con: sqlite3.Connection, zip_path: Path) -> dict:
    cur = con.cursor()
    counts = {}

    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()

        def get(name: str) -> object:
            matches = [n for n in names if n.endswith(name)]
            if not matches:
                return None
            return _read_zipped_json(zf, matches[0])

        # Identity
        identity = get("Identity.json") or {}
        for k, v in identity.items():
            cur.execute("INSERT INTO identity (key, value) VALUES (?,?)", (k, json.dumps(v)))
        counts["identity_keys"] = len(identity)

        # UserAttributes
        attrs = get("UserAttributes.json") or {}
        for k, v in attrs.items():
            cur.execute("INSERT INTO user_attributes (key, value) VALUES (?,?)", (k, json.dumps(v)))
        counts["user_attributes_keys"] = len(attrs)

        # Payments
        pay = get("Payments.json") or {}
        if isinstance(pay, dict):
            for k, v in pay.items():
                cur.execute("INSERT INTO payments (key, value) VALUES (?,?)", (k, json.dumps(v)))
        counts["payments_keys"] = len(pay) if isinstance(pay, dict) else 0

        # Inferences
        inf = get("Inferences.json") or {}
        for x in inf.get("inferences", []):
            cur.execute("INSERT OR IGNORE INTO inferences (inference_id, raw_json) VALUES (?,?)",
                        (x, json.dumps({"inference_id": x})))
        counts["inferences"] = len(inf.get("inferences", []))

        # Playlists — Playlist1.json is a dict {playlists: [...]}
        pl = get("Playlist1.json")
        playlist_n = 0
        if isinstance(pl, dict) and isinstance(pl.get("playlists"), list):
            for p in pl["playlists"]:
                items = p.get("items", [])
                num_tracks = len(items) if isinstance(items, list) else 0
                cur.execute(
                    "INSERT INTO playlists (owner_id, playlist_name, playlist_uri, num_tracks, num_followers, last_modified, collaborative, description, is_public, raw_json) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (
                        (p.get("owner") if isinstance(p.get("owner"), str) else None),
                        p.get("name"), p.get("uri"),
                        num_tracks,
                        p.get("numberOfFollowers") or p.get("numFollowers"),
                        p.get("lastModifiedDate"),
                        int(bool(p.get("collaborative"))), p.get("description"),
                        None,
                        json.dumps(p, ensure_ascii=False),
                    ),
                )
                playlist_n += 1
        elif isinstance(pl, list):
            # Older format
            for p in pl:
                owner = p.get("owner", {}).get("id") if isinstance(p.get("owner"), dict) else p.get("owner")
                cur.execute(
                    "INSERT INTO playlists (owner_id, playlist_name, playlist_uri, num_tracks, num_followers, last_modified, collaborative, description, is_public, raw_json) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (
                        owner, p.get("name"), p.get("uri"),
                        len(p.get("tracks", [])) if isinstance(p.get("tracks"), list) else p.get("numberOfTracks") or p.get("num_tracks"),
                        p.get("followers", {}).get("total") if isinstance(p.get("followers"), dict) else p.get("num_followers"),
                        p.get("lastModifiedDate") or p.get("last_modified_date"),
                        int(bool(p.get("collaborative"))), p.get("description"),
                        int(bool(p.get("public"))),
                        json.dumps(p, ensure_ascii=False),
                    ),
                )
                playlist_n += 1
        counts["playlists"] = playlist_n

        # YourLibrary.json — newer format is a dict with category keys
        lib = get("YourLibrary.json")
        lib_n = 0
        # Map: category -> list of items
        library_categories: list[tuple[str, list]]
        if isinstance(lib, dict):
            library_categories = [
                ("tracks", lib.get("tracks", []) or []),
                ("albums", lib.get("albums", []) or []),
                ("artists", lib.get("artists", []) or []),
                ("shows", lib.get("shows", []) or []),
                ("episodes", lib.get("episodes", []) or []),
                ("podcasts", lib.get("podcasts", []) or []),
                ("audiobooks", lib.get("audiobooks", []) or []),
            ]
        elif isinstance(lib, list):
            library_categories = [("unknown", lib)]
        else:
            library_categories = []
        for category, items in library_categories:
            for item in items:
                if not isinstance(item, dict):
                    continue
                # New format: name/track/album/artist/uri
                # Old format: uri, name, artists, album, added_at
                name = item.get("name") or item.get("track")
                album = item.get("album")
                artist = item.get("artist")
                artists_list = item.get("artists")
                artists_str = json.dumps(artists_list, ensure_ascii=False) if artists_list is not None else artist
                cur.execute(
                    "INSERT INTO library_items (category, uri, name, description, added_at, artists, album, raw_json) VALUES (?,?,?,?,?,?,?,?)",
                    (
                        category, item.get("uri"), name, item.get("description"),
                        item.get("addedAt") or item.get("added_at") or item.get("addedDate"),
                        artists_str, album,
                        json.dumps(item, ensure_ascii=False),
                    ),
                )
                lib_n += 1
        counts["library_items"] = lib_n

        # SearchQueries
        sq = get("SearchQueries.json")
        sq_n = 0
        if isinstance(sq, list):
            for q in sq:
                cur.execute(
                    "INSERT INTO search_queries (search_time, platform, search_query, interaction_uris) VALUES (?,?,?,?)",
                    (
                        q.get("searchTime") or q.get("search_time"),
                        q.get("platform"),
                        q.get("searchQuery") or q.get("search_query"),
                        json.dumps(q.get("searchInteractionURIs") or q.get("interaction_uris") or []),
                    ),
                )
                sq_n += 1
        counts["search_queries"] = sq_n

        # Follow
        fo = get("Follow.json") or {}
        for direction, key in [("following", "userIsFollowing"), ("followed_by", "userIsFollowedBy"), ("blocking", "userIsBlocking")]:
            for name in fo.get(key, []):
                cur.execute("INSERT INTO follow (direction, username) VALUES (?,?)", (direction, str(name)))
        counts["following"] = len(fo.get("userIsFollowing", []))
        counts["followed_by"] = len(fo.get("userIsFollowedBy", []))

        # Wrapped 2025
        wr = get("Wrapped2025.json") or {}
        # Flatten one level where possible
        for k, v in wr.items():
            cur.execute("INSERT INTO wrapped_2025 (key, value) VALUES (?,?)", (k, json.dumps(v, ensure_ascii=False)))
        counts["wrapped_keys"] = len(wr)

        # Sound Capsule
        sc = get("YourSoundCapsule.json") or {}
        for h in sc.get("highlights", []) or []:
            cur.execute("INSERT INTO sound_capsule_highlights (date, highlight_type, raw_json) VALUES (?,?,?)",
                        (h.get("date"), h.get("highlightType"), json.dumps(h, ensure_ascii=False)))
        counts["capsule_highlights"] = len(sc.get("highlights", []) or [])

        # Podcast streaming history (account zip)
        pod = get("StreamingHistory_podcast_0.json") or []
        pod_agg: dict[tuple[str, str], list] = defaultdict(lambda: [0, 0, None, None])
        for r in pod:
            if not isinstance(r, dict): continue
            k = (r.get("podcastName",""), r.get("episodeName",""))
            et = r.get("endTime")
            pod_agg[k][0] += 1
            pod_agg[k][1] += int(r.get("msPlayed") or 0)
            if et:
                if pod_agg[k][2] is None or et < pod_agg[k][2]: pod_agg[k][2] = et
                if pod_agg[k][3] is None or et > pod_agg[k][3]: pod_agg[k][3] = et
        for (pn, en), (plays, ms, first, last) in pod_agg.items():
            cur.execute("INSERT INTO podcasts (podcast_name, episode_name, plays, total_ms, first_seen, last_seen) VALUES (?,?,?,?,?,?)",
                        (pn, en, plays, ms, first, last))
        counts["podcast_episodes"] = len(pod_agg)

        # Audiobook streaming history
        ab = get("StreamingHistory_audiobook_0.json") or []
        ab_agg: dict[tuple[str, str, str], list] = defaultdict(lambda: [0, 0])
        for r in ab:
            if not isinstance(r, dict): continue
            k = (r.get("audiobookName",""), r.get("authorName",""), r.get("chapterName",""))
            ab_agg[k][0] += 1
            ab_agg[k][1] += int(r.get("msPlayed") or 0)
        for (an, au, cn), (plays, ms) in ab_agg.items():
            cur.execute("INSERT INTO audiobooks (audiobook_name, author_name, chapter_name, plays, total_ms) VALUES (?,?,?,?,?)",
                        (an, au, cn, plays, ms))
        counts["audiobook_chapters"] = len(ab_agg)

    con.commit()
    return counts


def main() -> int:
    print(f"[{_now_iso()}] Starting ingest into {DB_PATH}")
    con = open_db()
    create_schema(con)
    print(f"[{_now_iso()}] Schema created.")
    print(f"[{_now_iso()}] Ingesting extended streaming history ({ZIP_EXTENDED.name})...")
    ext = _ingest_extended_streaming(con, ZIP_EXTENDED)
    print(f"  -> {ext}")
    print(f"[{_now_iso()}] Ingesting account data ({ZIP_ACCOUNT.name})...")
    acc = _ingest_account_data(con, ZIP_ACCOUNT)
    print(f"  -> {acc}")

    # Metadata
    cur = con.cursor()
    cur.execute("INSERT INTO metadata (key, value) VALUES (?,?)", ("ingest_time_utc", _now_iso()))
    cur.execute("INSERT INTO metadata (key, value) VALUES (?,?)", ("zip_account", ZIP_ACCOUNT.name))
    cur.execute("INSERT INTO metadata (key, value) VALUES (?,?)", ("zip_extended", ZIP_EXTENDED.name))
    cur.execute("INSERT INTO metadata (key, value) VALUES (?,?)", ("source_path", str(SCHLEUSE)))
    cur.execute("INSERT INTO metadata (key, value) VALUES (?,?)", ("ingest_script", "src/ingest_spotify.py"))
    con.commit()

    # Summary
    cur.execute("SELECT COUNT(*) FROM events")
    print(f"\n[{_now_iso()}] DONE.")
    print(f"  events:                 {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM artists"); print(f"  artists:                {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM tracks");  print(f"  tracks:                 {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM monthly"); print(f"  monthly rows:           {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM playlists"); print(f"  playlists:              {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM library_items"); print(f"  library items:          {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM search_queries"); print(f"  search queries:         {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM follow"); print(f"  follow rows:            {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM inferences"); print(f"  inferences:             {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM podcasts"); print(f"  podcast episodes:       {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM audiobooks"); print(f"  audiobook chapters:     {cur.fetchone()[0]:,}")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
