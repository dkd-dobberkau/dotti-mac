# Ideas for Dotti-Mac

A collection of ideas for future development.

## Dotti Display Features

### Animationen
- Mehrere Frames speichern und abspielen
- Blinken, Farbwechsel, Lauflicht
- Übergangseffekte zwischen Bildern

### Text-Scroll
- Lauftext über das 8x8 Display
- Einstellbare Geschwindigkeit
- Verschiedene Schriftarten (minimal 3x5, 5x7)

### Uhr / Timer
- Aktuelle Zeit anzeigen (HH:MM)
- Countdown-Timer
- Pomodoro-Timer mit visueller Anzeige
- Stoppuhr

### Notifications
- CI/CD Status (GitHub Actions, Jenkins, GitLab)
- Neue E-Mails / Slack-Nachrichten
- Kalender-Erinnerungen
- System-Alerts

### Wetter
- Wetter-Icon basierend auf API-Daten
- Temperatur als Farbe oder Zahl
- Regen-Animation

### Musik-Visualisierung
- Spotify "Now Playing" Album-Art (8x8 pixelated)
- Audio-Pegel Anzeige
- Beat-Detection für Lichteffekte

### System-Monitor
- CPU-Auslastung als Balken
- RAM-Nutzung
- Netzwerk-Aktivität
- Festplatten-Status

---

## BLE Scanner Erweiterungen

### Export
- JSON Export für Scan-Ergebnisse
- CSV Export für Analyse
- SQLite-Datenbank für historische Daten

### Device Tracking
- Geräte über Zeit verfolgen (erscheinen/verschwinden)
- Anwesenheitserkennung (wer ist im Raum?)
- Bewegungsmuster analysieren

### Alerts
- Benachrichtigung wenn bestimmte Geräte erscheinen
- Alarm wenn unbekannte Geräte auftauchen
- Webhook-Integration

### Web UI
- Browser-basierter Scanner
- Live-Ansicht der Geräte
- Interaktive Probe-Funktion

---

## Web Editor Verbesserungen

### Animation-Editor
- Timeline mit mehreren Frames
- Frame-Dauer einstellbar
- Preview-Animation im Browser
- Export als Animation-Sequenz

### Import/Export
- PNG/GIF Import (automatisch auf 8x8 skalieren)
- Design-Export als JSON
- Teilen von Designs (URL-basiert)

### Bearbeitung
- Undo/Redo Historie
- Kopieren/Einfügen von Bereichen
- Spiegeln/Rotieren
- Farbverlauf-Tool
- Füll-Tool (Bucket)

### Collaboration
- Mehrere Benutzer gleichzeitig
- Design-Galerie
- Bewertungen/Likes

---

## Integrationen

### Home Assistant
- Als BLE-Light Entity integrieren
- Automationen (z.B. rot bei Alarm)
- Status-Anzeige für Smart Home

### MQTT
- Publish/Subscribe für IoT-Integration
- Kompatibel mit Node-RED
- Bridge zu anderen Systemen

### REST API
- Vollständige HTTP API
- OpenAPI/Swagger Dokumentation
- Webhook-Empfänger

### CLI Tool
```bash
# Beispiel-Befehle
dotti scan                    # Geräte finden
dotti connect                 # Verbinden
dotti show heart              # Preset anzeigen
dotti set 0,0 red             # Pixel setzen
dotti fill blue               # Alles füllen
dotti slot save 0             # In Slot speichern
dotti slot load 0             # Aus Slot laden
dotti animate rainbow 5       # Animation 5 Sekunden
dotti text "Hi" --scroll      # Lauftext
dotti off                     # Ausschalten
```

### Shortcuts / Automator
- macOS Shortcuts Integration
- Automator Actions
- Alfred/Raycast Plugins

---

## Hardware-Projekte

### Dotti-Cluster
- Mehrere Dottis als größeres Display (2x2 = 16x16)
- Synchronisierte Animationen

### Dotti-Wecker
- Raspberry Pi + Dotti
- Sanftes Aufwachen mit Lichteffekten
- Wecker-Funktionen

### Dotti-Dashbutton
- ESP32 + Dotti
- Physischer Button für Aktionen
- Status-Feedback auf dem Display

---

## Priorität

### Kurzfristig (einfach)
- [ ] CLI Tool mit Basis-Befehlen
- [ ] JSON Export für Scanner
- [ ] Undo/Redo im Editor

### Mittelfristig
- [ ] Animation-Editor
- [ ] Text-Scroll Funktion
- [ ] REST API

### Langfristig
- [ ] Home Assistant Integration
- [ ] Device Tracking
- [ ] Musik-Visualisierung
