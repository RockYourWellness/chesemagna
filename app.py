import streamlit as st
import google.generativeai as genai

# Configurazione API da Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

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

# --- GENERAZIONE ULTRA-RAPIDA (1-2 SECONDI) ---
if invia:
    if not (proteine or carboidrati or verdure):
        st.error("Inserisci almeno uno o due alimenti del tuo pasto per procedere.")
    elif not metodi_scelti:
        st.error("Seleziona almeno un metodo di cottura che sei disposto a usare.")
    else:
        with st.spinner("Creazione della ricetta..."):
            
            prompt_rapido = f"""
            Sei uno chef nutrizionista pratico e conciso. Crea una ricetta sfiziosa e veloce.
            
            DATI:
            - Carboidrati: {carboidrati} | Proteine: {proteine} | Verdure: {verdure}
            - Tempo: {tempo} | Voglia: {voglia}
            - Strumenti concessi: {', '.join(metodi_scelti)}

            REGOLE:
            - Usa SOLO gli strumenti concessi. Se tempo <= 15 min, ipotizza cereali precotti.
            - Niente paranoie caloriche o divieti assurdi (no pasta col pollo).
            - Sii conciso e diretto: massimo 200 parole in totale, zero preamboli.

            STRUTTURA:
            🍽️ **[Nome Piatto]**
            ⏱️ [Tempo] | 🍳 Strumento: [Uno tra {', '.join(metodi_scelti)}]
            💡 *[1 riga sul gusto]*

            🛒 **Ingredienti & Spezie:** [Lista sintetica con erbe/spezie suggerite]
            👨‍🍳 **Preparazione:** (Max 3 passaggi telegrafici)
            🌿 **Sostituzioni rapide:** [1 alternativa per spezia e 1 per legante/crema]
            """

            # Disattivazione del "thinking" interno per velocità istantanea
            gen_config = {
                "temperature": 0.6,
                "max_output_tokens": 450,
            }
            try:
                gen_config["thinking_config"] = {"thinking_budget": 0}
                model = genai.GenerativeModel("models/gemini-3.8-flash", generation_config=gen_config)
            except Exception:
                gen_config.pop("thinking_config", None)
                model = genai.GenerativeModel("models/gemini-3.8-flash", generation_config=gen_config)

            try:
                risposta = model.generate_content(prompt_rapido).text
                st.divider()
                st.markdown(risposta)
            except Exception as e:
                st.error(f"Errore: {e}")
