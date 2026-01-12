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
    kategorie = supabase.table("kategorie").select("*").execute().data or []

    # mapowanie kategorii
    mapa_kategorii = {}
    for k in kategorie:
        if "id" in k and "nazwa" in k:
            mapa_kategorii[k["id"]] = k["nazwa"]

    # ujednolicenie kluczy
    wynik = []
    for p in produkty:
        wynik.append({
            "nazwa": p.get("nazwa") or p.get("name") or "",
            "ilosc": p.get("ilosc") or p.get("liczba") or p.get("quantity") or 0,
            "kategoria": mapa_kategorii.get(
                p.get("kategoria_id") or p.get("kategoria"),
                ""
            ),
            "id": p.get("id")
        })

    return wynik

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

# ==================================================
# UI
# ==================================================
st.title("📦 Magazyn")
st.markdown("---")

# ==================================================
# KATEGORIE
# ==================================================
st.header("📁 Kategorie")

kategorie = get_kategorie()

col1, col2 = st.columns(2)

with col1:
    st.subheader("➕ Dodaj kategorię")
    with st.form("dodaj_kategorie"):
        nazwa_kat = st.text_input("Nazwa kategorii")
        if st.form_submit_button("Dodaj") and nazwa_kat:
            dodaj_kategorie(nazwa_kat)
            st.success("Kategoria dodana")
            st.rerun()

with col2:
    st.subheader("🗑 Usuń kategorię")
    if kategorie:
        mapa_kat = {k["nazwa"]: k["id"] for k in kategorie if "id" in k}
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
    with st.form("dodaj_produkt"):
        nazwa_p = st.text_input("Nazwa produktu")
        ilosc_p = st.number_input("Ilość", min_value=1, step=1)

        if kategorie:
            mapa_kat = {k["nazwa"]: k["id"] for k in kategorie if "id" in k}
            kat = st.selectbox("Kategoria", mapa_kat.keys())
        else:
            kat = None

        if st.form_submit_button("Dodaj") and nazwa_p and kat:
            dodaj_produkt(nazwa_p, ilosc_p, mapa_kat[kat])
            st.success("Produkt dodany")
            st.rerun()
