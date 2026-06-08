"""
label_topics.py — Generate marcus_topic_labels for the Spotify topics.

Reads topic_summary.json + the events DB, then writes:
  data/processed/marcus_spotify_topic_labels_v01.json (machine-readable)
  data/processed/marcus_spotify_topic_labels_v01.md   (human-readable)

Labels are rule-based but documented, so Marcus can edit and re-run.
The goal is to give each topic a Marcus-readable name, a life-phase anchor,
and reflection questions.
"""

from __future__ import annotations

import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/root/repos/signal-noise-system")
SRC_DB = ROOT / "data" / "processed" / "spotify.db"
SUMMARY = ROOT / "data" / "processed" / "topic_summary.json"
OUT_JSON = ROOT / "data" / "processed" / "marcus_spotify_topic_labels_v01.json"
OUT_MD = ROOT / "data" / "processed" / "marcus_spotify_topic_labels_v01.md"


# Heuristic rule-based labeling. Each rule scores a topic by checking artists
# and keywords; the best score wins. Marcus can override these.

# We tag topics with: marcus_label, suggested_label, life_phase, interpretation_axis

# (Artist substring, weight) — artists are positive signals for the rule
ARTIST_RULES: list[tuple[set[str], dict]] = [
    ({"NEU!", "Cluster", "Can", "Kraftwerk", "Faust", "Tangerine Dream", "Ash Ra Tempel", "Popol Vuh",
      "Amon Düül", "Embryo", "Amon Düül II", "La Düsseldorf", "Roedelius", "Michael Rother"},
     {"marcus_label": "Krautrock / Düsseldorf", "axis": "deutsch-experimentell",
      "life_phase": "TXL-Phase (2017-2018), Pandemie-Ausweitung (2020)",
      "notes": "NEU! dominiert. Hallogallo als 20h-Single definiert das Topic."}),
    ({"Ton Steine Scherben", "Slime", "Häppchen", "Normahl", "Wutanfall", "Biermann",
      "Marius Müller-Westernhagen", "Lilienthal"},
     {"marcus_label": "Deutsch-Punk / Polit-Punk (BRD)", "axis": "politisch-kulturell",
      "life_phase": "Aktiv ab 2018 (TXL + Pandemie)",
      "notes": "Ton Steine Scherben ist dein heimlicher Bezugspunkt. Fehlfarben kommt separat."}),
    ({"AC/DC", "Motörhead", "Judas Priest", "Iron Maiden", "Saxon", "Def Leppard",
      "Accept", "Scorpions", "Udo", "Warlock", "Running Wild", "Tank", "Girlschool",
      "Michael Schenker", "Mötley Crüe", "Whitesnake", "Bon Jovi", "Winger",
      "Cinderella", "Ratt", "Helloween"},
     {"marcus_label": "Heavy Metal / Hard Rock", "axis": "handwerklich-klassisch",
      "life_phase": "Konsistent seit 2013, Peak 2021",
      "notes": "AC/DC ist mit Abstand Spitze (212h). Konservativ-hören."}),
    ({"David Bowie", "Roxy Music", "Brian Eno", "T. Rex", "Iggy Pop", "Talking Heads",
      "Lou Reed", "Velvet Underground", "New York Dolls"},
     {"marcus_label": "Glam / Art Rock", "axis": "künstlerisch-experimentell",
      "life_phase": "Dauerhaft seit 2013",
      "notes": "Bowie 154h, der Cluster ist sehr breit."}),
    ({"Rolling Stones", "Chuck Berry", "Bo Diddley", "Little Richard", "Eddie Cochran",
      "Gene Vincent", "Jerry Lee Lewis", "Elvis", "Elvis Presley", "Buddy Holly"},
     {"marcus_label": "Rock'n'Roll-Ursprung", "axis": "historisch-klassisch",
      "life_phase": "Dauerhaft, Peak 2020",
      "notes": "Rolling Stones 148h, sehr altbackener Bezug."}),
    ({"Tom Petty", "Bruce Springsteen", "Bob Seger", "John Mellencamp", "Bob Dylan",
      "Southside Johnny", "Little Steven", "Gary U.S. Bonds"},
     {"marcus_label": "American Heartland Rock", "axis": "erzählerisch-bürgerlich",
      "life_phase": "Dauerhaft, Peak 2020 (Tom Petty 107h, Springsteen 50h)",
      "notes": "Storytelling-Rock. Tom Petty dominiert."}),
    ({"ZZ Top", "Stevie Ray Vaughan", "Lynyrd Skynyrd", "Allman Brothers", "Molly Hatchet",
      "38 Special", "Atlanta Rhythm Section", "The Outlaws", "Derek & The Dominos"},
     {"marcus_label": "Southern Rock / Texas Blues", "axis": "regional-klassisch",
      "life_phase": "Peak 2019-2020 (ZZ Top 160h)",
      "notes": "ZZ Top 160h, 2019 ist dein Southern-Rock-Jahr."}),
    ({"Smashing Pumpkins", "Soundgarden", "Alice in Chains", "Stone Temple Pilots",
      "Pearl Jam", "Mudhoney", "Screaming Trees", "Blind Melon", "Mother Love Bone"},
     {"marcus_label": "Grunge 90s", "axis": "jugendlich-nostalgisch",
      "life_phase": "Dauerhaft seit 2013, Smashing Pumpkins 113h",
      "notes": "Sehr 90er, sehr Kurt-Cobain."}),
    ({"Death", "Screaming Females", "Lightning Bolt", "Osees", "Thee Oh Sees",
      "Parquet Courts", "Ty Segall", "Oh Sees", "Deerhoof", "Thee Oh Sees"},
     {"marcus_label": "Underground / Proto-Punk / No-Wave", "axis": "aktuell-experimentell",
      "life_phase": "Stark 2020-2021",
      "notes": "Death (Proto-Punk aus Detroit, 70er) ist dein Liebling."}),
    ({"Bowie", "Eno", "Depeche Mode", "Cabaret Voltaire", "Yello",
      "DAF", "Einstürzende Neubauten", "Nitzer Ebb", "Portion Control"},
     {"marcus_label": "Elektronisch / Wave / Industrial", "axis": "urban-kühl",
      "life_phase": "Dauerhaft, Depeche Mode 75h",
      "notes": "Du hörst das nicht so viel wie erwartet — das ist mehr Beimischung."}),
    ({"Nirvana", "Foo Fighters", "Hüsker Dü", "Replacements", "The Fall",
      "Meat Puppets", "Minutemen", "R.E.M.", "Violent Femmes"},
     {"marcus_label": "Indie / Post-Punk / College Rock 80s", "axis": "kritisch-1980s",
      "life_phase": "Aktiv ab 2018",
      "notes": "The Fall taucht immer wieder auf — typisch britisch. R.E.M. ist post-R.E.M.-US-Indie."}),
    ({"Westernhagen", "Lindenberg", "Grönemeyer", "Wolf Maahn", "Hoffmann & Hoffmann",
      "Achim Reichel"},
     {"marcus_label": "Deutschrock (Mainstream)", "axis": "biographisch",
      "life_phase": "Westernhagen 77h, aktiv 2017-2021",
      "notes": "Westernhagen ist dein Deutschrock-Bezug — Kindheit/Jugend der 80er."}),
    ({"Midnight Oil", "INXS", "Men at Work", "Hunters & Collectors", "Icehouse",
      "Crowded House", "The Church", "Australian"},
     {"marcus_label": "Australian Rock", "axis": "regional-spezifisch",
      "life_phase": "Midnight Oil 103h, aktiv 2017-2021",
      "notes": "Midnight Oil 103h — überraschend viel. Klimakatastrophe-Bezug?"}),
    ({"Fu Manchu", "Queens of the Stone Age", "Kyuss", "Monster Magnet", "Masters of Reality",
      "Clutch", "Helmet", "Prong", "Sleep", "Electric Wizard"},
     {"marcus_label": "Stoner / Desert Rock", "axis": "saturiert-hypnotisch",
      "life_phase": "Peak 2019-2020 (Monster Magnet 91h)",
      "notes": "Monster Magnet 91h, Fu Manchu 7.5h. Sub-cluster innerhalb Southern Rock."}),
    ({"Carsick Cars", "White+", "P.K.14", "Hang on the Box", "The Peep Tempel",
      "Birdstriking", "PK14", "Snapline"},
     {"marcus_label": "Chinesischer Indie / Beijing-Szene", "axis": "exotisch-politisch",
      "life_phase": "Aktiv 2018-2020, Peep Tempel 8.6h, Carsick Cars 9.3h",
      "notes": "Überraschender Cluster. Marcus hat einen China-Punk-Bezug."}),
    ({"R.L. Burnside", "Junior Kimbrough", "Mississippi Fred McDowell", "John Lee Hooker",
      "Rory Gallagher", "Muddy Waters", "Howlin' Wolf", "Bukka White", "Asie Payton"},
     {"marcus_label": "Mississippi Blues / North Mississippi Hill Country",
      "axis": "regional-traditionell",
      "life_phase": "Peak 2023, R.L. Burnside 41h",
      "notes": "Rezent-Entdeckung! R.L. Burnside taucht 2023-2025 stark auf."}),
    ({"Slits", "Raincoats", "Au Pairs", "Essential Logic", "X-Ray Spex", "The Raincoats",
      "Delta 5", "Liliput"},
     {"marcus_label": "Post-Punk / Frauen-Bands (Punk-Adjacent)", "axis": "feministisch-1980",
      "life_phase": "Peak 2025, The Slits 47h",
      "notes": "Späte Entdeckung — Feministischer Post-Punk."}),
    ({"Fleetwood Mac", "Stevie Nicks", "Eagles", "Jackson Browne", "Linda Ronstadt",
      "Warren Zevon", "Crosby, Stills, Nash & Young", "Crosby"},
     {"marcus_label": "Westcoast / 70s Soft Rock", "axis": "konservativ-erwachsen",
      "life_phase": "Dauerhaft, Fleetwood Mac 30h",
      "notes": "Beige. Eagles 50h. Hörst du mehr als du vielleicht willst."}),
    ({"Voluptuous Horror of Karen Black", "Karen Black", "Kembra Pfahler", "Psychic TV",
      "Throbbing Gristle", "Cabaret Voltaire", "Coil", "Nurse With Wound", "Current 93"},
     {"marcus_label": "No-Wave / NYC / Industrial Underground", "axis": "avantgardistisch",
      "life_phase": "Voluptuous Horror 143h (Themen-Track, single heavy)",
      "notes": "Sehr Nischen, einprägsamer Cluster."}),
    ({"Viagra Boys", "Shame", "Dry Cleaning", "Black Country, New Road", "Squid",
      "Bdrmm", "Wunderhorse", "Fontaines D.C.", "Idles"},
     {"marcus_label": "UK/IE Post-Brexit Indie", "axis": "aktuell-szene",
      "life_phase": "Viagra Boys 65h, ab 2020",
      "notes": "Zeitgenössischer UK/IE-Indie."}),
    ({"Dire Straits", "Mark Knopfler", "Eric Clapton", "Ry Cooder", "B.B. King",
      "Stevie Ray Vaughan", "Chet Atkins"},
     {"marcus_label": "Blues-Rock / Gitarrenhandwerk", "axis": "handwerklich-solitär",
      "life_phase": "Dauerhaft",
      "notes": "Mark Knopfler-Fingerstyle-Verehrung."}),
    ({"Aerosmith", "Whitesnake", "Bon Jovi", "Def Leppard", "Winger",
      "Cinderella", "Ratt", "Twisted Sister", "Poison", "Warrant"},
     {"marcus_label": "Hair Metal / 80s Stadium Rock", "axis": "nostalgisch-theatralisch",
      "life_phase": "Peak 2023, Aerosmith 59h",
      "notes": "Wiederkehr 2023 — Jugenderinnerung."}),
    ({"Fehlfarben", "Palais Schaumburg", "Die Tödliche Doris", "Malaria!", "Nena",
      "Ideal", "Andreas Dorau", "DÖF", "Münchner Freiheit"},
     {"marcus_label": "Neue Deutsche Welle / NDW", "axis": "urban-1980",
      "life_phase": "Fehlfarben 50h, 2020 + 2024 Wiederkehr",
      "notes": "Fehlfarben 'Monarchie & Alltag' — typische Wiederkehr nach Pause."}),
    ({"Dr. Feelgood", "Eddie and the Hot Rods", "Eddie & the Hot Rods", "The Stranglers",
      "999", "The Undertones", "Stiff Little Fingers", "The Boys", "The Vibrators",
      "The Damned", "Eddie Cochran", "Ian Dury"},
     {"marcus_label": "Pub Rock / Punk-Vorläufer (UK 1976-78)", "axis": "kompakt-vorwärts",
      "life_phase": "Dauerhaft, Peak 2020",
      "notes": "Dr. Feelgood ist dein Pub-Rock-Einstieg. Verwandtschaft mit The Stranglers."}),
    ({"Flamin' Groovies", "The Dictators", "Cheap Trick", "The Real Kids", "The Nerves",
      "20/20", "Plimsouls", "The Shoes", "The Quick"},
     {"marcus_label": "Power Pop / 70s Punk Pop", "axis": "vergnügt-schneidend",
      "life_phase": "Flamin' Groovies 142h, Peak 2020",
      "notes": "Flamin' Groovies ist dein Power-Pop-Fixpunkt. Cheap Trick auch."}),
    ({"The Moody Blues", "Alan Parsons Project", "The Alan Parsons Project", "Pink Floyd",
      "Yes", "Genesis", "King Crimson", "Emerson, Lake & Palmer", "Camel",
      "Caravan", "Pavlov's Dog", "Strawbs", "Procol Harum"},
     {"marcus_label": "Prog / Classic Rock UK", "axis": "konservativ-erwachsen-1970",
      "life_phase": "Alan Parsons 79h, Peak 2020",
      "notes": "Prog-Klassiker. Wohl handwerkliche Wertschätzung."}),
    ({"Neil Young", "Crazy Horse", "Crosby, Stills, Nash & Young", "Buffalo Springfield",
      "Patti Smith", "Television", "The Replacements", "The Band"},
     {"marcus_label": "Americana / Singer-Songwriter Rock", "axis": "erzählerisch-nordamerikanisch",
      "life_phase": "Neil Young 215h, Peak 2020 (Pandemie-Hauptcluster)",
      "notes": "Sehr großer Cluster in 2020 — vermutlich der Pandemie-Hauptanker."}),
    ({"Clash", "The Clash", "Sex Pistols", "Ramones", "Buzzcocks", "Wire",
      "Sham 69", "Generation X", "Dead Kennedys", "Bad Brains"},
     {"marcus_label": "Punk (UK/US 1976-1982)", "axis": "aggressiv-urban",
      "life_phase": "The Clash 37h, Dauerhaft",
      "notes": "Klassischer Punk. Nicht so dominant wie erwartet."}),
    ({"Steppenwolf", "The Who", "The Kinks", "Thin Lizzy", "Humble Pie", "Free", "Bad Company",
      "Faces", "The Stooges", "MC5", "The Sonics", "13th Floor Elevators"},
     {"marcus_label": "Proto-Punk / 60s-70s Garage / Hard-Rock-Vorläufer",
      "axis": "historisch-proto",
      "life_phase": "Steppenwolf 27h, Peak 2020",
      "notes": "Steppenwolf 'Magic Carpet Ride' — die Wiege des Heavy Metal."}),
    ({"Steppenwolf", "Men Without Hats", "Oingo Boingo", "Devo", "DEVO", "XTC",
      "The B-52's", "Talking Heads", "B-52s", "Elvis Costello", "Squeeze", "Joe Jackson"},
     {"marcus_label": "New Wave / Synth-Pop 80s", "axis": "urban-tanzbar",
      "life_phase": "Devo/XTC dominant, Dauerhaft",
      "notes": "Hinweis: Überschneidung mit Post-Punk / Art Rock. Trennen ist schwer."}),
    ({"Phil Collins", "Genesis", "Peter Gabriel", "Sting", "The Police", "Roxette",
      "Tears for Fears", "Duran Duran", "Simple Minds", "a-ha", "OMD"},
     {"marcus_label": "80s Mainstream Pop-Rock (UK)", "axis": "mainstream-1980",
      "life_phase": "Phil Collins 51h, Peak 2022",
      "notes": "Mainstream-Pop der 80er. Nicht unbedingt peinlich."}),
    ({"Supertramp", "Kansas", "Styx", "Journey", "Foreigner", "Toto", "REO Speedwagon",
      "Boston", "Styx", "Asia", "Yes", "Electric Light Orchestra", "ELO"},
     {"marcus_label": "AOR / Stadion-Rock 70s-80s", "axis": "konservativ-erwachsen",
      "life_phase": "Supertramp 45h, Peak 2021",
      "notes": "AOR — Adult Oriented Rock. Der weiche Bühnenrock."}),
    ({"Keith Richards", "Mick Jagger", "Ron Wood", "Bill Wyman", "Charlie Watts",
      "The New Barbarians", "Willy DeVille"},
     {"marcus_label": "Rolling Stones Solo / Side Projects", "axis": "verwandt-klassisch",
      "life_phase": "Keith Richards 40h, Peak 2021",
      "notes": "Solo-Ausflüge der Stones-Mitglieder."}),
    ({"Billy Idol", "Generation X", "The Professionals", "Sigue Sigue Sputnik", "Adam Ant",
      "Gary Numan", "Tubeway Army", "Visage", "Ultravox"},
     {"marcus_label": "New Wave / 80s Pop (Billy Idol-Kosmos)", "axis": "urban-tanzbar",
      "life_phase": "Billy Idol 84h, Peak 2021",
      "notes": "Billy Idol als Fixpunkt, plus 80s New Wave."}),
    ({"Bob Marley", "Bob Marley & The Wailers", "Peter Tosh", "Jimmy Cliff", "Burning Spear",
      "Steel Pulse", "UB40", "Toots & The Maytals", "Inner Circle", "Third World"},
     {"marcus_label": "Reggae / Ska", "axis": "global-karibisch",
      "life_phase": "Bob Marley 55h, Peak 2020",
      "notes": "Bob Marley ist dein Reggae-Einstieg."}),
    ({"Queen", "Freddie Mercury", "David Bowie", "Roger Taylor", "Brian May"},
     {"marcus_label": "Queen & Soli", "axis": "theatralisch-klassisch",
      "life_phase": "Queen 40h, Peak 2020",
      "notes": "Queen — mit Abstand meist gehört in 2020."}),
    ({"Deep Purple", "Rainbow", "Whitesnake", "Uriah Heep", "Rush", "Black Sabbath",
      "Led Zeppelin", "Cream", "Blue Cheer"},
     {"marcus_label": "Hard Rock / Heavy Rock (UK 70s)", "axis": "handwerklich-klassisch",
      "life_phase": "Deep Purple 50h, Peak 2020",
      "notes": "Britischer Hard Rock. Deep Purple als Fixpunkt."}),
    ({"Tina Turner", "Ike Turner", "Prince", "Chaka Khan", "Rick James", "Parliament",
      "Sly & The Family Stone", "The Isley Brothers"},
     {"marcus_label": "Soul / Funk / R&B", "axis": "schwarz-amerikanisch",
      "life_phase": "Tina Turner 38h, Peak 2020",
      "notes": "Tina Turner als Brücke zwischen Soul, Funk, Pop."}),
    ({"ZZ Top", "Tom Petty", "Fleetwood Mac", "Eagles", "The Doobie Brothers", "Lynyrd Skynyrd",
      "Atlanta Rhythm Section"},
     {"marcus_label": "Americana Mainstream (overlap-Korrektur)", "axis": "erzählerisch-erwachsen",
      "life_phase": "Catchall für 70s Westcoast-Sounds",
      "notes": "Wird vermutlich mit Americana Heartland überlappen. Niedrigerer Score."}),
    ({"Cars", "Cheap Trick", "The Knack", "Blondie", "Ramones", "The Undertones",
      "The Rezillos", "The Go-Go's", "The Bangles"},
     {"marcus_label": "Power Pop / New Wave Hits (catchall)", "axis": "vergnügt-schneidend",
      "life_phase": "Dauerhaft",
      "notes": "Catchall für Power-Pop-Hits."}),
]


