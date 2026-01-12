import streamlit as st
import pandas as pd
from supabase import create_client

# =============================
# KONFIGURACJA
# =============================
st.set_page_config(page_title="Magazyn", layout="wide")

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# =============================
# FUNKCJE BAZY
# =============================
def get_produkty():
    res = supabase.table("produkty").select("*").execute()
    return res.data or []

def get_kategorie():
    res = supabase.table("kategorie").select("*").execute()
    return res.data or []

def dodaj_produkt(nazwa, ilosc, kategoria):
    supabase.table("produkty").insert(
        {
            "nazwa": nazwa,
            "ilosc": ilosc,
            "kategoria": kategoria
        }
    ).execute()

def usun_produkt(produkt_id):
    supabase.table("produkty").delete().eq("id", produkt_id).execute()

def dodaj_kategorie(nazwa):
    supabase.table("kategorie").insert(
        {
            "nazwa": nazwa
        }
    ).execute()

def usun_kategorie(kategoria_id):
    supabase.table("kategorie").delete().eq("id", kategoria_id).execute()

# =============================
# UI
# =============================
st.title("📦 Magazyn z kategoriami")
st.markdown("---")

# =============================
# KATEGORIE
# =============================
st.header("📁 Kategorie")

kategorie = get_kategorie()

col_k1, col_k2 = st.columns(2)

wit
