# Spotify Track-Topic Model

**Corpus:** top 2000 tracks by lifetime listening  
**Topics:** 33 + outliers  
**Outliers:** 512 tracks (25.6%)  
**Embedder:** `paraphrase-multilingual-MiniLM-L12-v2` (384-dim, normalized)  
**Reducer:** UMAP(n_neighbors=15, n_components=5, cosine)  
**Clusterer:** HDBSCAN(min_cluster=15, min_samples=2, eom)  

## Topic Index (ranked by total hours)

| # | Topic ID | Hours | Tracks | Peak year | Representative track | Top keywords |
|---|---|---:|---:|---:|---|---|
| 1 | 0 | 215.8 | 124 | 2020 | Neil Young — Rockin' in the Free World | chris, young, johnny, little, peel |
| 2 | 2 | 204.9 | 99 | 2020 | NEU! — Hallogallo | immer, zeit, falco, destrktiw komandh, destrktiw |
| 3 | 6 | 167.5 | 71 | 2021 | AC/DC — Jailbreak - Live - 1991 | rock, rock roll, roll, jack, shot |
| 4 | 1 | 166 | 103 | 2020 | Dr. Feelgood — She Does It Right - 2006 Remaster | remaster, iron, eagles, heads, version |
| 5 | 3 | 142.7 | 89 | 2020 | The Voluptuous Horror of Karen Black — Bills to... | turner, tina, tina turner, black, mother |
| 6 | 5 | 142.1 | 72 | 2020 | Flamin' Groovies — Shake Some Action | simple, simple minds, minds, coming, dream |
| 7 | 14 | 120.8 | 42 | 2019 | ZZ Top — Gimme All Your Lovin' | remix, remaster, mess, brown, need |
| 8 | 4 | 120.6 | 74 | 2020 | Nirvana — Come As You Are | band, blues, youth, version, original |
| 9 | 13 | 117.4 | 43 | 2020 | Tom Petty and the Heartbreakers — American Drea... | george, dream, american, girl, dont |
| 10 | 7 | 111.9 | 56 | 2021 | Death — Politicians In My Eyes | death, zombie, dead, white, live |
| 11 | 11 | 94.3 | 47 | 2020 | Radio Birdman — Hand Of Law | radio, hammer, golden, touch, stay |
| 12 | 10 | 92.3 | 47 | 2020 | David Bowie — Where Are We Now? | david, remaster, girl, china, space |
| 13 | 12 | 90.8 | 44 | 2020 | The Rolling Stones — Sympathy For The Devil - 5... | rolling, devil, remastered, stone, mono |
| 14 | 8 | 85.2 | 54 | 2020 | The Peep Tempel — Neuroplasticity | peter, tempel, peep, peep tempel, paul |
| 15 | 16 | 83.8 | 33 | 2021 | Billy Idol — Wasteland | billy, rebel, come, glory, save |
| 16 | 9 | 78.8 | 51 | 2020 | The Alan Parsons Project — Eye In The Sky | blue, golden, mother, moon, rising |
| 17 | 15 | 72 | 41 | 2021 | The Smashing Pumpkins — Bullet With Butterfly W... | remastered, eyes, tonight, left, arms |
| 18 | 17 | 64.6 | 31 | 2020 | Viagra Boys — Research Chemicals | boys, apart, line, need, slow |
| 19 | 23 | 64.6 | 27 | 2020 | Harry Nilsson — Jump Into The Fire | john, people, jump, save, stand |
| 20 | 22 | 62.3 | 27 | 2019 | Funkadelic — Maggot Brain | comes, living, revolution, temple, hammer |
| 21 | 26 | 60 | 23 | 2020 | Dire Straits — Industrial Disease | dire, dire straits, straits, arms, brothers |
| 22 | 28 | 58.9 | 21 | 2023 | Aerosmith — Livin' On The Edge | walk, livin, mama, gotta, edge |
| 23 | 20 | 58.3 | 29 | 2020 | Bruce Springsteen — Wrecking Ball | born, glory, edge, care, jack |
| 24 | 18 | 54.5 | 30 | 2020 | Bob Marley & The Wailers — Exodus | eric, stevie, wonder, stop, change |
| 25 | 19 | 51.1 | 29 | 2022 | Phil Collins — In The Air Tonight - 2015 Remast... | remaster, long, love remaster, heaven, number |
| 26 | 21 | 50.4 | 29 | 2020 | Deep Purple — Smoke On The Water - Remastered 2012 | deep, fehlfarben, child, highway, star |
| 27 | 25 | 47.3 | 24 | 2025 | The Slits — I Heard It Through The Grapevine | heard, jungle, glory, medicine, rising |
| 28 | 31 | 45.3 | 20 | 2021 | Supertramp — Bloody Well Right - Live At Pavill... | live, song, home, long, bloody |
| 29 | 24 | 40.9 | 24 | 2023 | R.L. Burnside — It's Bad You Know | sham, feel, wild, life, change |
| 30 | 27 | 40 | 23 | 2020 | Queen — Under Pressure - Remastered 2011 | remastered, radio, want, world, california |
| 31 | 30 | 39.5 | 20 | 2021 | Keith Richards — Struggle | hard, hate, make, away, live |
| 32 | 29 | 37.3 | 21 | 2020 | The Clash — London Calling - Remastered | black, iron, calling, bloody, stay |
| 33 | 32 | 26.9 | 20 | 2020 | Steppenwolf — Magic Carpet Ride | steppenwolf, ride, land, kommen, stiff |

