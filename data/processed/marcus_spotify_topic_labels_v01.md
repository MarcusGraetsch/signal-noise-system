# Marcus's Spotify Topic Labels v01

**Source:** BERTopic over top 2000 tracks (by lifetime hours)  
**Embedder:** `paraphrase-multilingual-MiniLM-L12-v2`  
**UMAP:** n_neighbors=15, n_components=5, cosine  
**HDBSCAN:** min_cluster=20, eom  
**Outliers:** 25.6% — these are your most idiosyncratic tracks  

## Labeled Topics (ranked by total hours)

| # | Topic | Marcus-Label | Axis | Life-Phase | Hours | Peak |
|---|---|---|---|---|---:|---|
| 1 | Neil Young — Rockin' in the Free World | **Americana / Singer-Songwriter Rock** | erzählerisch-nordamerikanisch | Neil Young 215h, Peak 2020 (Pandemie-Hauptcluster) | 215.8 | 2020 |
| 2 | NEU! — Hallogallo | **Krautrock / Düsseldorf** | deutsch-experimentell | TXL-Phase (2017-2018), Pandemie-Ausweitung (2020) | 204.9 | 2020 |
| 3 | AC/DC — Jailbreak - Live - 1991 | **Heavy Metal / Hard Rock** | handwerklich-klassisch | Konsistent seit 2013, Peak 2021 | 167.5 | 2021 |
| 4 | Dr. Feelgood — She Does It Right - 2006 Remaster | **Pub Rock / Punk-Vorläufer (UK 1976-78)** | kompakt-vorwärts | Dauerhaft, Peak 2020 | 166 | 2020 |
| 5 | The Voluptuous Horror of Karen Black — Bills to... | **No-Wave / NYC / Industrial Underground** | avantgardistisch | Voluptuous Horror 143h (Themen-Track, single heavy) | 142.7 | 2020 |
| 6 | Flamin' Groovies — Shake Some Action | **Deutsch-Punk / Polit-Punk (BRD)** | politisch-kulturell | Aktiv ab 2018 (TXL + Pandemie) | 142.1 | 2020 |
| 7 | ZZ Top — Gimme All Your Lovin' | **Southern Rock / Texas Blues** | regional-klassisch | Peak 2019-2020 (ZZ Top 160h) | 120.8 | 2019 |
| 8 | Nirvana — Come As You Are | **Indie / Post-Punk / College Rock 80s** | kritisch-1980s | Aktiv ab 2018 | 120.6 | 2020 |
| 9 | Tom Petty and the Heartbreakers — American Drea... | **American Heartland Rock** | erzählerisch-bürgerlich | Dauerhaft, Peak 2020 (Tom Petty 107h, Springsteen 50h) | 117.4 | 2020 |
| 10 | Death — Politicians In My Eyes | **Underground / Proto-Punk / No-Wave** | aktuell-experimentell | Stark 2020-2021 | 111.9 | 2021 |
| 11 | Radio Birdman — Hand Of Law | **Heavy Metal / Hard Rock** | handwerklich-klassisch | Konsistent seit 2013, Peak 2021 | 94.3 | 2020 |
| 12 | David Bowie — Where Are We Now? | **Glam / Art Rock** | künstlerisch-experimentell | Dauerhaft seit 2013 | 92.3 | 2020 |
| 13 | The Rolling Stones — Sympathy For The Devil - 5... | **Rock'n'Roll-Ursprung** | historisch-klassisch | Dauerhaft, Peak 2020 | 90.8 | 2020 |
| 14 | The Peep Tempel — Neuroplasticity | **Chinesischer Indie / Beijing-Szene** | exotisch-politisch | Aktiv 2018-2020, Peep Tempel 8.6h, Carsick Cars 9.3h | 85.2 | 2020 |
| 15 | Billy Idol — Wasteland | **New Wave / 80s Pop (Billy Idol-Kosmos)** | urban-tanzbar | Billy Idol 84h, Peak 2021 | 83.8 | 2021 |
| 16 | The Alan Parsons Project — Eye In The Sky | **Prog / Classic Rock UK** | konservativ-erwachsen-1970 | Alan Parsons 79h, Peak 2020 | 78.8 | 2020 |
| 17 | The Smashing Pumpkins — Bullet With Butterfly W... | **Grunge 90s** | jugendlich-nostalgisch | Dauerhaft seit 2013, Smashing Pumpkins 113h | 72 | 2021 |
| 18 | Viagra Boys — Research Chemicals | **UK/IE Post-Brexit Indie** | aktuell-szene | Viagra Boys 65h, ab 2020 | 64.6 | 2020 |
| 19 | Harry Nilsson — Jump Into The Fire | **American Heartland Rock** | erzählerisch-bürgerlich | Dauerhaft, Peak 2020 (Tom Petty 107h, Springsteen 50h) | 64.6 | 2020 |
| 20 | Funkadelic — Maggot Brain | **Stoner / Desert Rock** | saturiert-hypnotisch | Peak 2019-2020 (Monster Magnet 91h) | 62.3 | 2019 |
| 21 | Dire Straits — Industrial Disease | **Blues-Rock / Gitarrenhandwerk** | handwerklich-solitär | Dauerhaft | 60 | 2020 |
| 22 | Aerosmith — Livin' On The Edge | **Hair Metal / 80s Stadium Rock** | nostalgisch-theatralisch | Peak 2023, Aerosmith 59h | 58.9 | 2023 |
| 23 | Bruce Springsteen — Wrecking Ball | **American Heartland Rock** | erzählerisch-bürgerlich | Dauerhaft, Peak 2020 (Tom Petty 107h, Springsteen 50h) | 58.3 | 2020 |
| 24 | Bob Marley & The Wailers — Exodus | **Blues-Rock / Gitarrenhandwerk** | handwerklich-solitär | Dauerhaft | 54.5 | 2020 |
| 25 | Phil Collins — In The Air Tonight - 2015 Remast... | **80s Mainstream Pop-Rock (UK)** | mainstream-1980 | Phil Collins 51h, Peak 2022 | 51.1 | 2022 |
| 26 | Deep Purple — Smoke On The Water - Remastered 2012 | **Hard Rock / Heavy Rock (UK 70s)** | handwerklich-klassisch | Deep Purple 50h, Peak 2020 | 50.4 | 2020 |
| 27 | The Slits — I Heard It Through The Grapevine | **Post-Punk / Frauen-Bands (Punk-Adjacent)** | feministisch-1980 | Peak 2025, The Slits 47h | 47.3 | 2025 |
| 28 | Supertramp — Bloody Well Right - Live At Pavill... | **AOR / Stadion-Rock 70s-80s** | konservativ-erwachsen | Supertramp 45h, Peak 2021 | 45.3 | 2021 |
| 29 | R.L. Burnside — It's Bad You Know | **Mississippi Blues / North Mississippi Hill Country** | regional-traditionell | Peak 2023, R.L. Burnside 41h | 40.9 | 2023 |
| 30 | Queen — Under Pressure - Remastered 2011 | **Queen & Soli** | theatralisch-klassisch | Queen 40h, Peak 2020 | 40 | 2020 |
| 31 | Keith Richards — Struggle | **Rolling Stones Solo / Side Projects** | verwandt-klassisch | Keith Richards 40h, Peak 2021 | 39.5 | 2021 |
| 32 | The Clash — London Calling - Remastered | **Punk (UK/US 1976-1982)** | aggressiv-urban | The Clash 37h, Dauerhaft | 37.3 | 2020 |
| 33 | Steppenwolf — Magic Carpet Ride | **Proto-Punk / 60s-70s Garage / Hard-Rock-Vorläufer** | historisch-proto | Steppenwolf 27h, Peak 2020 | 26.9 | 2020 |

