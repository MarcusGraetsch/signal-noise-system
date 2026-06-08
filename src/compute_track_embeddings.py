"""
compute_track_embeddings.py — Direct transformers-based embedding of top-N tracks.

Bypasses sentence-transformers (which loads torch + tqdm wrapper) and goes
straight to transformers + mean pooling. We embed "artist - track" strings
using paraphrase-multilingual-MiniLM-L12-v2 (384-dim) and save to .npy.

Usage:
  /usr/bin/python3 src/compute_track_embeddings.py
"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path("/root/repos/signal-noise-system")
SRC_DB = ROOT / "data" / "processed" / "spotify.db"
OUT = ROOT / "data" / "processed" / "topic_embeddings.npy"
TOP_N = 2000
MODEL_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CACHE = "/root/.cache/huggingface"
MAX_LEN = 64
BATCH = 64


def main():
    # Force offline — we already have the model
    import os
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    print("Loading top tracks...", flush=True)
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
    """, (TOP_N,)).fetchall()
    con.close()
    strings = [f"{r['artist_name']} - {r['track_name']}" for r in rows]
    print(f"  {len(strings)} tracks", flush=True)

    print("Loading tokenizer + model...", flush=True)
    t0 = time.time()
    from transformers import AutoTokenizer, AutoModel
    tok = AutoTokenizer.from_pretrained(MODEL_ID, cache_dir=CACHE)
    model = AutoModel.from_pretrained(MODEL_ID, cache_dir=CACHE)
    model.eval()
    print(f"  loaded in {time.time()-t0:.1f}s", flush=True)

    print("Encoding...", flush=True)
    t0 = time.time()
    all_emb = []
    with torch.no_grad():
        for i in range(0, len(strings), BATCH):
            batch = strings[i:i+BATCH]
            enc = tok(batch, padding=True, truncation=True, max_length=MAX_LEN, return_tensors="pt")
            out = model(**enc)
            # Mean-pool over attention-mask
            mask = enc["attention_mask"].unsqueeze(-1).float()
            summed = (out.last_hidden_state * mask).sum(dim=1)
            counts = mask.sum(dim=1).clamp(min=1e-9)
            emb = summed / counts
            emb = F.normalize(emb, p=2, dim=1)
            all_emb.append(emb.cpu().numpy())
            if (i // BATCH) % 5 == 0:
                print(f"  {i+len(batch)}/{len(strings)} in {time.time()-t0:.1f}s", flush=True)
    emb = np.concatenate(all_emb, axis=0)
    print(f"  encoded {emb.shape} in {time.time()-t0:.1f}s", flush=True)

    np.save(OUT, emb)
    print(f"Saved to {OUT} ({OUT.stat().st_size/1024/1024:.1f} MB)", flush=True)


if __name__ == "__main__":
    main()
