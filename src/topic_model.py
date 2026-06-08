"""
topic_model.py — BERTopic over Marcus's distinct Spotify tracks.

Pipeline:
  1. Top-N tracks by lifetime listening (ms_played >= 30s, kind=audio)
  2. Embed track strings "artist - track" with paraphrase-multilingual-MiniLM-L12-v2
  3. UMAP reduce (5-dim), HDBSCAN cluster
  4. c-TF-IDF topic representation
  5. Cross-tabulate topics with year (peak listening)
  6. Coach-readable topic descriptions + labels

Outputs:
  - data/processed/topic_embeddings.npy        (N, 384)
  - data/processed/topic_assignments.jsonl     (track_name, artist_name, topic_id, hour_share, peak_year)
  - data/processed/topic_summary.json          (topic_id, label, keywords, top_tracks, year_distribution)
  - data/processed/topic_summary.md            (human-readable report)
  - data/processed/topic_heatmap.txt           (ASCII topic × year heatmap)
"""

from __future__ import annotations

import json
import sqlite3
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("/root/repos/signal-noise-system")
SRC_DB = ROOT / "data" / "processed" / "spotify.db"
OUT = ROOT / "data" / "processed"
EMB_FILE = OUT / "topic_embeddings.npy"
ASSIGN_FILE = OUT / "topic_assignments.jsonl"
SUMMARY_FILE = OUT / "topic_summary.json"
MD_FILE = OUT / "topic_summary.md"
HEATMAP_FILE = OUT / "topic_heatmap.txt"

TOP_N_TRACKS = 2000
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
EMBED_DIM = 384

