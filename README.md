# Maikiuants · Kampuntin – Website

Zweisprachige Website (Spanisch/Englisch) für Kampuntin und die Shuar-Gemeinschaft Maikiuants.
Sie läuft kostenlos auf **GitHub Pages** und wird mit **Jekyll** gebaut. Das übernimmt GitHub
automatisch, man muss nichts installieren.

| Seite | Spanisch | Englisch |
|---|---|---|
| Start (Shuar, Maikiuants, Kampuntin, Mission, Karte) | `/` | `/en/` |
| Touren: Viaje espiritual (11 Tage) und Viaje Arutam (22 Tage), ab Cuenca, max. 12 Personen | `/tours/` | `/en/tours/` |
| Volunteering | `/voluntariado/` | `/en/volunteering/` |
| Wissenschaft / Paraecología, Tiere, Buch | `/ciencia/` | `/en/science/` |
| Updates (Facebook & Instagram) | `/novedades/` | `/en/updates/` |
| Fotoalben & Videos | `/galeria/` | `/en/gallery/` |
| Team | `/equipo/` | `/en/people/` |
| Kontakt | `/contacto/` | `/en/contact/` |
| Impressum & Datenschutz | `/aviso-legal/` | `/en/legal/` |

---

## 1. Veröffentlichen & Änderungen hochladen

Die Website liegt im Repository **Kampuntin-Maikiuants/Kampuntin-Maikiuants.github.io** und ist
unter **https://kampuntin-maikiuants.github.io** erreichbar. Dieser Projektordner ist bereits mit
dem Repository verknüpft.

