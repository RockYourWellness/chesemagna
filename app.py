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
        carboidrati = st.text_input("Carboidrati:", placeholder="Es. Polenta precotta, riso, patate, pane")
    with col_p:
        proteine = st.text_input("Proteine:", placeholder="Es. Pollo, uova, tofu, ceci in scatola")
    with col_v:
        verdure = st.text_input("Verdure:", placeholder="Es. Zucchine, carote, peperoni, spinaci")

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

# --- GENERAZIONE CON GERARCHIA TERMICA RIGIDA ---
if invia:
    if not (proteine or carboidrati or verdure):
        st.error("Inserisci almeno uno o due alimenti del tuo pasto per procedere.")
    elif not metodi_scelti:
        st.error("Seleziona almeno un metodo di cottura che sei disposto a usare.")
    else:
        with st.spinner("🍳 Lo chef calcola tagli e gerarchia di cottura..."):
            
            prompt_utente = f"""
            DATI DEL PASTO:
            - Carboidrati: {carboidrati}
            - Proteine: {proteine}
            - Verdure: {verdure}
            - Tempo massimo totale: {tempo}
            - Voglia sensoriale: {voglia}
            - Metodi di cottura concessi: {', '.join(metodi_scelti)}

            LEGGI FISICHE DELLA COTTURA (RISPETTO TASSATIVO):
            1. GERARCHIA D'INSERIMENTO OBBLIGATORIA:
               - PRIMA FASE (Minuto 0): Entrano SEMPRE e SOLO gli ingredienti CRUDI che contengono acqua cellulare e devono cuocere (es. zucchine, carote crude, carne cruda). Devono avere un taglio funzionale al tempo (a rondelle sottili di 3 mm o julienne se il tempo è sotto i 15 min).
               - SECONDA FASE (Solo a metà o negli ultimi 4-5 minuti): Entrano gli ingredienti GIÀ COTTI o precotti (es. polenta pronta in panetto, ceci in scatola, riso già pronto). Devono solo scaldarsi o creare la crosta esterna.
               - DIVIETO ASSOLUTO: MAI inserire un ingrediente precotto all'inizio se ci sono verdure crude nello stesso strumento; si brucerebbe/seccherebbe.
            2. FOCUS FRIGGITRICE AD ARIA (se selezionata):
               - Le verdure crude necessitano di spazio e calore iniziale (es. 180°C per 8-10 min).
               - La polenta precotta (o legumi precotti) va oliata leggermente in superficie e aggiunta SOLO per gli ultimi 4-5 minuti a 200°C per dorare senza disidratare il cuore.
            3. STILE:
               - Nessun accostamento sgradevole (no pasta con pollo) e nessun conteggio calorico.
               - Massimo 140 parole, conciso e pratico.

            STRUTTURA:
            🍽️ **[Nome Invitante del Piatto]**
            ⏱️ [Tempo effettivo] | 🍳 Strumento: [Uno tra {', '.join(metodi_scelti)}]
            💡 *[1 riga su consistenza e gusto]*

            🛒 **Ingredienti e Tagli:**
            - [Carboidrato, Proteina, Verdura con spessore di taglio consigliato]
            - [Spezie, erbe o condimento furbi]

            👨‍🍳 **Passaggi a Scaglioni (Ordine Termico Corretto):**
            1. [Passo 1 - Minuto 0: Avvio ingrediente crudo/più lungo con taglio fine]
            2. [Passo 2 - Ultimi minuti: Aggiunta ingrediente precotto per dorare/scaldare]
            3. [Passo 3: Chiusura con aroma, spezia o emulsione rapida]

            🌿 **Spezie & Sostituzioni:**
            - *[Spezia/erba usata]:* alternativa comune
            - *[Condimento/legante]:* alternativa comune
            """

            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                # Esclusione modelli non testuali
                modelli_disponibili = [
                    m.id for m in client.models.list().data 
                    if not any(escluso in m.id.lower() for escluso in ["whisper", "guard", "vision", "embed"])
                ]

                # Priorità ai modelli Llama
                modelli_prioritari = sorted(
                    modelli_disponibili, 
                    key=lambda x: ("llama" in x.lower() or "mixtral" in x.lower() or "gemma" in x.lower()), 
                    reverse=True
                )

                ricetta = None
                for mod in modelli_prioritari:
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "Sei uno chef professionista e docente di chimica culinaria. "
                                        "Applichi con rigore la fisica termica: i cibi crudi ricchi d'acqua entrano sempre prima; "
                                        "i cibi precotti o secchi entrano sempre per ultimi. Rispondi solo in italiano."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": prompt_utente
                                }
                            ],
                            model=mod,
                            temperature=0.2,  # Abbassata per ridurre le allucinazioni e aumentare il rigore logico
                            max_tokens=450,
                        )
                        ricetta = chat_completion.choices[0].message.content
                        if ricetta:
                            break
                    except Exception:
                        continue

                if ricetta:
                    st.divider()
                    st.markdown(ricetta)
                else:
                    st.error("Errore momentaneo di generazione. Riprova tra pochi istanti.")

            except Exception as e:
                st.error(f"Errore di connessione a Groq: {e}")
