import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# -------------------------------------------------
# KONFIGURACJA
# -------------------------------------------------
st.set_page_config(page_title="Magazyn", layout="wide")

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# -------------------------------------------------
# FUNKCJE SUPABASE
# -------------------------------------------------
def pobierz_produkty():
    res = supabase.table("produkty").select("*").order("created_at").execute()
    data = res.data or []

    # 🔥 FIX: JSON -> tekst (kategorie)
    for row in data:
        if isinstance(row.get("kategorie"), dict):
            row["kategorie"] = row["kategorie"].get("nazwa", "")

    return data


def dodaj_produkt(nazwa, ilosc, kategoria):
    supabase.table("produkty").insert({
        "nazwa": nazwa,
        "ilosc": ilosc,
        "kategorie": {"nazwa": kategoria}
    }).execute()


def usun_produkt(produkt_id):
    supabase.table("produkty").delete().eq("id", produkt_id).execute()


# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("📦 Magazyn produktów")
st.markdown("---")

# -------------------------------------------------
# DODAWANIE
# -------------------------------------------------
st.subheader("➕ Dodaj produkt")

with st.form("dodaj_produkt"):
    c1, c2, c3 = st.columns(3)

    with c1:
        nazwa = st.text_input("Nazwa produktu")
    with c2:
        ilosc = st.number_input("Ilość", min_value=1, step=1)
    with c3:
        kategoria = st.text_input("Kategoria")

    submit = st.form_submit_button("Dodaj")

    if submit:
        if nazwa and kategoria:
            dodaj_produkt(nazwa, ilosc, kategoria)
            st.success("Produkt dodany")
            st.rerun()
        else:
            st.error("Uzupełnij wszystkie pola")

st.markdown("---")

# -------------------------------------------------
# LISTA PRODUKTÓW
# -------------------------------------------------
st.subheader("📋 Lista produktów")

produkty = pobierz_produkty()

if not produkty:
    st.info("Brak produktów w bazie")
else:
    df = pd.DataFrame(produkty)

    # kolejność kolumn
    kolumny = [c for c in ["nazwa", "ilosc", "kategorie"] if c in df.columns]
    st.dataframe(df[kolumny], use_container_width=True)

st.markdown("---")

# -------------------------------------------------
# USUWANIE
# -------------------------------------------------
st.subheader("🗑 Usuń produkt")

if produkty:
    mapa = {f"{p['nazwa']} ({p['kategorie']})": p["id"] for p in produkty}

    wybrany = st.selectbox("Wybierz produkt do usunięcia", mapa.keys())

    if st.button("❌ Usuń produkt"):
        usun_produkt(mapa[wybrany])
        st.success("Produkt usunięty")
        st.rerun()
else:
    st.info("Nie ma czego usuwać")

st.markdown("---")

# -------------------------------------------------
# STOPKA
# -------------------------------------------------
st.caption("Dane przechowywane w Supabase | Streamlit UI")
