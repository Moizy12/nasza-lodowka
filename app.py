import json
import time
import requests
import streamlit as st

# Konfiguracja strony pod telefony i tablety Apple
st.set_page_config(
    page_title="Nasza Lodówka",
    page_icon="🍳",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Styl CSS zoptymalizowany pod iOS / Safari
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-color: #0f1117;
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
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Brak klucza GEMINI_API_KEY w ustawieniach serwera (Secrets)!")
    API_KEY = None

st.title("🍳 Co dzisiaj jemy?")
st.write("Wpisz co mamy w domu, a wyczarujemy przepis z dokładnym makro!")

# Główny formularz
skladniki = st.text_area(
    "Co jest w lodówce / szafkach?",
    placeholder="np. pierś z kurczaka, ziemniaki, śmietana 12%, jajka, ser żółty...",
    height=110,
)

col1, col2 = st.columns(2)
with col1:
    typ_dania = st.selectbox(
        "Kategoria", ["Obiad", "Przekąska", "Deser", "Szybka kolacja", "Cokolwiek"]
    )
with col2:
    styl = st.selectbox(
        "Styl / Sprzęt",
        [
            "Szybki (do 15 min)",
            "Air Fryer",
            "Kreatywny / TikTok trend",
            "Tradycyjny / Domowy",
            "Fit / Wysokobiałkowy",
        ],
    )

if st.button("Szukaj przepisu 🚀"):
    if not API_KEY:
        st.error("Uzupełnij klucz API w sekretach Streamlita!")
    elif skladniki:
        with st.spinner("Wyczarowujemy przepis i liczymy makro..."):
            prompt = f"""
            Jesteś nowoczesnym, kreatywnym szefem kuchni oraz dietetykiem.
            
            Mam w domu następujące składniki: {skladniki}.
            Chcę przygotować: {typ_dania}.
            Preferowany styl / sprzęt: {styl}.

            Twoje zadanie:
            1. Zignoruj nudne i najbardziej oczywiste przepisy.
            2. Zaoferuj 2-3 wyjątkowe, apetyczne propozycje dań. Jeśli pasuje to do stylu, przemyć coś w klimacie viralowych trendów z social mediów (szybkie wrapy, smash dania, pomysłowe przekąski itp.).
            3. DLA KAŻDEGO PRZEPISU podaj:
               - Nazwę dania
               - Szacowane Makro i Kalorie na całe danie / porcję (Kcal, Białko, Tłuszcze, Węglowodany) - wyróżnij to ładnie graficznie/pogrubieniem!
               - Dokładne składniki i gramaturę
               - Instrukcję przygotowania krok po kroku
            4. Używaj głównie tego, co podałem (+ podstawy: sól, pieprz, woda, odrobina oleju). Jeśli coś warto dokupić, napisz to krótko w osobnej sekcji na końcu.
            
            Napisz to czytelnie i przejrzyście w Markdown, żeby wygodnie czytało się na ekranie iPhone'a.
            """

            # Lista modeli do testowania po kolei (system automatycznego przełączania zapasowego)
            dostepne_modele = [
                "gemini-3.8-flash",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-2.5-flash"
            ]

            sukces = False
            tekst_odpowiedzi = ""

            headers = {"Content-Type": "application/json"}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}

            for model_name in dostepne_modele:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
                try:
                    response = requests.post(
                        url, headers=headers, data=json.dumps(payload), timeout=12
                    )
                    res_json = response.json()

                    if response.status_code == 200:
                        tekst_odpowiedzi = res_json["candidates"][0]["content"]["parts"][0]["text"]
                        sukces = True
                        break
                    else:
                        # Jeśli model jest przeciążony lub niedostępny, pętla natychmiast sprawdza kolejny z listy
                        error_msg = res_json.get("error", {}).get("message", "")
                        if "high demand" in error_msg.lower() or "not found" in error_msg.lower() or "overloaded" in error_msg.lower():
                            continue
                        else:
                            # Inny błąd - też próbujemy kolejny model, a w ostateczności zapiszemy komunikat
                            continue
                except Exception:
                    continue

            if sukces:
                st.markdown("---")
                st.markdown(tekst_odpowiedzi)
            else:
                st.error("Wszystkie zapasowe kanały Google są obecnie mocno obciążone. Odczekaj 5 sekund i kliknij ponownie.")
    else:
        st.warning("Wpisz chociaż kilka składników z lodówki!")
