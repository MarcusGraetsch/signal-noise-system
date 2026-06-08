# Signal//Noise — Correlation Report: Listening vs. Email Volume

_Generated_: 2026-06-08T08:42:56Z

## Window

- Overlap of Spotify listening and email-sent volume: **2013-10 → 2026-04** (125 months)
- Spotify source: `data/processed/spotify.db` (events table, long format, ms_played >= 30s)
- Email source:  `~/.hermes/data/marcus_email_corpus.db` (sent_emails, ISO-date filtered)

## Pearson correlation

r = **+0.023**  →  weak positive correlation between monthly listening hours and email-sent volume.

Interpretation: Correlation is weak. Listening and email activity appear largely decoupled at the monthly level.

## Top 10 listening months (hours)

| ym | hours | plays | unique artists | emails |
|---|---:|---:|---:|---:|
| 2020-07 | 331.1 | 4,973 | 1,443 | 279 |
| 2020-06 | 308.1 | 4,717 | 1,425 | 251 |
| 2020-04 | 285.8 | 4,461 | 1,333 | 310 |
| 2019-12 | 262.7 | 4,303 | 840 | 194 |
| 2020-05 | 240.9 | 3,767 | 1,099 | 235 |
| 2021-07 | 238.9 | 3,615 | 875 | 224 |
| 2021-05 | 234.9 | 3,536 | 940 | 241 |
| 2020-09 | 188.4 | 2,809 | 898 | 323 |
| 2021-09 | 187.3 | 2,816 | 745 | 200 |
| 2020-08 | 185.8 | 2,718 | 1,038 | 289 |

## Top 10 email-volume months

| ym | emails | hours | plays |
|---|---:|---:|---:|
| 2025-11 | 1,120 | 71.2 | 1,180 |
| 2025-10 | 1,081 | 89.0 | 1,457 |
| 2026-01 | 987 | 53.5 | 965 |
| 2025-01 | 985 | 65.0 | 1,065 |
| 2023-11 | 981 | 69.9 | 1,112 |
| 2023-10 | 978 | 86.5 | 1,373 |
| 2025-12 | 976 | 94.7 | 1,522 |
| 2025-07 | 972 | 74.8 | 1,163 |
| 2019-06 | 955 | 79.3 | 1,243 |
| 2025-05 | 948 | 77.8 | 1,169 |

## Notable year transitions

| year | months | hours | plays | emails | hrs/month | mails/month |
|---|---:|---:|---:|---:|---:|---:|
| 2013 | 1 | 5 | 70 | 55 | 4.7 | 55 |
| 2015 | 7 | 30 | 471 | 845 | 4.3 | 121 |
| 2016 | 7 | 34 | 497 | 1,340 | 4.8 | 191 |
| 2017 | 12 | 264 | 4,492 | 3,204 | 22.0 | 267 |
| 2018 | 10 | 128 | 2,125 | 1,757 | 12.8 | 176 |
| 2019 | 12 | 1180 | 18,871 | 4,470 | 98.4 | 372 |
| 2020 | 12 | 2308 | 35,283 | 3,321 | 192.3 | 277 |
| 2021 | 12 | 1943 | 29,237 | 2,729 | 161.9 | 227 |
| 2022 | 12 | 1335 | 20,360 | 4,171 | 111.3 | 348 |
| 2023 | 12 | 969 | 15,243 | 9,544 | 80.7 | 795 |
| 2024 | 12 | 1058 | 17,103 | 9,530 | 88.2 | 794 |
| 2025 | 12 | 874 | 13,887 | 11,185 | 72.9 | 932 |
| 2026 | 4 | 296 | 5,109 | 3,447 | 74.0 | 862 |

## Life-phase markers (curated)

| start | end | category | label |
|---|---|---|---|
| 2013-10 | 2014-12 | platform | Erste Spotify-Nutzung; 2014 Gap in Extended Streaming (anderer Account/Reset) |
| 2015-11 | 2017-12 | relationship | Beziehung zu Traumfrau (Borderline) — erste Phase |
| 2018-01 | 2019-08 | work | Berlin TXL FUTR HUB (Urban Data Platform) |
| 2019-09 | 2021-12 | life | Corona-Periode + Homeoffice + Beziehungs-Krise/-Trennung Traumfrau |
| 2020-01 | 2021-12 | external | Pandemie / Lockdowns / Kontaktbeschränkungen |
| 2022-01 | 2023-12 | work | Job-Transition / HiSolutions-Vorbereitung |
| 2024-03 | 2026-04 | work | HiSolutions AG — Senior Consultant IT Management |
| 2012-11-20 | 2012-12-31 | platform | Gmail-Account eröffnet |

Notes are in `data/life_phases.json`.

## Findings (preliminary)

- **Largest year-over-year listening jump**: 2019 → 2020: +1127 hours.
- **Largest year-over-year email-volume jump**: 2025 → 2026: -7,738 sent.

## How to read this

- `data/processed/monthly_correlation.csv` — per-month hours, plays, unique counts, emails
- `data/processed/correlation_chart.txt` — ASCII side-by-side bar chart
- `data/processed/life_phases_overlay.csv` — curated life-phase markers
- The chart file is intentionally terminal-friendly for quick inspection.
