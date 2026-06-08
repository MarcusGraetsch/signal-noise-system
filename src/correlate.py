"""
correlate.py — Correlate Spotify listening hours with email-sent volume per month,
overlay known life-phase markers, write a markdown report + CSV + a text-based
bar chart for the time range where both data sources exist (2013-10 onward).

Inputs:
  - data/processed/spotify.db           (events table, monthly table)
  - ~/.hermes/data/marcus_email_corpus.db   (sent_emails table)
  - data/life_phases.json               (curated markers; checked in)

Outputs:
  - reports/correlation_report.md
  - data/processed/monthly_correlation.csv
  - data/processed/correlation_chart.txt  (ASCII bars for terminals)
  - data/processed/life_phases_overlay.csv
"""

from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPOTIFY_DB = ROOT / "data" / "processed" / "spotify.db"
EMAIL_DB = Path("/root/.hermes/data/marcus_email_corpus.db")
LIFE_PHASES = ROOT / "data" / "life_phases.json"
OUT_CSV = ROOT / "data" / "processed" / "monthly_correlation.csv"
OUT_REPORT = ROOT / "reports" / "correlation_report.md"
OUT_CHART = ROOT / "data" / "processed" / "correlation_chart.txt"
OUT_PHASES_CSV = ROOT / "data" / "processed" / "life_phases_overlay.csv"


def load_life_phases() -> list[dict]:
    if not LIFE_PHASES.exists():
        return []
    return json.loads(LIFE_PHASES.read_text())


def fetch_spotify_monthly(con: sqlite3.Connection) -> dict[str, dict]:
    """Returns {ym: {hours, plays, unique_artists, unique_tracks}}"""
    cur = con.cursor()
    cur.execute("""
        SELECT ym, year, month, hours, plays, unique_artists, unique_tracks
        FROM monthly
        ORDER BY year, month
    """)
    out = {}
    for ym, y, m, hours, plays, ua, ut in cur.fetchall():
        out[ym] = {"year": y, "month": m, "hours": hours, "plays": plays,
                   "unique_artists": ua, "unique_tracks": ut}
    return out


def fetch_email_monthly(con: sqlite3.Connection) -> dict[str, int]:
    cur = con.cursor()
    cur.execute("""
        SELECT substr(date,1,7) AS ym, COUNT(*)
        FROM sent_emails
        WHERE date LIKE '____-__-__%'
        GROUP BY ym
    """)
    return {ym: n for ym, n in cur.fetchall()}


def pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs)/n
    my = sum(ys)/n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    dx = sum((x-mx)**2 for x in xs) ** 0.5
    dy = sum((y-my)**2 for y in ys) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return num / (dx*dy)


def write_chart(merged: list[dict], out: Path) -> None:
    """Text-based chart of hours and email volume per month, side by side."""
    if not merged:
        out.write_text("(no data)\n")
        return
    # Determine scales
    max_h = max((r["hours"] or 0) for r in merged) or 1
    max_e = max((r["emails"] or 0) for r in merged) or 1
    width = 36
    lines = []
    lines.append(f"Spot listening hours vs. Sent emails per month  (2013-10 onward)")
    lines.append("Scale: hours 0..%.0f   emails 0..%d" % (max_h, max_e))
    lines.append("")
    header = f"{'month':<8} {'hrs':>5} {'listen':<{width}} {'mails':>5} {'emails':<{width}}"
    lines.append(header)
    lines.append("-" * len(header))
    for r in merged:
        h = r["hours"] or 0
        e = r["emails"] or 0
        hbar = "█" * int(round((h / max_h) * width))
        ebar = "▒" * int(round((e / max_e) * width))
        lines.append(f"{r['ym']:<8} {h:>5.1f} {hbar:<{width}} {e:>5d} {ebar:<{width}}")
    out.write_text("\n".join(lines) + "\n")


