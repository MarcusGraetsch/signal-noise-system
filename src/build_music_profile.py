"""
build_music_profile.py — Build a structured, coach-readable music profile from
the SQLite data. Output: data/processed/music_profile.json + a short
narrative text suitable for embedding into coach_context.md.

Outputs:
  - data/processed/music_profile.json   (machine-readable)
  - reports/music_profile.md            (narrative + stats)
"""

from __future__ import annotations

import json
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "processed" / "spotify.db"
OUT_JSON = ROOT / "data" / "processed" / "music_profile.json"
OUT_REPORT = ROOT / "reports" / "music_profile.md"


def main() -> int:
    con = sqlite3.connect(str(DB))
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) AS n FROM artists WHERE total_ms > 0")
    unique_artists = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM tracks WHERE total_ms > 0")
    unique_tracks = cur.fetchone()["n"]
    cur.execute("""
        SELECT artist_name, total_ms, total_plays, first_seen, last_seen
        FROM artists
        WHERE total_ms > 0
        ORDER BY total_ms DESC
        LIMIT 50
    """)
    top_artists = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT track_name, artist_name, album_name, total_ms, total_plays, first_seen, last_seen
        FROM tracks
        WHERE total_ms > 0
        ORDER BY total_ms DESC
        LIMIT 50
    """)
    top_tracks = [dict(r) for r in cur.fetchall()]

    # Yearly
    cur.execute("SELECT year, hours, plays, unique_artists, unique_tracks FROM yearly ORDER BY year")
    yearly = [dict(r) for r in cur.fetchall()]

    # Monthly
    cur.execute("SELECT year, month, ym, hours, plays, unique_artists FROM monthly ORDER BY year, month")
    monthly = [dict(r) for r in cur.fetchall()]

    # Listening patterns
    cur.execute("""
        SELECT strftime('%H', ts) AS hour_of_day, COUNT(*) AS plays, SUM(ms_played)/3600000.0 AS hours
        FROM events
        WHERE kind='audio' AND ms_played >= 30000
        GROUP BY hour_of_day
        ORDER BY hour_of_day
    """)
    by_hour = {r["hour_of_day"]: {"plays": r["plays"], "hours": round(r["hours"] or 0, 1)} for r in cur.fetchall()}

    cur.execute("""
        SELECT strftime('%w', ts) AS dow, COUNT(*) AS plays, SUM(ms_played)/3600000.0 AS hours
        FROM events
        WHERE kind='audio' AND ms_played >= 30000
        GROUP BY dow
        ORDER BY dow
    """)
    by_dow = {r["dow"]: {"plays": r["plays"], "hours": round(r["hours"] or 0, 1)} for r in cur.fetchall()}

    # Platform
    cur.execute("""
        SELECT platform, COUNT(*) AS plays, SUM(ms_played)/3600000.0 AS hours
        FROM events
        WHERE kind='audio' AND ms_played >= 30000
        GROUP BY platform
        ORDER BY hours DESC
    """)
    platforms = [{"platform": r["platform"], "plays": r["plays"], "hours": round(r["hours"] or 0, 1)} for r in cur.fetchall()]

    # Listening mode (shuffle ratio, skip ratio)
    cur.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN shuffle=1 THEN 1 ELSE 0 END) AS shuffled,
            SUM(CASE WHEN skipped=1 THEN 1 ELSE 0 END) AS skipped,
            SUM(CASE WHEN offline=1 THEN 1 ELSE 0 END) AS offline_plays,
            SUM(CASE WHEN incognito_mode=1 THEN 1 ELSE 0 END) AS incognito
        FROM events WHERE kind='audio' AND ms_played >= 30000
    """)
    modes = dict(cur.fetchone())

    # Discoveries — artists with first_seen in last 2 years
    cur.execute("""
        SELECT artist_name, first_seen, total_plays, total_ms/3600000.0 AS hours
        FROM artists
        WHERE first_seen >= '2024-01-01' AND total_ms > 0
        ORDER BY total_ms DESC
        LIMIT 20
    """)
    recent_discoveries = [dict(r) for r in cur.fetchall()]

    # Listening intensity extremes
    cur.execute("""
        SELECT ym, hours FROM monthly ORDER BY hours DESC LIMIT 1
    """)
    peak = dict(cur.fetchone() or {})
    cur.execute("""
        SELECT ym, hours FROM monthly WHERE hours > 0 ORDER BY hours ASC LIMIT 1
    """)
    minrow = dict(cur.fetchone() or {})

    # Decades (we don't have release year in extended history; estimate from first_seen)
    # Skip; just count unique artists per year for trend

    # Audiobooks + podcasts (account data)
    cur.execute("""
        SELECT audiobook_name, author_name, SUM(total_ms)/3600000.0 AS hours, SUM(plays) AS plays
        FROM audiobooks
        GROUP BY audiobook_name, author_name
        ORDER BY hours DESC
    """)
    audiobooks = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT podcast_name, SUM(plays) AS plays, SUM(total_ms)/3600000.0 AS hours
        FROM podcasts
        GROUP BY podcast_name
        ORDER BY hours DESC
        LIMIT 15
    """)
    podcasts = [dict(r) for r in cur.fetchall()]

    # Search queries — top searched terms
    cur.execute("""
        SELECT search_query, COUNT(*) AS n
        FROM search_queries
        WHERE search_query IS NOT NULL AND search_query != ''
        GROUP BY search_query
        ORDER BY n DESC
        LIMIT 20
    """)
    top_searches = [{"q": r["search_query"], "n": r["n"]} for r in cur.fetchall()]

    # Wrapped 2025 highlights
    cur.execute("SELECT key, value FROM wrapped_2025")
    wrapped = {r["key"]: r["value"] for r in cur.fetchall()}

    # Sound capsule highlights (sample)
    cur.execute("SELECT date, highlight_type, raw_json FROM sound_capsule_highlights ORDER BY date DESC LIMIT 5")
    capsule = [dict(r) for r in cur.fetchall()]

    profile = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "source": "data/processed/spotify.db (extended + account data)",
        "summary": {
            "date_range": f"{yearly[0]['year']}-01 → {yearly[-1]['year']}-{monthly[-1]['month']:02d}" if yearly else None,
            "total_hours": round(sum(y["hours"] for y in yearly), 0),
            "total_plays": sum(y["plays"] for y in yearly),
            "unique_artists": unique_artists,
            "unique_tracks": unique_tracks,
            "peak_month": peak,
            "lightest_month": minrow,
        },
        "top_artists": [
            {"artist": a["artist_name"], "hours": round(a["total_ms"]/3600000, 1),
             "plays": a["total_plays"], "first": a["first_seen"], "last": a["last_seen"]}
            for a in top_artists
        ],
        "top_tracks": [
            {"track": t["track_name"], "artist": t["artist_name"], "album": t["album_name"],
             "hours": round(t["total_ms"]/3600000, 1), "plays": t["total_plays"],
             "first": t["first_seen"], "last": t["last_seen"]}
            for t in top_tracks
        ],
        "yearly": [{"year": y["year"], "hours": y["hours"], "plays": y["plays"],
                    "unique_artists": y["unique_artists"], "unique_tracks": y["unique_tracks"]} for y in yearly],
        "by_hour_of_day": by_hour,
        "by_day_of_week": by_dow,  # 0=Sunday ... 6=Saturday
        "platforms": platforms,
        "modes": {
            "total_plays": modes.get("total"),
            "shuffled": modes.get("shuffled"),
            "shuffle_ratio": round(modes.get("shuffled", 0) / max(modes.get("total", 1), 1), 3),
            "skipped": modes.get("skipped"),
            "skip_ratio": round(modes.get("skipped", 0) / max(modes.get("total", 1), 1), 3),
            "offline_plays": modes.get("offline_plays"),
            "incognito": modes.get("incognito"),
        },
        "recent_discoveries": [
            {"artist": d["artist_name"], "first": d["first_seen"], "plays": d["total_plays"],
             "hours": round(d["hours"] or 0, 1)}
            for d in recent_discoveries
        ],
        "audiobooks": audiobooks,
        "podcasts": podcasts,
        "top_searches": top_searches,
        "wrapped_2025": wrapped,
        "capsule_recent": capsule,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(profile, ensure_ascii=False, indent=2))

    # Narrative report
    r = []
    r.append("# Marcus — Music Profile (Signal//Noise)")
    r.append("")
    r.append(f"_Generated_: {profile['generated_at']}")
    r.append("")
    s = profile["summary"]
    r.append("## Top-line")
    r.append("")
    r.append(f"- Date range: **{s['date_range']}**")
    r.append(f"- Total listening: **{s['total_hours']:,.0f} hours** ({s['total_plays']:,} plays)")
    r.append(f"- Peak month: **{s['peak_month'].get('ym', '?')}** ({s['peak_month'].get('hours', 0):.0f}h)")
    r.append(f"- Lightest month: **{s['lightest_month'].get('ym', '?')}** ({s['lightest_month'].get('hours', 0):.0f}h)")
    r.append("")

    r.append("## Top 20 artists (by hours)")
    r.append("")
    r.append("| # | hours | plays | artist | first → last |")
    r.append("|---:|---:|---:|---|---|")
    for i, a in enumerate(profile["top_artists"][:20], 1):
        r.append(f"| {i} | {a['hours']:.0f} | {a['plays']:,} | {a['artist']} | {a['first'][:10]} → {a['last'][:10]} |")
    r.append("")

    r.append("## Top 20 tracks (by hours)")
    r.append("")
    r.append("| # | hours | plays | track | artist | album |")
    r.append("|---:|---:|---:|---|---|---|")
    for i, t in enumerate(profile["top_tracks"][:20], 1):
        r.append(f"| {i} | {t['hours']:.0f} | {t['plays']:,} | {t['track']} | {t['artist']} | {t['album'] or ''} |")
    r.append("")

    r.append("## Yearly listening intensity")
    r.append("")
    r.append("```")
    r.append("year   hrs    plays  unique artists")
    for y in profile["yearly"]:
        bar = "█" * int(y["hours"] / 50)
        r.append(f"  {y['year']}  {y['hours']:>5.0f}  {y['plays']:>6,}  {y['unique_artists']:>5,}  {bar}")
    r.append("```")
    r.append("")

    # Day-of-week
    dow_names = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
    r.append("## By day of week (0=Sun)")
    r.append("")
    for d, v in sorted(by_dow.items(), key=lambda x: int(x[0])):
        r.append(f"- {dow_names[int(d)]}: {v['hours']:.0f}h ({v['plays']:,} plays)")
    r.append("")

    # Hour of day
    r.append("## By hour of day (24h)")
    r.append("")
    for h in range(24):
        v = by_hour.get(f"{h:02d}", {"hours":0, "plays":0})
        bar = "█" * int(v["hours"] / 50)
        r.append(f"  {h:02d}:00  {v['hours']:>6.0f}h  {v['plays']:>6,}  {bar}")
    r.append("")

    # Modes
    m = profile["modes"]
    r.append("## Listening mode")
    r.append("")
    r.append(f"- Shuffle ratio: **{m['shuffle_ratio']*100:.1f}%** of plays")
    r.append(f"- Skip ratio:   **{m['skip_ratio']*100:.1f}%** of plays")
    r.append(f"- Offline plays: {m['offline_plays']:,}")
    r.append(f"- Incognito:     {m['incognito']:,}")
    r.append("")

    r.append("## Platforms")
    r.append("")
    r.append("| platform | hours | plays |")
    r.append("|---|---:|---:|")
    for p in profile["platforms"]:
        r.append(f"| {p['platform']} | {p['hours']:.0f} | {p['plays']:,} |")
    r.append("")

    r.append("## Recent discoveries (first heard ≥ 2024-01-01)")
    r.append("")
    for d in profile["recent_discoveries"][:15]:
        r.append(f"- {d['artist']} — {d['hours']:.0f}h, {d['plays']} plays (first: {d['first'][:10]})")
    r.append("")

    r.append("## Audiobooks")
    r.append("")
    for a in profile["audiobooks"]:
        r.append(f"- *{a['audiobook_name']}* — {a['author_name']} ({a['hours']:.1f}h, {a['plays']} plays)")
    r.append("")

    r.append("## Top podcasts")
    r.append("")
    for p in profile["podcasts"]:
        r.append(f"- {p['podcast_name']} — {p['hours']:.0f}h, {p['plays']} plays")
    r.append("")

    r.append("## Top searches (1,382 total)")
    r.append("")
    for s in profile["top_searches"]:
        r.append(f"- `{s['q']}` ({s['n']}×)")
    r.append("")

    r.append("## Wrapped 2025 (Spotify's own stats)")
    r.append("")
    for k, v in profile["wrapped_2025"].items():
        # Try to make JSON nicer
        try:
            v_pretty = json.dumps(json.loads(v), ensure_ascii=False)[:200]
        except Exception:
            v_pretty = (v or "")[:200]
        r.append(f"- **{k}**: {v_pretty}")
    r.append("")

    # Coach-relevant narrative
    r.append("## Coach-relevant observations (hypotheses, not facts)")
    r.append("")
    r.append("These are **patterns**, not diagnoses. Treat as starting points for reflection, not conclusions.")
    r.append("")
    # Identify patterns
    peak_year = max(profile["yearly"], key=lambda y: y["hours"])
    low_year = min([y for y in profile["yearly"] if y["year"] >= 2017], key=lambda y: y["hours"])
    r.append(f"- **Peak listening year: {peak_year['year']}** ({peak_year['hours']:.0f}h). 2020/2021 dominate — overlaps with Corona lockdowns and a known difficult relationship period.")
    r.append(f"- **Lowest listening year (since 2017): {low_year['year']}** ({low_year['hours']:.0f}h). 2018 — coincides with the Berlin TXL FUTR HUB project (hands-on dev work, more in-person collaboration).")
    r.append(f"- **Genre concentration**: The top 20 artists cover Classic Rock (AC/DC, Motörhead, ZZ Top, Rolling Stones), Deutschrock/Krautrock (NEU!, Westernhagen, Ton Steine Scherben), and US punk-adjacent rock (Bowie, Smashing Pumpkins, Billy Idol). Diversity within a tightly defined aesthetic.")
    r.append(f"- **Long-burn tracks**: Several tracks exceed 8 hours lifetime listen-time (Hallogallo, Jailbreak-Live, Jump Into The Fire, Maggot Brain, Politicians In My Eyes). These signal 'comfort objects' — tracks that get returned to again and again.")
    r.append(f"- **Audiobooks (14 sessions, all 2026)**: Dalai Lama, 'Der Sinn des Lebens'. Single concentrated burst. Note as a possible recent pivot toward contemplative input.")
    r.append(f"- **Podcasts**: Dominated by DLF 'Die Nachrichten' — daily news consumption, not deep dives.")
    r.append(f"- **Skip ratio** of {m['skip_ratio']*100:.1f}% is moderate; shuffle ratio of {m['shuffle_ratio']*100:.1f}% suggests mostly deliberate listening rather than passive radio-style.")
    r.append("")

    r.append("## How to use this in coaching")
    r.append("")
    r.append("- For reflection on solitude (Bereich 3 'Weniger allein'): music may be **substituting for human company** in high-volume months — that is not a judgment, just a structural observation.")
    r.append("- For Bereich 4 ('Aus Online-Welt raus'): long-burn tracks are the inverse of algorithmic discovery; they may be a refuge from platform-shaped listening.")
    r.append("- For Bereich 5 ('Partnerin finden'): shared music is a known bonding vector; consider whether your top artists are *date-night friendly* (or 'signals taste that filters aggressively').")
    r.append("- For Bereich 7 ('Kreative Projekte'): the genres (Krautrock, Punk, Marxist theory adjacent) overlap with your writing interests — consider whether your listening feeds your intellectual work or merely punctuates it.")
    r.append("")
    r.append("---")
    r.append("")
    r.append(f"Machine-readable profile: `{OUT_JSON.relative_to(ROOT)}`")
    r.append(f"Source DB: `{DB.relative_to(ROOT)}`")

    OUT_REPORT.write_text("\n".join(r))
    print(f"Wrote: {OUT_JSON}")
    print(f"Wrote: {OUT_REPORT}")
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
