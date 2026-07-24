# Marcus's Spotify Topic Labels v02 (MusicBrainz-derived)

**Source:** `artist_genres.json` (MusicBrainz tags) + `topic_summary.json` (BERTopic).  
**Method:** Top tracks per topic → MusicBrainz tag lookup → weighted aggregate → synthesized label.

**Coverage:** 33/33 topics with MusicBrainz tags.


## Labeled Topics (ranked by total hours)

| # | Topic | MB-Label (synthesized) | Hours | Tracks | Peak | Top MB tags (weighted) |
|---|---|---|---:|---:|---:|---|
| 1 | Neil Young — Rockin' in the Free World | **Power Pop / Garage** | 215.8 | 124 | 2020 | power pop(310), rock and roll(232), garage rock(217), punk(155), rock(127) |
| 2 | NEU! — Hallogallo | **Post-Punk / Garage Rock** | 204.9 | 99 | 2020 | post-punk(746), garage rock(516), australian(430), noise rock(430), krautrock(156) |
| 3 | AC/DC — Jailbreak - Live - 1991 | **Hard Rock** | 167.5 | 71 | 2021 | hard rock(2905), rock(871), blues rock(697), rock and roll(116) |
| 4 | Dr. Feelgood — She Does It Right - 2006 Remaster | **Gothic Rock / Post-Punk** | 166.0 | 103 | 2020 | rock(213), gothic(150), new wave(150), post-punk(145), alternative rock(127) |
| 5 | The Voluptuous Horror of Karen Black — Bills to Pa | **Gothic Rock / Post-Punk** | 142.7 | 89 | 2020 | pop(115), gothic(64), post-punk(46), rock(43), dance-pop(39) |
| 6 | Flamin' Groovies — Shake Some Action | **Power Pop / Punk** | 142.1 | 72 | 2020 | punk(2112), power pop(1980), deutsch-punk(1870), polit-punk(1496), rock and roll(1386) |
| 7 | ZZ Top — Gimme All Your Lovin' | **Southern Rock / Blues** | 120.8 | 42 | 2019 | blues rock(774), rock(536), southern rock(476), hard rock(357), boogie rock(238) |
| 8 | Nirvana — Come As You Are | **Grunge** | 120.6 | 74 | 2020 | grunge(531), rock(277), alternative rock(260), noise rock(91), acoustic rock(66) |
| 9 | Tom Petty and the Heartbreakers — American Dream P | **Southern Rock / Heartland** | 117.4 | 43 | 2020 | rock(343), southern rock(184), heartland rock(142), pop rock(142), power pop(83) |
| 10 | Death — Politicians In My Eyes | **Proto-Punk** | 111.9 | 56 | 2021 | proto-punk(1460), punk(1178), garage rock(730), hardcore(584), american(467) |
| 11 | Radio Birdman — Hand Of Law | **Metal / Hard Rock** | 94.3 | 47 | 2020 | metal(736), hard rock(397), rock(232), speed metal(154), british(77) |
| 12 | David Bowie — Where Are We Now? | **Glam / Art Rock** | 92.3 | 47 | 2020 | art rock(869), glam rock(869), alternative rock(474), pop(395), art pop(276) |
| 13 | The Rolling Stones — Sympathy For The Devil - 50th | **Blues Rock** | 90.8 | 44 | 2020 | rock(1360), blues rock(718), british(264), classic rock(264), psychedelic rock(226) |
| 14 | The Peep Tempel — Neuroplasticity | **Post-Punk / Garage Rock** | 85.2 | 54 | 2020 | post-punk(512), garage rock(384), australian(320), noise rock(320), pop(52) |
| 15 | Billy Idol — Wasteland | **Hard Rock / New Wave** | 83.8 | 33 | 2021 | rock(396), hard rock(220), new wave(176), classic rock(132), alternative dance(88) |
| 16 | The Alan Parsons Project — Eye In The Sky | **Ndw** | 78.8 | 51 | 2020 | ndw(400), progressive rock(168), post-punk(120), folk rock(112), german(100) |
| 17 | The Smashing Pumpkins — Bullet With Butterfly Wing | **Alternative Rock** | 72.0 | 41 | 2021 | alternative rock(821), dream pop(145), neo-psychedelia(133), shoegaze(133), grunge(106) |
| 18 | Viagra Boys — Research Chemicals | **Garage Punk / Post-Punk** | 64.6 | 31 | 2020 | post-punk(227), garage punk(202), art punk(177), cowpunk(126), dance-punk(126) |
| 19 | Harry Nilsson — Jump Into The Fire | **Indie Rock** | 64.6 | 27 | 2020 | indie rock(488), baroque pop(139), chamber pop(128), indie pop(128), rock(111) |
| 20 | Funkadelic — Maggot Brain | **Stoner Rock** | 62.3 | 27 | 2019 | stoner rock(244), psychedelic rock(114), hard rock(91), heavy psych(91), space rock(61) |
| 21 | Dire Straits — Industrial Disease | **Soft Rock / Classic Rock** | 60.0 | 23 | 2020 | rock(826), soft rock(261), classic rock(217), pop rock(130), roots rock(130) |
| 22 | Aerosmith — Livin' On The Edge | **Hard Rock / Blues** | 58.9 | 21 | 2023 | hard rock(1373), blues rock(708), rock(443), classic rock(221), glam metal(177) |
| 23 | Bruce Springsteen — Wrecking Ball | **Heartland Rock / Americana** | 58.3 | 29 | 2020 | rock(550), heartland rock(388), americana(226), singer-songwriter(226), american(97) |
| 24 | Bob Marley & The Wailers — Exodus | **Blues Rock / Reggae** | 54.5 | 30 | 2020 | pop(199), rock(183), blues rock(140), dance-pop(112), reggae(110) |
| 25 | Phil Collins — In The Air Tonight - 2015 Remastere | **Soft Rock / Pop** | 51.1 | 29 | 2022 | soft rock(137), pop rock(133), pop(124), rock(71), adult contemporary(64) |
| 26 | Deep Purple — Smoke On The Water - Remastered 2012 | **Ndw / Funk** | 50.4 | 29 | 2020 | ndw(400), funk(301), rock(207), pop(189), hard rock(145) |
| 27 | The Slits — I Heard It Through The Grapevine | **Post-Punk / Punk** | 47.3 | 24 | 2025 | post-punk(470), punk(376), feminist punk(282), swamp rock(270), british(243) |
| 28 | Supertramp — Bloody Well Right - Live At Pavillon  | **Prog / Art Rock** | 45.3 | 20 | 2021 | progressive rock(352), rock(235), art rock(205), pop rock(147), art pop(88) |
| 29 | R.L. Burnside — It's Bad You Know | **Mississippi Blues** | 40.9 | 24 | 2023 | mississippi blues(790), blues(711), north mississippi hill country(632), electric blues(553), american(237) |
| 30 | Queen — Under Pressure - Remastered 2011 | **Glam Rock / Hard Rock** | 40.0 | 23 | 2020 | rock(1126), glam rock(628), hard rock(550), art rock(393), british(393) |
| 31 | Keith Richards — Struggle | **Blues Rock** | 39.5 | 20 | 2021 | rock(56), blues rock(28) |
| 32 | The Clash — London Calling - Remastered | **Metal** | 37.3 | 21 | 2020 | metal(1539), hard rock(308), punk rock(111), grunge(89), traditional doom metal(79) |
| 33 | Steppenwolf — Magic Carpet Ride | **Deutschrock / Singer-Songwriter** | 26.9 | 20 | 2020 | rock(126), deutschrock(120), german(75), singer-songwriter(66), hard rock(58) |

