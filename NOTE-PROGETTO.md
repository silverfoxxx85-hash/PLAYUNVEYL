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
- **Pannello "Parole e difficoltà" (deve entrare senza scorrere su 390×664):**
  - via il titolo "Parole e difficoltà" (resta solo per i lettori di schermo; si apre dal pulsante "Parole" e ha la maniglia);
  - via la legenda "Nascoste / Visibili", via il riquadro statistiche ("griglia 5×7" e "4 parole nascoste" tolti: si vedono dall'anteprima);
  - il tempo stimato va sotto la difficoltà: "Circa 2 min per svelarla", si aggiorna cambiando difficoltà;
  - "Modifica testo" diventa solo icona (matita che scrive su una riga, 40 px, aria-label "Modifica testo"), in alto a destra accanto alla frase;
  - la frase va a capo dopo "parola": "Tocca una parola / per nasconderla o mostrarla";
  - via "Rimescola la griglia" (va nell'anteprima);
  - "Fatto" sempre visibile in fondo (sticky); correggere i pulsanti schiacciati: il contenuto del pannello deve scorrere, non comprimersi (flex-shrink:0 sugli elementi).
- **Chi gioca:** prima lettera in lilla nelle caselle del messaggio, mai nella griglia. Aiuto disponibile da subito.
- **Vittoria:** resta il ritaglio 3:4 scelto da chi crea, il più grande possibile, con il messaggio sotto. Sugli schermi bassi o su desktop il messaggio scorre sopra l'immagine.
- **Anteprima del link:** "Ti ho nascosto qualcosa", con l'immagine `og.png` che ha le caselle e l'icona.

## Fatto il 6 ottobre 2026 (branch word-challenge)
Decisioni prese con Fara e già implementate. Provate con Playwright su 375×553 (iPhone SE Safari), 360×640, 390×664 (iPhone 13 Safari) e 390×844, con un messaggio di 50 caratteri.
- **Scrittura:** a tastiera aperta la pillola accanto al campo fa da stato ("Aggiungi parole" → "Fatto") e il pulsante in basso è nascosto (su iPhone finirebbe sotto la tastiera). A tastiera chiusa la pillola sparisce e il pulsante grande in basso fa da stato: "Aggiungi parole" (scuro, riapre la tastiera) → "Avanti". Nessun messaggio d'errore. Funzione `syncFoot()`.
- **Anteprima:** la scheda "La sua sfida" resta intera; la foto si adatta all'altezza (`layoutPreview`, minimo 160 px di altezza), così scheda, pulsanti e footer entrano senza scorrere. Su schermi bassi (max-height 600 px) spazi ridotti e frase "Trovando le parole…" nascosta.
  - Tre pulsanti a colonne uguali sotto la scheda: **Testo · Parole · Rimescola**.
  - "Prova a giocare" e "Invia" affiancati in basso (`.cfoot.row`).
  - Rimescola: le lettere nuove arrivano con un piccolo rimbalzo (`.ptiles.shuf`), niente più avviso "Griglia rimescolata".
  - Misure con messaggio lungo: foto 121×161 (SE), 173×231 (iPhone 13 Safari), 270×360 (schermi alti).
- **Pannello "Parole e difficoltà":** senza titolo (resta per i lettori di schermo e torna come "Modifica il testo" in modifica), senza legenda e senza statistiche. Frase su due righe "Tocca una parola / per nasconderla o mostrarla" con la matita (solo icona, matita su una riga) in alto a destra. Sotto la difficoltà "Circa N minuti per svelarla" (dipende dalle lettere nascoste, non dalla difficoltà). "Fatto" sempre visibile in fondo; niente più pulsanti schiacciati (`flex-shrink: 0`).
- **Angoli della cornice:** il raggio segue la griglia (`cornerR`: al massimo 3,4 × margine + raggio delle caselle; 22 px anteprima, 26 px partita come tetto), così sulle griglie piccole le caselle d'angolo non vengono tagliate.
- **Home e intro di chi riceve:** la demo si rimpicciolisce fino a 0,45 per far entrare tutto; i pulsanti non si comprimono più (prima "Inizia" su SE era alto 19 px).
- **Partita:** niente cronometro durante il gioco (il tempo si misura e compare solo alla fine); l'avanzamento ("0 di 6" con i pallini) sta al centro della barra in alto. Con più di 7 parole restano solo i numeri.
- **Vittoria:** "Rispondi" diventa "Fai sapere com'è andata" (forma senza genere).
- **Statistiche:** rimandate. Ipotesi pronta: GoatCounter (gratuito, senza cookie), 8 eventi su creazione, gioco e passaparola; serve che Fara crei l'account.

## Scelte di prodotto (ottobre 2026)
- **Chi invia non riceve notifiche:** per ora basta "Rispondi", che condivide il risultato in stile cartolina (tempo, quadratini, aiuti). Niente servizio dedicato finché non si fa la parte privacy.
- **Niente "Mostrami tutto":** chi si blocca aspetta gli aiuti. È il cuore del gioco: trasformare l'attesa in desiderio. Gli aiuti garantiscono comunque la fine (3 livelli per parola: prima lettera, ultima, parola intera).
- **Foto e video non si salvano:** scelta voluta, coerente con la privacy. Già oggi il media non si trascina e non si tiene premuto per salvarlo. Limiti noti (screenshot, indirizzo Cloudinary leggibile nel link).

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
