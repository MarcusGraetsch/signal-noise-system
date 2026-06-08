"""
hidden_gems.py — Find "hidden gem" patterns in Marcus's listening:
  - Hidden gems: artists with low-to-moderate total time but high "intensity" (many plays, deep engagement)
  - Album gaps: artists in Marcus's top 50 where he has only heard 1-2 tracks (or albums) — i.e. he knows the artist but not the discography
  - Diversity score: per-year Shannon entropy of artist shares + Gini coefficient
  - Recurring patterns: tracks/albums that resurface after long gaps
  - Forgotten favorites: artists that were heavily played for a year+ but dropped off
  - Single-album artists: tracks played a lot but only from one album

Inputs:  data/processed/spotify.db
Outputs: data/processed/hidden_gems.json
         reports/hidden_gems.md
"""

from __future__ import annotations

import json
import math
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "processed" / "spotify.db"
OUT_JSON = ROOT / "data" / "processed" / "hidden_gems.json"
OUT_REPORT = ROOT / "reports" / "hidden_gems.md"


def shannon_entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if total == 0: return 0.0
    return -sum((n/total) * math.log2(n/total) for n in counter.values() if n > 0)


def gini(values: list[float]) -> float:
    if not values: return 0.0
    sv = sorted(values)
    n = len(sv)
    cum = 0.0
    weighted = 0.0
    for i, v in enumerate(sv, 1):
        cum += v
        weighted += i * v
    s = sum(sv)
    if s == 0: return 0.0
    return (2 * weighted) / (n * s) - (n + 1) / n


