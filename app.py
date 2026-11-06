import streamlit as st
from groq import Groq

st.set_page_config(page_title="chesemagna", page_icon="🥗", layout="centered")

st.title("Che se magna")
st.markdown("Componi il tuo pasto con gli alimenti del piano: trasformeremo la solita routine in una ricetta veloce, aromatica e su misura.")

# --- MODULO FISSO (Campi essenziali senza chat) ---
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

# --- GENERAZIONE TESTUALE ULTRA-RAPIDA ---
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
            - Vietata la pasta col pollo e niente conteggi calorici.
            - Sintetico e appetitoso: massimo 130 parole.

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
                
                # 1. Filtro rigido: isoliamo SOLO i modelli di testo per chat (escludiamo audio, guard e vision)
                modelli_disponibili = [
                    m.id for m in client.models.list().data 
                    if not any(escluso in m.id.lower() for escluso in ["whisper", "guard", "vision", "embed"])
                ]

                # 2. Ordiniamo dando precedenza ai modelli Llama stabili
                modelli_prioritari = sorted(
                    modelli_disponibili, 
                    key=lambda x: ("llama" in x.lower() or "mixtral" in x.lower() or "gemma" in x.lower()), 
                    reverse=True
                )

                ricetta = None
                errore_ultimo = ""

                # 3. Tenta la generazione con il primo modello di testo valido
                for mod in modelli_prioritari:
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {
                                    "role": "system",
                                    "content": "Sei uno chef nutrizionista italiano esperto in piatti sani, rapidi e ricchi di gusto. Rispondi solo in italiano."
                                },
                                {
                                    "role": "user",
                                    "content": prompt_utente
                                }
                            ],
                            model=mod,
                            temperature=0.4,
                            max_tokens=400,
                        )
                        ricetta = chat_completion.choices[0].message.content
                        if ricetta:
                            break
                    except Exception as err:
                        errore_ultimo = str(err)
                        continue

                if ricetta:
                    st.divider()
                    st.markdown(ricetta)
                else:
                    st.error(f"Errore generazione: nessun modello compatibile ha risposto ({errore_ultimo})")

            except Exception as e:
                st.error(f"Errore di connessione a Groq: {e}")
