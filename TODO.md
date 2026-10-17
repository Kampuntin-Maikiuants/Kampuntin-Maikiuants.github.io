# To-do bis zur fertigen Website

Stand: 15. Oktober 2026 · Zum Abhaken: `[ ]` → `[x]`

Am einfachsten schickt ihr mir Infos, Texte und Fotos gesammelt, dann baue ich sie ein.

---

## 1. Fakten & Entscheidungen

Bereits eingebaut: E-Mail (ocstkampuntin@gmail.com), WhatsApp-Kontakte vom Flyer, Limón Indanza als
Ausgangsort mit Taxi 4×4 (50–60 USD), Internet im Gemeinschaftszentrum, Ausflug zum Wasserfall.

- [ ] **Tour-Preis** pro Person (10 Tage)
- [ ] **Anzahlung** in % und **Zahlungs-/Stornobedingungen**
- [ ] **Echte Tour-Termine** (die drei jetzigen sind Beispiele)
- [ ] **Volunteering:** Mindestaufenthalt, maximale Dauer, wie viele Freiwillige gleichzeitig
- [ ] **Sprachen:** Spricht jemand im Team Englisch (oder Deutsch)?
- [ ] **Sicherheit:** Erste Hilfe, Notfall-Kommunikation, Evakuierung (für die Tour-FAQ)
- [ ] **Spenden:** Gibt es eine Möglichkeit, euch zu unterstützen (Konto, Plattform)?
- [ ] **Seit wann** gibt es Kampuntin / die Touren? (Startseite: „Desde [año]“)
- [ ] **Kontakte vom Flyer** (Freddy Ankuash, Minki Ankuash, Julien Shakaim) sind eingebaut –
      kurz bei allen dreien nachfragen, ob Nummer und E-Mail öffentlich sichtbar sein dürfen
- [ ] **Domain:** Bleibt es bei `…github.io/…` oder eigene Adresse (z. B. kampuntin.org, ca. 10–15 €/Jahr)?

## 2. Texte überarbeiten & feinschleifen

Alle Texte stehen in `_data/es/…` (Spanisch) und `_data/en/…` (Englisch), eine Datei pro Seite.

- [ ] **Mission von Kampuntin** endgültig ausformulieren (Startseite)
- [ ] **Touren:** Tagesablauf (10 Tage) an euren echten Ablauf anpassen
- [ ] **Shuar-Leitsatz** auf der Startseite prüfen: „Iikia kampuntniuitji tura achitkiaji ii
      nekatairijiai“ (von der Infotafel abgeschrieben)
- [ ] **FAQ** auf Touren-, Volunteering- und Kontaktseite durchgehen
- [ ] **Englische Übersetzung** am Ende gegenlesen lassen
- [ ] Alle restlichen **[Platzhalter in eckigen Klammern]** – Liste siehe unten

> ⚠️ **Wichtig:** Alle Texte über Kultur, Wissen und Territorium der Shuar
> **von der Gemeinschaft Maikiuants prüfen und freigeben lassen.**

## 3. Wissenschaft

Bereits eingebaut (von der Infotafel): Kamerafallen 2024, *Atelopus sp.*, mögliche neue
Froschart vom 19.06.2024, Flüsse Yunkumas/Akaas mit pH 7,8, Wetterstation.

- [ ] **Gefährdungskategorien** der Arten (Jaguar = vom Aussterben bedroht usw.) – Quelle
      bestätigen (Rote Liste Ecuador? UICN?)
- [ ] **Kamerafallen-Fotos** von Jaguar, Brillenbär, Puma, Waldhund – kommen in `_data/species.yml`
      unter `snapshots` und erscheinen dann zum Aufklappen unter der jeweiligen Tier-Karte
- [ ] **Buch:** Autor·innen, Jahr, Seitenzahl, Verlag (Logo „natura“ auf dem Cover?) und wie man
      es bekommt (Kauf? Download? Kontakt?) – Titel, Cover, Buchseiten und 10 Tierfamilien sind drin
- [ ] **Schreibweise des Flusses:** Buch-Cover „Aakas“, Infotafel „Akaas“ – was stimmt?
- [ ] **Neue Forschungsstation:** Zeitplan / Details, falls ihr mehr zeigen wollt

## 4. Menschen & Erfahrungsberichte

- [ ] **Team-Seite:** Für jede Person Name, Rolle, 1–2 Sätze, quadratisches Porträtfoto
      (aktuell: Freddy, Minki, Julien + 5 Platzhalter aus der Gemeinschaft) – **mit Einverständnis**
- [ ] **Erfahrungsberichte:** 2–4 echte Berichte von Freiwilligen – **mit Einverständnis**

## 5. Fotos

**Für jedes Foto mit Personen (auch Kinder!) das Einverständnis einholen** – das gilt auch für
die schon eingebauten Fotos und Alben.

- [ ] Eingebaute Fotos durchsehen: passt die Auswahl? (Start, Touren, Volunteering, Wissenschaft)
- [ ] **Titelbild Touren:** im Moment ein Flussfoto von Jesko – gerne ein besseres
- [ ] **Galerie:** Alben prüfen (Fiesta, Leben in Maikiuants, Volunteering, Forschung),
      Titel und Daten in `_data/albums.yml` anpassen, weitere Alben anlegen
- [ ] Optional: weitere **Videos** (Forschungsvideo „Uso de suelo“ ist drin; lange Videos besser über YouTube)

## 6. Facebook & Instagram

- [ ] Prüfen: Sind beide Facebook-Konten **Seiten** (keine Privatprofile)?
- [ ] Prüfen: Ist @territorioshuar ein **Business-/Creator-Konto** und mit einer der Seiten verknüpft?
- [ ] **Automatischen Import einrichten** (Anleitung README, Abschnitt 3, ca. 20 Minuten) –
      ohne diesen Schritt erscheinen keine Facebook-Posts auf der Website

## 7. Rechtliches & Start

- [ ] **Impressum:** Adresse, Ort/Land
- [ ] **Datenschutz-/Impressumstext** kurz rechtlich prüfen lassen
- [ ] Ordner `_archiv` (alte Version) löschen
- [ ] Letzter Durchgang: alle Seiten am Handy anklicken, Links testen
- [ ] Website teilen 🎉 (WWOOF-Profil, Facebook, Instagram-Bio)

---

## Anhang: Restliche Platzhalter in den Textdateien

| Datei | Platzhalter |
|---|---|
| `home.yml` | [año] – seit wann Kampuntin |
| `tours.yml` | [XXX] USD, [XX] % Anzahlung, Zahlungs-/Stornobedingungen, Sicherheit, Sprachen |
| `volunteering.yml` | [2 semanas], [X meses], Sprachen, Anzahl Freiwillige, Erfahrungsberichte ([Nombre], [país], [año]) |
| `science.yml` | Buch (Autor·innen, Jahr, Seiten, Bezugsweg) |
| `contact.yml` | Sprachen, Stornobedingungen, Spenden |
| `legal.yml` | Adresse, Ort/Land |
| `team.yml` | 5× [Nombre] + Rollen/Texte |
| `tour_dates.yml` | Beispiel-Termine ersetzen |
