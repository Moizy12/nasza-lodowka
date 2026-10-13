import streamlit as st
from google import genai
from google.genai import errors

# Konfiguracja strony pod telefony i tablety Apple
st.set_page_config(
    page_title="Nasza Lodówka",
    page_icon="🍳",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Styl CSS oraz metadane PWA pod iOS / Safari bez pasków
st.markdown(
    """
    <link rel="manifest" href="manifest.json">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Lodówka">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0f1117 !important;
        color: #ffffff;
    }
    
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        background-color: #FF4B4B;
        color: white;
        border: none;
        padding: 0.85rem;
        font-size: 1.1rem;
    }
    div.stButton > button:hover {
        background-color: #ff3333;
    }
    
    div.stTextArea > div > div > textarea {
        border-radius: 10px;
        background-color: #1a1d24;
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Pobranie klucza API z sekretów Streamlita
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Brak klucza GEMINI_API_KEY w ustawieniach serwera (Secrets)!")
    api_key = None

st.title("🍳 Co dzisiaj jemy?")
st.write("Wpisz co mamy w domu, a wyczarujemy przepis z dokładnym makro!")

# Główny formularz
skladniki = st.text_area(
    "Co jest w lodówce / szafkach?",
    placeholder="np. pierś z kurczaka, ziemniaki, śmietana 12%, jajka, ser żółty...",
    height=110,
)

# Układ kolumn dla lepszego UI na telefonie
col1, col2, col3 = st.columns(3)
with col1:
    typ_dania = st.selectbox(
        "Kategoria", ["Obiad", "Przekąska", "Deser", "Szybka kolacja", "Cokolwiek"]
    )
with col2:
    czas = st.selectbox(
        "Czas", ["Do 15 min", "Do 30 min", "Powyżej 30 min"]
    )
with col3:
    styl = st.selectbox(
        "Styl",
        [
            "Klasyczny / Domowy",
            "Fit / Wysokobiałkowy",
            "TikTok trend / Kreatywny",
            "Chrupiące / Z frytkownicy",
        ],
    )

if st.button("Szukaj przepisu 🚀"):
    if not api_key:
        st.error("Uzupełnij klucz API w sekretach Streamlita!")
    elif skladniki:
        prompt = f"""
        Jesteś nowoczesnym, kreatywnym szefem kuchni oraz dietetykiem.
        
        Mam w domu następujące składniki: {skladniki}.
        Chcę przygotować: {typ_dania}.
        Maksymalny czas przygotowania: {czas}.
        Styl / Charakter dania: {styl}.

        Twoje zadanie:
        1. Zaoferuj 2-3 RÓŻNE od siebie, wyjątkowe i apetyczne propozycje dań mieszczące się w zadanym czasie ({czas}).
        2. DLA KAŻDEGO PRZEPISU podaj:
           - Nazwę dania
           - Szacowane Makro i Kalorie na całe danie / porcję (Kcal, Białko, Tłuszcze, Węglowodany) - wyróżnij to ładnie pogrubieniem!
           - Dokładne składniki i gramaturę
           - Zwięzłą instrukcję przygotowania krok po kroku
        3. Używaj głównie tego, co podałem (+ podstawy: sól, pieprz, woda, odrobina oleju). Pisze konkretnie, bez lania wody i zbędnych wstępów.
        
        Napisz to czytelnie w Markdown, dopasowanym pod ekran telefonu.
        """

        try:
            client = genai.Client(api_key=api_key)
            st.markdown("---")
            
            response_stream = client.models.generate_content_stream(
                model='gemini-3.8-flash',
                contents=prompt,
            )
            
            def generate_chunks():
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text

            st.write_stream(generate_chunks())
                
        except errors.APIError as e:
            st.error(f"Błąd API Google: {e}")
        except Exception as e:
            st.error(f"Wystąpił nieoczekiwany błąd: {e}")
    else:
        st.warning("Wpisz chociaż kilka składników z lodówki!")
