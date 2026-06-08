"""
playlists.py — Generate curated playlists from Marcus's listening history.

Outputs (Spotify-importable CSV format: playlist_name,artist_name,album_name,track_name,track_uri):
  - playlists/life_phases.csv  — one track per year, the "track of the year"
  - playlists/long_burn.csv    — "long-burn" tracks (>5h lifetime listening)
  - playlists/krautrock_drift.csv — German/Deutschrock artists from top time
  - playlists/hidden_gems.csv  — under-the-radar artists with high engagement
  - playlists/recurring.csv    — tracks that resurface after long gaps
  - playlists/forgotten_favorites.csv — artists heavy in past, quiet ≥ 2y
  - playlists/year_X_top.csv   — top 30 tracks per year, one playlist per year

Also outputs a markdown index: reports/playlists.md
"""

from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "processed" / "spotify.db"
PLAYLISTS = ROOT / "playlists"
OUT_INDEX = ROOT / "reports" / "playlists.md"


def write_playlist(name: str, tracks: list[dict], out_dir: Path) -> Path:
    """tracks: list of dicts with track_name, artist_name, album_name, track_uri (uri)"""
    out = out_dir / f"{name}.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["playlist_name", "artist_name", "album_name", "track_name", "track_uri", "first_played", "last_played", "plays", "hours"])
        w.writeheader()
        for t in tracks:
            w.writerow({
                "playlist_name": name,
                "artist_name": t.get("artist_name") or t.get("artist", ""),
                "album_name": t.get("album_name", ""),
                "track_name": t.get("track_name") or t.get("track", ""),
                "track_uri": t.get("track_uri") or t.get("spotify_track_uri", ""),
                "first_played": t.get("first_played") or t.get("first_seen", ""),
                "last_played": t.get("last_played") or t.get("last_seen", ""),
                "plays": t.get("plays", ""),
                "hours": t.get("hours", ""),
            })
    return out


