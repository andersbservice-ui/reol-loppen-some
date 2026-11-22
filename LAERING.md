# LAERING – hvad vi har lært + eksperiment-log

Læs før hver kørsel. Opdatér hver søndag.

## Succes-regel
Et opslag er en **vinder** hvis: ≥ 2x baseline-visninger ELLER ≥ 3 kommentarer ELLER ≥ 5 delinger.
Vindere får 2 nye varianter. Tabere flyttes til "Virker ikke".
Mindst ét "vildt" eksperiment om ugen.

## Baseline (opdateres når vi har tal)
- Visninger (median, sidste 28 dage): – (ingen data endnu)
- Baseline-format: "Spar penge"-video, 5 scener, 13-20 s, krog med pris, outro "Kom forbi Reol Loppen".

## Det ved vi på forhånd (research, ikke egne tal endnu)
- De første 1-2 sek. afgør alt. Første frame = lyst, konkret billede + krog (påstand/tal, max 8 ord).
- Billedskift hvert 1,5-2,5 s. Lyd fra første frame. Voiceover hjælper mest.
- Tal skaber nysgerrighed. Lokal vinkel (Langeskov) hjælper.
- Caption: gentag krogen + let spørgsmål. 3-6 hashtags.

## Idé-bank til Reol Loppen
- "Ny koster den X kr – hos os Y kr" (spar penge)
- "Ugens 5 fund under 50 kr" (karrusel)
- "Gæt prisen" (quiz – svar i kommentarer / sidste slide)
- "Det her stod på reol 23 i morges" (fund-historie)
- "Rigtigt eller forkert: brugt er altid dårligere" (myteknuser)
- Vilde: "Del 1 af 3", kommentar-ord ("Skriv LAMPE, så viser vi prisen"), 6-9 s loop uden outro, POV-tekst.

## Eksperiment-log
| ID | Dato/tid | Kanal | Format | Hypotese | Ændring vs. baseline | Visninger | Kommentarer | Delinger | Resultat |
|---|---|---|---|---|---|---|---|---|---|
| E01 | søn 22/11 15:45 | TikTok + IG Reel | Video, fund-tur (jul), 13 s, uden stemme | Julevinkel i nov. giver mange visninger | BASELINE (første video) | | | | afventer |
| K01 | tir 24/11 18:00 | TikTok foto + IG karrusel | Karrusel 7 slides, "5 ting du finder" | Nummererede fund giver gem/delinger | Baseline for karruseller | | | | afventer |
| E02 | tor 26/11 18:00 | TikTok + IG Reel | Video, butikstur, lokal krog | Lokal krog ("Langeskov") slår E01 | Krog: lokal vinkel i stedet for jul | | | | afventer |

## Virker
- Kunden har godkendt stilen (22/11 2026): venstrestillet tekst, gul fremhævning, outro "Kom forbi Reol Loppen".

## Virker ikke
- (endnu tom)

## Tekniske faldgruber
- TikTok-fotoopslag: kun JPEG/WEBP (lav_karrusel.py laver JPEG).
- Metricool cacher URL: ændret fil = nyt filnavn. ?v=2 virker ikke.
- Unsplash: brug download-URL fra download_asset.
- Hvidt logo: altid mørk baggrund bag (outro-panelet er mørkt).
- Piper-stemmen kunne ikke installeres i første opsætning (nov 2026): videoer har kun musik + effekter indtil den er på plads.

## Brugte fotos
| Foto (filnavn i Drive) | Brugt i | Dato |
|---|---|---|
| IMG_1856 | E01, K01 | nov 2026 |
| IMG_1857 | E02 (beskåret, bannere med bilmærker skåret væk) – senere erstattet af 1865 | nov 2026 |
| IMG_1858 | E02, K01 | nov 2026 |
| IMG_1859 | E02, K01 | nov 2026 |
| IMG_1860 | E01, K01 | nov 2026 |
| IMG_1861 | E01, K01 | nov 2026 |
| IMG_1862 | E01, K01 (pris 45 kr aflæst på prismærke) | nov 2026 |
| IMG_1863 | E02, K01 | nov 2026 |
| IMG_1864 | E02 | nov 2026 |
| IMG_1865 | E01, E02 (beskåret uden bannere) | nov 2026 |

OBS: IMG_1857/1865 har bannere med bilmærker (Michelin/BMW) til venstre – skær dem altid fra. IMG_1864 viser kasseapparat med Saldi/Flatpay-logo – skær fra.
