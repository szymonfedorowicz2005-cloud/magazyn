import streamlit as st
import pandas as pd
from supabase import create_client

# ==================================================
# KONFIGURACJA
# ==================================================
st.set_page_config(page_title="Magazyn", layout="wide")

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# ==================================================
# FUNKCJE BAZY
# ==================================================
def get_kategorie():
    return supabase.table("kategorie").select("*").execute().data or []

def get_produkty():
    produkty = supabase.table("produkty").select("*").execute().data or []

    wynik = []
    for p in produkty:
        wynik.append({
            "id": p.get("id"),
            "nazwa": p.get("nazwa") or p.get("name") or "",
            "ilosc": p.get("ilosc") or p.get("liczba") or p.get("quantity") or 0,
            "kategoria": p.get("kategoria") or ""  # tylko display
        })

    return wynik

def dodaj_kategorie(nazwa):
    supabase.table("kategorie").insert({"nazwa": nazwa}).execute()

def usun_kategorie(kategoria_id):
    supabase.table("kategorie").delete().eq("id", kategoria_id).execute()

def dodaj_produkt(nazwa, ilosc):
    supabase.table("produkty").insert({
        "nazwa": nazwa,
        "ilosc": ilosc
    }
