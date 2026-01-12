import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# --- Konfiguracja Streamlit ---
st.set_page_config(layout="wide") 

# --- Session state ---
if 'magazyn' not in st.session_state:
    st.session_state.magazyn = {}

if 'komunikat_usun' not in st.session_state:
    st.session_state.komunikat_usun = ""

if 'historia_operacji' not in st.session_state:
    st.session_state.historia_operacji = []

# --- Historia ---
def dodaj_do_historii(typ, nazwa, ilosc, nowa_ilosc):
    st.session_state.historia_operacji.append({
        'czas': datetime.now().strftime("%H:%M:%S"),
        'typ': typ,
        'towar': nazwa,
        'ilosc': ilosc,
        'status': f"-> {nowa_ilosc} szt."
    })

# --- Logika magazynu ---
def dodaj_sztuke(nazwa, ilosc):
    if not nazwa:
        st.error("Wprowadź nazwę towaru.")
        return

    ilosc = int(ilosc)

    if nazwa in st.session_state.magazyn:
        st.session_state.magazyn[nazwa] += ilosc
    else:
        st.session_state.magazyn[nazwa] = ilosc

    dodaj_do_historii("DODANO", nazwa, ilosc, st.session_state.magazyn[nazwa])
    st.success(f"Dodano {ilosc} szt. **{nazwa}**")

def usun_sztuke_callback():
    nazwa = st.session_state.select_usun
    ilosc = int(st.session_state.ilosc_usun)

    if nazwa not in st.session_state.magazyn:
        return

    obecna = st.session_state.magazyn[nazwa]

    if ilosc > obecna:
        st.session_state.komunikat_usun = "Za mało sztuk."
        return

    st.session_state.magazyn[nazwa] -= ilosc
    nowa = st.session_state.magazyn[nazwa]

    dodaj_do_historii("USUNIĘTO", nazwa, ilosc, nowa)

    if nowa == 0:
        del st.session_state.magazyn[nazwa]
        st.session_state.komunikat_usun = f"Usunięto cały produkt **{nazwa}**"
    else:
        st.session_state.komunikat_usun = f"Usunięto {ilosc} szt. **{nazwa}**"

def usun_produkt_callback():
    nazwa = st.session_state.select_usun_calosc
    if not nazwa:
        return

    ilosc = st.session_state.magazyn.get(nazwa, 0)

    dodaj_do_historii("USUNIĘTO CAŁOŚĆ", nazwa, ilosc, 0)
    del st.session_state.magazyn[nazwa]

    st.success(f"Produkt **{nazwa}** został całkowicie usunięty.")

# --- Layout ---
kol_l, kol_g, kol_p = st.columns([1, 4, 1.5])

with kol_g:
    st.title("🎁🎄 Świąteczny Magazyn 🎄🎁")
    st.markdown("---")

    # Dodawanie
    st.header("➕ Dodaj towar")
    with st.form("dodaj"):
        c1, c2 = st.columns([3, 1])
        with c1:
            nazwa = st.text_input("Nazwa towaru")
        with c2:
            ilosc = st.selectbox("Ilość", range(1, 6))
        if st.form_submit_button("Dodaj"):
            dodaj_sztuke(nazwa, ilosc)

    st.markdown("---")

    # Usuwanie ilości
    st.header("➖ Usuń ilość")
    if st.session_state.komunikat_usun:
        st.info(st.session_state.komunikat_usun)
        st.session_state.komunikat_usun = ""

    if st.session_state.magazyn:
        c3, c4 = st.columns([3, 1])
        with c3:
            st.selectbox(
                "Wybierz towar",
                list(st.session_state.magazyn.keys()),
                key="select_usun"
            )
        with c4:
            st.selectbox("Ilość", range(1, 6), key="ilosc_usun")

        st.button("Usuń ilość", on_click=usun_sztuke_callback)
    else:
        st.info("Brak towarów.")

    st.markdown("---")

    # Usuwanie całego produktu
    st.header("🗑 Usuń CAŁY produkt")
    if st.session_state.magazyn:
        st.selectbox(
            "Wybierz produkt",
            list(st.session_state.magazyn.keys()),
            key="select_usun_calosc"
        )
        st.button("❌ Usuń produkt", on_click=usun_produkt_callback)
    else:
        st.info("Brak towarów.")

    st.markdown("---")

    # Stan magazynu
    st.header("📊 Stan magazynu")
    if st.session_state.magazyn:
        df = pd.DataFrame({
            "Towar": st.session_state.magazyn.keys(),
            "Ilość": st.session_state.magazyn.values()
        })

        st.table(df)

        wykres = alt.Chart(df).mark_bar().encode(
            x="Towar",
            y="Ilość",
            tooltip=["Towar", "Ilość"]
        )
        st.altair_chart(wykres, use_container_width=True)
    else:
        st.info("Magazyn pusty.")

with kol_p:
    st.header("🔔 Historia")
    st.markdown("---")

    for h in reversed(st.session_state.historia_operacji):
        st.markdown(f"**{h['czas']} – {h['typ']}**")
        st.markdown(f"{h['towar']} ({h['ilosc']} szt.)")
        st.markdown(h['status'])
        st.markdown("---")