## Reflection questions per topic

Drawn from the rules and the listening peak. Marcus can edit these.

### 1. Americana / Singer-Songwriter Rock
**Cluster:** Neil Young — Rockin' in the Free World  
**Hours:** 215.8  | **Tracks:** 124  | **Peak:** 2020  
**Notes:** Sehr großer Cluster in 2020 — vermutlich der Pandemie-Hauptanker.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 2. Krautrock / Düsseldorf
**Cluster:** NEU! — Hallogallo  
**Hours:** 204.9  | **Tracks:** 99  | **Peak:** 2020  
**Notes:** NEU! dominiert. Hallogallo als 20h-Single definiert das Topic.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 3. Heavy Metal / Hard Rock
**Cluster:** AC/DC — Jailbreak - Live - 1991  
**Hours:** 167.5  | **Tracks:** 71  | **Peak:** 2021  
**Notes:** AC/DC ist mit Abstand Spitze (212h). Konservativ-hören.

**Reflection:** Wenn du einen Track aus diesem Cluster hörst — was kommt zurück?

### 4. Pub Rock / Punk-Vorläufer (UK 1976-78)
**Cluster:** Dr. Feelgood — She Does It Right - 2006 Remaster  
**Hours:** 166  | **Tracks:** 103  | **Peak:** 2020  
**Notes:** Dr. Feelgood ist dein Pub-Rock-Einstieg. Verwandtschaft mit The Stranglers.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 5. No-Wave / NYC / Industrial Underground
**Cluster:** The Voluptuous Horror of Karen Black — Bills to Pay  
**Hours:** 142.7  | **Tracks:** 89  | **Peak:** 2020  
**Notes:** Sehr Nischen, einprägsamer Cluster.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 6. Deutsch-Punk / Polit-Punk (BRD)
**Cluster:** Flamin' Groovies — Shake Some Action  
**Hours:** 142.1  | **Tracks:** 72  | **Peak:** 2020  
**Notes:** Ton Steine Scherben ist dein heimlicher Bezugspunkt. Fehlfarben kommt separat.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 7. Southern Rock / Texas Blues
**Cluster:** ZZ Top — Gimme All Your Lovin'  
**Hours:** 120.8  | **Tracks:** 42  | **Peak:** 2019  
**Notes:** ZZ Top 160h, 2019 ist dein Southern-Rock-Jahr.