def write_phases_csv(phases: list[dict], out: Path) -> None:
    import csv
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["start", "end", "label", "category", "note"])
        w.writeheader()
        for p in phases:
            w.writerow({k: p.get(k, "") for k in w.fieldnames})


def write_correlation_csv(merged: list[dict], out: Path) -> None:
    import csv
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["ym", "year", "month",
                                            "hours", "plays",
                                            "unique_artists", "unique_tracks",
                                            "emails"])
        w.writeheader()
        for r in merged:
            w.writerow(r)


def main() -> int:
    sp = sqlite3.connect(str(SPOTIFY_DB))
    em = sqlite3.connect(str(EMAIL_DB))
    spotify_monthly = fetch_spotify_monthly(sp)
    email_monthly = fetch_email_monthly(em)
    phases = load_life_phases()
    sp.close(); em.close()

    # Overlap window: months present in BOTH datasets
    common_yms = sorted(set(spotify_monthly) & set(email_monthly))
    if not common_yms:
        print("No overlapping months between Spotify and email data.")
        return 1
    print(f"Overlap window: {common_yms[0]} -> {common_yms[-1]}  ({len(common_yms)} months)")

    merged = []
    for ym in common_yms:
        s = spotify_monthly[ym]
        e = email_monthly.get(ym, 0)
        merged.append({
            "ym": ym, "year": s["year"], "month": s["month"],
            "hours": s["hours"], "plays": s["plays"],
            "unique_artists": s["unique_artists"], "unique_tracks": s["unique_tracks"],
            "emails": e,
        })

    write_correlation_csv(merged, OUT_CSV)
    write_chart(merged, OUT_CHART)
    write_phases_csv(phases, OUT_PHASES_CSV)

    # Pearson correlation
    xs = [r["hours"] for r in merged]
    ys = [r["emails"] for r in merged]
    r = pearson(xs, ys)
    if r is not None:
        print(f"Pearson r (hours vs emails) over {len(common_yms)} months: r = {r:+.3f}")
    else:
        print("Pearson r not computable.")

    # Top 10 listening months
    top_listen = sorted(merged, key=lambda r: -r["hours"])[:10]
    top_email = sorted(merged, key=lambda r: -r["emails"])[:10]

    # Build report
    lines = []
    lines.append("# Signal//Noise — Correlation Report: Listening vs. Email Volume")
    lines.append("")
    lines.append(f"_Generated_: {datetime.utcnow().isoformat(timespec='seconds')}Z")
    lines.append("")
    lines.append("## Window")
    lines.append("")
    lines.append(f"- Overlap of Spotify listening and email-sent volume: **{common_yms[0]} → {common_yms[-1]}** ({len(common_yms)} months)")
    lines.append(f"- Spotify source: `data/processed/spotify.db` (events table, long format, ms_played >= 30s)")
    lines.append(f"- Email source:  `~/.hermes/data/marcus_email_corpus.db` (sent_emails, ISO-date filtered)")
    lines.append("")
    lines.append("## Pearson correlation")
    lines.append("")
    if r is not None:
        strength = "weak" if abs(r) < 0.3 else "moderate" if abs(r) < 0.6 else "strong"
        direction = "positive" if r > 0 else "negative"
        lines.append(f"r = **{r:+.3f}**  →  {strength} {direction} correlation between monthly listening hours and email-sent volume.")
        lines.append("")
        lines.append("Interpretation: " + (
            "Months with more emails sent also tend to have more listening hours. "
            "Plausible drivers: busier work periods correlate with both more correspondence and more background music. "
            if r > 0.3 else
            "Months with more emails sent tend to have less listening hours. "
            "Plausible drivers: high-correspondence periods are cognitively more demanding (calls, writing) and consume time otherwise spent listening. "
            if r < -0.3 else
            "Correlation is weak. Listening and email activity appear largely decoupled at the monthly level."
        ))
    else:
        lines.append("(could not be computed)")
    lines.append("")

    lines.append("## Top 10 listening months (hours)")
    lines.append("")
    lines.append("| ym | hours | plays | unique artists | emails |")
    lines.append("|---|---:|---:|---:|---:|")
    for r0 in top_listen:
        lines.append(f"| {r0['ym']} | {r0['hours']:.1f} | {r0['plays']:,} | {r0['unique_artists']:,} | {r0['emails']:,} |")
    lines.append("")

    lines.append("## Top 10 email-volume months")
    lines.append("")
    lines.append("| ym | emails | hours | plays |")
    lines.append("|---|---:|---:|---:|")
    for r0 in top_email:
        lines.append(f"| {r0['ym']} | {r0['emails']:,} | {r0['hours']:.1f} | {r0['plays']:,} |")
    lines.append("")

    # Notable transitions
    lines.append("## Notable year transitions")
    lines.append("")
    yearly = defaultdict(lambda: {"hours": 0.0, "plays": 0, "emails": 0, "months": 0})
    for r0 in merged:
        y = r0["year"]
        yearly[y]["hours"] += r0["hours"]
        yearly[y]["plays"]  += r0["plays"]
        yearly[y]["emails"] += r0["emails"]
        yearly[y]["months"] += 1
    lines.append("| year | months | hours | plays | emails | hrs/month | mails/month |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for y in sorted(yearly):
        d = yearly[y]
        m = max(d["months"], 1)
        lines.append(f"| {y} | {d['months']} | {d['hours']:.0f} | {d['plays']:,} | {d['emails']:,} | {d['hours']/m:.1f} | {d['emails']/m:.0f} |")
    lines.append("")

    # Life phase overlay
    if phases:
        lines.append("## Life-phase markers (curated)")
        lines.append("")
        lines.append("| start | end | category | label |")
        lines.append("|---|---|---|---|")
        for p in phases:
            lines.append(f"| {p.get('start','')} | {p.get('end','')} | {p.get('category','')} | {p.get('label','')} |")
        lines.append("")
        lines.append("Notes are in `data/life_phases.json`.")
        lines.append("")

    # Findings
    lines.append("## Findings (preliminary)")
    lines.append("")
    # Find biggest year-over-year changes
    years_sorted = sorted(yearly)
    biggest_hr_jump = None
    biggest_mail_jump = None
    for i in range(1, len(years_sorted)):
        y_prev, y_cur = years_sorted[i-1], years_sorted[i]
        d_h = yearly[y_cur]["hours"] - yearly[y_prev]["hours"]
        d_m = yearly[y_cur]["emails"] - yearly[y_prev]["emails"]
        if biggest_hr_jump is None or abs(d_h) > abs(biggest_hr_jump[2]):
            biggest_hr_jump = (y_prev, y_cur, d_h)
        if biggest_mail_jump is None or abs(d_m) > abs(biggest_mail_jump[2]):
            biggest_mail_jump = (y_prev, y_cur, d_m)
    if biggest_hr_jump:
        yp, yc, dh = biggest_hr_jump
        lines.append(f"- **Largest year-over-year listening jump**: {yp} → {yc}: {dh:+.0f} hours.")
    if biggest_mail_jump:
        yp, yc, dm = biggest_mail_jump
        lines.append(f"- **Largest year-over-year email-volume jump**: {yp} → {yc}: {dm:+,} sent.")
    lines.append("")

    # Cross-references
    lines.append("## How to read this")
    lines.append("")
    lines.append("- `data/processed/monthly_correlation.csv` — per-month hours, plays, unique counts, emails")
    lines.append("- `data/processed/correlation_chart.txt` — ASCII side-by-side bar chart")
    lines.append("- `data/processed/life_phases_overlay.csv` — curated life-phase markers")
    lines.append("- The chart file is intentionally terminal-friendly for quick inspection.")
    lines.append("")

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text("\n".join(lines))

    print(f"Wrote: {OUT_REPORT}")
    print(f"Wrote: {OUT_CSV}")
    print(f"Wrote: {OUT_CHART}")
    print(f"Wrote: {OUT_PHASES_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