## Per-Topic Detail

### 1. Topic 0 — 215.8h, 124 tracks, peak 2020

**Keywords:** `chris`, `young`, `johnny`, `little`, `peel`, `heart`, `eric`, `beat`

**Top tracks:**
  - Neil Young — Rockin' in the Free World (6.7h)
  - Chris Spedding — Video Life (6.4h)
  - Garland Jeffreys — Matador (4.9h)
  - Chris de Burgh — Don't Pay The Ferryman (4.4h)
  - Derek & The Dominos — Layla (4.1h)
  - Chris Spedding — Time Warp (4.1h)
  - Rod Stewart — Maggie May (3.8h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 2.8  1.7 28.5 68.0 52.4 21.1 14.8  9.0 13.7  3.8
 █████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 2. Topic 2 — 204.9h, 99 tracks, peak 2020

**Keywords:** `immer`, `zeit`, `falco`, `destrktiw komandh`, `destrktiw`, `mekanik destrktiw`, `ride`, `space`

**Top tracks:**
  - NEU! — Hallogallo (19.8h)
  - The Peep Tempel — Dark Beach (8.6h)
  - Fu Manchu — Mongoose (7.5h)
  - BAP — Verdamp lang her (5.8h)
  - NEU! — Seeland (5.5h)
  - Public Image Ltd. — One Drop (5.1h)
  - kettcar — Landungsbrücken raus (3.9h)

**Year distribution (h):**
```
2015 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.2  5.1  2.0 24.7 59.5 45.6 26.4 12.9 10.4 13.8  4.3
 ·██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 3. Topic 6 — 167.5h, 71 tracks, peak 2021

**Keywords:** `rock`, `rock roll`, `roll`, `jack`, `shot`, `live`, `city`, `aint`

**Top tracks:**
  - AC/DC — Jailbreak - Live - 1991 (16.0h)
  - AC/DC — Back In Black (6.0h)
  - AC/DC — Hells Bells (5.7h)
  - AC/DC — Thunderstruck (5.0h)
  - AC/DC — Highway to Hell (4.9h)
  - AC/DC — Shoot to Thrill (4.3h)
  - AC/DC — You Shook Me All Night Long (4.3h)

**Year distribution (h):**
```
2013 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.1  1.2 17.7  0.5 10.7 34.0 37.5 17.4 19.5 11.1 13.8  4.1
 ·███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 4. Topic 1 — 166h, 103 tracks, peak 2020

**Keywords:** `remaster`, `iron`, `eagles`, `heads`, `version`, `road`, `california`, `years`

**Top tracks:**
  - Dr. Feelgood — She Does It Right - 2006 Remaster (6.0h)
  - Hawkwind — Silver Machine - Live at the Roundhouse London; 1996 Remaster (4.5h)
  - Eagles — Hotel California - 2013 Remaster (4.4h)
  - UFO — Doctor Doctor - 2007 Remaster (4.1h)
  - Grateful Dead — Touch of Grey - 2013 Remaster (3.5h)
  - Robin Trower — Too Rolling Stoned - 2007 Remaster (3.4h)
  - Fleetwood Mac — Go Your Own Way - 2004 Remaster (3.1h)

**Year distribution (h):**
```
2015 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.1  1.9  2.3 23.0 44.8 30.3 18.7 12.7 10.8 15.3  6.1
 ·███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 5. Topic 3 — 142.7h, 89 tracks, peak 2020

**Keywords:** `turner`, `tina`, `tina turner`, `black`, `mother`, `cult`, `lady`, `dancing`

**Top tracks:**
  - The Voluptuous Horror of Karen Black — Bills to Pay (6.7h)
  - The Voluptuous Horror of Karen Black — Neighborachie (5.0h)
  - The Voluptuous Horror of Karen Black — Shopping Spree (4.0h)
  - Sisters of Mercy — This Corrosion - 2018 Remaster (3.6h)
  - Tina Turner — Tonight (With David Bowie) - Live (3.3h)
  - Tina Turner — Break Every Rule - Live (3.2h)
  - The Voluptuous Horror of Karen Black — Alaska (3.0h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.7  0.5 26.5 47.5 30.1 12.8 10.4  6.3  5.2  2.6
 ████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 6. Topic 5 — 142.1h, 72 tracks, peak 2020

**Keywords:** `simple`, `simple minds`, `minds`, `coming`, `dream`, `antiseen`, `gotta`, `cherry`

**Top tracks:**
  - Flamin' Groovies — Shake Some Action (10.4h)
  - Flamin' Groovies — Slow Death (9.4h)
  - Ton Steine Scherben — Der Traum ist aus (4.3h)
  - Ton Steine Scherben — Wir müssen hier raus! (4.2h)
  - The Who — Who Are You (4.1h)
  - Ton Steine Scherben — Keine Macht für niemand (4.0h)
  - Buffalo — Freedom (3.8h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 3.8  0.7 21.3 35.8 35.7 16.7  8.5  7.3  8.7  3.7
 ███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 7. Topic 14 — 120.8h, 42 tracks, peak 2019

**Keywords:** `remix`, `remaster`, `mess`, `brown`, `need`, `heard`, `heads`, `planet`

**Top tracks:**
  - ZZ Top — Gimme All Your Lovin' (10.0h)
  - ZZ Top — My Head's in Mississippi (7.1h)
  - ZZ Top — Pearl Necklace (6.6h)
  - ZZ Top — Sharp Dressed Man - 2008 Remaster (5.6h)
  - ZZ Top — Rough Boy (5.4h)
  - ZZ Top — Sharp Dressed Man (5.3h)
  - ZZ Top — Cheap Sunglasses (5.2h)

**Year distribution (h):**
```
2015 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 1.4  2.0  0.2 30.2 27.1 13.5  8.4 11.1  4.4 21.7  0.7
 ██████·████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 8. Topic 4 — 120.6h, 74 tracks, peak 2020

**Keywords:** `band`, `blues`, `youth`, `version`, `original`, `heart`, `wont`, `remastered`

**Top tracks:**
  - Nirvana — Come As You Are (4.6h)
  - T. Rex — Bang a Gong (Get It On) - 2003 Remaster (4.6h)
  - Erick Sermon — Music (feat. Marvin Gaye) (4.1h)
  - The Fall — Lost in Music (3.7h)
  - Nirvana — Smells Like Teen Spirit (3.7h)
  - The Moody Blues — Steppin' In A Slide Zone (2.8h)
  - Psychic TV — Meet Every Situation Head On (Noise & Mista Luv Mix) (2.8h)

**Year distribution (h):**
```
2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.1  1.4  1.2 21.6 45.0 25.2 11.5  5.2  3.3  4.0  2.3
 ·█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 9. Topic 13 — 117.4h, 43 tracks, peak 2020

**Keywords:** `george`, `dream`, `american`, `girl`, `dont`, `mary`, `shadow`, `wheel`

**Top tracks:**
  - Tom Petty and the Heartbreakers — American Dream Plan B (9.6h)
  - Tom Petty and the Heartbreakers — Shadow People (7.7h)
  - Tom Petty — Runnin' Down A Dream (7.0h)
  - Tom Petty and the Heartbreakers — Fault Lines (5.9h)
  - Tom Petty — Free Fallin' (5.7h)
  - Tom Petty and the Heartbreakers — Learning To Fly (5.1h)
  - Tom Petty and the Heartbreakers — Refugee (4.6h)

**Year distribution (h):**
```
2013 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.5 12.4  4.5  3.3  0.8  4.3 21.9 20.1  7.9 11.4 11.7 14.5  4.0
 ██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 10. Topic 7 — 111.9h, 56 tracks, peak 2021

**Keywords:** `death`, `zombie`, `dead`, `white`, `live`, `human`, `stone`, `heroes`

**Top tracks:**
  - Death — Politicians In My Eyes (11.5h)
  - The Godfathers — Birth, School, Work, Death (5.9h)
  - Exodus — And Then There Were None - Live (4.8h)
  - Slayer — Seasons In The Abyss (3.7h)
  - Die Toten Hosen — Nichts bleibt für die Ewigkeit (3.4h)
  - Death — Let The World Turn (3.1h)
  - Exodus — Deliver Us to Evil - Live (3.0h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 1.5  0.9 20.1 29.5 31.4 13.7  5.6  4.4  2.7  2.1
 █████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 11. Topic 11 — 94.3h, 47 tracks, peak 2020

**Keywords:** `radio`, `hammer`, `golden`, `touch`, `stay`, `love like`, `city`, `love`

**Top tracks:**
  - Radio Birdman — Hand Of Law (6.4h)
  - Motörhead — 1916 (4.3h)
  - Motörhead — Killed by Death (4.0h)
  - Radio Birdman — Descent Into The Maelstrom (4.0h)
  - Motörhead — Get Back In Line (4.0h)
  - Motörhead — Overkill (3.9h)
  - Motörhead — Sympathy For The Devil (3.4h)

**Year distribution (h):**
```
2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.3  4.1  0.3 15.2 22.3 18.0 15.2 10.0  3.7  4.2  1.0
 ·████████·█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 12. Topic 10 — 92.3h, 47 tracks, peak 2020

**Keywords:** `david`, `remaster`, `girl`, `china`, `space`, `heroes`, `rebel`, `tomorrow`

**Top tracks:**
  - David Bowie — Where Are We Now? (7.7h)
  - David Bowie — Heroes - 2017 Remaster (5.3h)
  - David Bowie — Rebel Rebel - 2016 Remaster (4.2h)
  - David Bowie — The Stars (Are Out Tonight) (3.7h)
  - David Bowie — Let's Dance - 2018 Remaster (3.4h)
  - David Bowie — The Next Day (3.4h)
  - David Bowie — Wild Is the Wind - 2016 Remaster (3.3h)

**Year distribution (h):**
```
2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 1.0  1.3  0.2  5.4 23.5 22.8  9.8  9.3  9.4  7.4  2.3
 ████·███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 13. Topic 12 — 90.8h, 44 tracks, peak 2020

**Keywords:** `rolling`, `devil`, `remastered`, `stone`, `mono`, `beast`, `mess`, `square`

**Top tracks:**
  - The Rolling Stones — Sympathy For The Devil - 50th Anniversary Edition (6.5h)
  - The Rolling Stones — Gimme Shelter (5.0h)
  - The Rolling Stones — Emotional Rescue - Remastered 2009 (4.2h)
  - The Rolling Stones — Start Me Up - Remastered 2009 (3.5h)
  - The Rolling Stones — Criss Cross (3.3h)
  - The Rolling Stones — Sympathy For The Devil - Live (3.3h)
  - The Rolling Stones — (I Can't Get No) Satisfaction - Mono Version (3.2h)

**Year distribution (h):**
```
2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.1  0.2  1.9  0.4  6.1 26.1 23.1  9.5  8.4  6.4  6.1  2.5
 ··███·████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 14. Topic 8 — 85.2h, 54 tracks, peak 2020

**Keywords:** `peter`, `tempel`, `peep`, `peep tempel`, `paul`, `paul simon`, `simon`, `kommen`

**Top tracks:**
  - The Peep Tempel — Neuroplasticity (6.4h)
  - Paul Simon — Graceland (3.3h)
  - Georg Danzer — Weisse Pferde (3.2h)
  - Peter Gabriel — Solsbury Hill (3.2h)
  - Mark Knopfler — Why Aye Man (3.2h)
  - Mark Knopfler — What It Is (2.6h)
  - Paul Simon — You Can Call Me Al (2.4h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.2  0.1  9.7 22.3 18.6 12.8  7.1  3.6  7.3  3.3
 ··█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 15. Topic 16 — 83.8h, 33 tracks, peak 2021

**Keywords:** `billy`, `rebel`, `come`, `glory`, `save`, `tomorrow`, `calling`, `love`

**Top tracks:**
  - Billy Idol — Wasteland (6.2h)
  - Billy Idol — Shock To The System (5.5h)
  - Billy Idol — Eyes Without A Face (5.5h)
  - Billy Idol — Neuromancer (5.2h)
  - Billy Idol — Tomorrow People (4.7h)
  - Billy Idol — Adam In Chains (4.1h)
  - Billy Idol — Kings & Queens Of The Underground (3.8h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.1  0.1 16.6 16.8 22.5  7.1  8.7  6.6  2.4  3.0
 ··████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 16. Topic 9 — 78.8h, 51 tracks, peak 2020

**Keywords:** `blue`, `golden`, `mother`, `moon`, `rising`, `acid`, `joke`, `zone`

**Top tracks:**
  - The Alan Parsons Project — Eye In The Sky (4.2h)
  - Jethro Tull — Aqualung (4.1h)
  - Jefferson Airplane — White Rabbit (4.0h)
  - Karat — Der blaue Planet (3.0h)
  - Jethro Tull — Locomotive Breath (2.9h)
  - Golden Earring — Radar Love (2.1h)
  - Dozer — Big Sky Theory (2.1h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.6  0.8  7.4 27.0 19.0  9.3  4.3  4.1  4.0  2.4
 ██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 17. Topic 15 — 72h, 41 tracks, peak 2021

**Keywords:** `remastered`, `eyes`, `tonight`, `left`, `arms`, `fear`, `right`, `zombie`

**Top tracks:**
  - The Smashing Pumpkins — Bullet With Butterfly Wings - Remastered 2012 (5.8h)
  - The Smashing Pumpkins — Tonight, Tonight - Remastered 2012 (3.9h)
  - The Smashing Pumpkins — Porcelina Of The Vast Oceans - Remastered 2012 (3.2h)
  - The Cranberries — Zombie (3.1h)
  - The Smashing Pumpkins — 1979 - Remastered 2012 (2.7h)
  - The Smashing Pumpkins — Thru The Eyes Of Ruby - Remastered 2012 (2.5h)
  - The Smashing Pumpkins — X.Y.U. - Remastered 2012 (2.2h)

**Year distribution (h):**
```
2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.2  0.4  0.1  5.1 22.6 29.0  6.6  2.7  2.2  1.8  1.5
 ···██████████████████████████████████████████████████████████████████████████████████████████████████
```

### 18. Topic 17 — 64.6h, 31 tracks, peak 2020

**Keywords:** `boys`, `apart`, `line`, `need`, `slow`, `rebel`, `free`, `tonight`

**Top tracks:**
  - Viagra Boys — Research Chemicals (9.6h)
  - INXS — Original Sin (5.8h)
  - Viagra Boys — Just Like You (5.5h)
  - Viagra Boys — Slow Learner (2.9h)
  - Viagra Boys — Sports (2.8h)
  - Viagra Boys — Worms (2.5h)
  - TOTO — Hold the Line (2.3h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.3  0.6  4.7 28.6 16.4  4.5  2.0  3.4  3.4  0.8
 ·████████████████████████████████████████████████████████████████████████████████████████████████
```

### 19. Topic 23 — 64.6h, 27 tracks, peak 2020

**Keywords:** `john`, `people`, `jump`, `save`, `stand`, `funk`, `demon`, `wind`

**Top tracks:**
  - Harry Nilsson — Jump Into The Fire (12.4h)
  - Arcade Fire — Reflektor (5.9h)
  - Arcade Fire — Rebellion (Lies) (5.4h)
  - Arcade Fire — Wake Up (4.3h)
  - John Mellencamp — Paper In Fire (3.8h)
  - Arcade Fire — Neighborhood #1 (Tunnels) (3.3h)
  - Arcade Fire — The Suburbs (2.7h)

**Year distribution (h):**
```
2013 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.6  0.3  1.1  0.2  0.6  7.8 14.0 13.3  4.6  4.5  5.9  7.6  4.2
 █·██·██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 20. Topic 22 — 62.3h, 27 tracks, peak 2019

**Keywords:** `comes`, `living`, `revolution`, `temple`, `hammer`, `dreams`, `space`, `look`

**Top tracks:**
  - Funkadelic — Maggot Brain (11.7h)
  - Monster Magnet — Dopes To Infinity (5.4h)
  - Monster Magnet — Look To Your Orb For The Warning (5.3h)
  - Monster Magnet — Negasonic Teenage Warhead (4.8h)
  - Monster Magnet — Mindfucker (3.3h)
  - Monster Magnet — Space Lord (3.1h)
  - Monster Magnet — Mr. Destroyer (2.3h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025
 0.1  0.4 26.0 14.6  8.6  3.1  5.6  1.9  1.9
 ··███████████████████████████████████████████████████████████████████████████████████████████████████
```

### 21. Topic 26 — 60h, 23 tracks, peak 2020

**Keywords:** `dire`, `dire straits`, `straits`, `arms`, `brothers`, `walk`, `money`, `life`

**Top tracks:**
  - Dire Straits — Industrial Disease (8.6h)
  - Dire Straits — Brothers In Arms (8.2h)
  - Dire Straits — Sultans Of Swing (7.0h)
  - Dire Straits — Sultans of Swing (3.9h)
  - Dire Straits — Money for Nothing (3.9h)
  - Dire Straits — Money For Nothing (3.5h)
  - Dire Straits — Brothers in Arms (3.1h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.6  0.2  2.8 15.2 11.7  7.8  4.4  4.6  9.9  2.8
 █·██████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 22. Topic 28 — 58.9h, 21 tracks, peak 2023

**Keywords:** `walk`, `livin`, `mama`, `gotta`, `edge`, `dream`, `woman`, `crazy`

**Top tracks:**
  - Aerosmith — Livin' On The Edge (9.1h)
  - Aerosmith — Dream On (6.3h)
  - Aerosmith — Movin' Out (5.5h)
  - Aerosmith — Somebody (4.1h)
  - Aerosmith — Reefer Head Woman (3.8h)
  - Aerosmith — Walkin’ The Dog (3.7h)
  - Aerosmith — Eat The Rich (3.5h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.4  0.1  1.2  7.2  7.7  7.1 16.0 15.2  2.9  1.2
 ··████████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 23. Topic 20 — 58.3h, 29 tracks, peak 2020

**Keywords:** `born`, `glory`, `edge`, `care`, `jack`, `left`, `fever`, `darkness`

**Top tracks:**
  - Bruce Springsteen — Wrecking Ball (5.1h)
  - Bruce Springsteen — Dancing In the Dark (4.0h)
  - Bruce Springsteen — I'm On Fire (3.7h)
  - Bruce Springsteen — We Are Alive (3.6h)
  - Bruce Springsteen — Born to Run (3.1h)
  - Bruce Springsteen — Shackled And Drawn (3.0h)
  - Bruce Springsteen — We Take Care of Our Own (2.9h)

**Year distribution (h):**
```
2013 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 1.4  0.5  0.1  4.7 19.0 13.4  5.8  2.4  3.4  6.0  1.6
 ███·█████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 24. Topic 18 — 54.5h, 30 tracks, peak 2020

**Keywords:** `eric`, `stevie`, `wonder`, `stop`, `change`, `calling`, `world`, `shot`

**Top tracks:**
  - Bob Marley & The Wailers — Exodus (4.8h)
  - Bob Dylan — Hurricane (4.2h)
  - Dire Straits — Calling Elvis (4.1h)
  - Michael Jackson — Thriller (3.1h)
  - Michael Jackson — Beat It (2.8h)
  - Stevie Wonder — Superstition - Single Version (2.4h)
  - Eric Clapton — Lay Down Sally (2.4h)

**Year distribution (h):**
```
2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.1  0.1  1.1  0.5  3.1 16.6 12.3  6.7  3.7  2.0  2.5  5.7
 ··███████████████████████████████████████████████████████████████████████████████████████████████████████
```

### 25. Topic 19 — 51.1h, 29 tracks, peak 2022

**Keywords:** `remaster`, `long`, `love remaster`, `heaven`, `number`, `knows`, `tomorrow`, `robert`

**Top tracks:**
  - Phil Collins — In The Air Tonight - 2015 Remastered (4.8h)
  - Chris Rea — The Road to Hell, Pt. 1 & 2 - New Version 2008 (2.7h)
  - Phil Collins — Do You Remember? - 2016 Remaster (2.4h)
  - Phil Collins — Hang in Long Enough - 2016 Remaster (2.4h)
  - Elton John — Sick City - Remastered 1995 (2.4h)
  - Phil Collins — Like China - 2016 Remaster (2.4h)
  - Phil Collins — I Don't Care Anymore - 2016 Remaster (2.3h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.1  0.1  1.5  6.8 11.2 15.6  8.3  4.3  2.6  0.6
 ··██████████████████████████████████████████████████████████████████████████████████████████████████
```

### 26. Topic 21 — 50.4h, 29 tracks, peak 2020

**Keywords:** `deep`, `fehlfarben`, `child`, `highway`, `star`, `time`, `water`, `whats`

**Top tracks:**
  - Deep Purple — Smoke On The Water - Remastered 2012 (3.2h)
  - Prince — When Doves Cry (3.1h)
  - Prince — Let's Go Crazy (2.8h)
  - Prince — Rearrange (2.8h)
  - Prince — Purple Rain (2.7h)
  - Prince — Money Don't Grow On Trees (2.3h)
  - Blondie — Call Me (2.2h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 1.0  0.5  5.0 12.9 10.5  8.0  2.4  5.8  3.1  1.3
 ██████████████████████████████████████████████████████████████████████████████████████████████████
```

### 27. Topic 25 — 47.3h, 24 tracks, peak 2025

**Keywords:** `heard`, `jungle`, `glory`, `medicine`, `rising`, `runnin`, `edit`, `soul`

**Top tracks:**
  - The Slits — I Heard It Through The Grapevine (4.7h)
  - Creedence Clearwater Revival — Up Around The Bend (4.4h)
  - Creedence Clearwater Revival — Born On The Bayou (3.1h)
  - Creedence Clearwater Revival — I Heard It Through The Grapevine (2.8h)
  - Creedence Clearwater Revival — Graveyard Train (2.6h)
  - Soul Asylum — Runaway Train (2022 Remaster) (2.4h)
  - Creedence Clearwater Revival — Susie Q (2.2h)

**Year distribution (h):**
```
2015 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.2  1.1  0.5  3.0  8.2  6.8  4.3  5.7  3.5 10.9  3.2
 ·███████████████████████████████████████████████████████████████████████████████████████████
```

### 28. Topic 31 — 45.3h, 20 tracks, peak 2021

**Keywords:** `live`, `song`, `home`, `long`, `bloody`, `america`, `crime`, `right`

**Top tracks:**
  - Supertramp — Bloody Well Right - Live At Pavillon de Paris/1979 (4.3h)
  - Supertramp — Crime Of The Century - Live At Pavillon de Paris/1979 (3.5h)
  - Supertramp — School - Live At Pavillon de Paris/1979 (3.3h)
  - Supertramp — Fool's Overture - Live At Pavillon de Paris/1979 (3.2h)
  - Supertramp — Hide In Your Shell - Live At Pavillon de Paris/1979 (3.1h)
  - Supertramp — The Logical Song - Remastered 2010 (3.1h)
  - Supertramp — Take The Long Way Home - Live At Pavillon de Paris/1979 (2.4h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.4  0.1  0.8  8.6 17.2  7.3  2.1  4.7  2.3  1.7
 ··██████████████████████████████████████████████████████████████████████████████████
```

### 29. Topic 24 — 40.9h, 24 tracks, peak 2023

**Keywords:** `sham`, `feel`, `wild`, `life`, `change`, `broken`, `tears`, `steppenwolf`

**Top tracks:**
  - R.L. Burnside — It's Bad You Know (6.1h)
  - Dinosaur Jr. — Feel the Pain (3.4h)
  - Sham 69 — Feel It (2.6h)
  - R.L. Burnside — Everything Is Broken (1.8h)
  - Sham 69 — Information Libertaire (1.8h)
  - Sham 69 — Wild and Wonderful (1.7h)
  - Boy Harsher — Pain (1.6h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.1  0.2  5.4  6.6  6.5  2.9  7.5  6.1  3.0  2.6
 ··███████████████████████████████████████████████████████████████████████████████
```

### 30. Topic 27 — 40h, 23 tracks, peak 2020

**Keywords:** `remastered`, `radio`, `want`, `world`, `california`, `hammer`, `forever`, `break`

**Top tracks:**
  - Queen — Under Pressure - Remastered 2011 (4.2h)
  - Queen — Another One Bites The Dust - Remastered 2011 (4.1h)
  - Queen — Innuendo - Remastered 2011 (4.0h)
  - Queen — Radio Ga Ga - Remastered 2011 (3.6h)
  - Queen — Who Wants To Live Forever - Remastered 2011 (2.1h)
  - Queen — Under Pressure (1.9h)
  - Queen — A Kind Of Magic - Remastered 2011 (1.8h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.3  0.1  0.7  9.6  8.1  6.5  4.3  6.3  2.8  1.3
 ··████████████████████████████████████████████████████████████████████████████
```

### 31. Topic 30 — 39.5h, 20 tracks, peak 2021

**Keywords:** `hard`, `hate`, `make`, `away`, `live`, `high`, `remaster`, `dont`

**Top tracks:**
  - Keith Richards — Struggle (5.4h)
  - Keith Richards — Struggle - Live (4.4h)
  - Keith Richards — Take It So Hard (3.3h)
  - Keith Richards — Locked Away (3.1h)
  - Keith Richards — Locked Away - Live (2.5h)
  - Keith Richards — Hate It When You Leave (2.4h)
  - Keith Richards — Make No Mistake (2.0h)

**Year distribution (h):**
```
2017 2019 2020 2021 2022 2023 2024 2025 2026
 0.3  0.4  8.2 17.6  5.7  3.0  1.4  1.6  1.2
 ··██████████████████████████████████████████████████████████████████████
```

### 32. Topic 29 — 37.3h, 21 tracks, peak 2020

**Keywords:** `black`, `iron`, `calling`, `bloody`, `stay`, `master`, `seven`, `alive`

**Top tracks:**
  - The Clash — London Calling - Remastered (3.4h)
  - Black Sabbath — War Pigs (3.2h)
  - Black Sabbath — War Pigs - 2009 Remaster (2.9h)
  - Pearl Jam — Alive (2.9h)
  - Metallica — ...And Justice For All (2.3h)
  - Metallica — ...And Justice for All (Remastered) (2.1h)
  - The Clash — Rock the Casbah - Remastered (1.9h)

**Year distribution (h):**
```
2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 0.2  0.8  0.4  4.9  8.6  7.7  6.7  4.0  1.0  2.0  0.9
 ·█·█████████████████████████████████████████████████████████████████████
```

### 33. Topic 32 — 26.9h, 20 tracks, peak 2020

**Keywords:** `steppenwolf`, `ride`, `land`, `kommen`, `stiff`, `america`, `ghost`, `antiseen`

**Top tracks:**
  - Steppenwolf — Magic Carpet Ride (2.2h)
  - Patti Smith — Land: Horses / Land of a Thousand Dances / La Mer(de) (2.2h)
  - Men Without Hats — The Safety Dance (1.8h)
  - Steppenwolf — The Pusher (1.6h)
  - Stiff Little Fingers — Alternative Ulster (1.5h)
  - Wolf Maahn — Tanzen gegen den Wahnsinn (1.5h)
  - The Who — Pinball Wizard (1.5h)

**Year distribution (h):**
```
2017 2018 2019 2020 2021 2022 2023 2024 2025 2026
 1.1  0.7  4.3  7.5  5.6  2.4  1.5  1.3  1.9  0.5
 ██████████████████████████████████████████████████
```
