from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# ---------------------------------------------------------
# Studiengang
# ---------------------------------------------------------
class Studiengang(Base):
    __tablename__ = 'studiengang'

    id = Column(Integer, primary_key=True)
    l_abschluss = Column(String)            # "Bachelor", "Master"
    k_abschluss = Column(String)            # "B.Sc.", "M.A."
    l_name = Column(String)                 # "Betriebswirtschaftslehre"
    k_name = Column(String)                 # "BWL"
    fak = Column(String)                    # "WSF"
    inst = Column(String)                   # "IBWL"
    abint = Column(String)                  # 82
    stg = Column(Integer)                   # 105

    # Beziehungen
    pos = relationship("Pruefungsordnung", back_populates="studiengang")
    ref = relationship("Reform", back_populates="studiengang")

    def __repr__(self):
        return f"<Studiengang(name={self.l_name}, abschluss={self.l_abschluss})>"
    
# ---------------------------------------------------------
# Prüfungsordnungsversion
# ---------------------------------------------------------
class Pruefungsordnung(Base):
    __tablename__ = 'pruefungsordnung'
    id = Column(Integer, primary_key=True)
    studiengang_id = Column(Integer, ForeignKey('studiengang.id'))
    rsz = Column(Integer)                  # 6
    po_version = Column(Integer)           # 2024
    po_start = Column(Integer)             # 20212
    po_ende = Column(Integer)              # 20242
    
    # Beziehungen
    studiengang = relationship("Studiengang", back_populates="pos")

# ---------------------------------------------------------
# Studienreformverfahren
# ---------------------------------------------------------
class Reform(Base):
    __tablename__='studienreform'
    id = Column(Integer, primary_key=True)
    studiengang_id = Column(Integer, ForeignKey('studiengang.id'))
    hqe_id = Column(Integer, ForeignKey('hqe.id'))
    antrag = Column(Date)                    # 12.05.2024
    zyklus = Column(String)                  # "WS 2026/27"
    art = Column(String)                     # "Neueinrichtung"; "Schließung"; "Änderung"
    verfahren = Column(String)               # "vereinfachtes Verfahren"; "reguläres Verfahren"; "Verfahren mit Reformkommission";
    kon_verfahren = Column(String)  
    sk_el = Column(Date)                     # Erste Lesung SK: 12.05.2024
    sk_el_txt = Column(String)               # "Protokollauszug SK 1"  
    sk_zl = Column(Date)                     # Zweite Lesung SK: 12.06.2024
    sk_zl_txt = Column(String)               # "Protokollauszug SK 2"
    sk_dl = Column(Date)                     # Dritte Lesung SK: 12.07.2024
    sk_dl_txt = Column(String)               # "Protokollauszug SK 3"
    sk_vl = Column(Date)                     # Vierte Lesung SK: 12.08.2024
    sk_vl_txt = Column(String)               # "Protokollauszug SK 4"
    as_el = Column(Date)                     # 1. Beschlussfassung AS: 12.09.2024
    as_el_txt = Column(String)               # "Protokollauszug AS 1"
    as_zl = Column(Date)                     # 2. Beschlussfassung AS: 12.10.2024
    as_zl_txt = Column(String)               # "Protokollauszug AS 2"

    # Beziehungen
    studiengang = relationship("Studiengang", back_populates="ref")
    hqe = relationship("HQE", back_populates="ref")

# ---------------------------------------------------------
# HQEler
# ---------------------------------------------------------
class HQE(Base):
    __tablename__='hqe'
    id = Column(Integer, primary_key=True)
    l_name = Column(String)               # "Max Mustermann"
    k_name = Column(String)               # "MM"
    itmz = Column(String)                 # "cj1234"
    tel = Column(Integer)                 # 1234
    email = Column(String)                # "max.mustermann@uni-rostock.de" 

    # Beziehungen
    ref = relationship("Reform", back_populates="hqe")
