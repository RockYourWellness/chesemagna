import streamlit as st
import google.generativeai as genai

# Configurazione chiave API da Streamlit Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="chesemagna", page_icon="🥗", layout="centered")

st.title("Che se magna")
st.markdown("Componi il tuo pasto con gli alimenti del piano: trasformeremo la solita routine in una ricetta veloce, aromatica e su misura.")

# --- MODULO FISSO (Nessuna chat, campi puliti per il paziente) ---
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

# --- GENERAZIONE RICETTA CON GEMINI 3.8 FLASH ---
if invia:
    if not (proteine or carboidrati or verdure):
        st.error("Inserisci almeno uno o due alimenti del tuo pasto per procedere.")
    elif not metodi_scelti:
        st.error("Seleziona almeno un metodo di cottura che sei disposto a usare.")
    else:
        with st.spinner("Creazione della ricetta in corso..."):
            
            prompt_ricetta = f"""
            Sei uno chef specializzato in nutrizione sana, sostenibile e priva di paranoie.
            
            DATI DEL PASTO FORNITI DAL PAZIENTE:
            - Carboidrati: {carboidrati}
            - Proteine: {proteine}
            - Verdure: {verdure}
            - Tempo a disposizione: {tempo}
            - Voglia sensoriale: {voglia}
            - Metodi di cottura tassativamente ammessi: {', '.join(metodi_scelti)}

            VINCOLI E LINEE GUIDA:
            1. Usa SOLO i metodi di cottura indicati ({', '.join(metodi_scelti)}). Se l'utente non ha spuntato il forno, non proporre mai cotture al forno.
            2. Se il tempo è '10-15 minuti', ipotizza riso o cereali precotti o tagli ultra-sottili.
            3. Suggerisci attivamente spezie, erbe aromatiche e condimenti furbi (limone, yogurt bianco naturale, aceto, salsa di soia, semi) per assecondare la voglia richiesta senza appesantire.
            4. Inserisci sempre una sezione finale con SOSTITUZIONI pratiche per le spezie e i condimenti suggeriti, per chi ha la dispensa mezza vuota.
            5. Nessun tabù sgradevole (vietata pasta con il pollo) e nessun conteggio o paranoia calorica.

            FORMATO DI RISPOSTA:
            🍽️ **[Nome invitante del piatto]**
            ⏱️ **[Tempo stimato]** | 🍳 **Strumento:** [Solo uno tra {', '.join(metodi_scelti)}]
            💡 *[1 frase breve sul perché questa combinazione appaga la voglia del giorno]*

            🛒 **Ingredienti usati:**
            - [Carboidrati, Proteine, Verdure indicati dal paziente]
            - [Spezie ed erbette consigliate per dare sapore]

            👨‍🍳 **Passaggi Facili:**
            1. [Passo 1: taglio/aromatizzazione]
            2. [Passo 2: cottura con lo strumento ammesso]
            3. [Passo 3: mantecatura, emulsione o tocco finale]

            🌿 **Spezie, Erbette e Sostituzioni Furbe:**
            - *[Erba/Spezia usata]:* se non ce l'hai, usa [Alternativa comune]
            - *[Elemento cremoso/legante]:* se non ce l'hai, usa [Alternativa pratica]
            """

            try:
                # Modello aggiornato come richiesto da Google
                model = genai.GenerativeModel("gemini-3.8-flash")
                risposta = model.generate_content(prompt_ricetta).text

                st.divider()
                st.markdown(risposta)
            except Exception as e:
                st.error(f"Errore durante la creazione della ricetta: {e}")
