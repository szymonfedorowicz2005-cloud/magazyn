import streamlit as st
import pandas as pd
from supabase import create_client

# =============================
# KONFIGURACJA
# =============================
st.set_page_config(
    page_title="Magazyn – produkty",
    layout="wide"
)

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# =============================
# FUNKCJE BAZY
# =============================
def pobierz_produkty():
    res = supabase.table("produkty").select("*").execute()
    return res.data or []

def pobierz_kategorie():
    """
    Pobiera TYLKO istniejące kategorie z Supabase.
    Brak dodawania / usuwania.
    """
    res = supabase.table("kategorie").select("nazwa").execute()
    return [k["nazwa"] for k in res.data] if res.data else []

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

# =============================
# UI
# =============================
st.title("📦 Magazyn – produkty")
st.markdown("---")

# =============================
# DODAWANIE PRODUKTU
# =============================
st.subheader("➕ Dodaj produkt")

kategorie = pobierz_kategorie()

with st.form("formularz_dodaj"):
    nazwa = st.text_input("Nazwa produktu")
    ilosc = st.number_input("Ilość", min_value=1, step=1)

    if kategorie:
        kategoria = st.selectbox("Kategoria", kategorie)
    else:
        kategoria = ""

    submit = st.form_submit_button("Dodaj")

    if submit and nazwa:
        dodaj_produkt(nazwa, ilosc, kategoria)
        st.success("Produkt dodany")
        st.rerun()

st.markdown("---")

# =============================
# LISTA + USUWANIE
# =============================
st.subheader("📋 Lista produktów")

produkty = pobierz_produkty()

if produkty:
    df = pd.DataFrame(produkty)

    kolumny = [c for c in ["nazwa", "ilosc", "kategoria"] if c in df.columns]
    st.dataframe(df[kolumny], use_container_width=True)

    mapa = {
        f"{p.get('nazwa', 'brak nazwy')} (ID: {p.get('id')})": p["id"]
        for p in produkty
        if "id" in p
    }

    st.markdown("### 🗑 Usuń produkt")
    wybrany = st.selectbox("Wybierz produkt", mapa.keys())

    if st.button("Usuń produkt"):
        usun_produkt(mapa[wybrany])
        st.success("Produkt usunięty")
        st.rerun()
else:
    st.info("Brak produktów w magazynie")

st.caption("Supabase + Streamlit • kategorie tylko do wyboru")
