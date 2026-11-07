import streamlit as st
from groq import Groq

st.set_page_config(page_title="chesemagna", page_icon="🥗", layout="centered")

st.title("Che se magna")
st.markdown("Componi il tuo pasto con gli alimenti del piano: trasformeremo la solita routine in una ricetta veloce, saporita e senza complicazioni.")

# Lista delle aggiunte disponibili in dispensa
OPZIONI_AGGIUNTE = [
    "Basilico", "Prezzemolo", "Rosmarino", "Menta", "Salvia",
    "Paprika", "Curry", "Peperoncino", "Pepe", "Mix di spezie",
    "Yogurt bianco", "Succo di limone", "Aceto", "Aceto di mele",
    "Senape", "Salsa di soia", "Olive", "Capperi",
    "Semi di sesamo", "Semi di papavero", "Semi misti", "Lievito alimentare"
]

# --- MODULO FISSO ---
with st.form("modulo_ricetta"):
    st.subheader("1. Gli alimenti del tuo pasto")
    col_c, col_p, col_v = st.columns(3)
    with col_c:
        carboidrati = st.text_input("Carboidrati:", placeholder="Es. Pane, riso, patate, couscous, gallette")
    with col_p:
        proteine = st.text_input("Proteine:", placeholder="Es. Tofu, ceci, uova, tonno, formaggio, lenticchie")
    with col_v:
        verdure = st.text_input("Verdure:", placeholder="Es. Zucchine, carote, pomodori, spinaci, finocchi")

    # Menu a tendina: dispensa aromi/condimenti a disposizione
    aggiunte_scelte = st.multiselect(
        "Cosa hai in dispensa tra questi? (Seleziona pure tutto ciò che hai a casa, lo chef sceglierà solo la combinazione migliore):",
        options=OPZIONI_AGGIUNTE,
        default=[],
        placeholder="Seleziona erbe, spezie o condimenti disponibili a casa..."
    )

    st.subheader("2. Tempo e Voglia del momento")
    col_t, col_m = st.columns(2)
    with col_t:
        tempo = st.selectbox("Quanto tempo hai?", ["10-15 minuti (Ultra rapido)", "20-30 minuti", "Oltre 30 minuti"])
    with col_m:
        voglia = st.selectbox("Cosa ti andrebbe oggi?", [
            "Etnico / Speziato",
            "Fresco e semplice", 
            "Croccante e dorato", 
            "Morbido e cremoso", 
            "Profumato alle erbe", 
            "Rustico / Tradizionale"
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

# --- GENERAZIONE RICETTA CON ARMONIA DI SAPORI ---
if invia:
    if not (proteine or carboidrati or verdure):
        st.error("Inserisci almeno uno o due alimenti del tuo pasto per procedere.")
    elif not metodi_scelti:
        st.error("Seleziona almeno un'opzione tra i metodi di cottura.")
    else:
        with st.spinner("🍳 Lo chef seleziona la combinazione di sapori ideale..."):
            
            stringa_aggiunte = ", ".join(aggiunte_scelte) if aggiunte_scelte else "Condimenti base (olio EVO, sale, pepe)"
            
            prompt_utente = f"""
DATI PASTO:
- Carboidrato: {carboidrati if carboidrati else "Nessuno (non inventarlo)"}
- Proteina: {proteine if proteine else "Nessuna (non inventarla)"}
- Verdura: {verdure if verdure else "Nessuna (non inventarla)"}
- Dispensa aromi/condimenti disponibili a casa: {stringa_aggiunte}
- Tempo massimo: {tempo}
- Voglia di oggi: {voglia}
- Metodi concessi: {', '.join(metodi_scelti)}

DIRETTIVE DI COMBINAZIONE ED EQUILIBRIO:
1. GESTIONE DELLA DISPENSA (DIVIETO DI PASTICCIO):
   - Gli aromi/condimenti indicati sopra ({stringa_aggiunte}) sono una DISPENSA DI PARTENZA, NON una lista da usare tutta insieme!
   - NON usarli tutti: seleziona SOLTANTO i 1-2 (massimo 3) ingredienti che stanno davvero bene insieme per creare la combo migliore in base alla 'Voglia' scelta:
     * Se la voglia è 'Etnico / Speziato': pesca ad esempio solo salsa di soia e sesamo, oppure curry e yogurt.
     * Se la voglia è 'Fresco e semplice': punta su limone ed erba fresca (come menta o basilico).
     * Se la voglia è 'Morbido e cremoso': usa senape o yogurt per un'emulsione avvolgente.
   - Non mischiare sapori in contrasto sgradevole (es. origano con curry e soia insieme: vietato!).
2. FEDELTÀ AGLI INGREDIENTI: Usa ESCLUSIVAMENTE la proteina, il carboidrato e la verdura scritti dal paziente. Mai aggiungere altre carni o proteine. Zero aglio.
3. BUONSENSO SUI CARBOIDRATI: Se il carboidrato è pane, crostini, friselle o gallette, va servito fresco a fette a lato o come base; non cuocerlo negli elettrodomestici.
4. TEMPERATURE E TEMPI:
   - Se 'Nessuna cottura', crea un piatto freddo senza calore.
   - Se si cuoce, specifica sempre sia i minuti sia la temperatura esatta (es. 180°C in friggitrice, o fiamma vivace in padella). Le verdure crude entrano per prime a taglio sottile; i cibi già pronti solo alla fine.
5. LINGUAGGIO: Italiano limpido, casalingo e senza gergo da ristorante (niente carpacci, tartare, julienne, bowl).

STRUTTURA:
🍽️ **[Nome Semplice del Piatto]**
⏱️ **Tempo:** [Minuti] | 🌡️ **Cottura:** [Temperatura in °C, fiamma, o 'A crudo'] | 🍳 **Metodo:** [Strumento]
💡 *[1 frase sul profilo di sapore]*

🛒 **Ingredienti:**
- [Carboidrato: specificare se a fette a lato, base o cotto]
- [Proteina e Verdura con taglio pratico: a dadini, a fettine, ecc.]
- [Solo i 1-3 aromi/condimenti selezionati dalla dispensa per la combinazione vincente]

👨‍🍳 **Preparazione:** (Massimo 3 passaggi chiari e lineari)
1. [Passo 1: taglio e preparazione]
2. [Passo 2: cottura con minuti e temperatura, o emulsione a freddo]
3. [Passo 3: unione e impiattamento]

🌿 **Alternative se ti manca qualcosa:**
- *[Aroma/condimento scelto]:* puoi sostituirlo con [Alternativa comune]
"""

            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                # Filtro modelli testuali validi
                modelli_disponibili = [
                    m.id for m in client.models.list().data 
                    if not any(escluso in m.id.lower() for escluso in ["whisper", "guard", "vision", "embed", "tts"])
                ]

                modelli_prioritari = sorted(
                    modelli_disponibili, 
                    key=lambda x: ("llama" in x.lower() or "mixtral" in x.lower() or "gemma" in x.lower() or "qwen" in x.lower()), 
                    reverse=True
                )

                ricetta = None
                ultimo_errore = ""

                for mod in modelli_prioritari:
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "Sei un cuoco casalingo italiano esperto di armonia gastronomica. "
                                        "Selezioni solo i condimenti più adatti senza mai fare intrugli caotici. "
                                        "Rispetti rigidamente gli ingredienti dell'utente. Rispondi solo in italiano semplice."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": prompt_utente
                                }
                            ],
                            model=mod,
                            temperature=0.4,
                            max_tokens=450,
                        )
                        ricetta = chat_completion.choices[0].message.content
                        if ricetta:
                            break
                    except Exception as err:
                        ultimo_errore = str(err)
                        continue

                if ricetta:
                    st.divider()
                    st.markdown(ricetta)
                    
                    # Box rassicurante fisso
                    st.info("""
                    💡 **Promemoria senza stress:**
                    * **Spezie ed erbe:** sono solo un suggerimento. Usa pure quello che hai già a casa o che ti piace di più; se non ne hai, bastano un goccio d'olio e un pizzico di sale.
                    * **Massima libertà:** se un passaggio ti sembra scomodo o complicato, prendi solo quello che ti serve. Puoi cuocere le verdure come consigliato e fare il resto nel modo più comodo per te (come scaldare la polenta o il riso in un semplice pentolino, o mangiare il pane così com'è). La cucina deve toglierti pensieri, non aggiungerne!
                    """)
                else:
                    st.error(f"Nessun modello ha risposto: {ultimo_errore}")

            except Exception as e:
                st.error(f"Errore di connessione a Groq: {e}")
