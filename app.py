import streamlit as st
from groq import Groq

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

# --- GENERAZIONE ULTRA-RAPIDA CON GROQ (SUB-SECOND) ---
if invia:
    if not (proteine or carboidrati or verdure):
        st.error("Inserisci almeno uno o due alimenti del tuo pasto per procedere.")
    elif not metodi_scelti:
        st.error("Seleziona almeno un metodo di cottura che sei disposto a usare.")
    else:
        with st.spinner("🍳 Lo chef sta creando la ricetta..."):
            
            prompt_utente = f"""
            DATI DEL PASTO:
            - Carboidrati: {carboidrati}
            - Proteine: {proteine}
            - Verdure: {verdure}
            - Tempo a disposizione: {tempo}
            - Voglia sensoriale: {voglia}
            - Metodi di cottura ammessi: {', '.join(metodi_scelti)}

            VINCOLI:
            - Usa SOLO gli strumenti ammessi. Se il tempo è 10-15 min, ipotizza riso/cereali precotti o tagli sottili.
            - Niente accostamenti sgradevoli (vietata la pasta con il pollo) e niente calcoli di calorie.
            - Risposta diretta e sintetica, senza convenevoli.

            FORMATO DA RISPETTARE:
            🍽️ **[Nome Invitante del Piatto]**
            ⏱️ [Tempo] | 🍳 Strumento: [Uno tra gli ammessi]
            💡 *[1 frase sul gusto]*

            🛒 **Ingredienti usati:**
            - [Carboidrati, Proteine, Verdure]
            - [Spezie ed erbe consigliate]

            👨‍🍳 **Passaggi Facili:** (Massimo 3 passaggi chiari)
            1. [Passo 1]
            2. [Passo 2]
            3. [Passo 3]

            🌿 **Spezie, Erbette e Sostituzioni Furbe:**
            - *[Spezia/erba usata]:* se non ce l'hai, usa [Alternativa comune]
            - *[Condimento cremoso/legante]:* se non ce l'hai, usa [Alternativa comune]
            """

            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "Sei uno chef nutrizionista esperto in alimentazione sostenibile, gustosa e priva di paranoie. Rispondi sempre in italiano, in modo conciso e appetitoso."
                        },
                        {
                            "role": "user",
                            "content": prompt_utente
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.5,
                    max_tokens=450,
                )

                ricetta = chat_completion.choices[0].message.content
                st.divider()
                st.markdown(ricetta)

            except Exception as e:
                st.error(f"Dettaglio errore: {e}")
