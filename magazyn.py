import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# --- Konfiguracja Streamlit ---
# Ustawiamy szeroki układ strony
st.set_page_config(layout="wide") 

# Inicjalizacja magazynu w stanie sesji Streamlit.
if 'magazyn' not in st.session_state:
    st.session_state.magazyn = {}

if 'komunikat_usun' not in st.session_state:
    st.session_state.komunikat_usun = ""

# Lista do przechowywania historii operacji
if 'historia_operacji' not in st.session_state:
    st.session_state.historia_operacji = []


def dodaj_do_historii(typ, nazwa, ilosc, nowa_ilosc):
    """Dodaje wpis do historii operacji (logu)."""
    st.session_state.historia_operacji.append({
        'czas': datetime.now().strftime("%H:%M:%S"),
        'typ': typ,
        'towar': nazwa,
        'ilosc': ilosc,
        'status': f"-> {nowa_ilosc} szt."
    })


# --- Funkcje Logiki Magazynu ---

def dodaj_sztuke(nazwa, ilosc_do_dodania):
    """Dodaje określoną liczbę sztuk do danego towaru i rejestruje operację."""
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

    # Rejestracja w historii
    dodaj_do_historii(
        typ="DODANO", 
        nazwa=nazwa, 
        ilosc=ilosc_do_dodania, 
        nowa_ilosc=st.session_state.magazyn[nazwa]
    )


def usun_sztuke_callback():
    """Zmniejsza ilość sztuk wybranego towaru o wybraną wartość i rejestruje operację."""
    
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
        
        # Rejestracja w historii przed ewentualnym usunięciem wpisu
        dodaj_do_historii(
            typ="USUNIĘTO", 
            nazwa=nazwa_do_edycji, 
            ilosc=ilosc_do_usunięcia, 
            nowa_ilosc=ilosc_po_usunieciu
        )
        
        if ilosc_po_usunieciu == 0:
            del st.session_state.magazyn[nazwa_do_edycji]
            st.session_state.komunikat_usun = f"Usunięto {ilosc_do_usunięcia} sztuk (**{nazwa_do_edycji}**). Towar usunięty z magazynu."
        else:
            st.session_state.komunikat_usun = f"Usunięto {ilosc_do_usunięcia} sztuk (**{nazwa_do_edycji}**). Pozostało: **{ilosc_po_usunieciu}**."


# --- Interfejs użytkownika Streamlit (Układ z kolumnami) ---

# Użycie kolumn: [Świąteczna L | Główna (4) | Historia (1.5)]
kolumna_swiateczna_L, kolumna_glowna, kolumna_historia_P = st.columns([1, 4, 1.5])

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
        
        col_metr1, col_metr2 = st.columns(2)
        with col_metr1:
            st.metric(label="Liczba Różnych Towarów 🎁", value=len(st.session_state.magazyn))
        with col_metr2:
            st.metric(label="Całkowita Ilość Sztuk w Magazynie 📦", value=sum(st.session_state.magazyn.values()))

        st.subheader("Tabela Szczegółowa")
        st.table(df_magazyn)

        # --- WYKRES SŁUPKOWY ---
        st.subheader("Wizualizacja Ilości Towarów")

        df_magazyn_sorted = df_magazyn.sort_values(by='Ilość Sztuk', ascending=False)
        
        wykres = alt.Chart(df_magazyn_sorted).mark_bar().encode(
            x=alt.X('Nazwa Towaru', sort=None, title='Nazwa Towaru', 
                    axis=alt.Axis(labelAngle=0)), # Etykiety na osi X są poziome
            y=alt.Y('Ilość Sztuk', title='Ilość Sztuk'),
            tooltip=['Nazwa Towaru', 'Ilość Sztuk'],
            color=alt.condition(
                alt.datum['Ilość Sztuk'] > 10,  
                alt.value('darkgreen'),        
                alt.value('crimson')           
            )
        ).properties(
            title="Ilość Sztuk dla Każdego Towaru"
        ).interactive()
        
        st.altair_chart(wykres, use_container_width=True)

    else:
        st.info("Magazyn jest pusty. Zacznij kompletować świąteczne zapasy!")
        
    st.markdown("---")
    st.caption("Dane przechowywane w słowniku Pythona w pamięci aplikacji Streamlit.")


# --- Sekcje Boczne ---

with kolumna_swiateczna_L:
    st.markdown("### 🎅")
    st.markdown("🎄 Zimowy Magazyn")
    # Pamiętaj, aby zastąpić ten tekst linkiem do obrazka w swoim wdrożeniu Streamlit!
    st.text("[Miejsce na grafikę ze świątecznymi zapasami]") 

# --- Prawa Kolumna: Historia Operacji ---

with kolumna_historia_P:
    st.markdown("### 🔔 Log Operacji 🔔")
    st.markdown("---")

    if st.session_state.historia_operacji:
        historia_df = pd.DataFrame(st.session_state.historia_operacji)
        
        # Iterujemy od końca (iloc[::-1]), aby najnowsze były na górze
        for index, row in historia_df.iloc[::-1].iterrows():
            if row['typ'] == 'DODANO':
                ikonka = '⬆️'
                kolor = 'green'
            else:
                ikonka = '⬇️'
                kolor = 'red'
                
            st.markdown(f"**{ikonka} {row['czas']}**", unsafe_allow_html=True)
            st.markdown(f"**{row['typ']}**: `{row['towar']}` ({row['ilosc']} szt.)")
            st.markdown(f"<span style='color:{kolor}; font-size:12px;'>{row['status']}</span>", unsafe_allow_html=True)
            # Poprawione wywołanie st.markdown, które poprzednio generowało błąd
            st.markdown("---") 
    else:
        st.info("Brak zarejestrowanych operacji.")
    
    st.text("[Miejsce na grafikę ze świątecznym sezonem]")
