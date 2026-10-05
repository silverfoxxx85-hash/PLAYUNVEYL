# unveil — note di passaggio

Promemoria per riprendere il lavoro in una nuova sessione. Contiene le decisioni prese con Fara e le cose ancora da fare.

## Come lavoriamo
- Si parla in italiano. Prima si discute ("non generare nulla, parliamone"), poi mockup o anteprime, poi si implementa al "vai"/"procedi".
- Ogni versione: build, test con Playwright (solo Chromium), commit, consegna di `index.html` più le schermate.
- Le icone sono Flaticon Pro, con l'abbonamento di Fara: niente crediti da aggiungere.
- Non ricentrare l'icona della ragazza nella demo.

## Struttura
- `src/app.html` è il sorgente. `src/gen.js` è il generatore della griglia: deterministico, versionato con `GEN_VERSION`.
- `tools/build.sh` inserisce i font in base64 (Unbounded, DM Sans) e gen.js, e scrive `index.html` nella radice. È un unico file per GitHub Pages.
- `tools/lottie2svg.py` converte le animazioni Lottie in SVG animato (SMIL).
- Link condiviso: `#g=` più JSON in base64url `{v,m,h,s,d,k,u,c,n,f}`:
  - `n` = nome di chi invia;
  - `f` = indizi: 1 normale (prima lettera visibile), 0 difficile; se manca vale normale;
  - `c` = ritaglio [x,y,w,h] in frazioni.
- I media vengono caricati su Cloudinary, con caricamento non firmato e preset `sito_upload`.

## Stato attuale (branch word-challenge)
- **Home compatta:** un unico blocco centrato. Demo di misura massima 216 px, uguale per chi crea e chi riceve.
- **Pagina lilla allo svelamento:** la cartolina ruota mentre si allarga (`FLOOD_MODE='spin'`) e la pagina si inverte. L'icona della demo è solo sfocata e l'animazione parte una volta sola.
- **Messaggio:** massimo 50 caratteri, minimo 10 lettere nascoste. Il massimo di 35 lettere resta solo come limite tecnico.
- **Il pulsante fa da stato:**
  - scrittura: "Aggiungi parole" → "Fatto";
  - pannello: "Nascondi altre parole" / "Troppe lettere: mostrane una" / "Cambia qualche parola" → "Fatto".
- **Avvisi:** nessun avviso dentro le pagine. Ci sono messaggi in alto che spariscono da soli (`notify`). Gli errori sul file compaiono dentro il riquadro della foto. L'errore di caricamento nell'invio ha lo stile d'errore e "Riprova".
- **Pannello "Parole e difficoltà":**
  - ogni tocco funziona; «amo» e «amore» si scambiano da sole;
  - "Modifica testo" funziona dentro il pannello;
  - difficoltà Normale/Difficile.
- **Chi gioca:** prima lettera in lilla nelle caselle del messaggio, mai nella griglia. Aiuto disponibile da subito.
- **Vittoria:** resta il ritaglio 3:4 scelto da chi crea, il più grande possibile, con il messaggio sotto. Sugli schermi bassi o su desktop il messaggio scorre sopra l'immagine.
- **Anteprima del link:** "Ti ho nascosto qualcosa", con l'immagine `og.png` che ha le caselle e l'icona.

## Deciso, da fare (branch word-challenge)
- **Rimescola la griglia:** esce dal pannello "Parole e difficoltà" e diventa una terza pillola "Rimescola" nella pagina dell'anteprima, accanto a "Modifica" e "Parole e difficoltà". Così l'effetto si vede subito sulla griglia. Aggiungere un piccolo movimento delle lettere al rimescolamento e togliere l'avviso "Griglia rimescolata". Da verificare che le tre pillole stiano in una riga sui telefoni stretti.
- **Pulsante grande nella scrittura:** a tastiera aperta resta tutto com'è (la pillola fa da stato: "Aggiungi parole" → "Fatto", più il tasto Invio). A tastiera chiusa la stessa logica passa al pulsante grande in basso, come negli altri passi: dice "Aggiungi parole", attenuato, finché il messaggio non basta, e diventa "Avanti" quando è pronto. La pillola si nasconde. Nessun messaggio d'errore. A tastiera aperta il pulsante in basso resta nascosto su tutti i telefoni (su iPhone finirebbe sotto la tastiera).
- **Pagina dell'anteprima (deve entrare senza scorrere):**
  - la scheda "La sua sfida" resta intera sotto la foto: è il riscontro di come apparirà a chi riceve;
  - la foto si adatta all'altezza disponibile (non più fissa a 270×360), finché scheda, pulsanti e footer stanno tutti nello schermo;
  - sotto la scheda, tre pulsanti a colonne uguali, larghi quanto la scheda: **Testo · Parole · Rimescola** (icona + nome su una riga). "Testo" sostituisce "Modifica", "Parole" sostituisce "Parole e difficoltà" (il pannello mantiene il titolo completo);
  - "Prova a giocare" e "Invia" affiancati in basso: Prova a sinistra (solo bordo), Invia a destra (pieno).
  - Misure dal mockup: iPhone 13 Safari (390×664) foto circa 206×275; iPhone SE (375×553) resta stretto, da verificare la leggibilità delle lettere.
- **Pannello "Parole e difficoltà":** togliere la statistica "griglia 5×7" (gergo per chi crea), tenere parole nascoste e tempo stimato; il rimescolamento esce (vedi sopra). Correggere i pulsanti in fondo che su schermi bassi (390×664) vengono schiacciati in altezza.

## Prossimo passo concordato: branch `griglia-5x8`
Da fare su una branch separata, senza toccare word-challenge.
- **Cornice:** 5:8 invece di 3:4, nell'inquadratura, nell'anteprima e nella partita.
- **Griglie:** 4×6 per i messaggi corti e 5×8 per quelli medi. Massimo circa 30 lettere.
- **Link già inviati:** aumentare `GEN_VERSION` e tenere le vecchie misure, così i link vecchi generano la stessa griglia.
- **Vittoria:** riempire lo schermo (cover). Con 5:8 il taglio è di circa il 3–5% per lato. Su desktop o in orizzontale si resta all'altezza massima, con lo sfondo sfocato ai lati.
- **Consegna:** come file separato da provare (es. `index-5x8.html`).

## Rimandato (dopo)
- **Privacy:** cifratura del media nel browser, cancellazione dopo la soluzione o dopo 24 ore, link usabile una volta, pagina d'aiuto, segnalazioni.
- **Nome nell'anteprima del link:** "Alberto ti sta nascondendo qualcosa". Richiede un piccolo servizio (es. Cloudflare Worker) e va fatto insieme alla privacy.
- **Validazione dell'idea e statistiche d'uso.**