def main() -> int:
    PLAYLISTS.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    written = []

    # 1. "Track of the year" — for each year, the single track with the most listening hours
    cur.execute("""
        SELECT track_name, artist_name, album_name, ts_year,
               COUNT(*) AS plays, SUM(ms_played)/3600000.0 AS hours,
               MIN(ts) AS first, MAX(ts) AS last,
               MAX(spotify_track_uri) AS track_uri
        FROM events
        WHERE kind='audio' AND ms_played >= 30000 AND track_name IS NOT NULL
        GROUP BY track_name, artist_name, album_name, ts_year
    """)
    by_year_track: dict[int, list] = defaultdict(list)
    for r in cur.fetchall():
        by_year_track[r["ts_year"]].append({
            "track_name": r["track_name"],
            "artist_name": r["artist_name"],
            "album_name": r["album_name"],
            "track_uri": r["track_uri"],
            "plays": r["plays"],
            "hours": round(r["hours"] or 0, 1),
            "first_played": r["first"][:10] if r["first"] else "",
            "last_played": r["last"][:10] if r["last"] else "",
        })
    life_phases = []
    for y in sorted(by_year_track):
        top = sorted(by_year_track[y], key=lambda t: (-t["hours"], -t["plays"]))[0]
        life_phases.append(top)
    p = write_playlist("life_phases", life_phases, PLAYLISTS)
    written.append((p, "1 Track pro Jahr — 'Track of the Year'", "Erfasst deine 12,5 Jahre in 13 Tracks."))

    # 2. Long-burn — tracks with >5h lifetime listening
    cur.execute("""
        SELECT events.track_name, events.artist_name, events.album_name,
               SUM(events.ms_played)/3600000.0 AS hours, COUNT(*) AS plays,
               MIN(events.ts) AS first, MAX(events.ts) AS last,
               MAX(events.spotify_track_uri) AS track_uri
        FROM events
        WHERE events.kind='audio' AND events.ms_played >= 30000 AND events.track_name IS NOT NULL
        GROUP BY events.track_name, events.artist_name, events.album_name
        HAVING hours > 5
        ORDER BY hours DESC
        LIMIT 60
    """)
    long_burn = []
    seen = set()
    for r in cur.fetchall():
        key = (r["track_name"], r["artist_name"])
        if key in seen: continue
        seen.add(key)
        long_burn.append({
            "track_name": r["track_name"],
            "artist_name": r["artist_name"],
            "album_name": r["album_name"],
            "track_uri": r["track_uri"],
            "hours": round(r["hours"], 1),
            "plays": r["plays"],
            "first_played": r["first"][:10] if r["first"] else "",
            "last_played": r["last"][:10] if r["last"] else "",
        })
    p = write_playlist("long_burn", long_burn, PLAYLISTS)
    written.append((p, "Long-Burn — Tracks mit > 5h Lebenszeit-Hören", "Die 'Komfort-Objekte', die du immer wieder brauchst."))

    # 3. Krautrock-Drift — German/Deutschrock + Krautrock artists, by hours
    cur.execute("""
        SELECT artist_name, total_ms, total_plays
        FROM artists
        WHERE total_ms > 0
    """)
    # Identify German/Krautrock artists manually curated (well-known list)
    kraut = {
        "NEU!","Tangerine Dream","Kraftwerk","Can","Faust","Cluster","Harmonia",
        "Amon Düül","Amon Düül II","Popol Vuh","Ash Ra Tempel","Ash Ra","Grobschnitt",
        "Embryo","Birth Control","Ton Steine Scherben","Einstürzende Neubauten",
        "D.A.F.","DAF","Die Haut","Die Tödliche Doris","Malaria!","Palais Schaumburg",
        "Deutsch Amerikanische Freundschaft","Ideal","Abwärts","Mittagspause",
        "Die Goldenen Zitronen","Die Sterne","Bettina Köster","F.S.K.","Erdmöbel",
        "Kamera","Kakkmaddafakka","Felix Kubin","Hausfrauenbillard",
        "Westernhagen","BAP","Wolfgang Niedecken","Wolf Maahn","Udo Lindenberg",
        "Herbert Grönemeyer","Nena","Alphaville","Falco","Opus","DÖF",
        "Spider Murphy Gang","Geier Sturzflug","Fehlfarben","Sonderfahrten",
        "Hansa Records","Wiener Aktionismus","S.Y.P.H.","Klaus Dinger","Conny Plank",
        "Michael Rother","Rolf-Ulrich Kaiser","Peter Baumann","Edgar Froese",
        "La Düsseldorf","Rhythmus 66","Organisation","Carlos Perón",
        "Wumpscut","Atari Teenage Riot","Bohren & der Club of Gore",
    }
    deutsch_rock = {
        "Die Ärzte","Die Toten Hosen","Wir Sind Helden","Sportfreunde Stiller",
        "Madsen","Jupiter Jones","Kettcar","Tocotronic","Tomte","Olli Schulz",
        "Kraftklub","SDP","Deichkind","Fettes Brot","Beginner","Sido","Bushido",
        "Eminem","Rammstein","Lindemann","Oomph!","Unheilig","In Extremo",
        "Subway to Sally","Saltatio Mortis","ASP","Ost+Front","Megaherz",
        "Eisbrecher","Stahlhammer","Goethes Erben","ASP","Lacrimosa",
        "Tanzwut","In Strict Confidence","KMFDM","Welle:Erdball","Covenant",
        "VNV Nation","Apoptygma Berzerk","And One","De/Vision","Mesh","Camouflage",
        "Wolfsheim","Project Pitchfork","Icon of Coil","Hocico","Suicide Commando",
        "Hanzel und Gretyl","Oomph!","Rammstein","Eisbrecher",
    }
    targets = kraut | deutsch_rock
    rows = list(cur.fetchall())
    kraut_artists = sorted([r for r in rows if r["artist_name"] in targets],
                           key=lambda r: -r["total_ms"])[:30]
    # For each of these, get top tracks
    kraut_tracks = []
    for ar in kraut_artists:
        c2 = con.cursor()
        c2.execute("""
            SELECT track_name, album_name, SUM(ms_played)/3600000.0 AS hours, COUNT(*) AS plays,
                   MAX(spotify_track_uri) AS track_uri
            FROM events
            WHERE kind='audio' AND ms_played >= 30000 AND artist_name = ?
            GROUP BY track_name, album_name
            ORDER BY hours DESC LIMIT 2
        """, (ar["artist_name"],))
        for t in c2.fetchall():
            kraut_tracks.append({
                "track_name": t["track_name"],
                "artist_name": ar["artist_name"],
                "album_name": t["album_name"],
                "track_uri": t["track_uri"],
                "hours": round(t["hours"] or 0, 1),
                "plays": t["plays"],
            })
    kraut_tracks.sort(key=lambda t: -t["hours"])
    p = write_playlist("krautrock_drift", kraut_tracks[:60], PLAYLISTS)
    written.append((p, "Krautrock-Drift — Deutsch / Krautrock Top-Tracks", "Klassiker + Neu-Entdeckungen aus dem deutschsprachigen Korpus."))

    # 4. Hidden gems — from previous analysis
    hg = json.loads((ROOT / "data" / "processed" / "hidden_gems.json").read_text())
    hg_artists = [h["artist"] for h in hg["hidden_gems"][:20]]
    hg_tracks = []
    for artist in hg_artists:
        c2 = con.cursor()
        c2.execute("""
            SELECT track_name, album_name, SUM(ms_played)/3600000.0 AS hours, COUNT(*) AS plays,
                   MAX(spotify_track_uri) AS track_uri
            FROM events
            WHERE kind='audio' AND ms_played >= 30000 AND artist_name = ?
            GROUP BY track_name, album_name
            ORDER BY hours DESC LIMIT 3
        """, (artist,))
        for t in c2.fetchall():
            hg_tracks.append({
                "track_name": t["track_name"],
                "artist_name": artist,
                "album_name": t["album_name"],
                "track_uri": t["track_uri"],
                "hours": round(t["hours"] or 0, 1),
                "plays": t["plays"],
            })
    hg_tracks.sort(key=lambda t: -t["hours"])
    p = write_playlist("hidden_gems", hg_tracks[:50], PLAYLISTS)
    written.append((p, "Hidden Gems — Under-the-radar Artists, engagiert gehört", "Artists die du < 10h gehört hast, aber mit voller Aufmerksamkeit."))

    # 5. Recurring after gaps
    rec = json.loads((ROOT / "data" / "processed" / "hidden_gems.json").read_text())
    rec_tracks = []
    for r in rec["recurring_after_gaps"][:25]:
        c2 = con.cursor()
        c2.execute("""
            SELECT track_name, artist_name, album_name, COUNT(*) AS plays, SUM(ms_played)/3600000.0 AS hours,
                   MAX(spotify_track_uri) AS track_uri
            FROM events
            WHERE kind='audio' AND track_name = ? AND COALESCE(artist_name,'') = COALESCE(? ,'')
            GROUP BY track_name, artist_name, album_name
            ORDER BY hours DESC LIMIT 1
        """, (r["track"], r["artist"]))
        for t in c2.fetchall():
            rec_tracks.append({
                "track_name": t["track_name"],
                "artist_name": t["artist_name"],
                "album_name": t["album_name"],
                "plays": t["plays"],
                "hours": round(t["hours"] or 0, 1),
            })
    p = write_playlist("recurring", rec_tracks, PLAYLISTS)
    written.append((p, "Recurring After Gaps — Tracks die nach Pause zurückkommen", "Bedeutungs-Anker: was eine echte Abwesenheit überlebt hat."))

    # 6. Forgotten favorites — artists not heard in 2+ years, but heavy past plays
    favs = json.loads((ROOT / "data" / "processed" / "hidden_gems.json").read_text())
    fav_tracks = []
    for f in favs["forgotten_favorites"][:15]:
        c2 = con.cursor()
        c2.execute("""
            SELECT track_name, album_name, SUM(ms_played)/3600000.0 AS hours, COUNT(*) AS plays,
                   MAX(spotify_track_uri) AS track_uri
            FROM events
            WHERE kind='audio' AND ms_played >= 30000 AND artist_name = ?
            GROUP BY track_name, album_name
            ORDER BY hours DESC LIMIT 2
        """, (f["artist"],))
        for t in c2.fetchall():
            fav_tracks.append({
                "track_name": t["track_name"],
                "artist_name": f["artist"],
                "album_name": t["album_name"],
                "hours": round(t["hours"] or 0, 1),
                "plays": t["plays"],
            })
    p = write_playlist("forgotten_favorites", fav_tracks, PLAYLISTS)
    written.append((p, "Forgotten Favorites — ehemals heavy, ≥ 2 Jahre still", "Re-Discovery-Material."))

    # 7. Per-year top 30
    year_dir = PLAYLISTS / "by_year"
    year_dir.mkdir(parents=True, exist_ok=True)
    for y in sorted(by_year_track):
        top = sorted(by_year_track[y], key=lambda t: (-t["hours"], -t["plays"]))[:30]
        write_playlist(f"year_{y}", top, year_dir)
    written.append((year_dir, "Per-Year Top 30 — ein Playlist pro Jahr", "13 Playlists, 30 Tracks pro Jahr, 2013-2026."))

    # Index report
    r = []
    r.append("# Signal//Noise — Generated Playlists")
    r.append("")
    r.append(f"_Generated_: {datetime.utcnow().isoformat(timespec='seconds')}Z")
    r.append("")
    r.append("Alle Playlists sind im **Spotify-Import-Format** (CSV mit track_uri) und können via Tools wie [Spotlistr](https://www.spotlistr.com/) oder direkt über die Spotify-API in deinen Account geladen werden.")
    r.append("")
    r.append("## Generierte Playlists")
    r.append("")
    for path, title, desc in written:
        if path.is_dir():
            r.append(f"### {title}")
            r.append(f"")
            r.append(f"_{desc}_")
            r.append("")
            r.append(f"Ordner: `playlists/{path.name}/`")
            r.append("")
            for yp in sorted(path.glob("year_*.csv")):
                # count rows
                with yp.open() as fh:
                    n = sum(1 for _ in fh) - 1
                r.append(f"- `{yp.name}` — {n} tracks")
            r.append("")
        else:
            # count rows
            with path.open() as fh:
                n = sum(1 for _ in fh) - 1
            r.append(f"### {title}")
            r.append("")
            r.append(f"_{desc}_")
            r.append("")
            r.append(f"Datei: `playlists/{path.name}` ({n} tracks)")
            r.append("")
    r.append("## How to import")
    r.append("")
    r.append("1. Open [Spotlistr CSV-to-Spotify converter](https://www.spotlistr.com/static/search/playlist-converter/)")
    r.append("2. Upload a CSV file from `playlists/`")
    r.append("3. Spotlistr resolves URIs to your account and creates a new playlist")
    r.append("4. (Alternativ: programmatic via Spotify Web API + PKCE flow)")
    r.append("")
    r.append("## Generation")
    r.append("")
    r.append("All playlists are generated by `src/playlists.py` from the SQLite events table. Re-run to refresh.")
    r.append("")

    OUT_INDEX.write_text("\n".join(r))
    print(f"Wrote {len(written)} playlists and an index at {OUT_INDEX}")
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