## Marcus-Curated Topics

To override a label: edit `data/processed/marcus_spotify_topic_overrides.json`
with the topic `id` and your preferred `label` + `notes`.

```json
{
  "0": {"label": "My label for topic 0", "notes": "Why I disagree with MB"},
  "5": {"label": "Deutschrock + NDW", "notes": "Mixed cluster, both labels apply"}
}
```


## Reflection Questions

### 1. Power Pop / Garage  —  Neil Young — Rockin' in the Free World
**Hours:** 215.8  |  **Tracks:** 124  |  **Peak:** 2020  |  **Tags:** power pop, rock and roll, garage rock, punk, rock

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 2. Post-Punk / Garage Rock  —  NEU! — Hallogallo
**Hours:** 204.9  |  **Tracks:** 99  |  **Peak:** 2020  |  **Tags:** post-punk, garage rock, australian, noise rock, krautrock

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 3. Hard Rock  —  AC/DC — Jailbreak - Live - 1991
**Hours:** 167.5  |  **Tracks:** 71  |  **Peak:** 2021  |  **Tags:** hard rock, rock, blues rock, rock and roll

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 4. Gothic Rock / Post-Punk  —  Dr. Feelgood — She Does It Right - 2006 Remaster
**Hours:** 166.0  |  **Tracks:** 103  |  **Peak:** 2020  |  **Tags:** rock, gothic, new wave, post-punk, alternative rock

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 5. Gothic Rock / Post-Punk  —  The Voluptuous Horror of Karen Black — Bills to Pay
**Hours:** 142.7  |  **Tracks:** 89  |  **Peak:** 2020  |  **Tags:** pop, gothic, post-punk, rock, dance-pop

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 6. Power Pop / Punk  —  Flamin' Groovies — Shake Some Action
**Hours:** 142.1  |  **Tracks:** 72  |  **Peak:** 2020  |  **Tags:** punk, power pop, deutsch-punk, polit-punk, rock and roll

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 7. Southern Rock / Blues  —  ZZ Top — Gimme All Your Lovin'
**Hours:** 120.8  |  **Tracks:** 42  |  **Peak:** 2019  |  **Tags:** blues rock, rock, southern rock, hard rock, boogie rock

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 8. Grunge  —  Nirvana — Come As You Are
**Hours:** 120.6  |  **Tracks:** 74  |  **Peak:** 2020  |  **Tags:** grunge, rock, alternative rock, noise rock, acoustic rock

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 9. Southern Rock / Heartland  —  Tom Petty and the Heartbreakers — American Dream Plan B
**Hours:** 117.4  |  **Tracks:** 43  |  **Peak:** 2020  |  **Tags:** rock, southern rock, heartland rock, pop rock, power pop

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 10. Proto-Punk  —  Death — Politicians In My Eyes
**Hours:** 111.9  |  **Tracks:** 56  |  **Peak:** 2021  |  **Tags:** proto-punk, punk, garage rock, hardcore, american

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 11. Metal / Hard Rock  —  Radio Birdman — Hand Of Law
**Hours:** 94.3  |  **Tracks:** 47  |  **Peak:** 2020  |  **Tags:** metal, hard rock, rock, speed metal, british

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 12. Glam / Art Rock  —  David Bowie — Where Are We Now?
**Hours:** 92.3  |  **Tracks:** 47  |  **Peak:** 2020  |  **Tags:** art rock, glam rock, alternative rock, pop, art pop

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 13. Blues Rock  —  The Rolling Stones — Sympathy For The Devil - 50th Anniversa
**Hours:** 90.8  |  **Tracks:** 44  |  **Peak:** 2020  |  **Tags:** rock, blues rock, british, classic rock, psychedelic rock

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 14. Post-Punk / Garage Rock  —  The Peep Tempel — Neuroplasticity
**Hours:** 85.2  |  **Tracks:** 54  |  **Peak:** 2020  |  **Tags:** post-punk, garage rock, australian, noise rock, pop

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 15. Hard Rock / New Wave  —  Billy Idol — Wasteland
**Hours:** 83.8  |  **Tracks:** 33  |  **Peak:** 2021  |  **Tags:** rock, hard rock, new wave, classic rock, alternative dance

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 16. Ndw  —  The Alan Parsons Project — Eye In The Sky
**Hours:** 78.8  |  **Tracks:** 51  |  **Peak:** 2020  |  **Tags:** ndw, progressive rock, post-punk, folk rock, german

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 17. Alternative Rock  —  The Smashing Pumpkins — Bullet With Butterfly Wings - Remast
**Hours:** 72.0  |  **Tracks:** 41  |  **Peak:** 2021  |  **Tags:** alternative rock, dream pop, neo-psychedelia, shoegaze, grunge

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 18. Garage Punk / Post-Punk  —  Viagra Boys — Research Chemicals
**Hours:** 64.6  |  **Tracks:** 31  |  **Peak:** 2020  |  **Tags:** post-punk, garage punk, art punk, cowpunk, dance-punk

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 19. Indie Rock  —  Harry Nilsson — Jump Into The Fire
**Hours:** 64.6  |  **Tracks:** 27  |  **Peak:** 2020  |  **Tags:** indie rock, baroque pop, chamber pop, indie pop, rock

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 20. Stoner Rock  —  Funkadelic — Maggot Brain
**Hours:** 62.3  |  **Tracks:** 27  |  **Peak:** 2019  |  **Tags:** stoner rock, psychedelic rock, hard rock, heavy psych, space rock

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 21. Soft Rock / Classic Rock  —  Dire Straits — Industrial Disease
**Hours:** 60.0  |  **Tracks:** 23  |  **Peak:** 2020  |  **Tags:** rock, soft rock, classic rock, pop rock, roots rock

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 22. Hard Rock / Blues  —  Aerosmith — Livin' On The Edge
**Hours:** 58.9  |  **Tracks:** 21  |  **Peak:** 2023  |  **Tags:** hard rock, blues rock, rock, classic rock, glam metal

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 23. Heartland Rock / Americana  —  Bruce Springsteen — Wrecking Ball
**Hours:** 58.3  |  **Tracks:** 29  |  **Peak:** 2020  |  **Tags:** rock, heartland rock, americana, singer-songwriter, american

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 24. Blues Rock / Reggae  —  Bob Marley & The Wailers — Exodus
**Hours:** 54.5  |  **Tracks:** 30  |  **Peak:** 2020  |  **Tags:** pop, rock, blues rock, dance-pop, reggae

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 25. Soft Rock / Pop  —  Phil Collins — In The Air Tonight - 2015 Remastered
**Hours:** 51.1  |  **Tracks:** 29  |  **Peak:** 2022  |  **Tags:** soft rock, pop rock, pop, rock, adult contemporary

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 26. Ndw / Funk  —  Deep Purple — Smoke On The Water - Remastered 2012
**Hours:** 50.4  |  **Tracks:** 29  |  **Peak:** 2020  |  **Tags:** ndw, funk, rock, pop, hard rock

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 27. Post-Punk / Punk  —  The Slits — I Heard It Through The Grapevine
**Hours:** 47.3  |  **Tracks:** 24  |  **Peak:** 2025  |  **Tags:** post-punk, punk, feminist punk, swamp rock, british

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 28. Prog / Art Rock  —  Supertramp — Bloody Well Right - Live At Pavillon de Paris/1
**Hours:** 45.3  |  **Tracks:** 20  |  **Peak:** 2021  |  **Tags:** progressive rock, rock, art rock, pop rock, art pop

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 29. Mississippi Blues  —  R.L. Burnside — It's Bad You Know
**Hours:** 40.9  |  **Tracks:** 24  |  **Peak:** 2023  |  **Tags:** mississippi blues, blues, north mississippi hill country, electric blues, american

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 30. Glam Rock / Hard Rock  —  Queen — Under Pressure - Remastered 2011
**Hours:** 40.0  |  **Tracks:** 23  |  **Peak:** 2020  |  **Tags:** rock, glam rock, hard rock, art rock, british

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 31. Blues Rock  —  Keith Richards — Struggle
**Hours:** 39.5  |  **Tracks:** 20  |  **Peak:** 2021  |  **Tags:** rock, blues rock

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 32. Metal  —  The Clash — London Calling - Remastered
**Hours:** 37.3  |  **Tracks:** 21  |  **Peak:** 2020  |  **Tags:** metal, hard rock, punk rock, grunge, traditional doom metal

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?

### 33. Deutschrock / Singer-Songwriter  —  Steppenwolf — Magic Carpet Ride
**Hours:** 26.9  |  **Tracks:** 20  |  **Peak:** 2020  |  **Tags:** rock, deutschrock, german, singer-songwriter, hard rock

**Reflection:** Welche Lebensphase / Stimmung deckt das bei dir ab? Wenn du diesen Cluster hörst — was kommt zurück?
