import streamlit as st
import pandas as pd

# Inicjalizacja listy towarów i zmiennych stanu
if 'towary' not in st.session_state:
    st.session_state.towary = []
    
if 'usunieto' not in st.session_state:
    st.session_state.usunieto = ""

def dodaj_towar(nazwa):
    """Dodaje nowy towar do magazynu."""
    if nazwa and nazwa not in st.session_state.towary:
        st.session_state.towary.append(nazwa)
        st.success(f"Dodano: **{nazwa}**")
    elif nazwa in st.session_state.towary:
        st.warning(f"Towar **{nazwa}** już znajduje się w magazynie.")
    else:
        st.error("Wprowadź nazwę towaru.")

def usun_towar_callback():
    """Usuwa towar z magazynu i aktualizuje stan.
    Ta funkcja jest wywoływana jako callback przycisku."""
    
    # st.session_state.select_usun pobiera wartość z pola st.selectbox z kluczem 'select_usun'
    towar_do_usunięcia = st.session_state.select_usun 
    
    try:
        if towar_do_usunięcia:
            # Usuwamy towar z głównej listy
            st.session_state.towary.remove(towar_do_usunięcia)
            # Ustawiamy komunikat o sukcesie w stanie sesji, aby wyświetlić go po ponownym uruchomieniu
            st.session_state.usunieto = f"Usunięto: **{towar_do_usunięcia}**"
        else:
            st.session_state.usunieto = "Nie wybrano towaru do usunięcia."
    except ValueError:
        st.session_state.usunieto = f"Błąd: Towar **{towar_do_usunięcia}** nie został znaleziony."


# --- Interfejs użytkownika Streamlit ---

st.title("📦 Prosty Magazyn Towarów")
st.markdown("Aplikacja wykorzystuje listę Pythona do przechowywania danych (bez zapisu do pliku).")

## Sekcja Dodawania Towaru
st.header("➕ Dodaj Nowy Towar")

with st.form("dodaj_formularz", clear_on_submit=True):
    nowy_towar = st.text_input("Nazwa Towaru", key="input_dodaj")
    submit_dodaj = st.form_submit_button("Dodaj do Magazynu")

    if submit_dodaj:
        dodaj_towar(nowy_towar)

## Sekcja Bieżącego Stanu Magazynu
st.header("📊 Stan Magazynu")

if st.session_state.towary:
    # Tworzenie DataFrame z listy dla lepszej wizualizacji
    df_magazyn = pd.DataFrame(st.session_state.towary, columns=['Nazwa Towaru'])
    df_magazyn.index += 1 # Numeracja od 1
    st.table(df_magazyn)
    st.metric(label="Liczba Różnych Towarów", value=len(st.session_state.towary))
else:
    st.info("Magazyn jest pusty. Dodaj pierwszy towar!")

## Sekcja Usuwania Towaru
st.header("➖ Usuń Towar")

# Wyświetlamy komunikat z callbacka usunięcia (jeśli istnieje)
if st.session_state.usunieto:
    st.info(st.session_state.usunieto)
    # Czyścimy komunikat, aby nie wyświetlał się ciągle
    st.session_state.usunieto = "" 

if st.session_state.towary:
    # Wykorzystanie st.selectbox dla wyboru towaru do usunięcia
    towar_do_usunięcia = st.selectbox(
        "Wybierz towar do usunięcia",
        st.session_state.towary,
        key="select_usun" # Klucz jest niezbędny, aby callback mógł odczytać wartość
    )

    # Użycie callbacku on_click, który automatycznie odświeża stan aplikacji
    st.button(
        "Usuń Wybrany Towar",
        on_click=usun_towar_callback
    )
else:
    st.info("Nie ma towarów do usunięcia.")

st.markdown("---")
st.caption("Aplikacja magazynu w Streamlit, dane przechowywane w pamięci (lista).")
