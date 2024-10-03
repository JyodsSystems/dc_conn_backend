import os
import json
from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)


class DB:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host="mysql_db",  # Name des Datenbank-Containers im Docker-Compose
                user="bot",      # Benutzername aus Docker-Compose
                password="bot",  # Passwort aus Docker-Compose
                database="registerdb"  # Datenbankname aus Docker-Compose
            )
            if self.conn.is_connected():
                self.cursor = self.conn.cursor(dictionary=True)
                print("Verbindung zur Datenbank erfolgreich.")
                self.init_main_table()
                self.init_secondary_table()
                self.init_mapping_table()
        except Error as e:
            print(f"Fehler beim Verbinden zur Datenbank: {e}")
            self.conn = None
            self.cursor = None

    def init_main_table(self):
        """Erstellt die Tabelle 'users' in der Datenbank, falls sie noch nicht existiert."""
        query = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                steam_id BIGINT NOT NULL UNIQUE,
                discord_id BIGINT DEFAULT NULL UNIQUE,
                reg_key VARCHAR(32) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        self.execute_query(query)

    def init_secondary_table(self):
        """Erstellt die Tabelle 'players' in der Datenbank, falls sie noch nicht existiert."""
        query = """
            CREATE TABLE IF NOT EXISTS players (
                id INT AUTO_INCREMENT PRIMARY KEY,
                g_id INT NOT NULL,
                steam_id BIGINT NOT NULL,
                name VARCHAR(32) NOT NULL,
                job VARCHAR(32) NOT NULL,
                model VARCHAR(64) NOT NULL,
                wallet INT NOT NULL,
                faction VARCHAR(32) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        self.execute_query(query)

    def init_mapping_table(self):
        """Erstellt die Tabelle 'mapping' in der Datenbank, falls sie noch nicht existiert."""
        query = """
            CREATE TABLE IF NOT EXISTS mapping (
                id INT AUTO_INCREMENT PRIMARY KEY,
                dc_rank_id BIGINT NULL,
                gmod_job VARCHAR(32) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        self.execute_query(query)

    def execute_query(self, query, params=None):
        """Führt eine SQL-Abfrage (INSERT, UPDATE, DELETE) aus."""
        try:
            if self.cursor:
                self.cursor.execute(query, params)
                self.conn.commit()
                print("Abfrage erfolgreich ausgeführt.")
        except Error as e:
            print(f"Fehler bei der Ausführung der Abfrage: {e}")

    def fetch_all(self, query, params=None):
        """Führt eine SELECT-Abfrage aus und gibt alle Ergebnisse zurück."""
        try:
            if self.cursor:
                self.cursor.execute(query, params)
                result = self.cursor.fetchall()
                self.conn.commit()
                return result
        except Error as e:
            print(f"Fehler beim Abrufen der Daten: {e}")
            return None

    def fetch_one(self, query, params=None):
        """Führt eine SELECT-Abfrage aus und gibt das erste Ergebnis zurück."""
        try:
            if self.cursor:
                self.cursor.execute(query, params)
                result = self.cursor.fetchone()
                self.conn.commit()
                return result
        except Error as e:
            print(f"Fehler beim Abrufen der Daten: {e}")
            return None

    def close(self):
        """Schließt die Verbindung zur Datenbank."""
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("Datenbankverbindung geschlossen.")

db = DB()

def check_steam_id(steam_id : int) -> bool:
    """
    Überprüft, ob eine Steam-ID bereits in der Datenbank existiert.

    Args:
        steam_id (int): Die Steam-ID, die überprüft werden soll.

    Returns:
        bool: True, wenn die Steam-ID existiert, False andernfalls.
    """

    query = "SELECT * FROM users WHERE steam_id = %s;"
    result = db.fetch_one(query, (steam_id,))
    return result is not None

def check_discord_id_gmod(steam_id : int) -> bool:
    """
    Überprüft, ob eine Discord-ID bereits in der Datenbank existiert.

    Args:
        steam_id (int): Die Steam-ID, die überprüft werden soll.

    Returns:
        bool: True, wenn die Discord-ID existiert, False andernfalls.
    """

    query = "SELECT discord_id FROM users WHERE steam_id = %s;"
    result = db.fetch_one(query, (steam_id,))
    return result["discord_id"] is not None if result else False

def get_reg_key(steam_id : int) -> str:
    """
    Gibt den Registrierungsschlüssel einer Steam-ID zurück.

    Args:
        steam_id (int): Die Steam-ID, deren Registrierungsschlüssel zurückgegeben werden soll.

    Returns:
        str: Der Registrierungsschlüssel der Steam-ID.
    """

    query = "SELECT reg_key FROM users WHERE steam_id = %s;"
    result = db.fetch_one(query, (steam_id,))
    return result["reg_key"] if result else None

def register_steam_id(steam_id : int) -> None:
    """
    Registriert eine Steam-ID in der Datenbank.

    Args:
        steam_id (int): Die Steam-ID, die registriert werden soll.
    """

    query = "INSERT INTO users (steam_id, reg_key) VALUES (%s, %s);"
    db.execute_query(query, (steam_id, os.urandom(16).hex()))

def link_discord_id(reg_key : str, discord_id : int) -> None:
    """
    Verknüpft eine Discord-ID mit einer Steam-ID.

    Args:
        reg_key (str): Der Registrierungsschlüssel, der überprüft werden soll.
        discord_id (int): Die Discord-ID, die mit der Steam-ID verknüpft werden soll.

    Raises:
        Exception: Wenn der Registrierungsschlüssel ungültig ist.
    """

    if not check_reg_key(reg_key):
        raise Exception("Ungültiger Registrierungsschlüssel.")

    query = "UPDATE users SET discord_id = %s WHERE reg_key = %s;"
    db.execute_query(query, (discord_id, reg_key))
    
def check_reg_key(reg_key : str) -> bool:
    """
    Überprüft, ob ein Registrierungsschlüssel in der Datenbank existiert.

    Args:
        reg_key (str): Der Registrierungsschlüssel, der überprüft werden soll.

    Returns:
        bool: True, wenn der Registrierungsschlüssel existiert, False andernfalls.
    """

    query = "SELECT * FROM users WHERE reg_key = %s;"
    result = db.fetch_one(query, (reg_key,))
    return result is not None

def already_used_reg_key(reg_key : str) -> bool:
    """
    Überprüft, ob ein Registrierungsschlüssel bereits verwendet wurde.  

    Args:
        reg_key (str): Der Registrierungsschlüssel, der überprüft werden soll.

    Returns:
        bool: True, wenn der Registrierungsschlüssel bereits verwendet wurde, False andernfalls.
    """

    query = "SELECT discord_id FROM users WHERE reg_key = %s;"
    result = db.fetch_one(query, (reg_key,))
    return result["discord_id"] is not None if result else False

def check_discord_id(discord_id : int) -> bool:
    """
    Überprüft, ob eine Discord-ID bereits in der Datenbank existiert.

    Args:
        discord_id (int): Die Discord-ID, die überprüft werden soll.

    Returns:
        bool: True, wenn die Discord-ID existiert, False andernfalls.
    """

    query = "SELECT * FROM users WHERE discord_id = %s;"
    result = db.fetch_one(query, (discord_id,))
    return result is not None

def add_or_change_entry(id, sid, name, job, model, wallet, faction) -> None:
    """
    Fügt einen neuen Spieler hinzu oder ändert einen bestehenden Spieler.

    Args:
        id (int): Die ID des Spielers.
        sid (int): Die Steam-ID des Spielers.
        name (str): Der Name des Spielers.
        job (str): Der Job des Spielers.
        model (str): Das Model des Spielers.
        wallet (int): Der Kontostand des Spielers.
        faction (str): Die Fraktion des Spielers.

    Returns:
        None
    """
    query = "SELECT * FROM players WHERE g_id = %s;"
    result = db.fetch_one(query, (id,))

    if result:
        query = "UPDATE players SET steam_id = %s, name = %s, job = %s, model = %s, wallet = %s, faction = %s WHERE g_id = %s;"
        db.execute_query(query, (sid, name, job, model, wallet, faction, id))
    else:
        query = "INSERT INTO players (g_id, steam_id, name, job, model, wallet, faction) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        db.execute_query(query, (id, sid, name, job, model, wallet, faction))    

def get_discord_users_with_all_ranks():
    # SQL-Abfrage mit COALESCE zur Handhabung von NULL-Werten
    query = """
        SELECT users.discord_id, COALESCE(mapping.dc_rank_id, 0) AS dc_rank_id
        FROM users
        JOIN players ON users.steam_id = players.steam_id
        JOIN mapping ON players.job = mapping.gmod_job;
    """
    result = db.fetch_all(query)

    data = {}  # Hier werden die Daten gespeichert

    for row in result:
        discord_id = row.get("discord_id")
        dc_rank_id = row.get("dc_rank_id")

        # Sicherstellen, dass discord_id und dc_rank_id gültige Werte sind
        if discord_id is not None and dc_rank_id is not None:
            if discord_id in data:
                data[discord_id].append(dc_rank_id)
            else:
                data[discord_id] = [dc_rank_id]

    return data

def delete_every_entry_except_ids(ids):
    query = "DELETE FROM players WHERE g_id NOT IN (%s);" % ",".join(ids)
    db.execute_query(query)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/register/<string:steam_id>", methods=['POST'])
def register(steam_id):

    if check_steam_id(steam_id):
        if check_discord_id_gmod(steam_id):
            return "Account bereits registriert und verknüpft.", 400
            # return jsonify({"message": "Account bereits registriert und verknüpft."}), 400
        else:
            key = get_reg_key(steam_id)
            return "Steam-ID bereits registriert, aber noch nicht verknüpft. Gib auf dem Discord den Befehl /link mit folgendem Registrierungsschlüssel ein: " + key, 400
            # return jsonify({"message": "Steam-ID bereits registriert, aber noch nicht verknüpft. Gib auf dem Discord den Befehl /register " + key + " ein."}), 400
        
    try:
        register_steam_id(steam_id)
        return "Steam-ID erfolgreich registriert. Gib auf dem Discord den Befehl /link mit folgendem Registrierungsschlüssel ein: " + get_reg_key(steam_id), 201
        # return jsonify({"message": "Steam-ID erfolgreich registriert. Gib auf dem Discord den Befehl `/link " + get_reg_key(steam_id) + "` ein."}), 201
    except Exception as e:
        return "Fehler beim Registrieren der Steam-ID " + str(e), 500
        # return jsonify({"message": "Fehler beim Registrieren der Steam-ID."}), 500
    
@app.route("/link", methods=['POST'])
def link():
    data = request.get_json()
    reg_key = data["reg_key"]
    discord_id = data["discord_id"]

    if not reg_key or not discord_id:
        return jsonify({"message": "Ungültige Anfrage."}), 400
    
    if not check_reg_key(reg_key):
        return jsonify({"message": "Ungültiger Registrierungsschlüssel."}), 200
    
    if already_used_reg_key(reg_key):
        return jsonify({"message": "Dieser Registrierungsschlüssel wurde bereits verwendet oder existiert nicht."}), 200
    
    if check_discord_id(discord_id):
        return jsonify({"message": "Du bist bereits registriert."}), 200

    try:
        link_discord_id(reg_key, discord_id)
        return jsonify({"message": "Discord-ID erfolgreich mit Steam-ID verknüpft."}), 200
    except:
        return jsonify({"message": "Fehler beim Verknüpfen der IDs."}), 200
    
@app.route("/sync", methods=['POST'])
def sync():
    # Zugriff die form-Daten
    form_data = request.form.get("data")


    if not form_data:
        return jsonify({"message": "Keine Daten empfangen"}), 400
    

    try:
        # Formulardaten müssen ggf. als JSON dekodiert werden
        players = json.loads(form_data)  # Wandelt den JSON-String in Python-Objekte um
    except Exception as e:
        return jsonify({"message": "Ungültige JSON-Daten: " + str(e)}), 400

    ids = [player.get("id") for player in players]
    print(f"Empfangene Spieler-IDs: {ids}")

    # Verarbeitung der Spielerdaten
    for player in players:
        id = player.get("id")
        sid = player.get("sid")
        name = player.get("name")
        job = player.get("job")
        model = player.get("model")
        wallet = int(player.get("wallet", 0))
        faction = player.get("faction", "none") or "none"

        if not all([id, sid, name, job, model, wallet]):
            return jsonify({"message": f"Ungültige Anfrage. Daten fehlen: {player}"}), 400

        # Hier kannst du die Funktion aufrufen, um den Eintrag zu speichern
        add_or_change_entry(id, sid, name, job, model, wallet, faction)

    delete_every_entry_except_ids(ids)

    return jsonify({"message": "Daten erfolgreich synchronisiert."}), 200

@app.route("/dc/sync", methods=['GET'])
def dc_sync():
    try:
        data = get_discord_users_with_all_ranks()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"message": "Fehler beim Abrufen der Daten.", "error": str(e)}), 500
    
