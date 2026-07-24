"""
label_topics_v2.py — Re-label topics using MusicBrainz user-contributed tags.

Instead of guessing genres by hand, we:
  1. For each topic, look up MusicBrainz tags for the topic's artists
  2. Aggregate tags across all artists in the topic, weighted by total hours
  3. Take the top 5-7 tags as the topic's "MusicBrainz genre fingerprint"
  4. Synthesize a human-readable label from the top tag(s) + a short adjective
  5. Let Marcus override the synthesized label after the fact (curated file)

This is dramatically more accurate than the previous hand-rolled rules.
"""

import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

GENRES_FILE = Path("/root/repos/signal-noise-system/data/processed/artist_genres.json")
OVERRIDES_FILE = Path("/root/repos/signal-noise-system/data/processed/artist_genre_overrides.json")
TOPIC_FILE = Path("/root/repos/signal-noise-system/data/processed/topic_summary.json")
EVENTS_DB = Path("/root/repos/signal-noise-system/data/processed/spotify.db")
OUT_JSON = Path("/root/repos/signal-noise-system/data/processed/marcus_spotify_topic_labels_v02.json")
OUT_MD = Path("/root/repos/signal-noise-system/data/processed/marcus_spotify_topic_labels_v02.md")
CURATED_OVERRIDES = Path("/root/repos/signal-noise-system/data/processed/marcus_spotify_topic_overrides.json")

# Common music-tag normalization: merge near-duplicates
TAG_ALIASES = {
    "rock": "rock",
    "hard rock": "hard rock",
    "classic rock": "classic rock",
    "punk": "punk",
    "punk rock": "punk rock",
    "post-punk": "post-punk",
    "post punk": "post-punk",
    "new wave": "new wave",
    "synth-pop": "synth-pop",
    "synth pop": "synth-pop",
    "alternative": "alternative",
    "alternative rock": "alternative rock",
    "indie": "indie",
    "indie rock": "indie rock",
    "electronica": "electronic",
    "electronic": "electronic",
    "hip hop": "hip-hop",
    "hip-hop": "hip-hop",
    "rap": "hip-hop",
    "metal": "metal",
    "heavy metal": "metal",
    "thrash metal": "metal",
    "death metal": "metal",
    "black metal": "metal",
    "doom metal": "metal",
    "pop": "pop",
    "pop rock": "pop rock",
    "folk": "folk",
    "folk rock": "folk rock",
    "country": "country",
    "country rock": "country",
    "blues": "blues",
    "blues rock": "blues rock",
    "jazz": "jazz",
    "soul": "soul",
    "funk": "funk",
    "r&b": "r&b",
    "reggae": "reggae",
    "ska": "ska",
    "krautrock": "krautrock",
    "psychedelic": "psychedelic",
    "psychedelic rock": "psychedelic rock",
    "no wave": "no-wave",
    "no-wave": "no-wave",
    "progressive rock": "progressive rock",
    "prog rock": "progressive rock",
    "ambient": "ambient",
    "experimental": "experimental",
    "experimental rock": "experimental",
    "noise": "noise",
    "industrial": "industrial",
    "gothic": "gothic",
    "gothic rock": "gothic",
    "german": "german",
    "deutschrock": "deutschrock",
    "ndw": "ndw",
    "neue deutsche welle": "ndw",
    "pub rock": "pub rock",
    "garage rock": "garage rock",
    "proto-punk": "proto-punk",
    "proto punk": "proto-punk",
    "power pop": "power pop",
    "surf": "surf",
    "surf rock": "surf",
    "british": "british",
    "american": "american",
    "australian": "australian",
    "singer-songwriter": "singer-songwriter",
    "singer/songwriter": "singer-songwriter",
    "americana": "americana",
    "country rock": "country rock",
    "southern rock": "southern rock",
    "heartland rock": "heartland rock",
    "roots rock": "roots rock",
    "boogie rock": "boogie rock",
    "stoner rock": "stoner rock",
    "stoner metal": "stoner rock",
    "desert rock": "stoner rock",
    "blues-rock": "blues rock",
    "hardcore": "hardcore",
    "hardcore punk": "hardcore",
    "emo": "emo",
    "grunge": "grunge",
    "shoegaze": "shoegaze",
    "dream pop": "dream pop",
    "post-rock": "post-rock",
    "post rock": "post-rock",
    "math rock": "math rock",
    "noise rock": "noise rock",
    "sludge": "sludge",
    "sludge metal": "sludge",
    "post-hardcore": "post-hardcore",
    "garage punk": "garage punk",
    "rock and roll": "rock and roll",
    "rock & roll": "rock and roll",
    "rock'n'roll": "rock and roll",
    "chinese rock": "chinese rock",
    "chinese indie": "chinese indie",
    "beijing": "beijing",
    "deutsch-punk": "deutsch-punk",
    "polit-punk": "polit-punk",
    "west-berlin": "west-berlin",
    "feminist punk": "feminist punk",
    "mississippi blues": "mississippi blues",
    "north mississippi hill country": "north mississippi hill country",
    "electric blues": "electric blues",
    "soft rock": "soft rock",
    "pop rock": "pop rock",
    "glam rock": "glam rock",
    "glam": "glam rock",
}