**Einmalig einrichten**
1. [GitHub Desktop](https://desktop.github.com) installieren und mit dem Konto anmelden, das
   Zugriff auf *Kampuntin-Maikiuants* hat.
2. **File → Add Local Repository…** → diesen Ordner („Kampuntin Website“) auswählen.
3. Unten links bei „Summary“ z. B. *Erste Version der Website* eintragen → **Commit to main**
   → oben **Publish branch**.
4. Auf github.com: **Settings → Pages → Source: „GitHub Actions“**.
5. Tab **Actions**: Ist der erste Durchlauf rot (weil Pages noch aus war), anklicken →
   **Re-run all jobs**. Nach 1–2 Minuten ist die Seite online.

**Später, bei jeder Änderung:** GitHub Desktop öffnen → Änderungen erscheinen links →
kurze Beschreibung → **Commit to main** → **Push origin**. Fertig.

Eigene Domain (z. B. `kampuntin.org`): unter **Settings → Pages → Custom domain** eintragen und
in `_config.yml` bei `url:` die Adresse ergänzen.

---

## Handbücher für die Übergabe (PDF)

Druckfertige Schritt-für-Schritt-Anleitungen für alle, die die Website pflegen:
`manual/Manual-pagina-web-ES.pdf` (Spanisch) und `manual/Website-handbook-EN.pdf` (Englisch).
Sie erklären Zugang, Tour-Termine und Plätze (Pages CMS), das Popup auf der Startseite, Galerien und
Fotos, Facebook/Instagram auf „Novedades“, Team, Texte, Videos, eine eigene Domain und was zu tun ist, wenn
etwas schiefgeht.

Neu erzeugen, wenn sich die Website ändert (auf diesem Mac):
`PYTHONPATH=vendor/py python3 scripts/make_manual.py`. Die Bildschirmfotos liegen in `manual/img/`.
Der Ordner `manual` wird nicht mit der Website veröffentlicht.

## 2. Inhalte bearbeiten

Jede Änderung geht direkt auf github.com: Datei öffnen → Stift-Symbol → ändern → **Commit changes**.
Nach 1–2 Minuten ist die Änderung online.

| Was | Wo |
|---|---|
| Texte jeder Seite | `_data/es/*.yml` (Spanisch), `_data/en/*.yml` (Englisch) und `_data/fr/*.yml` (Französisch), eine Datei pro Seite |
| Menü, Buttons, Fußzeile | `_data/es/ui.yml`, `_data/en/ui.yml`, `_data/fr/ui.yml` |
| Sprachen im Umschalter | `_config.yml` → `languages: [es, en, fr]` (Seiten in `pages/es`, `pages/en`, `pages/fr`) |
| E-Mail, WhatsApp, Instagram, Facebook, WWOOF, Name der Organisation | `_config.yml` |
| Tour-Termine | `_data/tour_dates.yml` |
| Team (Namen, Rollen, Fotos) | `_data/team.yml` |
| Bedrohte Arten | `_data/species.yml` |
| Neue Froschart, Flusstiere, Buch | `_data/es/science.yml`, `_data/en/science.yml` |
| Erfahrungsberichte, FAQ Volunteering | `_data/es/volunteering.yml`, `_data/en/volunteering.yml` |
| 6 Fotos „Leben in der Jea“ (Touren + Volunteering) | `_data/jea_photos.yml` |
| Menü-Reihenfolge | `_data/navigation.yml` |
| Videos (eigene MP4 in `assets/video/` oder YouTube) | `_data/videos.yml` |
| Fotoalben (Titel, Datum, Titelbild) | `_data/albums.yml` |
| Design (Farben, Schriften) | `assets/css/style.css`, ganz oben unter `:root` |
| Hintergrundmuster an/aus | `_config.yml` → `background_pattern: true/false` (Stärke: `opacity` bei „Hintergrundmuster“ in `style.css`) |
| Logo von Anouk Segebart (Kopf- und Fußzeile) | `assets/img/logo-128.png` / `logo-256.png` (eingebunden über `_includes/logo.html`) · Browser-Icons: `assets/img/favicon-32/48/192.png` · iPhone-Icon: `assets/img/apple-touch-icon.png` · Original im Ordner `Logo-Entwurf` neben der Website |
| Credits „Las caras detrás de esta web“ | `_data/<sprache>/people.yml` unter `credits`; Webmaster in `_config.yml` → `webmaster` |
| Shuar-Namen im Team | `_data/team.yml` → `shuar_name: "…"` |
| Detailkarte Limón Indanza – Maikiuants | wird erzeugt mit `python3 scripts/make_region_map.py` (Daten: OpenStreetMap) |
| Besucherstatistik (GoatCounter) | `_config.yml` → `goatcounter: "kontoname"` – Anleitung unten, Abschnitt 4 |
| Tour-Hinweis auf der Startseite an/aus | `_config.yml` → `tour_popup: true/false` (Texte: `tour_popup` in `_data/es|en/home.yml`; Termin kommt automatisch aus `tour_dates.yml`) |

**Fotos einbauen:** Bild hochladen (z. B. nach `assets/img/fotos/`). Dann im passenden
Text-File bei `image: ""` den Pfad eintragen, z. B. `image: "/assets/img/fotos/inicio.jpg"`.
Solange kein Bild eingetragen ist, erscheint ein grüner Platzhalter mit Bildbeschreibung.

**Galerie (Fotoalben):** Jedes Album ist ein eigener Ordner in `assets/galeria/`, z. B.
`assets/galeria/2026-09-tour-septiembre/`. Neuen Ordner anlegen, Fotos hineinladen, fertig: Das
Album erscheint automatisch mit dem ersten Foto als Titelbild. Ein Klick darauf zeigt alle Fotos
zum Durchblättern.
- Ordnernamen **mit Datum beginnen** (`2026-11-minga-de-siembra`). Dann steht das neueste Album
  vorne, und Monat/Jahr werden automatisch angezeigt.
- Schöner Titel, Datum oder ein anderes Titelbild: optional in `_data/albums.yml` eintragen.
- Die drei neuesten Alben erscheinen zusätzlich unten auf der Tour-Seite.
- Auf github.com legt man einen neuen Ordner so an: **Add file → Create new file**, als Namen
  `assets/galeria/2026-11-minga/_LEEME.txt` eingeben (der Schrägstrich erzeugt den Ordner),
  speichern, dann im Ordner **Add file → Upload files**.

> Bilder vorher verkleinern (ca. 1600 px breit, unter 500 KB). GitHub Pages empfiehlt höchstens
> 1 GB pro Website. Längere Videos besser auf YouTube hochladen und in `_data/videos.yml` eintragen.

**Tipp für YAML-Dateien:** Einrückung (Leerzeichen) beibehalten. Enthält ein Text einen
Doppelpunkt mit Leerzeichen dahinter, den ganzen Text in "Anführungszeichen" setzen.

---

## 3. Updates über Facebook & Instagram

Die Novedades-Seite zeigt oben die Konten (Facebook **Kampuntin** und **Maikiuants**, Instagram
**@territorioshuar**) und darunter die **neuesten Beiträge als eigene Karten mit Text und Fotos**,
ohne eingebettetes Facebook. Die drei neuesten erscheinen auch auf der Startseite.

### So funktioniert der automatische Import

Alle 6 Stunden holt GitHub über die offizielle Facebook-Schnittstelle (Graph API) die neuesten
Beiträge, speichert Text und Fotos im Repository (`_data/social_posts.json`,
`assets/img/social/`) und veröffentlicht die Website neu. Das Programm dafür ist
`scripts/import_social.py`, der Zeitplan steht in `.github/workflows/website.yml`.

Solange kein Zugangsschlüssel (Token) hinterlegt ist, passiert nichts. Die Seite zeigt dann nur
die drei Konten als große Karten.

> Die früher eingebettete Facebook-Chronik ist abgeschaltet: Facebook zeigt sie nur noch
> Besuchern, die bei Facebook eingeloggt sind – alle anderen sahen ein leeres weißes Feld.

**Voraussetzungen**
- Es müssen **Facebook-Seiten** sein (keine privaten Profile), und wer einrichtet, muss dort
  Admin sein.
- Für Instagram: @territorioshuar muss ein **Business- oder Creator-Konto** sein und mit einer
  der beiden Facebook-Seiten verknüpft sein. Dann kommt Instagram automatisch mit, ohne
  zusätzlichen Schlüssel.

**Einrichtung (einmalig, ca. 20 Minuten)**
1. Auf [developers.facebook.com](https://developers.facebook.com) mit dem Facebook-Konto anmelden,
   das die Seiten verwaltet → **Meine Apps → App erstellen** (Typ „Business“, Name z. B.
   „Kampuntin Website“).
2. **Tools → Graph API Explorer** öffnen, oben die neue App wählen. Unter „Berechtigungen“
   hinzufügen: `pages_show_list`, `pages_read_engagement` und für Instagram zusätzlich
   `instagram_basic` und `business_management`. Dann **Generate Access Token** und bestätigen.
3. **Tools → Access Token Debugger**: das Token einfügen → **Debug** → unten
   **Extend Access Token** (langlebiges Token) → kopieren.
4. Zurück im Graph API Explorer das langlebige Token einsetzen und die Abfrage `me/accounts`
   ausführen. Die Antwort enthält für **jede Seite** ein eigenes `access_token`. Diese
   Seiten-Tokens laufen nicht ab.
5. Auf GitHub im Repository: **Settings → Secrets and variables → Actions → New repository
   secret**. Name: `FB_PAGE_TOKENS`, Wert: die Seiten-Tokens, **eins pro Zeile**.
6. **Actions → Website bauen & Social Media importieren → Run workflow**. Nach 1–2 Minuten
   erscheinen die Beiträge auf der Website.

**Kontrollieren, ob es läuft:** Tab **Actions** → letzten Durchlauf anklicken. Oben unter
„Annotations“ steht eine kurze Meldung:
- gelb *„Kein Secret FB_PAGE_TOKENS gesetzt“* → Schritte 1–5 sind noch nicht erledigt,
- rot *„Token Nr. 1: …“* → das Token ist falsch oder abgelaufen (Meldung von Facebook steht dabei),
- blau *„… Beiträge geladen“* → alles gut.

**Gut zu wissen**
- Ändert jemand das Facebook-Passwort oder entzieht der App die Rechte, werden die Tokens
  ungültig. Dann Schritte 2–5 wiederholen.
- GitHub pausiert zeitgesteuerte Abläufe, wenn 60 Tage lang nichts im Repository passiert. Dann
  unter Actions einmal „Enable workflow“ klicken.
- Nach dem Hinterlegen des Tokens nicht 6 Stunden warten: **Actions → Website bauen & Social
  Media importieren → Run workflow** startet den Import sofort.
- Einzelne Instagram-Posts lassen sich zusätzlich von Hand einbetten: Link in
  `_data/instagram_embeds.yml` eintragen (lädt erst nach Klick).

**Pages CMS (optional):** Mit [app.pagescms.org](https://app.pagescms.org) (kostenlos, Login mit
GitHub) lassen sich die Tour-Termine und freien Plätze in einem Formular bearbeiten – auch vom
Handy. Die Einstellungen dafür stehen in `.pages.yml`, die Anleitung auf Spanisch für die Leitung
ganz unten („Guía rápida: actualizar las plazas de un tour“). Wer das Formular nutzen soll,
braucht ein GitHub-Konto und muss unter **Settings → Collaborators** eingeladen werden.

---

## 4. Was GitHub Pages (kostenlos) kann – und was nicht

GitHub Pages liefert nur fertige Seiten aus. Es gibt keinen Server und keine Datenbank. Deshalb:

| Funktion | Lösung in dieser Website |
|---|---|
| Kontaktformular | Gibt es bewusst nicht: GitHub Pages kann keine E-Mails versenden. Die Kontaktseite führt direkt zu WhatsApp und E-Mail. (Nachrüstbar über einen Dienst wie Formspree.) |
| Buchung & Zahlung | Läuft über Kontakt/WhatsApp. Für Online-Zahlung wäre ein externer Dienst nötig. |
| Kommentare, Logins, Newsletter | Nicht eingebaut. Bei Bedarf über externe Dienste möglich. |
| Statistiken | Keine, also auch kein Cookie-Banner nötig. |
| Karte auf der Startseite | Eigene Grafik (`_includes/map-ecuador.html`, Umrisse von Natural Earth), kein Google Maps, keine Daten an Dritte. Der Link führt zu OpenStreetMap mit den genauen Koordinaten. |

Grenzen laut GitHub: Website bis 1 GB, ca. 100 GB Datenvolumen pro Monat, öffentliches
Repository. GitHub Pages ist nicht für Websites gedacht, die hauptsächlich dem Online-Verkauf
dienen. Eine Informationsseite mit Buchung per Kontakt ist üblich. Wenn später Online-Zahlung
dazukommen soll, lohnt sich ein anderer Hoster (z. B. Netlify oder Cloudflare Pages, beide mit
kostenlosem Plan).

---

### Besucherstatistik

GitHub Pages zeigt keine Besucherzahlen (unter *Insights → Traffic* sieht man nur Besuche des
Repositorys, nicht der Website). Empfehlung: **GoatCounter** – kostenlos für Projekte wie dieses,
ohne Cookies, ohne Einwilligungs-Banner, und die Zahlen lassen sich mit Kampuntin teilen.

1. Auf [goatcounter.com](https://www.goatcounter.com) ein Konto anlegen, Code z. B. `kampuntin`.
2. In `_config.yml` eintragen: `goatcounter: "kampuntin"` → speichern, pushen.
3. Ab dann zählt die Seite Besuche. Im Impressum erscheint automatisch ein kurzer Hinweis dazu.
4. Teilen: In GoatCounter unter *Settings → Users* Kampuntin als Benutzer einladen, oder unter
   *Settings → Site settings* die Statistik öffentlich machen und den Link weitergeben.

## 5. Vor dem Start: Checkliste

- [ ] Alle Platzhalter ersetzen. Sie stehen in **[eckigen Klammern]**, z. B. `[ciudad de encuentro]`,
      `[XXX] USD`, `[Nombre]`. Auf GitHub findet die Suche (Taste `/`) alle Stellen.
- [ ] E-Mail-Adresse in `_config.yml` eintragen (WhatsApp, Facebook und Instagram sind schon drin).
- [ ] Echte Tour-Termine in `_data/tour_dates.yml`.
- [ ] Die Liste bedrohter Arten (`_data/species.yml`) mit den echten Monitoring-Daten abgleichen.
- [ ] Name, Foto und Geschichte der neuen Froschart sowie die Angaben zum Buch eintragen.
- [ ] Mission von Kampuntin ausformulieren (`_data/es/home.yml`, `_data/en/home.yml`).
- [ ] Erfahrungsberichte durch echte ersetzen (mit Einverständnis).
- [ ] Alle Texte über Kultur, Wissen und Territorium **von der Gemeinschaft Maikiuants prüfen lassen**.
- [ ] Für jedes Foto und jede Personenbeschreibung das Einverständnis der Personen einholen.
- [ ] Impressum & Datenschutz (`_data/*/legal.yml`) rechtlich prüfen lassen.

---

## 6. Lokale Vorschau (optional, für Technik-Interessierte)

Auf diesem Mac liegt das Bauwerkzeug im Ordner `vendor/` (wird nicht zu GitHub hochgeladen):

```bash
./vendor/build.sh
```

baut die Seite nach `_site/`. `./vendor/vorschau.sh` erzeugt zusätzlich die Offline-Vorschau
neben dem Projekt (`../Vorschau` und `../Kampuntin-Website-offline.zip`).

Auf einem anderen Rechner: Ruby 3.x installieren (z. B. `brew install ruby`), dann
`bundle install` und `bundle exec jekyll serve` – danach unter http://localhost:4000 ansehen.

---

## Guía rápida (español): subir un álbum de fotos

1. En github.com abre la carpeta `assets/galeria`.
2. **Add file → Create new file** y escribe como nombre `2026-11-nombre-del-album/_LEEME.txt`
   (con la fecha al principio). Guarda con **Commit changes**.
3. Abre la nueva carpeta → **Add file → Upload files** y sube las fotos (reducidas a unos 1600 px).
4. En uno o dos minutos el álbum aparece en la galería. Título y fecha opcionales en
   `_data/albums.yml`.

## Guía rápida (español): actualizar las plazas de un tour

Se hace en un minuto, también desde el celular. Se necesita una cuenta de GitHub con acceso al
repositorio (la primera vez hay que pedir la invitación).

1. Abre [app.pagescms.org](https://app.pagescms.org) e inicia sesión con GitHub.
2. Elige el repositorio **Kampuntin-Maikiuants.github.io** → **Fechas de tours**.
3. En la fecha del tour escribe en **Plazas libres** cuántas plazas quedan (por ejemplo 12, y
   después de cada reserva un número menos). Con **0** aparece «Completo».
   Si no quieres contar plazas, deja el campo vacío y elige un **Estado**, por ejemplo
   «Plazas a consultar».
4. Para una fecha nueva: **Agregar**, llenar inicio y fin (y si aún no es exacta, el texto en
   «Texto en vez de la fecha»).
5. **Guardar.** En uno o dos minutos la página web está actualizada.

