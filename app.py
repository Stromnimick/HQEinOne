import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Import der Modelle
from models import Base, Studiengang, Pruefungsordnung, Reform, HQE

# Lade Konfiguration aus der .env Datei (nur für lokale Entwicklung wichtig)
load_dotenv()

# Hole die Variablen (egal ob aus .env oder vom Server-System)
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# Prüfen, ob alles da ist
if not all([db_user, db_password, db_host, db_name]):
    st.error("Fehler: Datenbank-Konfiguration fehlt! Bitte .env prüfen.")
    st.stop()

# Verbindungs-String bauen
db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Verbindung herstellen
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# Dieser Befehl schaut in models.py und erstellt alle Tabellen, die noch fehlen.
Base.metadata.create_all(engine)

# Seiten-Konfiguration
st.set_page_config(page_title="HQE in One", layout="wide")

# Navigation
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Bereich wählen:",
    ["Studiengänge", "Genehmigungsverfahren", "Daten anlegen und bearbeiten"]
)

# =========================================================
# ANSICHT: Daten anlegen und bearbeiten
# =========================================================
if menu == "Daten anlegen und bearbeiten":
    st.title("Daten anlegen und bearbeiten")

    # Erstelle die Tabs
    tab1, tab2 = st.tabs(["Studiengänge", "Weitere Daten"])

    with tab1:
        st.subheader(f"Studiengänge")
            
        with st.form("neuer_studiengang"):
            l_abschluss_input = st.selectbox("Abschluss (lang)", ["Bachelor", "Master", "Lehramt", "Staatsexamen"])
            k_abschluss_input = st.selectbox("Abschluss (kurz)", ["B.Sc.", "B.A.", "B.Eng.", "M.Sc.", "M.A.", "M.Eng."])
            l_name_input = st.text_input("Name (lang)")
            k_name_input = st.text_input("Name (kurz)")
            fak_input = st.selectbox("Fakultät", ["AUF", "IEF", "JUF", "MNF", "MSF", "PHF", "THF", "UMR", "WSF"])
            inst_input = st.selectbox("Institut", ["MNF-Math", "WSF-IBWL"])
            abint_input = st.text_input("abint POS Nummer")
            stg_input = st.text_input("stg POS Nummer")
            
            # Der Button muss exakt so eingerückt sein wie die Inputs
            submitted = st.form_submit_button("Studiengang speichern")

        if submitted:
            # Objekt erstellen
            neuer_sg = Studiengang(
                l_abschluss = l_abschluss_input, 
                k_abschluss = k_abschluss_input, 
                l_name =l_name_input, 
                k_name = k_name_input, 
                fak = fak_input,
                inst =  inst_input,
                abint = abint_input,
                stg =  stg_input,
            )
                    
            # Zur Datenbank hinzufügen
            session.add(neuer_sg)
            session.commit()
            st.success(f"Studiengang '{k_abschluss_input} ({l_name_input})' wurde angelegt!")
            st.rerun()

        # Anzeige der Daten
        st.divider()
        st.subheader("Alle Studiengänge")

        # alle Studiengänge auslesen
        alle_sg = session.query(Studiengang).all()

        # Umwandeln in eine Tabelle für Streamlit
        data = []
        for sg in alle_sg:
            data.append({
            "ID": sg.id,
            "Name": sg.l_name,
            "Name (kurz)": sg.k_name,
            "Abschluss": sg.l_abschluss,
            "Abschluss (kurz)": sg.k_abschluss,
            "Fakultät": sg.fak,
            "Institut": sg.inst
        })

        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)

            st.divider()
            st.subheader("Datensatz bearbeiten oder löschen")
            
            # Auswahl des Studiengangs anhand des Namens (oder ID)
            sg_dict = {f"{sg.l_name} ({sg.k_abschluss})": sg for sg in alle_sg}
            auswahl_name = st.selectbox("Studiengang zum Bearbeiten/Löschen wählen:", options=list(sg_dict.keys()))
            ausgewählter_sg = sg_dict[auswahl_name]

            col1, col2 = st.columns(2)

            with col1:
                # LÖSCHEN BUTTON
                if st.button("🗑️ Ausgewählten Studiengang unwiderruflich löschen", type="primary"):
                    session.delete(ausgewählter_sg)
                    session.commit()
                    st.warning(f"Studiengang {auswahl_name} gelöscht!")
                    st.rerun()

            with col2:
                # BEARBEITEN (Expander öffnet ein vorausgefülltes Formular)
                with st.expander("📝 Daten bearbeiten"):
                    with st.form("edit_form"):
                        # Die 'value' Parameter füllen das Formular mit den alten Daten
                        edit_l_name = st.text_input("Name (lang)", value=ausgewählter_sg.l_name)
                        edit_fak = st.selectbox("Fakultät", ["AUF", "IEF", "JUF", "MNF", "MSF", "PHF", "THF", "UMR", "WSF"], 
                                                index=["AUF", "IEF", "JUF", "MNF", "MSF", "PHF", "THF", "UMR", "WSF"].index(ausgewählter_sg.fak))
                        edit_inst = st.selectbox("Institut", ["MNF-Math", "WSF-IBWL"], 
                                                index=["MNF-Math", "WSF-IBWL"].index(ausgewählter_sg.inst))

                        edit_submitted = st.form_submit_button("Änderungen speichern")
                        
                        if edit_submitted:
                            # Bestehendes Objekt aktualisieren
                            ausgewählter_sg.l_name = edit_l_name
                            ausgewählter_sg.fak = edit_fak
                            ausgewählter_sg.inst = edit_inst
                            # ... hier weitere Felder analog hinzufügen ...
                            
                            session.commit()
                            st.success("Änderungen gespeichert!")
                            st.rerun()

        else:
            st.info("Noch keine Studiengänge in der Datenbank.")