# Generics that should be filtered out as primary labels
GENERIC_TAGS = {
    "rock", "pop", "electronic", "seen live", "english", "male", "female",
    "vocal", "love", "american", "british", "german", "australian", "canadian",
    "french", "japanese", "swedish", "brazilian", "irish", "scottish", "spanish",
    "dutch", "italian", "box set", "compilation", "various artists", "favourites",
    "favorites", "under 2000 listeners", "00s", "10s", "20s", "70s", "80s", "90s",
    "instrumental", "cover", "tribute", "live",
}

# Specificity bonus: more specific tags win over generic
SPECIFIC_BONUS_MODULE = {
    "krautrock": 100, "post-punk": 50, "pub rock": 50, "proto-punk": 50,
    "grunge": 50, "shoegaze": 50, "gothic": 30, "ambient": 30, "industrial": 30,
    "noise": 30, "experimental": 30, "stoner rock": 50, "doom metal": 50,
    "thrash metal": 50, "black metal": 50, "death metal": 50, "power metal": 50,
    "speed metal": 50, "symphonic metal": 50, "folk metal": 50, "viking metal": 50,
    "ndw": 50, "neue deutsche welle": 50, "schlager": 50,
    "heartland rock": 50, "southern rock": 50, "boogie rock": 30,
    "country rock": 30, "roots rock": 30, "alternative rock": 30,
    "indie rock": 30, "noise rock": 30, "post-rock": 30, "math rock": 30,
    "blues rock": 20, "hard rock": 20, "classic rock": 20,
    "art rock": 20, "psychedelic rock": 20, "garage rock": 20, "surf": 20,
    "power pop": 30, "folk": 10, "blues": 10, "country": 10, "reggae": 20,
    "ska": 20, "punk rock": 30, "hardcore": 30, "emo": 30, "metalcore": 30,
    "synth-pop": 30, "new wave": 30, "gothic rock": 30, "dream pop": 30,
    "funk": 10, "soul": 10, "r&b": 10, "jazz": 10, "hip-hop": 20,
    "trip hop": 20, "electronica": 20, "idm": 20, "drum and bass": 20,
    "americana": 50, "singer-songwriter": 30, "acoustic": 10,
    "no-wave": 50, "no wave": 50, "mathcore": 30, "garage punk": 30,
    "chinese rock": 50, "chinese indie": 50, "beijing": 30,
    "deutsch-punk": 80, "deutschrock": 50, "polit-punk": 60,
    "west-berlin": 40, "feminist punk": 60, "mississippi blues": 60,
    "north mississippi hill country": 60, "electric blues": 30,
    "soft rock": 20, "pop rock": 15, "glam rock": 40, "garage punk": 30,
}

