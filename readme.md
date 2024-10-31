
### .gitignore
Enthält Regeln, um bestimmte Dateien und Verzeichnisse von der Versionskontrolle auszuschließen.

### .vscode/
Enthält Einstellungen für Visual Studio Code.

### Bot/
Enthält die Implementierung des Bots.

- **bot.py**: Hauptskript für den Bot.
- **cogs/sync.py**: Modul für die Synchronisation von Daten.
- **Dockerfile**: Docker-Konfigurationsdatei für den Bot.
- **requirements.txt**: Liste der Python-Abhängigkeiten für den Bot.
- **services/log_service.py**: Dienst zum Protokollieren von Ereignissen.
- **singelton/global_var.py**: Modul zur Verwaltung globaler Variablen.

### docker-compose.yaml
Docker Compose Datei zur Orchestrierung der Container für den Bot und den Server.

### Server/
Enthält die Implementierung des Servers.

- **server.py**: Hauptskript für den Server.
- **Dockerfile**: Docker-Konfigurationsdatei für den Server.
- **requirements.txt**: Liste der Python-Abhängigkeiten für den Server.

## Ausführung des Systems

1. **Voraussetzungen**:
   - Docker
   - Docker Compose

2. **Schritte zur Ausführung**:
   - Klone das Repository:
     ```sh
     git clone <repository-url>
     cd <repository-directory>
     ```
   - Passe die Enviroments in `docker-compose.yaml` an. Mindestens den Bot Token.

   - Starte die Docker-Container:
     ```sh
     docker-compose up --build
     ```

Dies wird die Container für den Bot und den Server erstellen und starten. Der Bot und der Server werden dann gemäß den in den jeweiligen Dockerfiles definierten Konfigurationen ausgeführt.