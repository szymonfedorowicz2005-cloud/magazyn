import streamlit as st
import pandas as pd

# Inicjalizacja magazynu w stanie sesji Streamlit.
# Magazyn jest słownikiem: {'Nazwa Towaru': Liczba_Sztuk}
if 'magazyn' not in st.session_state:
    st.session_state.magazyn = {}

# Inicjalizacja komunikatów stanu sesji
if 'komunikat_usun' not in st.session_state:
    st.session_state.komunikat_usun = ""

def dodaj_sztuke(nazwa, ilosc_do_dodania):
    """Dodaje określoną liczbę sztuk do danego towaru."""
    if not nazwa:
        st.error("Wprowadź nazwę towaru.")
        return

    # Upewniamy się, że ilość do dodania jest dodatnia
    ilosc_do_dodania = int(ilosc_do_dodania)
    
    if nazwa in st.session_state.magazyn:
        # Towar istnieje: zwiększamy ilość
        st.session_state.magazyn[nazwa] += ilosc_do_dodania
        st.success(f"Dodano {ilosc_do_dodania} sztuk (**{nazwa}**). Aktualna ilość: **{st.session_state.magazyn[nazwa]}**.")
    else:
        # Nowy towar: dodajemy go z podaną ilością
        st.session_state.magazyn[nazwa] = ilosc_do_dodania
        st.success(f"Dodano nowy towar: **{nazwa}** (ilość: {ilosc_do_dodania}).")

def usun_sztuke_callback():
    """Zmniejsza ilość sztuk wybranego towaru o wybraną wartość."""
    
    # Pobieramy nazwę i ilość z pól formularza za pomocą kluczy
    nazwa_do_edycji = st.session_state.select_usun # Nazwa z selectboxa towarów
    ilosc_do_usunięcia = int(st.session_state.ilosc_usun) # Ilość z selectboxa ilości
    
    if not nazwa_do_edycji:
        st.session_state.komunikat_usun = "Nie wybrano towaru do edycji."
        return
        
    ilosc_obecna = st.session_state.magazyn.get(nazwa_do_edycji, 0)
    
    if ilosc_obecna == 0:
        # Powinno być niemożliwe, jeśli selectbox jest poprawny
        st.session_state.komunikat_usun = f"Błąd: Towar **{nazwa_do_edycji}** nie jest już w magazynie."
    elif ilosc_do_usunięcia > ilosc_obecna:
        st.session_state.komunikat_usun = f"Błąd: Nie można usunąć {ilosc_do_usunięcia} sztuk, ponieważ dostępnych jest tylko {ilosc_obecna}."
    else:
        # Aktualizujemy ilość
        st.session_state.magazyn[nazwa_do_edycji] -= ilosc_do_usunięcia
        ilosc_po_usunieciu = st.session_state.magazyn[nazwa_do_edycji]
        
        if ilosc_po_usunieciu == 0:
            # Usuwamy wpis, jeśli osiągnięto 0
            del st.session_state.magazyn[nazwa_do_edycji]
            st.session_state.komunikat_usun = f"Usunięto {ilosc_do_usunięcia} sztuk (**{nazwa_do_edycji}**). Towar usunięty z magazynu."
        else:
            st.session_state.komunikat_usun = f"Usunięto {ilosc_do_usunięcia} sztuk (**{nazwa_do_edycji}**). Pozostało: **{ilosc_po_usunieciu}**."


# --- Interfejs użytkownika Streamlit ---

st.title("📦 Magazyn Towarów z Wyborem Ilości")
st.markdown("Możesz dodać/usunąć od 1 do 5 sztuk w jednej operacji. Dane przechowywane w słowniku.")

## Sekcja Dodawania Towaru
st.header("➕ Dodaj Towar (1-5 sztuk)")

with st.form("dodaj_formularz", clear_on_submit=True):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        nowy_towar = st.text_input("Nazwa Towaru", key="input_dodaj")
    
    with col2:
        ilosc_dodaj = st.selectbox("Ilość", options=list(range(1, 6)), index=0, key="ilosc_dodaj")

    submit_dodaj = st.form_submit_button("Dodaj do Magazynu")

    if submit_dodaj:
        # Wywołujemy funkcję z dwoma argumentami
        dodaj_sztuke(nowy_towar, ilosc_dodaj)

## Sekcja Bieżącego Stanu Magazynu
st.header("📊 Stan Magazynu")

if st.session_state.magazyn:
    # Konwersja słownika na DataFrame
    towary_data = {
        'Nazwa Towaru': list(st.session_state.magazyn.keys()),
        'Ilość Sztuk': list(st.session_state.magazyn.values())
    }
    df_magazyn = pd.DataFrame(towary_data)
    df_magazyn.index += 1
    
    st.table(df_magazyn)
    
    st.metric(label="Liczba Różnych Towarów", value=len(st.session_state.magazyn))
    st.metric(label="Całkowita Ilość Sztuk w Magazynie", value=sum(st.session_state.magazyn.values()))
    
else:
    st.info("Magazyn jest pusty. Dodaj pierwszy towar!")

## Sekcja Usuwania Towaru
st.header("➖ Usuń Towar (1-5 sztuk)")

# Wyświetlamy komunikat i czyścimy go
if st.session_state.komunikat_usun:
    st.info(st.session_state.komunikat_usun)
    st.session_state.pop('komunikat_usun')


if st.session_state.magazyn:
    towary_dostepne = list(st.session_state.magazyn.keys())
    
    col3, col4 = st.columns([3, 1])
    
    with col3:
        towar_do_usunięcia = st.selectbox(
            "Wybierz towar do edycji",
            towary_dostepne,
            key="select_usun" # Klucz dla callbacka
        )
    
    with col4:
         # Selectbox dla wyboru ilości do usunięcia
        ilosc_usun = st.selectbox(
            "Ilość",
            options=list(range(1, 6)),
            index=0,
            key="ilosc_usun" # Klucz dla callbacka
        )
    
    # Użycie callbacku on_click
    st.button(
        "Usuń Wybraną Ilość Sztuk",
        on_click=usun_sztuke_callback
    )
else:
    st.info("Nie ma towarów do usunięcia.")

st.markdown("---")
st.caption("Dane przechowywane w słowniku Pythona w pamięci aplikacji Streamlit.")
