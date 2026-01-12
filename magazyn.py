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

def dodaj_produkt(nazwa, ilosc):
    supabase.table("produkty").insert(
        {
            "nazwa": nazwa,
            "ilosc": ilosc
        }
    ).execute()

def usun_produkt(produkt_id):
    supabase.table("produkty").delete().eq("id", produkt_id).execute()

# =============================
# UI
# =============================
st.title("📦 Magazyn – wersja stabilna")
st.markdown("---")

# =============================
# DODAWANIE
# =============================
st.subheader("➕ Dodaj produkt")

with st.form("dodaj"):
    nazwa = st.text_input("Nazwa produktu")
    ilosc = st.number_input("Ilość", min_value=1, step=1)
    submit = st.form_submit_button("Dodaj")

    if submit and nazwa:
        dodaj_produkt(nazwa, ilosc)
        st.success("Produkt dodany")
        st.rerun()

st.markdown("---")

# =============================
# LISTA + USUWANIE
# =============================
st.subheader("📋 Produkty")

produkty = get_produkty()

if produkty:
    df = pd.DataFrame(produkty)
    st.dataframe(df, use_container_width=True)

    mapa = {p["nazwa"]: p["id"] for p in produkty if "id" in p}

    wybrany = st.selectbox("Wybierz produkt do usunięcia", mapa.keys())

    if st.button("🗑 Usuń produkt"):
        usun_produkt(mapa[wybrany])
        st.success("Produkt usunięty")
        st.rerun()
else:
    st.info("Brak produktów w magazynie")

st.caption("Supabase + Streamlit • wersja stabilna")