def label_topic(topic: dict, con: sqlite3.Connection) -> dict:
    """Assign rule-based labels. Returns dict to merge into topic summary."""
    artists_in_topic = []
    for tt in topic.get("top_tracks", []):
        artists_in_topic.append(tt["artist"])
    artists_blob = " | ".join(artists_in_topic)

    # Some rules are "corrections" for noisy top-level rules and should be
    # preferred ONLY if the top track is a strong match.
    CORRECTION_RULES = {
        "Pub Rock / Punk-Vorläufer (UK 1976-78)",
        "Power Pop / 70s Punk Pop",
        "Prog / Classic Rock UK",
        "Americana / Singer-Songwriter Rock",
        "Punk (UK/US 1976-1982)",
        "Proto-Punk / 60s-70s Garage / Hard-Rock-Vorläufer",
        "New Wave / Synth-Pop 80s",
        "80s Mainstream Pop-Rock (UK)",
        "AOR / Stadion-Rock 70s-80s",
        "Rolling Stones Solo / Side Projects",
        "New Wave / 80s Pop (Billy Idol-Kosmos)",
        "Reggae / Ska",
        "Queen & Soli",
        "Hard Rock / Heavy Rock (UK 70s)",
        "Soul / Funk / R&B",
        "No-Wave / NYC / Industrial Underground",
        "Americana Mainstream (overlap-Korrektur)",
        "Power Pop / New Wave Hits (catchall)",
    }

    # Score each rule with a **weight** per artist. Avoid substring blow-up.
    # Use exact (case-insensitive) match against the rule's artist names.
    best_rule = None
    best_score = 0.0
    matched = []
    for art_set, payload in ARTIST_RULES:
        # For each rule artist, count how many topic tracks contain it as
        # a stand-alone substring (split on comma+space).
        score = 0.0
        for art in art_set:
            art_l = art.lower()
            for tt in topic.get("top_tracks", []):
                tt_artists = [s.strip().lower() for s in tt["artist"].split(",")]
                if any(art_l == a or a.startswith(art_l + " ") or a.startswith(art_l + " &")
                       for a in tt_artists):
                    score += 2.0
        # Bonus for top-track artist match
        if topic["top_tracks"]:
            top_artist_l = topic["top_tracks"][0]["artist"].lower()
            for art in art_set:
                art_l = art.lower()
                if (art_l == top_artist_l
                    or top_artist_l.startswith(art_l + " ")
                    or top_artist_l.startswith(art_l + " &")
                    or top_artist_l == "the " + art_l
                    or top_artist_l.startswith(art_l)):
                    score += 5.0
                    break
        # Penalty for "correction" rules unless top track matches
        if payload["marcus_label"] in CORRECTION_RULES:
            if topic["top_tracks"]:
                top_artist_l = topic["top_tracks"][0]["artist"].lower()
                has_top_match = any(
                    art.lower() == top_artist_l
                    or top_artist_l.startswith(art.lower() + " ")
                    or top_artist_l.startswith(art.lower() + " &")
                    or top_artist_l == "the " + art.lower()
                    or top_artist_l.startswith(art.lower())
                    for art in art_set
                )
                if not has_top_match:
                    score *= 0.3  # Heavy penalty — only win on strong top-track match
        if score > best_score:
            best_score = score
            best_rule = payload
        if score > 0:
            matched.append((art_set, payload["marcus_label"], score))

    # Multi-label fusion: if a non-correction rule scored well, prefer it
    strong = [(s, l) for (_art, l, s) in matched if s > 4 and l not in CORRECTION_RULES]
    strong.sort(key=lambda x: -x[0])
    if strong and best_rule and best_rule["marcus_label"] in CORRECTION_RULES:
        # Best non-correction rule should win
        for s, l in strong:
            for _art, payload in ARTIST_RULES:
                if payload["marcus_label"] == l:
                    best_rule = payload
                    best_score = s
                    break
            if best_rule["marcus_label"] == l:
                break

    # Multi-label: if a SECOND rule is also strong (>50% of best), fuse them
    fusion_label = None
    if best_rule and best_score >= 4.0 and strong:
        for s, l in strong:
            if l != best_rule["marcus_label"] and s >= best_score * 0.5 and s >= 4.0:
                fusion_label = l
                break

    if best_rule is None or best_score < 2.0:
        # Fallback: peak-year based label
        if topic["peak_year"] and topic["peak_year"] <= 2018:
            label = f"Frühe Konsolidierung (peak {topic['peak_year']})"
        elif topic["peak_year"] == 2020:
            label = "Pandemie-Höhepunkt 2020"
        elif topic["peak_year"] in (2024, 2025, 2026):
            label = f"Rezente Entdeckung (peak {topic['peak_year']})"
        else:
            label = f"Cluster (peak {topic['peak_year']})"
        return {
            "marcus_label": label,
            "axis": "unbekannt",
            "life_phase": "—",
            "notes": "Kein Artist-Rule-Match. Manuell zu labeln.",
            "rule_score": best_score,
        }
    else:
        out = dict(best_rule)
        if fusion_label:
            out["marcus_label"] = f"{out['marcus_label']} + {fusion_label}"
        out["rule_score"] = best_score
        return out


