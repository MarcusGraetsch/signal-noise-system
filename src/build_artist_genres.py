"""
build_artist_genres.py — Look up artist genres from MusicBrainz.

For each top artist (by lifetime listening hours), query MusicBrainz:
  1. Search by name (fuzzy), get artist MBID
  2. Fetch full artist record with `inc=tags`
  3. Extract user-contributed tags + their vote counts

Caches results in data/processed/artist_genres.json so we don't re-query.
Respects MusicBrainz rate limit (1 request per second per their guidelines).

Output:
  data/processed/artist_genres.json: {
    "NEU!": {"mbid": "ade...", "tags": [["krautrock", 6], ["experimental", 3], ...], "country": "DE"}
  }
  reports/artist_genres.md: human-readable table
"""

import json
import time
import sqlite3
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

USER_AGENT = "MarcusM3 (marcusgraetsch@gmail.com)"
MB_BASE = "https://musicbrainz.org/ws/2"
HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/json"}
CACHE = Path("/root/repos/signal-noise-system/data/processed/artist_genres.json")
DB = Path("/root/repos/signal-noise-system/data/processed/spotify.db")
OUT_MD = Path("/root/repos/signal-noise-system/reports/artist_genres.md")


def _get(url: str, retries: int = 3) -> dict:
    """GET with 1s politeness delay and basic retry."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req) as r:
                return json.loads(r.read())
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                raise


def search_artist(name: str) -> str | None:
    """Fuzzy search MusicBrainz, return best MBID or None."""
    q = urllib.parse.quote(name)
    url = f"{MB_BASE}/artist/?query={q}&fmt=json&limit=5"
    data = _get(url)
    artists = data.get("artists", [])
    if not artists:
        return None
    # Pick the highest-scored artist whose name matches (case-insensitive substring)
    name_l = name.lower().replace("!", "").replace("'", "").replace("'", "").replace(".", "").strip()
    for a in artists:
        aname = a.get("name", "").lower().replace("!", "").replace("'", "").replace("'", "").replace(".", "").strip()
        if aname == name_l:
            return a["id"]
    # Fallback: highest-scored result
    return artists[0]["id"] if artists else None


def get_tags_with_country(mbid: str) -> tuple[list[tuple[str, int]], str | None]:
    """Fetch user-contributed tags AND country in a single request."""
    url = f"{MB_BASE}/artist/{mbid}?inc=tags&fmt=json"
    data = _get(url)
    tags = data.get("tags", [])
    out = []
    for t in tags:
        # count is optional; treat 0 as 1
        c = max(1, int(t.get("count", 1)))
        out.append((t["name"].lower(), c))
    out.sort(key=lambda x: -x[1])
    return out, data.get("country")


def main():
    con = sqlite3.connect(DB)
    # Top 600 artists by lifetime hours (>=30s plays, audio only)
    # ~ 95% of total hours captured, manageable lookup size
    rows = con.execute("""
        SELECT artist_name,
               SUM(ms_played)/3600000.0 AS hours,
               COUNT(DISTINCT track_name) AS n_tracks
        FROM events
        WHERE kind='audio' AND ms_played >= 30000
              AND artist_name IS NOT NULL AND artist_name != ''
        GROUP BY artist_name
        HAVING hours > 0.5
        ORDER BY hours DESC
        LIMIT 600
    """).fetchall()
    print(f"Top {len(rows)} artists to look up")

    cache = {}
    if CACHE.exists():
        cache = json.loads(CACHE.read_text())
    print(f"  ({len(cache)} already cached)")

    new_count = 0
    fails = []
    for i, (artist, hours, n_tracks) in enumerate(rows):
        if artist in cache and "tags" in cache[artist]:
            continue
        # Search for MBID
        try:
            mbid = search_artist(artist)
            if not mbid:
                cache[artist] = {"mbid": None, "tags": [], "country": None, "hours": hours, "n_tracks": n_tracks, "error": "no match"}
                fails.append((artist, "no match"))
            else:
                tags, country = get_tags_with_country(mbid)
                cache[artist] = {
                    "mbid": mbid, "tags": tags, "country": country,
                    "hours": hours, "n_tracks": n_tracks,
                }
                new_count += 1
        except Exception as e:
            cache[artist] = {"mbid": None, "tags": [], "country": None, "hours": hours, "n_tracks": n_tracks, "error": str(e)}
            fails.append((artist, str(e)))
        # MusicBrainz rate limit: 1 req/sec for service, ideally 1.5s.
        # We make 2 requests per artist (search + tags), so 2.2s between artists.
        time.sleep(2.2)
        # Persist after each artist (crash-safe)
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2))
        if (i + 1) % 50 == 0:
            print(f"  ... {i+1}/{len(rows)} ({new_count} new, {len(fails)} failed)")

    # Final report
    n_with_tags = sum(1 for v in cache.values() if v.get("tags"))
    print(f"\nDone. {n_with_tags}/{len(rows)} artists have tags. {len(fails)} failures.")

    # Write human-readable report: top 100 artists with their tags
    sorted_artists = sorted(cache.items(),
                            key=lambda x: -x[1].get("hours", 0))
    lines = ["# Top Artists — MusicBrainz Tags\n"]
    lines.append("Top 100 artists by lifetime listening hours, with their MusicBrainz tags.\n")
    lines.append("| # | Artist | Hours | Tracks | Country | Top tags (count ≥ 1) |")
    lines.append("|---|---|---:|---:|---|---|")
    for i, (artist, info) in enumerate(sorted_artists[:100], 1):
        if i > 100:
            break
        tags = info.get("tags", [])
        tag_str = ", ".join(f"{t}({c})" for t, c in tags[:8]) if tags else "(no tags)"
        country = info.get("country") or "—"
        hours = info.get("hours", 0)
        n_tracks = info.get("n_tracks", 0)
        lines.append(f"| {i} | {artist} | {hours:.1f} | {n_tracks} | {country} | {tag_str} |")

    if fails:
        lines.append("\n## Lookups without MBID match\n")
        for a, e in fails[:50]:
            lines.append(f"- {a}: {e}")
    OUT_MD.write_text("\n".join(lines))
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
