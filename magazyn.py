import streamlit as st
import pandas as pd

# Inicjalizacja listy towarów w stanie sesji Streamlit.
# Stan sesji (st.session_state) jest kluczowy w Streamlit,
# ponieważ przechowuje dane między ponownymi uruchomieniami aplikacji
# i odświeżeniami strony, co jest niezbędne dla 'magazynu'.
if 'towary' not in st.session_state:
    st.session_state.towary = []

def dodaj_towar(nazwa):
    """Dodaje nowy towar do magazynu."""
    if nazwa and nazwa not in st.session_state.towary:
        st.session_state.towary.append(nazwa)
        st.success(f"Dodano: **{nazwa}**")
    elif nazwa in st.session_state.towary:
        st.warning(f"Towar **{nazwa}** już znajduje się w magazynie.")
    else:
        st.error("Wprowadź nazwę towaru.")

def usun_towar(nazwa):
    """Usuwa towar z magazynu."""
    try:
        st.session_state.towary.remove(nazwa)
        st.info(f"Usunięto: **{nazwa}**")
    except ValueError:
        st.error(f"Błąd: Towar **{nazwa}** nie został znaleziony.")

# --- Interfejs użytkownika Streamlit ---

st.title("📦 Prosty Magazyn Towarów")
st.markdown("Aplikacja wykorzystuje listę Pythona do przechowywania danych (bez zapisu do pliku).")

## Sekcja Dodawania Towaru
st.header("➕ Dodaj Nowy Towar")
# Używamy st.form, aby zgrupować widgety i umożliwić ich jednoczesne przetworzenie
# po naciśnięciu przycisku 'Submit', co zapobiega ciągłemu odświeżaniu.
with st.form("dodaj_formularz", clear_on_submit=True):
    nowy_towar = st.text_input("Nazwa Towaru", key="input_dodaj")
    submit_dodaj = st.form_submit_button("Dodaj do Magazynu")

    if submit_dodaj:
        dodaj_towar(nowy_towar)

## Sekcja Bieżącego Stanu Magazynu
st.header("📊 Stan Magazynu")

if st.session_state.towary:
    # Tworzenie DataFrame z listy dla lepszej wizualizacji w Streamlit
    df_magazyn = pd.DataFrame(st.session_state.towary, columns=['Nazwa Towaru'])
    df_magazyn.index += 1 # Numeracja od 1
    st.table(df_magazyn)
    st.metric(label="Liczba Różnych Towarów", value=len(st.session_state.towary))
else:
    st.info("Magazyn jest pusty. Dodaj pierwszy towar!")

## Sekcja Usuwania Towaru
st.header("➖ Usuń Towar")

if st.session_state.towary:
    # Wykorzystanie st.selectbox dla wyboru towaru do usunięcia
    # Opcje są generowane dynamicznie z bieżącej listy towarów
    towar_do_usunięcia = st.selectbox(
        "Wybierz towar do usunięcia",
        st.session_state.towary,
        key="select_usun"
    )

    if st.button("Usuń Wybrany Towar"):
        usun_towar(towar_do_usunięcia)
        # Musimy wymusić ponowne uruchomienie, aby Streamlit odświeżył selectbox po usunięciu
        st.experimental_rerun()
else:
    st.info("Nie ma towarów do usunięcia.")

st.markdown("---")
st.caption("Aplikacja magazynu w Streamlit, dane przechowywane w pamięci (lista).")