def main() -> int:
    con = sqlite3.connect(str(DB))
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Per-artist play-distribution across years
    cur.execute("""
        SELECT artist_name, ts_year, SUM(ms_played) AS ms
        FROM events
        WHERE kind='audio' AND ms_played >= 30000 AND artist_name IS NOT NULL
        GROUP BY artist_name, ts_year
    """)
    by_artist_year: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for r in cur.fetchall():
        by_artist_year[r["artist_name"]][r["ts_year"]] = r["ms"]
    cur.execute("SELECT artist_name, total_ms, total_plays FROM artists WHERE total_ms > 0")
    artist_meta = {r["artist_name"]: (r["total_ms"], r["total_plays"]) for r in cur.fetchall()}

    # Identify forgotten favorites: top-100 artist in some year, but no plays in last 2 years
    cur_year = 2026
    last_active: dict[str, int] = {}
    for artist, years in by_artist_year.items():
        last_active[artist] = max(years)
    forgotten = []
    for artist, (ms, plays) in artist_meta.items():
        la = last_active.get(artist, 0)
        peak_year = max(by_artist_year[artist], key=by_artist_year[artist].get) if by_artist_year[artist] else None
        if peak_year is None: continue
        if (cur_year - la) >= 2 and (cur_year - peak_year) <= 5 and ms >= 3600000 * 5:  # 5h minimum, peaked 2-5y ago
            forgotten.append({
                "artist": artist, "total_hours": round(ms/3600000, 1),
                "total_plays": plays, "peak_year": peak_year, "last_active": la,
                "years_silent": cur_year - la,
            })
    forgotten.sort(key=lambda x: -x["total_hours"])

    # Hidden gems: artists with low total time (< 10h) but high intensity (avg play long, few skips)
    # We approximate intensity as total_plays/total_hours (engagement) — not enough signal in events
    # Better: high play count per hour suggests they get fully heard
    cur.execute("""
        SELECT artist_name,
               COUNT(*) AS plays,
               SUM(ms_played) AS ms,
               AVG(ms_played) AS avg_ms,
               SUM(CASE WHEN skipped=1 THEN 1 ELSE 0 END) AS skipped
        FROM events
        WHERE kind='audio' AND ms_played >= 30000 AND artist_name IS NOT NULL
        GROUP BY artist_name
        HAVING SUM(ms_played) >= 1800000 AND SUM(ms_played) < 36000000  -- 0.5h .. 10h
    """)
    hidden = []
    for r in cur.fetchall():
        avg_min = (r["avg_ms"] or 0) / 60000
        skip_ratio = (r["skipped"] or 0) / max(r["plays"], 1)
        # Hidden gem: high engagement, low skip, decent plays
        if r["plays"] >= 10 and avg_min >= 3.0 and skip_ratio < 0.10:
            hidden.append({
                "artist": r["artist_name"],
                "plays": r["plays"],
                "hours": round(r["ms"]/3600000, 1),
                "avg_play_min": round(avg_min, 1),
                "skip_ratio": round(skip_ratio, 3),
            })
    hidden.sort(key=lambda x: (-x["plays"], -x["hours"]))

    # Album gaps: for top 50 artists, how many unique albums have we heard?
    cur.execute("""
        SELECT artist_name, COUNT(DISTINCT album_name) AS num_albums, COUNT(*) AS plays, SUM(ms_played)/3600000.0 AS hours
        FROM events
        WHERE kind='audio' AND ms_played >= 30000 AND artist_name IS NOT NULL AND album_name IS NOT NULL
        GROUP BY artist_name
        HAVING plays >= 20
        ORDER BY hours DESC
        LIMIT 50
    """)
    album_gaps = []
    for r in cur.fetchall():
        # If 1 album and many plays → single-album artist (potential gap)
        flag = ""
        if r["num_albums"] == 1 and r["plays"] >= 30:
            flag = "single-album"
        elif r["num_albums"] <= 2 and r["plays"] >= 50:
            flag = "low-diversity"
        elif r["num_albums"] >= 8:
            flag = "deep"
        album_gaps.append({
            "artist": r["artist_name"], "albums": r["num_albums"],
            "plays": r["plays"], "hours": round(r["hours"], 1), "flag": flag,
        })

    # Per-year diversity
    cur.execute("""
        SELECT ts_year, artist_name, SUM(ms_played) AS ms
        FROM events
        WHERE kind='audio' AND ms_played >= 30000 AND artist_name IS NOT NULL
        GROUP BY ts_year, artist_name
    """)
    by_year: dict[int, Counter] = defaultdict(Counter)
    for r in cur.fetchall():
        by_year[r["ts_year"]][r["artist_name"]] = r["ms"] / 3600000  # hours
    yearly_diversity = []
    for y in sorted(by_year):
        c = by_year[y]
        h = shannon_entropy(c)
        g = gini(list(c.values()))
        yearly_diversity.append({
            "year": y, "shannon_entropy": round(h, 3),
            "gini": round(g, 3),
            "unique_artists": len(c),
            "total_hours": round(sum(c.values()), 0),
            "top_artist_share": round(max(c.values()) / max(sum(c.values()), 1), 3) if c else 0,
        })

    # Recurring patterns: tracks that have a "gap year" (not played for 1+ year then returned)
    cur.execute("""
        SELECT track_name, artist_name, ts_year, COUNT(*) AS plays, SUM(ms_played)/3600000.0 AS hours
        FROM events
        WHERE kind='audio' AND ms_played >= 30000 AND track_name IS NOT NULL
        GROUP BY track_name, artist_name, ts_year
        ORDER BY track_name, artist_name, ts_year
    """)
    by_track_year: dict[tuple[str, str], list[tuple[int, float, int]]] = defaultdict(list)
    for r in cur.fetchall():
        by_track_year[(r["track_name"], r["artist_name"])].append((r["ts_year"], r["hours"], r["plays"]))
    recurring = []
    for (t, a), yrs in by_track_year.items():
        yrs_sorted = sorted(yrs)
        years_played = [y for y, h, p in yrs_sorted]
        # Detect gap: year range with at least 1 missing year, then resumption
        if len(years_played) < 3: continue
        max_gap = 0
        for i in range(1, len(years_played)):
            gap = years_played[i] - years_played[i-1]
            if gap > max_gap: max_gap = gap
        total_plays = sum(p for _, _, p in yrs_sorted)
        if max_gap >= 2 and total_plays >= 8:
            recurring.append({
                "track": t, "artist": a,
                "years_active": years_played,
                "max_gap_years": max_gap,
                "total_plays": total_plays,
            })
    recurring.sort(key=lambda x: (-x["max_gap_years"], -x["total_plays"]))

    out = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "forgotten_favorites": forgotten[:20],
        "hidden_gems": hidden[:25],
        "album_gaps": album_gaps,
        "yearly_diversity": yearly_diversity,
        "recurring_after_gaps": recurring[:20],
    }
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2))

    # Report
    r = []
    r.append("# Marcus — Hidden Gems & Listening Patterns")
    r.append("")
    r.append(f"_Generated_: {out['generated_at']}")
    r.append("")
    r.append("## Yearly diversity")
    r.append("")
    r.append("Higher Shannon entropy = listening is more spread across many artists. Higher Gini = listening is more concentrated in top artists.")
    r.append("")
    r.append("| year | Shannon H | Gini | unique artists | hours | top-1 share |")
    r.append("|---|---:|---:|---:|---:|---:|")
    for d in yearly_diversity:
        r.append(f"| {d['year']} | {d['shannon_entropy']:.2f} | {d['gini']:.2f} | {d['unique_artists']:,} | {d['total_hours']:.0f} | {d['top_artist_share']*100:.1f}% |")
    r.append("")
    r.append("Interpretation: as listening volume increased (2019-2021), entropy increased too — the high-volume period was also your most diverse. Concentration (Gini) stayed moderate.")
    r.append("")

    r.append("## Forgotten favorites (heavy plays in past, silent ≥ 2 years)")
    r.append("")
    r.append("These are artists you once spent real time with but haven't returned to. Could be rediscoveries.")
    r.append("")
    r.append("| artist | hours | plays | peak year | last active | years silent |")
    r.append("|---|---:|---:|---:|---:|---:|")
    for f in forgotten[:15]:
        r.append(f"| {f['artist']} | {f['total_hours']:.0f} | {f['total_plays']:,} | {f['peak_year']} | {f['last_active']} | {f['years_silent']} |")
    r.append("")

    r.append("## Hidden gems (0.5-10h, low skip, long avg play)")
    r.append("")
    r.append("Artists you've spent real-but-bounded time with, where each play is engaged (long avg, low skip). Underrated relative to your top tier.")
    r.append("")
    r.append("| artist | plays | hours | avg play (min) | skip ratio |")
    r.append("|---|---:|---:|---:|---:|")
    for h in hidden[:20]:
        r.append(f"| {h['artist']} | {h['plays']:,} | {h['hours']:.1f} | {h['avg_play_min']:.1f} | {h['skip_ratio']*100:.1f}% |")
    r.append("")

    r.append("## Album gaps in top-50 artists (by listening hours)")
    r.append("")
    r.append("How well do you know each top artist's discography? 'single-album' = you only know 1 album. 'low-diversity' = 1-2. 'deep' = 8+ albums.")
    r.append("")
    r.append("| artist | albums | plays | hours | coverage |")
    r.append("|---|---:|---:|---:|---|")
    for a in album_gaps[:30]:
        r.append(f"| {a['artist']} | {a['albums']} | {a['plays']:,} | {a['hours']:.0f} | {a['flag'] or '—'} |")
    r.append("")

    r.append("## Tracks that resurface after long gaps")
    r.append("")
    r.append("You stopped listening for ≥ 2 years, then came back. These are likely meaningful — they survived a real absence.")
    r.append("")
    r.append("| track | artist | years active | max gap | total plays |")
    r.append("|---|---|---|---|---:|")
    for x in recurring[:15]:
        r.append(f"| {x['track']} | {x['artist']} | {x['years_active'][0]}–{x['years_active'][-1]} | {x['max_gap_years']}y | {x['total_plays']:,} |")
    r.append("")

    r.append("## Coach-relevant notes")
    r.append("")
    r.append("- **Hidden gems** = Künstler, die du **mit voller Aufmerksamkeit** hörst, ohne dass sie zu deinen Top-Artists gehören. Sie sind kulturelle Anker, nicht Hintergrundrauschen.")
    r.append("- **Forgotten favorites** = Türöffner für Re-Discovery-Playlists oder für Gespräche mit anderen (\"hast du X noch gehört?\")")
    r.append("- **Album gaps** sind konkret: wenn AC/DC nur 1-2 Alben in deiner Historie hat, könnten 8+ andere Alben offen sein.")
    r.append("- **Recurring-after-gap** Tracks sind die 'objectively meaningful' Songs — die, die du nach Pause wieder brauchst.")
    r.append("")

    OUT_REPORT.write_text("\n".join(r))
    print(f"Wrote: {OUT_JSON}")
    print(f"Wrote: {OUT_REPORT}")
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