# Pair-table: canonical labels for tag combinations
LABEL_PAIRS_MODULE = {
    frozenset(["krautrock", "experimental"]): "Krautrock / Experimental",
    frozenset(["krautrock", "ambient"]): "Krautrock / Ambient",
    frozenset(["krautrock", "art rock"]): "Krautrock / Art Rock",
    frozenset(["krautrock", "stoner rock"]): "Krautrock (mit Stoner-Adstrich)",
    frozenset(["pub rock", "rock and roll"]): "Pub Rock",
    frozenset(["pub rock", "punk rock"]): "Pub Rock / Punk",
    frozenset(["pub rock", "blues rock"]): "Pub Rock / Blues",
    frozenset(["grunge", "alternative rock"]): "Grunge",
    frozenset(["grunge", "hard rock"]): "Grunge",
    frozenset(["post-punk", "new wave"]): "Post-Punk / New Wave",
    frozenset(["post-punk", "gothic"]): "Gothic Rock / Post-Punk",
    frozenset(["post-punk", "noise rock"]): "Post-Punk / Noise",
    frozenset(["post-punk", "proto-punk"]): "Proto-Punk → Post-Punk",
    frozenset(["post-punk", "garage punk"]): "Post-Punk / Garage",
    frozenset(["proto-punk", "punk"]): "Proto-Punk",
    frozenset(["proto-punk", "hardcore"]): "Proto-Punk / Hardcore",
    frozenset(["proto-punk", "garage rock"]): "Proto-Punk / Garage",
    frozenset(["no-wave", "experimental"]): "No-Wave / Experimental",
    frozenset(["no-wave", "art rock"]): "No-Wave / Art Rock",
    frozenset(["no-wave", "post-punk"]): "No-Wave / Post-Punk",
    frozenset(["industrial", "experimental"]): "Industrial / Experimental",
    frozenset(["industrial", "noise"]): "Industrial / Noise",
    frozenset(["industrial", "electronic"]): "Industrial / Electronic",
    frozenset(["industrial", "post-punk"]): "Industrial / Post-Punk",
    frozenset(["electronic", "experimental"]): "Electronic / Experimental",
    frozenset(["synth-pop", "new wave"]): "New Wave / Synth-Pop",
    frozenset(["americana", "singer-songwriter"]): "Americana / Singer-Songwriter",
    frozenset(["americana", "country rock"]): "Americana / Country Rock",
    frozenset(["heartland rock", "singer-songwriter"]): "Heartland Rock",
    frozenset(["southern rock", "blues rock"]): "Southern Rock / Blues",
    frozenset(["southern rock", "heartland rock"]): "Southern Rock / Heartland",
    frozenset(["stoner rock", "hard rock"]): "Stoner / Desert Rock",
    frozenset(["stoner rock", "metal"]): "Stoner Rock",
    frozenset(["hard rock", "blues rock"]): "Hard Rock / Blues",
    frozenset(["hard rock", "rock and roll"]): "Hard Rock",
    frozenset(["hard rock", "classic rock"]): "Classic Hard Rock",
    frozenset(["hard rock", "new wave"]): "Hard Rock / New Wave",
    frozenset(["hard rock", "punk rock"]): "Hard Rock / Punk",
    frozenset(["classic rock", "rock and roll"]): "Classic Rock",
    frozenset(["folk", "folk rock"]): "Folk",
    frozenset(["folk rock", "country rock"]): "Folk Rock / Country",
    frozenset(["blues", "blues rock"]): "Blues",
    frozenset(["blues", "country"]): "Blues / Country",
    frozenset(["mississippi blues", "blues"]): "Mississippi Blues",
    frozenset(["mississippi blues", "blues rock"]): "Mississippi Blues",
    frozenset(["soul", "funk"]): "Soul / Funk",
    frozenset(["soul", "r&b"]): "Soul / R&B",
    frozenset(["funk", "r&b"]): "Funk / R&B",
    frozenset(["reggae", "ska"]): "Reggae / Ska",
    frozenset(["reggae", "rock"]): "Reggae",
    frozenset(["ndw", "new wave"]): "NDW / New Wave",
    frozenset(["ndw", "synth-pop"]): "NDW / Synth-Pop",
    frozenset(["neue deutsche welle", "new wave"]): "NDW / New Wave",
    frozenset(["neue deutsche welle", "german"]): "NDW (Neue Deutsche Welle)",
    frozenset(["deutsch-punk", "polit-punk"]): "Deutsch-Punk / Polit-Punk",
    frozenset(["deutsch-punk", "punk"]): "Deutsch-Punk",
    frozenset(["deutsch-punk", "west-berlin"]): "Deutsch-Punk (West-Berlin)",
    frozenset(["power pop", "rock and roll"]): "Power Pop",
    frozenset(["power pop", "garage rock"]): "Power Pop / Garage",
    frozenset(["power pop", "punk"]): "Power Pop / Punk",
    frozenset(["punk rock", "hardcore"]): "Punk / Hardcore",
    frozenset(["punk rock", "post-punk"]): "Punk → Post-Punk",
    frozenset(["punk rock", "new wave"]): "Punk / New Wave",
    frozenset(["punk rock", "garage rock"]): "Punk / Garage",
    frozenset(["punk", "rock and roll"]): "Punk / Rock'n'Roll",
    frozenset(["alternative rock", "indie rock"]): "Alt-Indie",
    frozenset(["alternative rock", "punk rock"]): "Alt-Punk",
    frozenset(["alternative rock", "grunge"]): "Alt-Rock / Grunge",
    frozenset(["alternative rock", "hard rock"]): "Alt-Rock / Hard Rock",
    frozenset(["progressive rock", "art rock"]): "Prog / Art Rock",
    frozenset(["progressive rock", "symphonic metal"]): "Prog / Symphonic",
    frozenset(["progressive rock", "classic rock"]): "Prog / Classic Rock",
    frozenset(["progressive rock", "rock"]): "Prog Rock",
    frozenset(["death metal", "metal"]): "Death Metal",
    frozenset(["death metal", "progressive metal"]): "Progressive Death Metal",
    frozenset(["garage punk", "post-punk"]): "Garage Punk / Post-Punk",
    frozenset(["garage punk", "noise rock"]): "Garage Punk / Noise",
    frozenset(["chinese rock", "post-punk"]): "Chinese Rock / Post-Punk",
    frozenset(["chinese rock", "noise rock"]): "Chinese Rock / Noise",
    frozenset(["chinese indie", "post-punk"]): "Chinese Indie / Post-Punk",
    frozenset(["deutschrock", "rock"]): "Deutschrock",
    frozenset(["deutschrock", "german"]): "Deutschrock",
    frozenset(["soft rock", "pop rock"]): "Soft Rock / Pop",
    frozenset(["glam rock", "hard rock"]): "Glam Rock / Hard Rock",
    frozenset(["glam rock", "art rock"]): "Glam / Art Rock",
}