**Reflection:** Wenn du einen Track aus diesem Cluster hörst — was kommt zurück?

### 8. Indie / Post-Punk / College Rock 80s
**Cluster:** Nirvana — Come As You Are  
**Hours:** 120.6  | **Tracks:** 74  | **Peak:** 2020  
**Notes:** The Fall taucht immer wieder auf — typisch britisch. R.E.M. ist post-R.E.M.-US-Indie.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 9. American Heartland Rock
**Cluster:** Tom Petty and the Heartbreakers — American Dream Plan B  
**Hours:** 117.4  | **Tracks:** 43  | **Peak:** 2020  
**Notes:** Storytelling-Rock. Tom Petty dominiert.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 10. Underground / Proto-Punk / No-Wave
**Cluster:** Death — Politicians In My Eyes  
**Hours:** 111.9  | **Tracks:** 56  | **Peak:** 2021  
**Notes:** Death (Proto-Punk aus Detroit, 70er) ist dein Liebling.

**Reflection:** Wenn du einen Track aus diesem Cluster hörst — was kommt zurück?

### 11. Heavy Metal / Hard Rock
**Cluster:** Radio Birdman — Hand Of Law  
**Hours:** 94.3  | **Tracks:** 47  | **Peak:** 2020  
**Notes:** AC/DC ist mit Abstand Spitze (212h). Konservativ-hören.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 12. Glam / Art Rock
**Cluster:** David Bowie — Where Are We Now?  
**Hours:** 92.3  | **Tracks:** 47  | **Peak:** 2020  
**Notes:** Bowie 154h, der Cluster ist sehr breit.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 13. Rock'n'Roll-Ursprung
**Cluster:** The Rolling Stones — Sympathy For The Devil - 50th Anniversary Edition  
**Hours:** 90.8  | **Tracks:** 44  | **Peak:** 2020  
**Notes:** Rolling Stones 148h, sehr altbackener Bezug.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 14. Chinesischer Indie / Beijing-Szene
**Cluster:** The Peep Tempel — Neuroplasticity  
**Hours:** 85.2  | **Tracks:** 54  | **Peak:** 2020  
**Notes:** Überraschender Cluster. Marcus hat einen China-Punk-Bezug.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 15. New Wave / 80s Pop (Billy Idol-Kosmos)
**Cluster:** Billy Idol — Wasteland  
**Hours:** 83.8  | **Tracks:** 33  | **Peak:** 2021  
**Notes:** Billy Idol als Fixpunkt, plus 80s New Wave.

**Reflection:** Wenn du einen Track aus diesem Cluster hörst — was kommt zurück?

### 16. Prog / Classic Rock UK
**Cluster:** The Alan Parsons Project — Eye In The Sky  
**Hours:** 78.8  | **Tracks:** 51  | **Peak:** 2020  
**Notes:** Prog-Klassiker. Wohl handwerkliche Wertschätzung.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 17. Grunge 90s
**Cluster:** The Smashing Pumpkins — Bullet With Butterfly Wings - Remastered 2012  
**Hours:** 72  | **Tracks:** 41  | **Peak:** 2021  
**Notes:** Sehr 90er, sehr Kurt-Cobain.

**Reflection:** Wenn du einen Track aus diesem Cluster hörst — was kommt zurück?

### 18. UK/IE Post-Brexit Indie
**Cluster:** Viagra Boys — Research Chemicals  
**Hours:** 64.6  | **Tracks:** 31  | **Peak:** 2020  
**Notes:** Zeitgenössischer UK/IE-Indie.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 19. American Heartland Rock
**Cluster:** Harry Nilsson — Jump Into The Fire  
**Hours:** 64.6  | **Tracks:** 27  | **Peak:** 2020  
**Notes:** Storytelling-Rock. Tom Petty dominiert.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 20. Stoner / Desert Rock
**Cluster:** Funkadelic — Maggot Brain  
**Hours:** 62.3  | **Tracks:** 27  | **Peak:** 2019  
**Notes:** Monster Magnet 91h, Fu Manchu 7.5h. Sub-cluster innerhalb Southern Rock.

