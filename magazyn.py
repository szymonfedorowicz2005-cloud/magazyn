import streamlit as st
import pandas as pd

# Inicjalizacja magazynu w stanie sesji Streamlit.
# Magazyn jest teraz słownikiem (dictionary):
# {'Nazwa Towaru': Liczba_Sztuk}
if 'magazyn' not in st.session_state:
    st.session_state.magazyn = {}

def dodaj_sztuke(nazwa):
    """Dodaje 1 sztukę do danego towaru w magazynie."""
    if not nazwa:
        st.error("Wprowadź nazwę towaru.")
        return

    # Jeśli towar istnieje, zwiększamy ilość o 1
    if nazwa in st.session_state.magazyn:
        st.session_state.magazyn[nazwa] += 1
        st.success(f"Dodano kolejną sztukę (**{nazwa}**). Aktualna ilość: **{st.session_state.magazyn[nazwa]}**.")
    # Jeśli towar jest nowy, dodajemy go z ilością 1
    else:
        st.session_state.magazyn[nazwa] = 1
        st.success(f"Dodano nowy towar: **{nazwa}** (ilość: 1).")

def usun_sztuke_callback():
    """Zmniejsza ilość sztuk wybranego towaru o 1 lub usuwa go, jeśli osiągnie 0."""
    
    # Pobieramy nazwę z pola selectbox za pomocą klucza 'select_usun'
    nazwa_do_edycji = st.session_state.select_usun 
    
    if not nazwa_do_edycji:
        st.error("Nie wybrano towaru do edycji.")
        return

    ilosc = st.session_state.magazyn.get(nazwa_do_edycji, 0)
    
    if ilosc > 1:
        # Zmniejszamy ilość o 1
        st.session_state.magazyn[nazwa_do_edycji] -= 1
        st.session_state.komunikat_usun = f"Usunięto 1 sztukę (**{nazwa_do_edycji}**). Pozostało: **{st.session_state.magazyn[nazwa_do_edycji]}**."
    elif ilosc == 1:
        # Usuwamy wpis, jeśli pozostała 1 sztuka
        del st.session_state.magazyn[nazwa_do_edycji]
        st.session_state.komunikat_usun = f"Usunięto ostatnią sztukę (**{nazwa_do_edycji}**). Towar usunięty z magazynu."
    else:
        # Ten warunek nie powinien wystąpić, jeśli selectbox jest poprawny
        st.session_state.komunikat_usun = f"Błąd: Towar **{nazwa_do_edycji}** nie jest już w magazynie."


# --- Interfejs użytkownika Streamlit ---

st.title("📦 Prosty Magazyn Towarów z Ilością Sztuk")
st.markdown("Aplikacja wykorzystuje słownik Pythona do śledzenia ilości sztuk dla każdego towaru.")

## Sekcja Dodawania Towaru (Dodaj 1 sztukę)
st.header("➕ Dodaj 1 Sztukę Towaru")

with st.form("dodaj_formularz", clear_on_submit=True):
    nowy_towar = st.text_input("Nazwa Towaru (wprowadź lub powtórz nazwę istniejącego)", key="input_dodaj")
    submit_dodaj = st.form_submit_button("Dodaj 1 Sztukę")

    if submit_dodaj:
        # Używamy st.form_submit_button, więc wywołanie funkcji musi być w tym bloku
        dodaj_sztuke(nowy_towar)

## Sekcja Bieżącego Stanu Magazynu
st.header("📊 Stan Magazynu")

if st.session_state.magazyn:
    # Konwersja słownika na DataFrame dla ładnej tabeli
    towary_data = {
        'Nazwa Towaru': list(st.session_state.magazyn.keys()),
        'Ilość Sztuk': list(st.session_state.magazyn.values())
    }
    df_magazyn = pd.DataFrame(towary_data)
    df_magazyn.index += 1 # Numeracja od 1
    
    # Wyświetlamy tabelę
    st.table(df_magazyn)
    
    # Dodatkowe wskaźniki
    st.metric(label="Liczba Różnych Towarów", value=len(st.session_state.magazyn))
    st.metric(label="Całkowita Ilość Sztuk w Magazynie", value=sum(st.session_state.magazyn.values()))
    
else:
    st.info("Magazyn jest pusty. Dodaj pierwszy towar!")


## Sekcja Usuwania Towaru (Usuń 1 sztukę)
st.header("➖ Usuń 1 Sztukę Towaru")

# Wyświetlamy komunikat z callbacka usunięcia (jeśli istnieje) i czyścimy go
if 'komunikat_usun' in st.session_state and st.session_state.komunikat_usun:
    st.info(st.session_state.komunikat_usun)
    st.session_state.pop('komunikat_usun')


if st.session_state.magazyn:
    # Używamy list(st.session_state.magazyn.keys()) jako opcji dla selectboxa
    towary_dostepne = list(st.session_state.magazyn.keys())
    
    towar_do_usunięcia = st.selectbox(
        "Wybierz towar, z którego chcesz usunąć 1 sztukę",
        towary_dostepne,
        key="select_usun" # Klucz jest niezbędny dla callbacka
    )

    # Użycie callbacku on_click, który automatycznie odświeża stan aplikacji
    st.button(
        "Usuń 1 Sztukę Wybranego Towaru",
        on_click=usun_sztuke_callback
    )
else:
    st.info("Nie ma towarów do usunięcia.")

st.markdown("---")
st.caption("Dane przechowywane w słowniku Pythona w pamięci aplikacji Streamlit.")