def normalize_tag(tag: str) -> str:
    return TAG_ALIASES.get(tag.lower().strip(), tag.lower().strip())


def get_topic_artist_weights(topic: dict, con: sqlite3.Connection) -> dict[str, float]:
    """For a topic's top tracks, look up each artist's lifetime hours in the DB.
    Return {artist: hours_weight} so we can weight tags by listening intensity."""
    weights = {}
    for tt in topic.get("top_tracks", []):
        artist = tt["artist"]
        # Sum hours across all tracks of this artist in the topic — use the
        # track hours from the topic summary, not the full DB
        weights[artist] = weights.get(artist, 0) + tt.get("hours", 0)
    return weights


def aggregate_tags(weights: dict[str, float], genres_cache: dict) -> tuple[list[tuple[str, int]], int]:
    """For each artist in weights, fetch their MusicBrainz tags and weight by listening hours.
    Returns ([(tag, weighted_count), ...], n_artists_with_tags).

    Manual overrides (curated by Marcus) get a 10x weight boost to ensure they
    dominate the topic fingerprint.
    """
    tag_counter = Counter()
    n_with = 0
    for artist, weight in weights.items():
        info = genres_cache.get(artist)
        if not info or not info.get("tags"):
            continue
        n_with += 1
        boost = 10.0 if info.get("override") else 1.0
        for tag, count in info["tags"]:
            ntag = normalize_tag(tag)
            tag_counter[ntag] += count * weight * boost
    return tag_counter.most_common(20), n_with


