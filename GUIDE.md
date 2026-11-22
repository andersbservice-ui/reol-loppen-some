# GUIDE – Reol Loppens automatiske sociale medier

Læs denne fil og LAERING.md før hver kørsel.

## Butikken
- **Reol Loppen**, Langeskov Centeret. Loppebutik med reoler.
- Målgruppe: kunder der vil købe (genbrugsjægere, familier, samlere i og omkring Langeskov).
- Emner: ugens fund · genbrug og spar penge (ny-pris vs. vores pris) · butikken og hverdagen.
- Fast slutlinje: **"Kom forbi Reol Loppen" / "Langeskov Centeret"** (står i tools/brand.json).
- Kanaler: TikTok + Instagram (Reels/karruseller) via Metricool.
- Frekvens: 3-4 opslag om ugen (fx 2 videoer + 1-2 karruseller).
- Billeder: KUN butikkens egne fotos fra Google Drive-mappen **"Reol Loppen – Til sociale medier"**
  Aldrig Unsplash eller andre fotos.
  Hent nye fotos til `assets/fotos/`, se hvad der er på dem, og skriv selv tekst og manus.
  Står der en pris i filnavnet (fx `lampe_45kr.jpg`), må den bruges. Ellers ingen pris.
  Notér brugte fotos i LAERING.md ("Brugte fotos"), så samme foto ikke bruges to gange.

## Værktøjer
| Fil | Hvad | Kommando |
|---|---|---|
| tools/lav_video.py | JSON-spec → mp4 1080x1920, 30 fps, altid med lyd | `python3 tools/lav_video.py specs/E01.json` |
| tools/lyd.py | Eget lydspor (beat, whoosh, pop, chime). Bruges automatisk | – |
| tools/stemme.py | Dansk piper-stemme. Bruges automatisk hvis `tools/piper/piper` + `da_DK-talesyntese-medium.onnx` findes | – |
| tools/lav_karrusel.py | JSON-spec → 5-7 JPEG-slides | `python3 tools/lav_karrusel.py specs/K01.json` |
| tools/tjek-safezone.sh | Kontaktark med TikToks dækkede felter i rødt | `tools/tjek-safezone.sh output/E01.mp4` |
| tools/brand.json | Navn, farver, logo, slutlinje, faste hashtags | – |

Eksempler: `specs/eksempel_video.json`, `specs/eksempel_karrusel.json`.

## Sådan laves et opslag
1. Vælg eksperiment i LAERING.md (ID, hypotese, ÉN ændring mod baseline). Skriv det ind FØR udgivelse.
2. Skriv spec. Video: 5-8 scener à 1,5-2,5 s. Manus som talesprog, max ~2,5 ord/s.
3. Render. Kør tjek-safezone.sh og SE på kontaktarket:
   - Første frame lys og konkret, krogen synlig fra 0,0 s.
   - Ingen tekst i røde felter. Intet ansigt, ingen nummerplader.
   - Lyd findes (ffprobe viser audio-stream).
4. Push til repo (grenen `indhold`, aldrig main). Media = raw.githubusercontent.com-links.
   Ændret fil = NYT filnavn (Metricool cacher).
5. Planlæg i Metricool (createScheduledPost), tjek med getScheduledPosts.

## Layout (540x960-koordinater)
- Overskrift øverst til venstre fra y 112. Tekst/undertekster nederst til venstre, slutter y 740, bredde ≤ 420.
- TikTok dækker y<110, y>750, og x>460 i y 380-780.
- Mørk gradient kun top og bund; fotoet lyst i midten.

## Metricool
- Brand "Reol-Loppen", blogId/brand id **7957274**. Tidszone: Europe/Copenhagen (Metricool viser Europe/Madrid = samme tid).
- Konti: Instagram `reol_loppen_langeskov`, TikTok `reolloppen`, Facebook-side (bruges ikke endnu).
- Fotomappe i Google Drive: id `1qK0Ch83BQPmcamnI_2lYE1Rs27cPaaaU`.
- TikTok: `tiktokData`: title (påkrævet), privacyOption PUBLIC_TO_EVERYONE,
  commercialContentOwnBrand true, isAigc true. Karruseller: autoAddMusic true.
- Instagram: videoer som Reels, karruseller som karrusel (JPEG).
- Tider: hverdage 18:00, weekend 12:00 (Europe/Copenhagen). Justér efter getBestTimeToPostByNetwork.
- Opdateret opslag skifter id (uuid bliver). Send hele opslaget.

## Caption-skabelon
```
<krog gentaget>
<let spørgsmål, fx "Hvad ville du have købt – 1, 2 eller 3?">
Kom forbi Reol Loppen i Langeskov Centeret 📍
#reolloppen #langeskov #loppefund #genbrug (+1-2 emne-hashtags)
```

## Regler
- Ingen falske påstande eller lovede resultater. Priser kun hvis de er rigtige.
- Ingen genkendelige ansigter, nummerplader eller tydelige bilmærke-logoer.
- Salg kun i outro og sidste linje af teksten.
