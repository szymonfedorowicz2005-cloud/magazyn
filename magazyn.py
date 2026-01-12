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
    res = supabase.table("kategorie").select("id, nazwa").execute()
    return res.data or []

def dodaj_produkt(nazwa, liczba, kategoria_id):
    supabase.table("produkty").insert(
        {
            "nazwa": nazwa,
            "liczba": liczba,
            "kategoria_id": kategoria_id
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
mapa_kategorii = {k["nazwa"]: k["id"] for k in kategorie}

with st.form("formularz_dodaj"):
    nazwa = st.text_input("Nazwa produktu")
    liczba = st.number_input("Liczba sztuk", min_value=1, step=1)

    if kategorie:
        wybrana_kategoria = st.selectbox(
            "Kategoria",
            list(mapa_kategorii.keys())
        )
    else:
        st.error("Brak kategorii w bazie")
        wybrana_kategoria = None

    submit = st.form_submit_button("Dodaj")

    if submit and nazwa and wybrana_kategoria:
        dodaj_produkt(
            nazwa=nazwa,
            liczba=liczba,
            kategoria_id=mapa_kategorii[wybrana_kategoria]
        )
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

    # mapowanie kategorii ID → nazwa
    if kategorie and "kategoria_id" in df.columns:
        mapa_id_nazwa = {k["id"]: k["nazwa"] for k in kategorie}
        df["kategoria"] = df["kategoria_id"].map(mapa_id_nazwa)

    st.dataframe(
        df[["nazwa", "liczba", "kategoria"]],
        use_container_width=True
    )

    mapa = {
        f'{p["nazwa"]} (ID: {p["id"]})': p["id"]
        for p in produkty
    }

    st.markdown("### 🗑 Usuń produkt")
    wybrany = st.selectbox("Wybierz produkt", mapa.keys())

    if st.button("Usuń produkt"):
        usun_produkt(mapa[wybrany])
        st.success("Produkt usunięty")
        st.rerun()
else:
    st.info("Brak produktów w magazynie")

st.caption("Supabase + Streamlit • wersja zgodna ze schematem bazy")
