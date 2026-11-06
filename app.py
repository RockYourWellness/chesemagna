import streamlit as st
from groq import Groq

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

# --- GENERAZIONE ULTRA-RAPIDA CON GROQ ---
if invia:
    if not (proteine or carboidrati or verdure):
        st.error("Inserisci almeno uno o due alimenti del tuo pasto per procedere.")
    elif not metodi_scelti:
        st.error("Seleziona almeno un metodo di cottura che sei disposto a usare.")
    else:
        with st.spinner("🍳 Preparazione della ricetta..."):
            
            prompt_utente = f"""
            DATI DEL PASTO:
            - Carboidrati: {carboidrati}
            - Proteine: {proteine}
            - Verdure: {verdure}
            - Tempo a disposizione: {tempo}
            - Voglia sensoriale: {voglia}
            - Metodi di cottura ammessi: {', '.join(metodi_scelti)}

            VINCOLI:
            - Usa SOLO gli strumenti ammessi. Se tempo <= 15 min, ipotizza cereali precotti.
            - Vietata la pasta col pollo e niente calcoli calorici.
            - Breve, pratico e diretto: massimo 130 parole.

            STRUTTURA:
            🍽️ **[Nome Invitante del Piatto]**
            ⏱️ [Tempo] | 🍳 Strumento: [Uno tra gli ammessi]
            💡 *[1 frase sul gusto]*

            🛒 **Ingredienti usati:**
            - [Carboidrati, Proteine, Verdure]
            - [Spezie ed erbe consigliate]

            👨‍🍳 **Passaggi Facili:** (Max 3 passaggi chiari)
            1. [Passo 1]
            2. [Passo 2]
            3. [Passo 3]

            🌿 **Spezie & Sostituzioni Furbe:**
            - *[Spezia/erba usata]:* alternativa comune
            - *[Condimento cremoso/legante]:* alternativa comune
            """

            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                # Rilevamento automatico del miglior modello Llama attivo sull'account
                modelli_disponibili = [m.id for m in client.models.list().data]
                preferiti = ["llama-3.1-8b-instant", "llama3-8b-8192", "mixtral-8x7b-32768"]
                
                modello_scelto = next((m for m in preferiti if m in modelli_disponibili), modelli_disponibili[0])

                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "Sei uno chef nutrizionista italiano specializzato in piatti veloci, aromatici e senza paranoie. Rispondi sempre in italiano."
                        },
                        {
                            "role": "user",
                            "content": prompt_utente
                        }
                    ],
                    model=modello_scelto,
                    temperature=0.4,
                    max_tokens=400,
                )

                ricetta = chat_completion.choices[0].message.content
                st.divider()
                st.markdown(ricetta)

            except Exception as e:
                st.error(f"Dettaglio errore: {e}")
