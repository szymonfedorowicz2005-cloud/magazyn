import streamlit as st
import pandas as pd
from supabase import create_client

# --------------------------------------------------
# KONFIGURACJA
# --------------------------------------------------
st.set_page_config(page_title="Magazyn", layout="wide")

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# --------------------------------------------------
# FUNKCJE BAZY
# --------------------------------------------------
def get_kategorie():
    res = supabase.table("kategorie").select("*").order("nazwa").execute()
    return res.data or []

def get_produkty():
    produkty = supabase.table("produkty").select("*").execute().data or []
    kategorie = supabase.table("kategorie").select("id, nazwa").execute().data or []

    mapa_kategorii = {k["id"]: k["nazwa"] for k in kategorie}

    for p in produkty:
        p["kategoria"] = mapa_kategorii.get(p.get("kategoria_id"), "")

    return produkty

def dodaj_kategorie(nazwa):
    supabase.table("kategorie").insert({"nazwa": nazwa}).execute()

def usun_kategorie(kategoria_id):
    supabase.table("kategorie").delete().eq("id", kategoria_id).execute()

def dodaj_produkt(nazwa, ilosc, kategoria_id):
    supabase.table("produkty").insert({
        "nazwa": nazwa,
        "ilosc": ilosc,
        "kategoria_id": kategoria_id
    }).execute()

def usun_produkt(produkt_id):
    supabase.table("produkty").delete().eq("id", produkt_id).execute()

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("📦 Magazyn (Supabase + Streamlit)")
st.markdown("---")

# ==================================================
# KATEGORIE
# ==================================================
st.header("📁 Kategorie")

kategorie = get_kategorie()

col1, col2 = st.columns(2)

with col1:
    st.subheader("➕ Dodaj kategorię")
    with st.form("dodaj_kat"):
        nazwa_kat = st.text_input("Nazwa kategorii")
        if st.form_submit_button("Dodaj"):
            if nazwa_kat:
                dodaj_kategorie(nazwa_kat)
                st.success("Kategoria dodana")
                st.rerun()

with col2:
    st.subheader("🗑 Usuń kategorię")
    if kategorie:
        mapa_kat = {k["nazwa"]: k["id"] for k in kategorie}
        wybrana = st.selectbox("Wybierz kategorię", mapa_kat.keys())
        if st.button("Usuń kategorię"):
            usun_kategorie(mapa_kat[wybrana])
            st.success("Kategoria usunięta")
            st.rerun()
    else:
        st.info("Brak kategorii")

st.markdown("---")

# ==================================================
# PRODUKTY
# ==================================================
st.header("📦 Produkty")

produkty = get_produkty()

col3, col4 = st.columns(2)

with col3:
    st.subheader("➕ Dodaj produkt")
    with st.form("dodaj_prod"):
        nazwa_p = st.text_input("Nazwa