def synthesize_label(top_tags: list[tuple[str, float]], n_artists: int) -> tuple[str, str, str]:
    """Pick a concise human-readable label from the top tags.
    Returns (label, secondary_descriptor, axis).

    Strategy:
    - Drop generic tags (rock, pop, electronic) if more specific tags exist
    - Drop country/language tags (german, british, american) — they're not genres
    - Drop tags with very low weighted counts (< 5% of #1)
    - Take top 2 surviving tags, joined with " / "
    - Use known genre pairs for canonical labels
    """
    if not top_tags:
        return ("(no tags found)", "—", "unbekannt")

    GENERIC = GENERIC_TAGS
    SPECIFIC_BONUS = SPECIFIC_BONUS_MODULE
    label_pairs = LABEL_PAIRS_MODULE

    # Filter: drop generic AND low-weight
    max_count = top_tags[0][1]
    filtered = []
    for tag, count in top_tags:
        if tag in GENERIC:
            continue
        if count < max_count * 0.05:
            continue
        score = count + SPECIFIC_BONUS.get(tag, 0)
        filtered.append((tag, count, score))

    if not filtered:
        # All generic — fall back to first non-generic from the original list
        for tag, count in top_tags:
            if tag not in GENERIC:
                return tag.title(), None, "musikwissenschaftlich-aggregiert"
        # Truly nothing useful
        return top_tags[0][0].title(), None, "musikwissenschaftlich-aggregiert"

    # Sort by score, take top 2
    filtered.sort(key=lambda x: -x[2])
    top2 = [filtered[0][0]]
    if len(filtered) > 1 and filtered[1][2] >= filtered[0][2] * 0.5:
        top2.append(filtered[1][0])

    # Canonical labels
    label = label_pairs.get(frozenset(top2))
    if not label:
        # Use a / join with the first two tags
        label = " / ".join(t.title() for t in top2[:2])

    secondary = filtered[2][0] if len(filtered) > 2 else None
    return label, secondary, "musikwissenschaftlich-aggregiert"