def main():
    summary = json.loads(SUMMARY.read_text())
    con = sqlite3.connect(str(SRC_DB))
    con.row_factory = sqlite3.Row

    for t in summary["topics"]:
        labels = label_topic(t, con)
        t.update(labels)

    summary["rule_set"] = "v01 — artist-substring rules, see label_topics.py"
    OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"wrote {OUT_JSON}")

    # Markdown
    md = ["# Marcus's Spotify Topic Labels v01\n"]
    md.append("**Source:** BERTopic over top 2000 tracks (by lifetime hours)  ")
    md.append("**Embedder:** `paraphrase-multilingual-MiniLM-L12-v2`  ")
    md.append("**UMAP:** n_neighbors=15, n_components=5, cosine  ")
    md.append("**HDBSCAN:** min_cluster=20, eom  ")
    md.append("**Outliers:** 25.6% — these are your most idiosyncratic tracks  \n")

    md.append("## Labeled Topics (ranked by total hours)\n")
    md.append("| # | Topic | Marcus-Label | Axis | Life-Phase | Hours | Peak |")
    md.append("|---|---|---|---|---|---:|---|")
    for i, t in enumerate(summary["topics"], 1):
        # Use representative track as Topic column
        rep = ""
        if t["top_tracks"]:
            rep = f"{t['top_tracks'][0]['artist']} — {t['top_tracks'][0]['track']}"
        if len(rep) > 50: rep = rep[:47] + "..."
        md.append(f"| {i} | {rep} | **{t['marcus_label']}** | {t['axis']} | {t['life_phase']} | {t['total_hours']:g} | {t['peak_year']} |")

    md.append("\n## Reflection questions per topic\n")
    md.append("Drawn from the rules and the listening peak. Marcus can edit these.\n")
    for i, t in enumerate(summary["topics"], 1):
        md.append(f"### {i}. {t['marcus_label']}")
        md.append(f"**Cluster:** {t['top_tracks'][0]['artist']} — {t['top_tracks'][0]['track']}  ")
        md.append(f"**Hours:** {t['total_hours']:g}  | **Tracks:** {t['size']}  | **Peak:** {t['peak_year']}  ")
        md.append(f"**Notes:** {t['notes']}\n")
        # Generate a reflection question
        if t['peak_year'] == 2020:
            q = "Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?"
        elif t['peak_year'] in (2017, 2018):
            q = "Wie hängt dieser Cluster mit deinem Berlin-TXL-Jahr zusammen?"
        elif t['peak_year'] in (2023, 2024, 2025, 2026):
            q = "Was hat dich 2023+ an diesem Cluster neu interessiert?"
        elif "Biographisch" in t.get("axis", ""):
            q = "Welche Kindheits-/Jugenderfahrung verknüpfst du mit diesem Cluster?"
        elif "Politisch" in t.get("axis", ""):
            q = "Hat sich dein politisches Verständnis über diesen Cluster verändert?"
        else:
            q = "Wenn du einen Track aus diesem Cluster hörst — was kommt zurück?"
        md.append(f"**Reflection:** {q}\n")
    OUT_MD.write_text("\n".join(md))
    print(f"wrote {OUT_MD}")
    print(f"\nCoverage: {sum(1 for t in summary['topics'] if t.get('rule_score', 0) > 0)}/{len(summary['topics'])} topics rule-labeled")
    con.close()


if __name__ == "__main__":
    main()
