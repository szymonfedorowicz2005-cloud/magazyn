import streamlit as st
import pandas as pd
import altair as alt # Importujemy Altair do tworzenia wykresów

# --- Konfiguracja Świąteczna ---
st.set_page_config(layout="wide") # Użyjemy szerszego układu dla lepszego wyglądu wykresu

# Inicjalizacja magazynu w stanie sesji Streamlit.
if 'magazyn' not in st.session_state:
    st.session_state.magazyn = {}

if 'komunikat_usun' not in st.session_state:
    st.session_state.komunikat_usun = ""

# --- Funkcje Logiki ---

def dodaj_sztuke(nazwa, ilosc_do_dodania):
    """Dodaje określoną liczbę sztuk do danego towaru."""
    if not nazwa:
        st.error("Wprowadź nazwę towaru.")
        return

    ilosc_do_dodania = int(ilosc_do_dodania)
    
    if nazwa in st.session_state.magazyn:
        st.session_state.magazyn[nazwa] += ilosc_do_dodania
        st.success(f"Dodano {ilosc_do_dodania} sztuk (**{nazwa}**). Aktualna ilość: **{st.session_state.magazyn[nazwa]}**.")
    else:
        st.session_state.magazyn[nazwa] = ilosc_do_dodania
        st.success(f"Dodano nowy towar: **{nazwa}** (ilość: {ilosc_do_dodania}).")

def usun_sztuke_callback():
    """Zmniejsza ilość sztuk wybranego towaru o wybraną wartość."""
    
    nazwa_do_edycji = st.session_state.select_usun
    ilosc_do_usunięcia = int(st.session_state.ilosc_usun)
    
    if not nazwa_do_edycji:
        st.session_state.komunikat_usun = "Nie wybrano towaru do edycji."
        return
        
    ilosc_obecna = st.session_state.magazyn.get(nazwa_do_edycji, 0)
    
    if ilosc_obecna == 0:
        st.session_state.komunikat_usun = f"Błąd: Towar **{nazwa_do_edycji}** nie jest już w magazynie."
    elif ilosc_do_usunięcia > ilosc_obecna:
        st.session_state.komunikat_usun = f"Błąd: Nie można usunąć {ilosc_do_usunięcia} sztuk, ponieważ dostępnych jest tylko {ilosc_obecna}."
    else:
        st.session_state.magazyn[nazwa_do_edycji] -= ilosc_do_usunięcia
        ilosc_po_usunieciu = st.session_state.magazyn[nazwa_do_edycji]
        
        if ilosc_po_usunieciu == 0:
            del st.session_state.magazyn[nazwa_do_edycji]
            st.session_state.komunikat_usun = f"Usunięto {ilosc_do_usunięcia} sztuk (**{nazwa_do_edycji}**). Towar usunięty z magazynu."
        else:
            st.session_state.komunikat_usun = f"Usunięto {ilosc_do_usunięcia} sztuk (**{nazwa_do_edycji}**). Pozostało: **{ilosc_po_usunieciu}**."


# --- Interfejs użytkownika Streamlit (Świąteczny Układ) ---

# Użycie kolumn do dodania świątecznej atmosfery po bokach
kolumna_swiateczna_L, kolumna_glowna, kolumna_swiateczna_P = st.columns([1, 4, 1])

with kolumna_glowna:
    st.title("🎁🎄 Świąteczny Magazyn Towarów 🎄🎁")
    st.markdown("---")

    ## 1. Sekcja Dodawania Towaru
    st.header("➕ Dodaj Towar do Worka Św. Mikołaja (1-5 sztuk)")

    with st.form("dodaj_formularz", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            nowy_towar = st.text_input("Nazwa Prezentu/Towaru", key="input_dodaj")
        
        with col2:
            ilosc_dodaj = st.selectbox("Ilość", options=list(range(1, 6)), index=0, key="ilosc_dodaj")

        submit_dodaj = st.form_submit_button("Dodaj do Magazynu")

        if submit_dodaj:
            dodaj_sztuke(nowy_towar, ilosc_dodaj)

    st.markdown("---")

    ## 2. Sekcja Usuwania Towaru
    st.header("➖ Usuń Towar (Zwrot/Wydanie - 1 do 5 sztuk)")

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
                key="select_usun"
            )
        
        with col4:
            ilosc_usun = st.selectbox(
                "Ilość",
                options=list(range(1, 6)),
                index=0,
                key="ilosc_usun"
            )
        
        st.button(
            "Usuń Wybraną Ilość Sztuk",
            on_click=usun_sztuke_callback
        )
    else:
        st.info("Brak towarów do usunięcia.")

    st.markdown("---")

    ## 3. Sekcja Bieżącego Stanu Magazynu (na samym dole)
    st.header("📊 Aktualny Stan Magazynu i Wskaźniki")

    if st.session_state.magazyn:
        # Przygotowanie danych do tabeli i wykresu
        towary_data = {
            'Nazwa Towaru': list(st.session_state.magazyn.keys()),
            'Ilość Sztuk': list(st.session_state.magazyn.values())
        }
        df_magazyn = pd.DataFrame(towary_data)
        df_magazyn.index += 1
        
        # Wskaźniki obok siebie
        col_metr1, col_metr2 = st.columns(2)
        with col_metr1:
            st.metric(label="Liczba Różnych Towarów 🎁", value=len(st.session_state.magazyn))
        with col_metr2:
            st.metric(label="Całkowita Ilość Sztuk w Magazynie 📦", value=sum(st.session_state.magazyn.values()))

        st.subheader("Tabela Szczegółowa")
        st.table(df_magazyn)

        # --- WYKRES SŁUPKOWY ---
        st.subheader("Wizualizacja Ilości Towarów")

        # Sortowanie danych przed wykresem dla lepszej czytelności
        df_magazyn_sorted = df_magazyn.sort_values(by='Ilość Sztuk', ascending=False)
        
        wykres = alt.Chart(df_magazyn_sorted).mark_bar().encode(
            x=alt.X('Nazwa Towaru', sort=None, title='Nazwa Towaru'), # sort=None utrzymuje kolejność DF
            y=alt.Y('Ilość Sztuk', title='Ilość Sztuk'),
            tooltip=['Nazwa Towaru', 'Ilość Sztuk'],
            color=alt.condition(
                alt.datum['Ilość Sztuk'] > 10,  # warunek: jeśli ilość jest duża
                alt.value('darkgreen'),        # Kolor dla dużych ilości
                alt.value('crimson')           # Kolor dla mniejszych ilości (świąteczna czerwień)
            )
        ).properties(
            title="Ilość Sztuk dla Każdego Towaru"
        ).interactive() # Umożliwia powiększanie i przesuwanie
        
        st.altair_chart(wykres, use_container_width=True)

    else:
        st.info("Magazyn jest pusty. Zacznij kompletować świąteczne zapasy!")
        
    st.markdown("---")
    st.caption("Dane przechowywane w słowniku Pythona w pamięci aplikacji Streamlit.")


# --- Sekcje Świąteczne Po Bokach ---

with kolumna_swiateczna_L:
    st.markdown("### 🎅")
    st.markdown("🎄 Zimowy Magazyn")
    st.image("https://images.unsplash.com/photo-1512411545638-31627c2e08cc?w=300&h=600&fit=crop", caption="Świąteczne zapasy")

with kolumna_swiateczna_P:
    st.markdown("### 🔔")
    st.markdown("🌟 Mikołaj Wita")
    st.image("https://images.unsplash.com/photo-1513295834857-e1757835158a?w=300&h=600&fit=crop", caption="Sezon świąteczny")