def main():
    if not GENRES_FILE.exists():
        print(f"ERROR: {GENRES_FILE} not found. Run build_artist_genres.py first.")
        return
    if not TOPIC_FILE.exists():
        print(f"ERROR: {TOPIC_FILE} not found. Run topic_model.py first.")
        return

    genres_cache = json.loads(GENRES_FILE.read_text())
    # Apply manual overrides
    if OVERRIDES_FILE.exists():
        overrides = json.loads(OVERRIDES_FILE.read_text())
        # Strip the comment key
        overrides.pop("_comment", None)
        for artist, ov in overrides.items():
            if "note" in ov and "tags" not in ov and "mbid" not in ov:
                continue  # comment-only entry
            if artist in genres_cache:
                # Merge: override wins on key fields
                if ov.get("mbid") is not None:
                    genres_cache[artist]["mbid"] = ov["mbid"]
                if "tags" in ov:
                    genres_cache[artist]["tags"] = ov["tags"]
                genres_cache[artist]["override"] = ov.get("note", "")
            else:
                genres_cache[artist] = {
                    "mbid": ov.get("mbid"),
                    "tags": ov.get("tags", []),
                    "country": None,
                    "hours": 0,
                    "n_tracks": 0,
                    "override": ov.get("note", ""),
                }
        print(f"Applied {len(overrides)} artist-genre overrides")
    topic_data = json.loads(TOPIC_FILE.read_text())
    con = sqlite3.connect(EVENTS_DB)
    con.row_factory = sqlite3.Row

    # Curated overrides (Marcus-edited)
    overrides = {}
    if CURATED_OVERRIDES.exists():
        overrides = json.loads(CURATED_OVERRIDES.read_text())

    out_topics = []
    n_no_tags = 0
    for topic in topic_data["topics"]:
        weights = get_topic_artist_weights(topic, con)
        top_tags, n_with = aggregate_tags(weights, genres_cache)

        if not top_tags:
            n_no_tags += 1
            synthesized = ("(no MB tags — manual review needed)", "—", "unbekannt")
        else:
            synthesized = synthesize_label(top_tags, n_with)

        primary, secondary, axis = synthesized
        top_artist_obj = topic["top_tracks"][0] if topic["top_tracks"] else {"artist": "?", "track": "?"}

        # Build the topic record
        rec = {
            "id": topic["id"],
            "rank": None,  # filled in after sort
            "primary_genre": primary,
            "secondary_descriptor": secondary,
            "axis": axis,
            "hours": topic["total_hours"],
            "tracks": topic["size"],
            "peak_year": topic["peak_year"],
            "representative_track": f"{top_artist_obj['artist']} — {top_artist_obj['track']}",
            "mb_tag_fingerprint": [(t, round(c, 1)) for t, c in top_tags[:7]],
            "n_artists_with_tags": n_with,
            "n_artists_total": len(weights),
            "n_outliers": topic.get("n_outliers", 0),
        }

        # Apply Marcus override if present
        if str(topic["id"]) in overrides:
            ov = overrides[str(topic["id"])]
            rec["marcus_label"] = ov.get("label", primary)
            rec["marcus_notes"] = ov.get("notes", "")
            rec["marcus_curated"] = True
        else:
            rec["marcus_label"] = primary
            rec["marcus_notes"] = "(auto from MusicBrainz tags — edit marcus_spotify_topic_overrides.json to curate)"
            rec["marcus_curated"] = False

        out_topics.append(rec)

    # Rank by hours
    out_topics.sort(key=lambda r: -r["hours"])
    for i, t in enumerate(out_topics, 1):
        t["rank"] = i

    # JSON
    out = {
        "version": "v02",
        "method": "MusicBrainz user-contributed tags, weighted by lifetime hours",
        "topics": out_topics,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"Wrote {OUT_JSON}")

    # Markdown
    md = ["# Marcus's Spotify Topic Labels v02 (MusicBrainz-derived)\n"]
    md.append(f"**Source:** `{GENRES_FILE.name}` (MusicBrainz tags) + `{TOPIC_FILE.name}` (BERTopic).  ")
    md.append(f"**Method:** Top tracks per topic → MusicBrainz tag lookup → weighted aggregate → synthesized label.\n")
    md.append(f"**Coverage:** {len(out_topics) - n_no_tags}/{len(out_topics)} topics with MusicBrainz tags.\n")
    md.append("\n## Labeled Topics (ranked by total hours)\n")
    md.append("| # | Topic | MB-Label (synthesized) | Hours | Tracks | Peak | Top MB tags (weighted) |")
    md.append("|---|---|---|---:|---:|---:|---|")
    for t in out_topics:
        tags_str = ", ".join(f"{tag}({int(c)})" for tag, c in t["mb_tag_fingerprint"][:5])
        md.append(f"| {t['rank']} | {t['representative_track'][:50]} | **{t['marcus_label']}** | {t['hours']:.1f} | {t['tracks']} | {t['peak_year']} | {tags_str} |")

    md.append("\n## Marcus-Curated Topics\n")
    md.append("To override a label: edit `data/processed/marcus_spotify_topic_overrides.json`")
    md.append("with the topic `id` and your preferred `label` + `notes`.\n")
    md.append("```json")
    md.append('{')
    md.append('  "0": {"label": "My label for topic 0", "notes": "Why I disagree with MB"},')
    md.append('  "5": {"label": "Deutschrock + NDW", "notes": "Mixed cluster, both labels apply"}')
    md.append('}')
    md.append("```\n")

    md.append("\n## Reflection Questions\n")
    for t in out_topics:
        mb_summary = ", ".join(t["marcus_label"] for t in [t]) + " (MB: " + ", ".join(tag for tag, _ in t["mb_tag_fingerprint"][:3]) + ")"
        md.append(f"### {t['rank']}. {t['marcus_label']}  —  {t['representative_track'][:60]}")
        md.append(f"**Hours:** {t['hours']:.1f}  |  **Tracks:** {t['tracks']}  |  **Peak:** {t['peak_year']}  |  **Tags:** {', '.join(t for t,_ in t['mb_tag_fingerprint'][:5])}")
        md.append(f"\n**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?")
        md.append("")

    OUT_MD.write_text("\n".join(md))
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
