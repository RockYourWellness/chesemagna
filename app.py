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
        carboidrati = st.text_input("Carboidrati:", placeholder="Es. Pane, crostini, mais, riso precotto, friselle")
    with col_p:
        proteine = st.text_input("Proteine:", placeholder="Es. Tofu, ceci in scatola, tonno, uova, feta")
    with col_v:
        verdure = st.text_input("Verdure:", placeholder="Es. Zucchine, cetrioli, pomodori, spinaci, carote")

    st.subheader("2. Tempo e Voglia del momento")
    col_t, col_m = st.columns(2)
    with col_t:
        tempo = st.selectbox("Quanto tempo hai?", ["10-15 minuti (Ultra rapido)", "20-30 minuti", "Oltre 30 minuti"])
    with col_m:
        voglia = st.selectbox("Cosa ti andrebbe oggi?", [
            "Fresco e aromatico", 
            "Croccante e sfizioso", 
            "Cremoso e avvolgente", 
            "Speziato / Etnico", 
            "Rustico / Mediterraneo"
        ])

    st.subheader("3. Metodi di cottura che vuoi usare")
    st.caption("Spunta solo gli strumenti che hai e che SEI DISPOSTO ad accendere oggi:")
    metodi_scelti = st.multiselect(
        "Strumenti ammessi per oggi:",
        [
            "Nessuna cottura (A crudo / Piatto freddo)",
            "Padella / Fornelli", 
            "Friggitrice ad aria", 
            "Forno", 
            "Microonde", 
            "Vaporiera", 
            "Frullatore / Minipimer"
        ],
        default=["Nessuna cottura (A crudo / Piatto freddo)"]
    )

    invia = st.form_submit_button("✨ Svolta la mia cena")

# --- GENERAZIONE RICETTA (SENZA AGLIO E CON REGOLE TERMICHE) ---
if invia:
    if not (proteine or carboidrati or verdure):
        st.error("Inserisci almeno uno o due alimenti del tuo pasto per procedere.")
    elif not metodi_scelti:
        st.error("Seleziona almeno un'opzione tra i metodi di cottura (anche solo 'A crudo').")
    else:
        with st.spinner("🍳 Lo chef crea la combinazione ideale..."):
            
            prompt_utente = f"""
            DATI DEL PASTO:
            - Carboidrati: {carboidrati}
            - Proteine: {proteine}
            - Verdure: {verdure}
            - Tempo massimo: {tempo}
            - Voglia sensoriale: {voglia}
            - Metodi ammessi: {', '.join(metodi_scelti)}

            VINCOLI TASSATIVI:
            1. DIVIETO TOTALE DELL'AGLIO:
               - È SEVERAMENTE VIETATO usare aglio in qualsiasi forma (fresco, in polvere, spicchi o strane invenzioni). A molti pazienti non piace o causa problemi digestivi.
               - Per dare sapore usa erbe mediterranee (basilico, origano, rosmarino, timo, prezzemolo), scorza di agrumi o spezie classiche (pepe, paprika dolce, origano, zenzero).
            2. OPZIONE "NESSUNA COTTURA (A CRUDO / PIATTO FREDDO)":
               - Se c'è 'Nessuna cottura' tra le scelte o è l'unica selezionata: NON nominare fornelli o calore.
               - Proponi bowl, insalate ricche, tartare o carpacci vegetali.
               - Cura l'emulsione del condimento: olio, acidità (limone, aceto o soia) e leganti freddi semplici (yogurt, senape).
            3. CARBOIDRATI READY-TO-EAT:
               - Pane fresco, crostini, friselle o gallette non vanno cotti negli elettrodomestici: usali a crudo come accompagnamento o base d'appoggio.
            4. ORDINE TERMICO (SE SI CUOCE):
               - Verdure crude e carni entrano per prime con tagli sottili. Ingredienti precotti (es. polenta, ceci) entrano solo negli ultimi 4 minuti per non seccare.
            5. STILE:
               - Niente accostamenti assurdi (no pasta con pollo), niente conteggi calorici.
               - Massimo 130 parole, conciso e pratico.

            STRUTTURA:
            🍽️ **[Nome Invitante del Piatto]**
            ⏱️ [Tempo] | 🍳 Metodo: [Nessuna cottura OPPURE strumento usato]
            💡 *[1 riga sul gusto]*

            🛒 **Ingredienti e Tagli:**
            - [Carboidrato: specificare se a lato, base o cotto]
            - [Proteina e Verdura con indicazione di taglio precisa]
            - [Erbe aromatiche, spezie e condimento suggeriti (NO aglio)]

            👨‍🍳 **Passaggi Rapidi:** (Massimo 3 passaggi chiari)
            1. [Passo 1]
            2. [Passo 2]
            3. [Passo 3]

            🌿 **Erbe & Sostituzioni:**
            - *[Erba/spezia usata]:* alternativa comune
            - *[Condimento usato]:* alternativa comune
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
                                        "Sei uno chef nutrizionista italiano. Crei ricette sane, saporite e concrete. "
                                        "Non usi MAI l'aglio. Rispondi solo in italiano senza allucinazioni culinarie."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": prompt_utente
                                }
                            ],
                            model=mod,
                            temperature=0.2,
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
