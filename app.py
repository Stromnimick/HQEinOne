import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# 1. Lade Konfiguration aus der .env Datei (nur für lokale Entwicklung wichtig)
load_dotenv()

# 2. Hole die Variablen (egal ob aus .env oder vom Server-System)
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# Prüfen, ob alles da ist
if not all([db_user, db_password, db_host, db_name]):
    st.error("Fehler: Datenbank-Konfiguration fehlt! Bitte .env prüfen.")
    st.stop()

# 3. Verbindungs-String bauen
db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

st.title("HQE in One")

try:
    # Verbindung herstellen
    engine = create_engine(db_url)
    
    # Test-Verbindung mit der modernen SQLAlchemy Syntax
    with engine.connect() as conn:
        st.success(f"Verbunden mit Datenbank: {db_name} auf {db_host} ✅")
        
        # Tabelle erstellen (falls nicht existiert)
        conn.execute(text("CREATE TABLE IF NOT EXISTS module (id SERIAL PRIMARY KEY, name TEXT, ects INTEGER)"))
        conn.commit() # Wichtig bei neuen SQLAlchemy Versionen!

        # Formular für neue Module
        with st.form("neues_modul"):
            name_input = st.text_input("Modulname")
            ects_input = st.number_input("ECTS", step=3)
            submitted = st.form_submit_button("Speichern")
            
            if submitted:
                conn.execute(text("INSERT INTO module (name, ects) VALUES (:name, :ects)"), 
                             {"name": name_input, "ects": ects_input})
                conn.commit()
                st.success(f"Modul {name_input} gespeichert!")

        # Daten anzeigen
        # Pandas liest direkt SQL
        df = pd.read_sql("SELECT * FROM module", conn)
        st.dataframe(df)

except Exception as e:
    st.error(f"Datenbank-Fehler: {e}")