@app.route("/dc/roles", methods=['GET'])
def dc_roles():
    query = "SELECT * FROM mapping;"
    result = db.fetch_all(query)

    data = []
    for row in result:
        data.append({"dc_rank_id": row["dc_rank_id"], "gmod_job": row["gmod_job"]})

    return jsonify(data), 200
    
@app.route("/map", methods=['POST'])
def map():
    
    json_data = request.get_json()

    #check if file is build like {"data":[{"gmod_job": 123456789, "rank_id": 123456789}, ...]}
    if "data" not in json_data:
        return jsonify({"message": "Error: File is not build like {\"data\":[{\"gmod_job\": 123456789, \"rank_id\": 123456789}, ...]}"}), 400
    
    if not isinstance(json_data["data"], list):
        return jsonify({"message": "Error: File is not a list of dictionaries"}), 400
    
    if not json_data["data"]:
        return jsonify({"message": "Error: File is empty"}), 400
    
    data = json_data["data"]

    for entry in data:
        if not isinstance(entry, dict):
            return jsonify({"message": "Error: File is not a list of dictionaries"}), 400

        if "gmod_job" not in entry or "rank_id" not in entry:
            return jsonify({"message": "Error: File is not build like {\"data\":[{\"gmod_job\": 123456789, \"rank_id\": 123456789}, ...]}"}), 400
        
    #clear table
    query = "DELETE FROM mapping;"
    db.execute_query(query)
    db.conn.commit()

    for entry in data:
        gmod_job = entry["gmod_job"]
        rank_id = entry["rank_id"]

        query = "INSERT INTO mapping (dc_rank_id, gmod_job) VALUES (%s, %s);"
        db.execute_query(query, (rank_id, gmod_job))

    return jsonify({"message": "Mapping erfolgreich hinzugefügt."}), 201

    

app.run(host='0.0.0.0', port=5000, debug=True)