# UMAP + HDBSCAN tuned for short-text track titles (sparse, low semantic overlap)
UMAP_PARAMS = dict(n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine", random_state=42)
HDBSCAN_PARAMS = dict(min_cluster_size=20, min_samples=2, metric="euclidean",
                      cluster_selection_method="eom", prediction_data=True)
BERTOPIC_PARAMS = dict(top_n_words=8, nr_topics="auto", verbose=False,
                       calculate_probabilities=False)


def load_top_tracks() -> tuple[list[str], list[tuple[str, str]], np.ndarray]:
    """Return (embed_strings, (track, artist) tuples, total_ms array)."""
    con = sqlite3.connect(str(SRC_DB))
    con.row_factory = sqlite3.Row
    rows = con.execute("""
        SELECT track_name, artist_name, SUM(ms_played) AS total_ms
        FROM events
        WHERE kind='audio' AND ms_played >= 30000
          AND track_name IS NOT NULL AND artist_name IS NOT NULL
        GROUP BY track_name, artist_name
        ORDER BY total_ms DESC
        LIMIT ?
    """, (TOP_N_TRACKS,)).fetchall()
    con.close()
    strings = [f"{r['artist_name']} - {r['track_name']}" for r in rows]
    tuples = [(r["track_name"], r["artist_name"]) for r in rows]
    weights = np.array([r["total_ms"] for r in rows], dtype=np.float64)
    return strings, tuples, weights


def compute_or_load_embeddings(strings: list[str]) -> np.ndarray:
    if EMB_FILE.exists():
        arr = np.load(EMB_FILE)
        if arr.shape == (len(strings), EMBED_DIM):
            print(f"  loaded cached embeddings: {arr.shape}")
            return arr
    raise RuntimeError(
        f"  no cached embeddings at {EMB_FILE}. "
        f"Run `src/compute_track_embeddings.py` first."
    )


def run_bertopic(emb: np.ndarray, docs: list[str]) -> tuple["list[int]", "object"]:
    from bertopic import BERTopic
    from umap import UMAP
    from hdbscan import HDBSCAN
    from sklearn.feature_extraction.text import CountVectorizer

    umap = UMAP(**UMAP_PARAMS)
    hdbscan = HDBSCAN(**HDBSCAN_PARAMS)
    # Multilingual stop words union (English + German + French)
    try:
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        import nltk
        from nltk.corpus import stopwords
        nltk.download("stopwords", quiet=True)
        all_stops = set(ENGLISH_STOP_WORDS) | set(stopwords.words("german")) | set(stopwords.words("french"))
    except Exception:
        all_stops = None
    vectorizer = CountVectorizer(stop_words=list(all_stops) if all_stops else "english",
                                  ngram_range=(1, 2), min_df=3, max_df=0.7,
                                  token_pattern=r"(?u)\b[a-zA-ZäöüÄÖÜß]{4,}\b")

    topic_model = BERTopic(umap_model=umap, hdbscan_model=hdbscan, vectorizer_model=vectorizer,
                           **BERTOPIC_PARAMS)
    topics, probs = topic_model.fit_transform(docs, embeddings=emb)
    return topics, topic_model


def build_year_distribution(tuples: list[tuple[str, str]], topics: list[int]) -> dict:
    """For each topic, compute year-distribution weighted by total listening time."""
    con = sqlite3.connect(str(SRC_DB))
    con.row_factory = sqlite3.Row
    topic_year: dict[int, Counter] = defaultdict(Counter)
    topic_total_ms: dict[int, int] = defaultdict(int)

    for (track, artist), topic in zip(tuples, topics):
        if topic == -1:
            continue
        rows = con.execute("""
            SELECT strftime('%Y', ts) AS y, SUM(ms_played) AS ms
            FROM events
            WHERE kind='audio' AND ms_played >= 30000
              AND track_name=? AND artist_name=?
            GROUP BY y
        """, (track, artist)).fetchall()
        for r in rows:
            y = int(r["y"])
            topic_year[topic][y] += r["ms"]
            topic_total_ms[topic] += r["ms"]
    con.close()
    return {t: dict(years) for t, years in topic_year.items()}


def main():
    print("=== Step 1: Loading top tracks ===")
    strings, tuples, weights = load_top_tracks()
    print(f"  loaded {len(strings)} tracks covering {weights.sum()/3.6e6:.0f}h")

    print("=== Step 2: Computing embeddings ===")
    emb = compute_or_load_embeddings(strings)

    print("=== Step 3: Running BERTopic ===")
    t0 = time.time()
    topics, model = run_bertopic(emb, strings)
    n_total = len(topics)
    n_outliers = sum(1 for t in topics if t == -1)
    n_topics = len(set(topics) - {-1})
    print(f"  BERTopic: {n_topics} topics, {n_outliers}/{n_total} outliers ({100*n_outliers/n_total:.1f}%) in {time.time()-t0:.1f}s")

    # Reduce topics that are very similar (optional, we use 'auto' nr_topics)
    try:
        topics = model.transform(emb)[0]
    except Exception:
        pass

    print("=== Step 4: Building year distributions ===")
    year_dist = build_year_distribution(tuples, topics)

    # Build topic info table
    topic_info = model.get_topic_info()
    print(f"  {len(topic_info)} topic rows from model")

    # Aggregate stats per topic
    print("=== Step 5: Writing summary ===")
    topic_summary = {"n_tracks": len(strings), "n_outliers": n_outliers,
                     "n_topics": n_topics, "topics": []}

    for _, row in topic_info.iterrows():
        tid = int(row["Topic"])
        if tid == -1:
            continue
        words = model.get_topic(tid) or []
        kw_list = [w for w, _ in words[:10]]
        # Top tracks in this topic by weight
        idxs = [i for i, t in enumerate(topics) if t == tid]
        idxs_sorted = sorted(idxs, key=lambda i: -weights[i])[:10]
        top_tracks = [{"track": tuples[i][0], "artist": tuples[i][1], "hours": round(weights[i]/3.6e6, 1)}
                       for i in idxs_sorted]
        ydist = year_dist.get(tid, {})
        peak_year = max(ydist, key=ydist.get) if ydist else None
        total_ms = sum(ydist.values())
        topic_summary["topics"].append({
            "id": tid,
            "size": int(row["Count"]),
            "keywords": kw_list,
            "top_tracks": top_tracks,
            "total_hours": round(total_ms/3.6e6, 1),
            "peak_year": peak_year,
            "year_distribution": {str(y): round(ms/3.6e6, 1) for y, ms in sorted(ydist.items())},
        })

    topic_summary["topics"].sort(key=lambda t: -t["total_hours"])

    SUMMARY_FILE.write_text(json.dumps(topic_summary, indent=2, ensure_ascii=False))
    print(f"  wrote {SUMMARY_FILE}")

    # Per-track assignment file
    with ASSIGN_FILE.open("w") as f:
        for (track, artist), topic, w in zip(tuples, topics, weights):
            f.write(json.dumps({
                "track": track, "artist": artist, "topic": int(topic),
                "hours": round(float(w)/3.6e6, 2)
            }, ensure_ascii=False) + "\n")
    print(f"  wrote {ASSIGN_FILE}")

    # Markdown report
    write_markdown(topic_summary, MD_FILE)
    print(f"  wrote {MD_FILE}")

    # Heatmap
    write_heatmap(topic_summary, HEATMAP_FILE)
    print(f"  wrote {HEATMAP_FILE}")


def write_markdown(summary: dict, path: Path):
    md = []
    md.append("# Spotify Track-Topic Model\n")
    md.append(f"**Corpus:** top {summary['n_tracks']} tracks by lifetime listening  ")
    md.append(f"**Topics:** {summary['n_topics']} + outliers  ")
    md.append(f"**Outliers:** {summary['n_outliers']} tracks ({100*summary['n_outliers']/summary['n_tracks']:.1f}%)  ")
    md.append(f"**Embedder:** `paraphrase-multilingual-MiniLM-L12-v2` (384-dim, normalized)  ")
    md.append(f"**Reducer:** UMAP(n_neighbors=15, n_components=5, cosine)  ")
    md.append(f"**Clusterer:** HDBSCAN(min_cluster=15, min_samples=2, eom)  \n")

    md.append("## Topic Index (ranked by total hours)\n")
    md.append("| # | Topic ID | Hours | Tracks | Peak year | Representative track | Top keywords |")
    md.append("|---|---|---:|---:|---:|---|---|")
    for i, t in enumerate(summary["topics"], 1):
        kw = ", ".join(t["keywords"][:5])
        rep = t["top_tracks"][0]["artist"] + " — " + t["top_tracks"][0]["track"] if t["top_tracks"] else "—"
        if len(rep) > 50: rep = rep[:47] + "..."
        md.append(f"| {i} | {t['id']} | {t['total_hours']:g} | {t['size']} | {t['peak_year']} | {rep} | {kw} |")

    md.append("\n## Per-Topic Detail\n")
    for i, t in enumerate(summary["topics"], 1):
        md.append(f"### {i}. Topic {t['id']} — {t['total_hours']:g}h, {t['size']} tracks, peak {t['peak_year']}\n")
        md.append(f"**Keywords:** {', '.join('`' + k + '`' for k in t['keywords'])}\n")
        md.append("**Top tracks:**")
        for tt in t["top_tracks"][:7]:
            md.append(f"  - {tt['artist']} — {tt['track']} ({tt['hours']}h)")
        if t["year_distribution"]:
            md.append("\n**Year distribution (h):**")
            md.append("```")
            years = sorted(t["year_distribution"].keys())
            bars = "".join(["█" * int(min(t["year_distribution"][y] * 2, 30)) or "·" for y in years])
            md.append(" ".join(years))
            md.append(" ".join([f"{t['year_distribution'][y]:>4.1f}" for y in years]))
            md.append(" " + bars)
            md.append("```")
        md.append("")
    path.write_text("\n".join(md))


def write_heatmap(summary: dict, path: Path):
    all_years = sorted({y for t in summary["topics"] for y in t["year_distribution"]})
    if not all_years:
        path.write_text("(no topics)")
        return
    lines = ["Topic × Year heatmap (hours, scaled to terminal width)"]
    lines.append("=" * 80)
    header = "  Topic │ Hours │ Tracks │ " + " ".join([y[-2:] for y in all_years])
    lines.append(header)
    lines.append("-" * len(header))
    for t in summary["topics"][:30]:  # top 30 topics
        yvals = [t["year_distribution"].get(y, 0) for y in all_years]
        peak = max(yvals) if yvals else 1
        bar_width = 40 // max(1, len(all_years))
        bars = "".join("█" * int((v/peak) * bar_width) if v > 0 else "·" * bar_width
                        for v in yvals)
        # Use representative track for label
        if t["top_tracks"]:
            label = t["top_tracks"][0]["artist"].split(",")[0][:14]
        else:
            label = f"topic{t['id']}"
        if len(label) > 14:
            label = label[:14]
        lines.append(f"  {label:>14} │ {t['total_hours']:>5.0f} │ {t['size']:>5}  │ {bars}  ({t['peak_year']})")
    lines.append("-" * len(header))
    lines.append("Legend:  █ = relative hours per year, · = none,  peak year in parens")
    path.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
