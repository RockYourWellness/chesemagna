import streamlit as st
import requests
import time

st.set_page_config(page_title="chesemagna", page_icon="🥗", layout="centered")

st.title("🥗 Che se magna")
st.markdown("Componi il tuo pasto con gli alimenti del piano: trasformeremo la solita routine in una ricetta veloce, aromatica e su misura.")

# --- MODULO FISSO ---
with st.form("modulo_ricetta"):
    st.subheader("1. Gli alimenti del tuo pasto")
    col_c, col_p, col_v = st.columns(3)
    with col_c:
        carboidrati = st.text_input("Carboidrati:", placeholder="Es. Riso, patate, couscous")
    with col_p:
        proteine = st.text_input("Proteine:", placeholder="Es. Pollo, uova, tofu, ceci")
    with col_v:
        verdure = st.text_input("Verdure:", placeholder="Es. Zucchine, carote, spinaci")

    st.subheader("2. Tempo e Voglia del momento")
    col_t, col_m = st.columns(2)
    with col_t:
        tempo = st.selectbox("Quanto tempo hai?", ["10-15 minuti (Ultra rapido)", "20-30 minuti", "Oltre 30 minuti"])
    with col_m:
        voglia = st.selectbox("Cosa ti andrebbe oggi?", [
            "Croccante e sfizioso", 
            "Cremoso e avvolgente", 
            "Speziato / Etnico", 
            "Fresco e aromatico", 
            "Rustico / Mediterraneo"
        ])

    st.subheader("3. Metodi di cottura che vuoi usare")
    st.caption("Spunta solo gli strumenti che hai e che SEI DISPOSTO ad accendere oggi:")
    metodi_scelti = st.multiselect(
        "Strumenti ammessi per oggi:",
        ["Padella / Fornelli", "Friggitrice ad aria", "Forno", "Microonde", "Vaporiera", "Frullatore / Minipimer"],
        default=["Padella / Fornelli"]
    )

    invia = st.form_submit_button("✨ Svolta la mia cena")

# --- GENERAZIONE CON RIDONDANZA E FALLBACK ---
if invia:
    if not (proteine or carboidrati or verdure):
        st.error("Inserisci almeno uno o due alimenti del tuo pasto per procedere.")
    elif not metodi_scelti:
        st.error("Seleziona almeno un metodo di cottura che sei disposto a usare.")
    else:
        with st.spinner("🍳 Lo chef sta preparando la ricetta..."):
            
            prompt_rapido = f"""
            Sei uno chef nutrizionista. Crea subito una ricetta sfiziosa e veloce.
            
            DATI:
            - Carboidrati: {carboidrati} | Proteine: {proteine} | Verdure: {verdure}
            - Tempo: {tempo} | Voglia: {voglia}
            - Strumenti concessi: {', '.join(metodi_scelti)}

            REGOLE:
            - Usa SOLO gli strumenti concessi. Se tempo <= 15 min, ipotizza cereali precotti.
            - Vietata la pasta col pollo e niente calcolo calorie.
            - Telegrafico: massimo 130 parole in totale, niente convenevoli.

            STRUTTURA:
            🍽️ **[Nome Piatto]**
            ⏱️ [Tempo] | 🍳 Strumento: [Uno tra {', '.join(metodi_scelti)}]
            💡 *[1 riga sul gusto]*

            🛒 **Ingredienti usati:**
            - [Carboidrati, Proteine, Verdure]
            - [Spezie ed erbe consigliate]

            👨‍🍳 **Preparazione:** (Max 3 passaggi rapidissimi)
            1. [Passo 1]
            2. [Passo 2]
            3. [Passo 3]

            🌿 **Spezie & Sostituzioni Furbe:**
            - *[Spezia/erba]:* se manca, usa [Alternativa comune]
            - *[Legante/crema]:* se manca, usa [Alternativa comune]
            """

            api_key = st.secrets["GEMINI_API_KEY"]
            
            # Modelli da provare in ordine di priorità
            modelli = ["gemini-3.8-flash", "gemini-2.5-pro"]
            ricetta_generata = None
            
            payload = {
                "contents": [{"parts": [{"text": prompt_rapido}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 320
                }
            }

            for model_name in modelli:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                try:
                    res = requests.post(url, json=payload, timeout=10)
                    if res.status_code == 200:
                        dati = res.json()
                        ricetta_generata = dati["candidates"][0]["content"]["parts"][0]["text"]
                        break
                    elif res.status_code in [503, 429]:
                        # Se il server è saturo, aspetta 1 secondo e prova il modello di riserva
                        time.sleep(1)
                        continue
                except requests.exceptions.Timeout:
                    continue
                except Exception:
                    continue

            if ricetta_generata:
                st.divider()
                st.markdown(ricetta_generata)
            else:
                st.warning("I server di Google sono momentaneamente saturi in questo minuto. Premi di nuovo il pulsante per ritentare.")
