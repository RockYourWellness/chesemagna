import streamlit as st
import requests

st.set_page_config(page_title="chesemagna", page_icon="🥗", layout="centered")

st.title("Che se magna")
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

# --- CHIAMATA DIRETTA ULTRA-RAPIDA (HTTP REST) ---
if invia:
    if not (proteine or carboidrati or verdure):
        st.error("Inserisci almeno uno o due alimenti del tuo pasto per procedere.")
    elif not metodi_scelti:
        st.error("Seleziona almeno un metodo di cottura che sei disposto a usare.")
    else:
        with st.spinner("Creo la tua ricetta in 2 secondi..."):
            
            prompt_rapido = f"""
            Sei uno chef nutrizionista pratico e conciso. Crea una ricetta sfiziosa e veloce.
            
            DATI:
            - Carboidrati: {carboidrati} | Proteine: {proteine} | Verdure: {verdure}
            - Tempo: {tempo} | Voglia: {voglia}
            - Strumenti concessi: {', '.join(metodi_scelti)}

            REGOLE TASSATIVE:
            - Usa SOLO gli strumenti concessi. Se tempo <= 15 min, ipotizza cereali precotti o tagli sottili.
            - Vietata la pasta col pollo e niente calcolo calorie.
            - Massima brevità: massimo 160 parole in totale, zero saluti o introduzioni.

            STRUTTURA DA RISPETTARE:
            🍽️ **[Nome Piatto]**
            ⏱️ [Tempo] | 🍳 Strumento: [Uno tra {', '.join(metodi_scelti)}]
            💡 *[1 riga sul gusto]*

            🛒 **Ingredienti usati:**
            - [Carboidrati, Proteine, Verdure]
            - [Spezie ed erbe consigliate]

            👨‍🍳 **Passaggi Facili:** (Massimo 3 passaggi telegrafici)
            1. [Passo 1]
            2. [Passo 2]
            3. [Passo 3]

            🌿 **Spezie, Erbette e Sostituzioni Furbe:**
            - *[Spezia/erba usata]:* alternativa con [Alternativa comune]
            - *[Condimento cremoso]:* alternativa con [Alternativa pratica]
            """

            api_key = st.secrets["GEMINI_API_KEY"]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [
                    {
                        "parts": [{"text": prompt_rapido}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 380
                }
            }

            try:
                # Timeout rigido a 8 secondi: risposta istantanea senza blocchi di rete
                response = requests.post(url, json=payload, timeout=8)
                
                if response.status_code == 200:
                    dati = response.json()
                    testo_ricetta = dati["candidates"][0]["content"]["parts"][0]["text"]
                    st.divider()
                    st.markdown(testo_ricetta)
                else:
                    st.error(f"Errore Google ({response.status_code}): {response.text}")
                    
            except requests.exceptions.Timeout:
                st.error("I server di Google hanno impiegato più di 8 secondi. Riprova: al secondo tentativo risponde subito.")
            except Exception as e:
                st.error(f"Errore imprevisto: {e}")
