# unveil — note di passaggio

Promemoria per riprendere il lavoro in una nuova sessione. Contiene le decisioni prese con Fara e le cose ancora da fare.

## Come lavoriamo
- Si parla in italiano. Prima si discute ("non generare nulla, parliamone"), poi mockup o anteprime, poi si implementa al "vai"/"procedi".
- Ogni versione: build, test con Playwright (solo Chromium), commit, consegna di `index.html` più le schermate.
- Le icone sono Flaticon Pro, con l'abbonamento di Fara: niente crediti da aggiungere.
- Non ricentrare l'icona della ragazza nella demo.

## Struttura
- `src/app.html` è il sorgente. `src/gen.js` è il generatore della griglia: deterministico, versionato con `GEN_VERSION`.
- `tools/build.sh` inserisce i caratteri in base64 (Silkscreen Bold e Figtree) e gen.js, e scrive `index.html` nella radice. È un unico file per GitHub Pages.
- `tools/fonts.py` prepara i caratteri: parte dagli originali in `src/fonts/originali/`, tiene solo i caratteri latini e scrive `src/fonts/silkscreen-bold.woff` e `figtree.woff` (`python3 tools/fonts.py`, poi `tools/build.sh`). Licenze in `src/fonts/OFL-Figtree-Silkscreen.txt`.
- `tools/pixelfont.py` (i caratteri pixel disegnati da noi, ora non più usati) resta per memoria: rigenera i TTF se mai servissero.
- `tools/lottie2svg.py` converte le animazioni Lottie in SVG animato (SMIL). Gestisce anche i livelli visibili solo in un intervallo (ip/op) e i colori dati per espressione (Base Color → tratti, Highlight → accenti).
- Icone dei momenti: sorgenti Lottie in `src/art/lottie/`, convertite in `src/art/ico-NOME.svg` (`python3 tools/lottie2svg.py src/art/lottie/NOME.json src/art/ico-NOME.svg`); `tools/build.sh` le inserisce tutte in `ICONS.NOME`. Ricolorate con `ICO_LILLA` (tratti #b3a6ff, accenti #e9e4ff), animazione una volta sola.
- Link condiviso: `#g=` più JSON in base64url `{v,m,h,s,d,k,u,c,n,f}`:
  - `n` = nome di chi invia;
  - `f` = indizi: 1 normale (prima lettera visibile), 0 difficile; se manca vale normale;
  - `c` = ritaglio [x,y,w,h] in frazioni.
- I media vengono caricati su Cloudinary, con caricamento non firmato e preset `sito_upload`.

## Stato attuale (branch word-challenge)
- **Home e intro di chi riceve gemelle:** stessi blocchi nella stessa posizione (logo, guida animata, puntini, testi, frase fissa, pulsante). Demo di misura massima 216 px, identica nelle due pagine. Vedi sotto, "Guida animata".
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
- **Icone animate dei momenti** (Flaticon, abbonamento di Fara):
  - scelta della foto: **immagine** (due foto che si rimescolano) sopra il +; nascosta su schermi bassi (max-height 600 px) per non schiacciare il +;
  - scrittura: **messaggio** (telefono con fumetti # e cuore), al centro dello spazio libero sotto il campo, solo a tastiera chiusa, grande al massimo 150 px e nascosta sotto i 90 (`fitWriteArt`); riparte ogni volta che ricompare;
  - "Inviata!": **aeroplanino** al posto del logo, parte all'apertura e vola libero fuori dal riquadro;
  - pagina d'errore di chi riceve, tre casi (`gameError(kind)`): **latte** "Questa sfida è scaduta" (foto o video non più disponibili), **cuore spezzato** "Questo link non funziona" (link rotto o sfida non valida), **spina** "Sei offline" con pulsante "Riprova".
  - La ragazza della demo (home e intro) resta quella di prima (`ICO_ANIM`).
- **Niente più "sorpresa"** (suona vecchio): "sfida" dove parla chi riceve, "la tua foto / il tuo video" nel caricamento e nell'invio (`mediaName`).
- **Statistiche:** rimandate. Ipotesi pronta: GoatCounter (gratuito, senza cookie), 8 eventi su creazione, gioco e passaparola; serve che Fara crei l'account.

## Fatto il 6 ottobre 2026, seconda parte (branch word-challenge)
Decisioni prese con Fara e implementate (commit 2f25788 e successivo). Provate con Playwright su 375×553, 390×664, 390×844 e 1280×800.
- **Guida animata al posto della demo** (`mountGuide`, usata da home e intro): tre passi che avanzano da soli, un solo giro che finisce sul lilla. Toccando l'animazione riparte, toccando un puntino si salta a quel passo.
  - **Fine guida:** l'ultima frase resta circa un secondo sul lilla, poi svanisce e subito dopo, al suo posto, compare il pulsante "↻ Rivedi come funziona" (a contorno scuro, 46 px, secondario rispetto al pulsante pieno). Sempre in sequenza, mai in dissolvenza incrociata: frase via in 0,3 s, pausa, pulsante da trasparente a pieno in 0,35 s; al "Rivedi" il contrario. I puntini restano visibili sull'ultimo passo (`.gwrap`, classi `end` e `hold`). La griglia resta invisibile finché la guida non parte (niente lampo iniziale) e il primo testo non rifà la dissolvenza alla fine del logo iniziale.
  - Chi crea (`GUIDE_CREA`): "Scegli una foto / o un video." · "Scrivi una / frase segreta." · "Chi la riceve / dovrà trovarle." (sotto: "Ogni parola scoperta rivela parte dell'immagine."). Al passo 3 ECCOMI si trascina, QUI si tocca lettera per lettera.
  - Chi riceve (`GUIDE_GIOCA`), un'azione per passo:
    1. "Trova le parole / nella griglia." · "Trascina il dito o tocca le lettere una a una." Il dito trascina ECCOMI, che resta accesa.
    2. "Ogni parola scoperta / rivela parte della foto." ("del video" per i video), senza sottotitolo. ECCOMI sparisce e scopre un pezzo.
    3. "Trovale tutte." · "Se ti blocchi, usa l'aiuto." Il dito tocca Q, U, I; QUI sparisce e la foto si svela.
  - Ogni cambio di passo cade in un momento fermo (niente dito, niente selezioni a metà).
  - Nella demo niente aiuto e niente ingrandimento della casella selezionata (cambia solo colore): ingrandita, accanto alla parte già scoperta si fondeva col lilla e sembrava alta il doppio.
  - Anche il tutorial del "?" trascina ECCOMI e tocca QUI.
  - A capo scelti a mano con `<br>`, il resto con `text-wrap: balance`.
  - Tempi misurati: chi crea passi a 6,1 s e 9,6 s, "Rivedi" a 14 s; chi riceve passi a 6,0 s e 8,9 s, "Rivedi" a 12 s.
- **Frase della griglia: ECCOMI QUI** (`DEMO_L = 'ECCQMOUII'`, E C C / Q M O / U I I). Nove lettere, nessuna casella avanzata (`DEMO_REST` vuoto). ECCOMI si trascina con un pezzo in diagonale, QUI si tocca. Niente caselle del messaggio nella demo: si scoprono nel gioco.
- **Home e intro gemelle:** logo in alto nella stessa posizione, stessi margini e spazi (`#introOv` copia `.home`), stessa misura della demo. Sotto i testi c'è una frase fissa (`.tagline`): "Spoiler: dovrà guadagnarsela." per chi crea, "Alberto ti sta nascondendo qualcosa" per chi riceve ("Qualcuno" se manca il nome, "Bentornato!" alla ripresa). Lilla sul nero, bianca quando la pagina diventa lilla. Sta sempre in due righe: con nomi lunghi il carattere si rimpicciolisce (`fitTag`), così nulla si sposta.
- **Svelamento lilla:** l'immagine della demo è rientrata di 6 px con raggio 18 (esattamente dentro la cornice), è sfocata solo l'icona e il lilla parte dal rettangolo dell'immagine: niente "saltino". Sul lilla il pulsante è bianco (#f6eef4) con testo scuro e senza ombra; il puntino della "ı" del logo diventa bianco.
- **Buchi morbidi nella demo** (`holesPath(open, g, true)`): le parti scoperte hanno la forma delle caselle unite (angoli arrotondati, raccordi concavi intorno alle caselle ancora coperte). Partita e anteprima usano ancora la forma vecchia.
- **"?" nell'intestazione della creazione** (`#helpBtn`, al posto del logo): apre il tutorial in tre passi (`TUT_STEPS`) su scheda scura, con l'ultimo passo che si allaga di lilla. Si apre solo dal pulsante: niente apertura automatica, niente "Non mostrarlo più".
- **Sfondo animato (doodle):** caselle con le lettere a contorno, come le altre icone (anche nello sfondo fisso delle altre pagine). Ogni icona ha la sua cella (`DD_CELL` 100 px, stacco minimo `DD_GAP` 6 px) e non ne esce mai, nemmeno ruotando: le icone non possono sovrapporsi. Verificato con 400 istanti casuali per schermo, stacco minimo misurato circa 10 px.
- **Generatore v3 (`GEN_VERSION = 3`): il centro della griglia coperto da parole.** Una parola scelta a caso parte dal centro, e fra le prime griglie valide (fino a 10) si tiene quella con il centro più coperto (`centerScore`: «cuore» = 1-4 caselle più vicine al centro, «zona centrale» = riquadro di metà lato). Centro coperto da parole: 26% prima, 97% ora (480 griglie di prova). Effetto: il riempimento finisce più spesso ai bordi, a volte in basso.
  - `generate({…, v})` usa la versione del link: chi riceve passa `cfg.v || 2`, quindi i link v2 danno esattamente la griglia di prima (verificato su 480 griglie). I link nuovi hanno `v: 3`.
- **Rimescola senza ripetizioni** (`pickShuffleSeed`): prima a volte le parole tornavano negli stessi posti (cambiavano solo le lettere di riempimento). Ora si confronta la disposizione delle parole: si scartano quella attuale e le ultime 4 viste, e si chiede che cambi almeno un terzo delle lettere (fino a 30 tentativi). Con poche combinazioni possibili si gira fra quelle, mai la stessa due volte di fila.
- **Vittoria in tre momenti** (dal 7 ottobre senza invito al pizzico) (`vicPlay`, stato in `VIC`; la foto è sempre il rettangolo del ritaglio, anche più grande dello schermo):
  1. *Spettacolo:* la cartolina si mette a fuoco al suo posto, si allarga a tutto schermo ancorata a sinistra (in orizzontale: in alto), coriandoli, scorre piano fino all'altro lato e torna lentamente al centro, sempre a schermo pieno. Nessun rimpicciolimento. Comandi bloccati: un tocco salta alla foto ferma al centro.
  2. *Esplorazione:* al centro compare un box lilla (132 px, angoli 34 px, anello scuro) con l'icona animata del pizzico (Flaticon, `ICONS.pinch`, mano scura e frecce bianche, box senza ombra), solo la prima volta su quel telefono (`unveil:pinch`); dopo ~2,7 s, o al primo tocco, il box svanisce e poi compare la freccia "Avanti" in basso a destra (cerchio lilla 56 px; dopo 6 s un impulso). Niente testi sopra la foto.
  3. *Azione:* con la freccia sale dal basso il pannello (fondo pieno, angoli in alto 28 px) con messaggio e pulsanti, sopra la foto che resta a schermo pieno.
  - **Zoom:** due dita, rotellina/trackpad: da "intera con 12 px di margine" a 5× lo schermo pieno; elastico oltre i limiti. Più grande dello schermo si sposta fino ai bordi (con il pannello aperto, fino al pannello). Doppio tocco: alterna intera e schermo pieno.
  - **Angoli:** seguono sempre lo spazio libero: dritti quando la foto tocca i bordi, 26 px (raggio della partita) con 12 px di margine o più.
  - "Riduci movimento": niente spettacolo, subito la foto a schermo pieno. Riaprendo una sfida già risolta: foto e pannello subito.
- **Riquadro "La sua sfida" a messaggio vuoto:** "Ogni parola inserita diventerà una fila di caselle vuote da scoprire." e, più piccolo, "Quelle di una o due lettere restano visibili." Mentre si scrive, "Le parole di una o due lettere restano visibili." compare sotto il messaggio solo se ce n'è almeno una (`#seeNote`).
- **Meta description:** "Nascondi una foto o un video tra le parole di un messaggio: per vederla, dovrà trovarle." (og:description invariata).

## Fatto il 7 ottobre 2026 (branch `caratteri-pixel`, nata da word-challenge)
Modifica delicata: tocca tutti i testi dell'app. Per questo sta su una branch nuova; word-challenge resta com'era.
- **Caratteri pixel "unveil Pixel"**, disegnati da noi (nessuna licenza), veri TTF generati da `tools/pixelfont.py`:
  - **Bold** ("Compresso", 5×9 pixel, aste di 2): solo maiuscole (le minuscole mostrano le maiuscole), numeri, accenti, punteggiatura. Pesi 600–900.
  - **Medium** (4×9, aste di 1): maiuscole, minuscole con ascendenti e discendenti, numeri, accenti italiani, punteggiatura (anche ’ “ ” … ·). Pesi 400–599.
  - Ogni pixel è un contorno; i pixel vicini si sovrappongono di 4 unità e si arrotondano solo gli angoli esterni. Pixel = 80 unità su 1000; maiuscola 720; ascendente 960, discendente 240: (960−240)/2 = 360 = metà maiuscola, così le lettere stanno al centro in altezza. Mezzo pixel di spalla a sinistra e a destra: al centro anche in larghezza (misurato da 18 a 40 px: scarto entro mezzo pixel).
  - (Sostituiti nella seconda parte: vedi sotto.) Uso: `--display` (Bold) per logo, titoli, pulsanti, griglie; `--pixel` e `--body` (Medium) per tutto il resto. Attenzione: un testo con font-weight 600 o più esce in Bold maiuscolo; nei testi del messaggio il peso è forzato a 500.
  - I testi piccoli sono stati alzati di 2 px (12→14, 13→15, 14→16, 15→17, 16→18, 17→19): il Medium è più stretto di DM Sans.
  - Logo: "UNVEIL" in Bold, con un pixel lilla sopra la I.
  - Da provare su Safari/iPhone (testati solo Chromium e FreeType). Peso: circa 126 KB di TTF; si può ridurre unendo i contorni.
- **Schermata di gioco "Ordine":** messaggio con pillole (un posto fisso per lettera, pallini al posto delle lettere mancanti, lettere che si riempiono una a una quando la parola è trovata); barra di avanzamento a segmenti; altezza del messaggio fissata alla partenza, così la griglia non cambia misura; buchi morbidi anche in partita e nell'anteprima.
- **Luce dietro la griglia:** alone che respira più un anello di luce che segue il dito lungo la cornice (angolo dal centro, molla morbida, più intensa vicino al bordo) e un impulso dove si trova una parola. Si spegne alla vittoria; con "Riduci movimento" niente anello.
- **Musica lo-fi generata** (`makeMusic`, Web Audio, nessun file): piano elettrico con tremolo ed eco, basso, batteria con swing, fruscio di vinile; 74 bpm, in Do come gli effetti. Generativa: voicing, rullate e piccole frasi cambiano. Parte con "Inizia", segue il pulsante dei suoni, si abbassa alla vittoria, tace con l'audio del video, si ferma uscendo e in pausa quando l'app va in secondo piano. Le fonti di musica libera online non erano raggiungibili; se Fara vuole un brano vero (es. Pixabay Music), va come file separato caricato all'inizio della partita.

## Fatto il 7 ottobre 2026, seconda parte (branch `caratteri-pixel`)
I caratteri pixel disegnati da noi non hanno convinto Fara: sostituiti con due caratteri scelti da lei (entrambi SIL OFL 1.1, gratuiti, file in `src/fonts/originali/`).
- **Silkscreen Bold** (`--display`) per titoli, frase fissa, logo, griglie (partita, anteprima, guida, caselle dello sfondo) e **parole da trovare**: le lettere nelle pillole e la parola quando viene trovata.
  - Le minuscole di Silkscreen sono uguali alle maiuscole. Pixel = 125 unità, maiuscola 625 (5 pixel).
  - Ascendente ritoccato a 875 (`tools/fonts.py`): (875−250)/2 = 312 = metà maiuscola, così le lettere stanno al centro delle caselle (misurato: scarto entro mezzo pixel). Spalle già simmetriche.
  - Tra le lettere un pixel invece di due nei titoli (`letter-spacing: -.125em`), titoli con `text-wrap: balance`.
  - Lettere della griglia al 60% della casella (prima 52%): Silkscreen ha la maiuscola più bassa.
- **Figtree** (variabile 300–900, solo dritto) per tutto il resto: messaggio, pulsanti, testi, campi. Le misure dei testi sono tornate quelle di prima dei caratteri pixel.
- DM Sans, Unbounded e i TTF "unveil Pixel" non sono più incorporati e sono stati tolti da `src/fonts` (restano nella storia della branch).
- Il resto della prima parte (schermata "Ordine", luce ad anello, musica lo-fi, frecce bianche del pizzico) resta invariato.

## Fatto il 7 ottobre 2026, terza parte (branch `caratteri-pixel`)
Prove di Fara e della sua compagna sul telefono; varianti della frase confrontate in `varianti-frase` (scelta: B, misura media, parola trovata in Regular).
- **La frase (partita, "La sua sfida", messaggio della vittoria):** parole visibili tutte in Figtree 600 bianco, stessa misura (via il grigio e la misura più piccola delle parole corte). Parole del gioco in **Silkscreen Regular viola** (`--word`), al 96% della misura del testo (a metà fra minuscole e maiuscole di Figtree):
  - pillola: una riga di testo (`line-height: 1`, padding uguale sopra e sotto le maiuscole di Silkscreen), così lettere e trattini poggiano sulla **stessa linea di base** di Figtree;
  - lettere mancanti: **trattini bassi** di 4×1 pixel di Silkscreen sulla linea di base, uno spazio fisso di 6 pixel per lettera (stesso ritmo delle lettere: rivelandole il ritmo non cambia);
  - parola trovata: resta in Silkscreen Regular viola dentro la frase; nella vittoria il messaggio mostra in viola tutte le parole nascoste.
  - Il grigio resta solo nel pannello "Tocca una parola" (parole che non si possono nascondere).
- **Frase fissa:** "Spoiler:" e il nome di chi invia in bianco, il resto lilla; sul lilla la parola chiave diventa scura e il resto bianco (`.tagline .tk`).
- **Scatta e Registra:** fondo viola, icona e testo scuri.
- **Guida obbligatoria alla prima visita** (`gateButton`, `d.lock/unlock` in `mountGuide`): la guida non avanza da sola; a destra dei puntini c'è la pillola "Avanti". Il pulsante grande è spento con "Guarda come si gioca · 1/3" (in home "Guarda come funziona · n/3"); toccato fa un piccolo scatto e fa pulsare "Avanti". Si accende ("Inizia" / "Nascondi qualcosa", con un rimbalzo) solo a fine animazione del terzo passo. Ricordato per telefono (`unveil:guida:gioca`, `unveil:guida:crea`). In home non si blocca se su quel telefono si è già vista la guida di gioco; niente blocco per "Prova a giocare", per chi riprende una partita e con "Riduci movimento".
- **Vittoria:** tolto l'invito al pizzico (icona e box); finito lo spettacolo arriva subito la freccia, ora senza ombra né bordo scuro.
- **Una sola colonna:** margine laterale 24 px per pagine, pannelli e piè di pagina; pulsanti grandi alti 54 px e larghi al massimo 360 px, allineati alle schede.

## Fatto il 7 ottobre 2026, quarta parte (branch `splash-e-scrittura`, nata da caratteri-pixel)
- **Frase fissa nello splash:** sotto il logo, "Nascondi qualcosa" per chi crea (stesso tempo di prima) e "Alberto ti ha nascosto qualcosa" per chi riceve (nome in bianco, ~1 s in più; un tocco salta). Tolte le frasi fisse sotto le guide: le due home restano identiche e la guida cresce fino a 270 px (`DEMO_MAX = 1.5`). Il nome resta per i lettori di schermo (`#introTitle`, nascosto) e nel titolo della scheda.
- **"Spoiler: dovrà guadagnarsela."** ora è il sottotitolo di "Inviata!" / "Link copiato!" (Silkscreen, Spoiler in bianco).
- **Guida alla prima visita:** puntini e freccia sono un solo comando centrato (pillola scura con il cerchio lilla in fondo, `.gdots.gated`); a guida finita la pillola sparisce e restano i puntini.
- **"Prova a giocare":** niente intro, si va subito alla partita.
- **Scrittura:** la parola che si sta scrivendo conta subito (nel conteggio e in "La sua sfida", come pillola più tenue `.slot.nascent`); si chiude da sola dopo un secondo di pausa, al limite dei caratteri, con spazio/punteggiatura o chiudendo la tastiera. Niente più parola "in sospeso" fino allo spazio.
- **"La sua sfida" a messaggio vuoto:** riquadro d'aiuto lilla tenue (viola al 16%, titolo lilla); al primo tasto sfuma nello scuro.
- **Griglia di gioco e dell'anteprima in Silkscreen Regular** (lettere più aperte, uguali a quelle delle parole da trovare). La guida resta in Bold. Per tornare indietro basta togliere la regola `.tile, .pv .ptiles span { font-family: var(--word) }`.

## Scelte di prodotto (ottobre 2026)
- **Chi invia non riceve notifiche:** per ora basta "Rispondi", che condivide il risultato in stile cartolina (tempo, quadratini, aiuti). Niente servizio dedicato finché non si fa la parte privacy.
- **Niente "Mostrami tutto":** chi si blocca aspetta gli aiuti. È il cuore del gioco: trasformare l'attesa in desiderio. Gli aiuti garantiscono comunque la fine (3 livelli per parola: prima lettera, ultima, parola intera).
- **Foto e video non si salvano:** scelta voluta, coerente con la privacy. Già oggi il media non si trascina e non si tiene premuto per salvarlo. Limiti noti (screenshot, indirizzo Cloudinary leggibile nel link).

- **Niente difficoltà "Facile"** (messaggio scritto per intero, da trovare solo nella griglia): scartata, toglie il gusto di scoprire il messaggio. Restano normale e difficile.

## Prossimo passo concordato: branch `griglia-5x8`
Da fare su una branch separata, senza toccare word-challenge.
- **Cornice:** 5:8 invece di 3:4, nell'inquadratura, nell'anteprima e nella partita.
- **Griglie:** 4×6 per i messaggi corti e 5×8 per quelli medi. Massimo circa 30 lettere.
- **Link già inviati:** aumentare `GEN_VERSION` (sarà la 4) e tenere le vecchie misure, così i link vecchi generano la stessa griglia (`generate` riceve già la versione del link).
- **Vittoria:** in stand-by l'idea di riempire lo schermo (cover; con 5:8 il taglio è di circa il 3–5% per lato). Da rivalutare rispetto alla cartolina arrotondata con lo zoom, che oggi è la scelta attuale.
- **Consegna:** come file separato da provare (es. `index-5x8.html`).

## Rimandato (dopo)
- **Privacy:** cifratura del media nel browser, cancellazione dopo la soluzione o dopo 24 ore, link usabile una volta, pagina d'aiuto, segnalazioni.
- **Nome nell'anteprima del link:** "Alberto ti sta nascondendo qualcosa". Richiede un piccolo servizio (es. Cloudflare Worker) e va fatto insieme alla privacy.
- **Validazione dell'idea e statistiche d'uso.**