**Reflection:** Wenn du einen Track aus diesem Cluster hörst — was kommt zurück?

### 21. Blues-Rock / Gitarrenhandwerk
**Cluster:** Dire Straits — Industrial Disease  
**Hours:** 60  | **Tracks:** 23  | **Peak:** 2020  
**Notes:** Mark Knopfler-Fingerstyle-Verehrung.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 22. Hair Metal / 80s Stadium Rock
**Cluster:** Aerosmith — Livin' On The Edge  
**Hours:** 58.9  | **Tracks:** 21  | **Peak:** 2023  
**Notes:** Wiederkehr 2023 — Jugenderinnerung.

**Reflection:** Was hat dich 2023+ an diesem Cluster neu interessiert?

### 23. American Heartland Rock
**Cluster:** Bruce Springsteen — Wrecking Ball  
**Hours:** 58.3  | **Tracks:** 29  | **Peak:** 2020  
**Notes:** Storytelling-Rock. Tom Petty dominiert.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 24. Blues-Rock / Gitarrenhandwerk
**Cluster:** Bob Marley & The Wailers — Exodus  
**Hours:** 54.5  | **Tracks:** 30  | **Peak:** 2020  
**Notes:** Mark Knopfler-Fingerstyle-Verehrung.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 25. 80s Mainstream Pop-Rock (UK)
**Cluster:** Phil Collins — In The Air Tonight - 2015 Remastered  
**Hours:** 51.1  | **Tracks:** 29  | **Peak:** 2022  
**Notes:** Mainstream-Pop der 80er. Nicht unbedingt peinlich.

**Reflection:** Wenn du einen Track aus diesem Cluster hörst — was kommt zurück?

### 26. Hard Rock / Heavy Rock (UK 70s)
**Cluster:** Deep Purple — Smoke On The Water - Remastered 2012  
**Hours:** 50.4  | **Tracks:** 29  | **Peak:** 2020  
**Notes:** Britischer Hard Rock. Deep Purple als Fixpunkt.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 27. Post-Punk / Frauen-Bands (Punk-Adjacent)
**Cluster:** The Slits — I Heard It Through The Grapevine  
**Hours:** 47.3  | **Tracks:** 24  | **Peak:** 2025  
**Notes:** Späte Entdeckung — Feministischer Post-Punk.

**Reflection:** Was hat dich 2023+ an diesem Cluster neu interessiert?

### 28. AOR / Stadion-Rock 70s-80s
**Cluster:** Supertramp — Bloody Well Right - Live At Pavillon de Paris/1979  
**Hours:** 45.3  | **Tracks:** 20  | **Peak:** 2021  
**Notes:** AOR — Adult Oriented Rock. Der weiche Bühnenrock.

**Reflection:** Wenn du einen Track aus diesem Cluster hörst — was kommt zurück?

### 29. Mississippi Blues / North Mississippi Hill Country
**Cluster:** R.L. Burnside — It's Bad You Know  
**Hours:** 40.9  | **Tracks:** 24  | **Peak:** 2023  
**Notes:** Rezent-Entdeckung! R.L. Burnside taucht 2023-2025 stark auf.

**Reflection:** Was hat dich 2023+ an diesem Cluster neu interessiert?

### 30. Queen & Soli
**Cluster:** Queen — Under Pressure - Remastered 2011  
**Hours:** 40  | **Tracks:** 23  | **Peak:** 2020  
**Notes:** Queen — mit Abstand meist gehört in 2020.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 31. Rolling Stones Solo / Side Projects
**Cluster:** Keith Richards — Struggle  
**Hours:** 39.5  | **Tracks:** 20  | **Peak:** 2021  
**Notes:** Solo-Ausflüge der Stones-Mitglieder.

**Reflection:** Wenn du einen Track aus diesem Cluster hörst — was kommt zurück?

### 32. Punk (UK/US 1976-1982)
**Cluster:** The Clash — London Calling - Remastered  
**Hours:** 37.3  | **Tracks:** 21  | **Peak:** 2020  
**Notes:** Klassischer Punk. Nicht so dominant wie erwartet.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?

### 33. Proto-Punk / 60s-70s Garage / Hard-Rock-Vorläufer
**Cluster:** Steppenwolf — Magic Carpet Ride  
**Hours:** 26.9  | **Tracks:** 20  | **Peak:** 2020  
**Notes:** Steppenwolf 'Magic Carpet Ride' — die Wiege des Heavy Metal.

**Reflection:** Was hat dieser Cluster in 2020 für dich bedeutet? Ersatz für was?
