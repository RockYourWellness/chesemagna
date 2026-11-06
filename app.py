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

# --- GENERAZIONE CON SUPPORTO PIATTI FREDDI/CRUDO ---
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

            VINCOLI RIGIDI E BUONSENSO:
            1. OPZIONE "NESSUNA COTTURA (A CRUDO / PIATTO FREDDO)":
               - Se tra i metodi c'è 'Nessuna cottura', o se è l'unica scelta: ZERO FONTI DI CALORE! Non nominare fornelli, forni o friggitrici.
               - Crea un'insalatona strutturata, una bowl da assemblaggio, una tartare vegetale o un carpaccio fresco.
               - Gestisci gli ingredienti a freddo: verdure tagliate finissime (marinate al limone o all'aceto se crude e dure come zucchine/carote), proteine sciacquate/sgocciolate o a dadini (tofu marinato con soia, legumi, uova se sode o formaggio), carboidrati freschi (pane, crostini, friselle o mais).
               - Focus totale sull'EMULSIONE del condimento: consiglia una vinaigrette o salsa veloce (olio, acidità come limone/aceto/soia, senape o yogurt) ed erbe fresche per legare il tutto.
            2. GESTIONE CARBOIDRATI READY-TO-EAT:
               - Pane, crostini, friselle o gallette non vanno mai cotti dentro elettrodomestici: usali come accompagnamento a lato o come base d'appoggio.
            3. STILE:
               - Vietata la pasta con pollo e niente calcolo di calorie o grammature.
               - Sintetico, pratico e gustoso: massimo 140 parole.

            STRUTTURA DA RISPETTARE:
            🍽️ **[Nome Invitante del Piatto]**
            ⏱️ [Tempo] | 🍳 Metodo: [Nessuna cottura (A crudo) OPPURE strumento usato]
            💡 *[1 riga su equilibrio aromatico e consistenze]*

            🛒 **Ingredienti e Tagli:**
            - [Carboidrato: specificare se fresco a lato o base]
            - [Proteina e Verdura con taglio funzionale, es. julienne, fettine a velo, cubetti]
            - [Emulsione o condimento aromatico suggerito]

            👨‍🍳 **Passaggi Rapidi (Zero Sforzo):** (Max 3 passaggi)
            1. [Passo 1: taglio verdure / marinatura espressa a freddo]
            2. [Passo 2: unione ingredienti e condimento con l'emulsione]
            3. [Passo 3: abbinamento carboidrato, es. crostone o a lato]

            🌿 **Spezie & Sostituzioni Furbe:**
            - *[Ingrediente aromatico/erba]:* alternativa comune
            - *[Condimento/salsa usata]:* alternativa comune
            """

            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                modelli_disponibili = [
                    m.id for m in client.models.list().data 
                    if not any(escluso in m.id.lower() for escluso in ["whisper", "guard", "vision", "embed"])
                ]

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
                                        "Sei uno chef nutrizionista esperto in alimentazione pratica e senza paranoie. "
                                        "Se l'utente non vuole accendere fornelli, crei piatti freddi, bowl e insalate "
                                        "aromatiche con emulsioni a crudo saporite. Rispondi sempre in italiano."
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
