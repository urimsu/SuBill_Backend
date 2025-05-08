from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import mysql.connector
from mysql.connector import Error
import os

originLink="http://subill.su-tech.org"

host_name=os.environ.get('hostname')# type: ignore
host_user=os.environ.get('hostuser')# type: ignore
host_password=os.environ.get('hostpassword')# type: ignore
host_database=os.environ.get('hostdatabase') # type: ignore


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": originLink}})  # Erlaube nur Anfragen von Angular

def listInString(liste):
    finalString=''
    for i in liste:
        finalString+=f"{i[0]} - {i[1]}\n"
    return finalString


def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='w01f678f.kasserver.com',            # z.B. 'mysql5.all-inkl.com'
            user='d0418500',    # dein MySQL-Benutzername
            password='Silleman1122.',     # dein MySQL-Passwort
            database='d0418500'    # deine MySQL-Datenbank
        )
        print("Verbindung zur Datenbank erfolgreich")
    except Error as e:
        print(f"Fehler beim Verbinden zur Datenbank: {e}")
    
    return connection

def fetch_data(connection):
    cursor = connection.cursor()
    select_query = "SELECT * FROM `Kunden-Tabelle`"  # Ändere 'benutzer' in den Namen deiner Tabelle
    cursor.execute(select_query)

    # Hole die Spaltennamen
    columns = [column[0] for column in cursor.description]

    rows = cursor.fetchall()

    kundenDaten=[]

    for row in rows:
        row_dict = dict(zip(columns, row))
        kundenDaten.append([row_dict['Kundennummer'],row_dict['Firma'],row_dict['Nachname'],row_dict['Name'],row_dict['Straße'],row_dict['Plz und Wohnort'], row_dict['Dienstleistung']])

    #print('KundenDaten von allen Kunden: ',kundenDaten)
    return kundenDaten

def databaseAddData(connection, firma,name, nachname, strasse, plzUndOrt, dienstleistung):
    cursor = connection.cursor()
    
    insert_query = """
    INSERT INTO `Kunden-Tabelle` (`Kundennummer`,`Firma`,`Name`, `Nachname`, `Straße`, `Plz und Wohnort`, `Dienstleistung`) 
    VALUES (NULL, %s, %s, %s, %s, %s, %s);
    """
    
    try:
        cursor.execute(insert_query, (firma, name, nachname, strasse, plzUndOrt, dienstleistung))
        connection.commit()  # Vergiss nicht, die Änderungen zu speichern
    except Exception as e:
        print(f"Fehler beim Einfügen der Daten: {e}")
        connection.rollback()  # Bei einem Fehler zurückrollen

def databaseDeleteData(connection,kundennummer):
    cursor = connection.cursor()
    
    delete_query = """DELETE FROM `Kunden-Tabelle` WHERE `Kundennummer` = %s"""    
    try:
        cursor.execute(delete_query, (kundennummer,))
        connection.commit()  # Vergiss nicht, die Änderungen zu speichern
        return jsonify({"message": "Daten erfolgreich gelöscht!"}), 200
    except Exception as e:
        print(f"Fehler beim loeschen der Daten: {e}")
        connection.rollback()  # Bei einem Fehler zurückrollen
    finally:
        cursor.close()


@app.route('/', methods=['POST'])
def receive_daten():
    try:
        data = request.get_json()  # Empfange die JSON-Daten
        if not data:
            return jsonify({"message": "Keine Daten empfangen!"}), 400
        
        firma = data.get('firma', '')
        vorname = data.get('vorname', '')
        nachname = data.get('nachname', '')
        strasse = data.get('strasse', '')
        plzUndOrt = data.get('plzUndOrt', '')
        rechnungsnummer = data.get('rechnungsnummer', '')
        rechnungsgrund = data.get('rechnungsgrund', '')

        print(f"Empfangene Daten: {data}")

        conn = create_connection()
        # Beispielaufruf
        if conn:
            fetch_data(conn)
        databaseAddData(conn,firma ,vorname, nachname, strasse, plzUndOrt, listInString(rechnungsgrund))
        conn.close()

        return jsonify({
            "message": "Daten empfangen!",
            "Firma": firma,
            "receivedVorname": vorname,
            "receivedNachname": nachname,
            "strasse": strasse,
            "plzUndOrt": plzUndOrt,
            "rechnungsnummer": rechnungsnummer,
            "rechnungsgrund": rechnungsgrund
        }), 200
    except Exception as e:
        print(f"Fehler aufgetreten: {e}")  # Ausgabe des Fehlers in die Konsole
        return jsonify({"message": "Fehler beim Empfangen der Daten!", "error": str(e)}), 500
    
    

@app.route('/deleteData', methods=["POST"])
@cross_origin(origin=originLink)
def deleteDaten():
    conn=create_connection()
    try:
        data = request.get_json()  # Empfange die JSON-Daten
        if not data:
            return jsonify({"message": "Keine Daten empfangen!"}), 400
        kundennummer=data.get('kundennummer',)
        databaseDeleteData(conn,kundennummer)
        conn.close()
        return jsonify({"deleted: ": kundennummer})
    except Exception as e:
        print(f"Fehler aufgetreten: {e}")  # Ausgabe des Fehlers in die Konsole
        return jsonify({"message": "Fehler beim Loeschen der Daten!", "error": str(e)}), 500
        

@app.route('/kundenData', methods=["GET"])
@cross_origin(origin=originLink)  # Nur Anfragen von localhost:4200 erlauben
def sendDaten():
    conn=create_connection()
    kundendaten=fetch_data(conn)
    return jsonify(kundendaten)


if __name__ == '__main__':
    app.run(debug=True)
