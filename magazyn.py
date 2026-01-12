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
    response = supabase.table("produkty").select("*").execute()
    return response.data or []

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
st.title("📦 Magazyn – zarządzanie produktami")
st.markdown("---")

# =============================
# DODAWANIE PRODUKTU
# =============================
st.subheader("➕ Dodaj produkt")

with st.form("formularz_dodaj"):
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
st.subheader("📋 Lista produktów")

produkty = pobierz_produkty()

if produkty:
    df = pd.DataFrame(produkty)

    # pokazujemy tylko bezpieczne kolumny
    kolumny = [c for c in ["nazwa", "ilosc"] if c in df.columns]
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

st.caption("Supabase + Streamlit • wersja stabilna (tylko produkty)")
