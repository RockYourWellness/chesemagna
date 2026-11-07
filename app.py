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

# --- GENERAZIONE RICETTA ---
if invia:
    if not (proteine or carboidrati or verdure):
        st.error("Inserisci almeno uno o due alimenti del tuo pasto per procedere.")
    elif not metodi_scelti:
        st.error("Seleziona almeno un'opzione tra i metodi di cottura.")
    else:
        with st.spinner("🍳 Lo chef seleziona la combinazione ideale..."):
            
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
1. GESTIONE DELLA DISPENSA (ARMONIA DI SAPORI):
   - Gli aromi indicati ({stringa_aggiunte}) sono una DISPENSA DI PARTENZA, NON una lista da usare tutta insieme.
   - Scegli SOLTANTO 1-2 (massimo 3) ingredienti che legano alla perfezione in base alla 'Voglia' scelta:
     * 'Etnico / Speziato': valorizza soia e sesamo, oppure curry e yogurt/limone.
     * 'Fresco e semplice': punta su limone ed erbe fresche (menta o basilico).
     * 'Morbido e cremoso': usa yogurt o senape per una salsa rapida.
   - Vietati accostamenti sgradevoli o caotici (es. no curry insieme a origano e soia).
2. FEDELTÀ AGLI INGREDIENTI: Usa ESCLUSIVAMENTE la proteina, il carboidrato e la verdura scritti dal paziente. Mai aggiungere altre fonti proteiche inventate. Zero aglio.
3. BUONSENSO SUI CARBOIDRATI: Se il carboidrato è pane, crostini, friselle o gallette, servilo a fette a lato o come base d'appoggio; non metterlo a cuocere negli elettrodomestici.
4. TEMPERATURE E TEMPI:
   - Se 'Nessuna cottura', crea un piatto freddo senza alcuna fonte di calore.
   - Se si cuoce, specifica minuti e temperatura esatta (°C in friggitrice/forno, o fiamma in padella). Le verdure crude entrano per prime tagliate sottili; i cibi già pronti solo alla fine.
5. LINGUAGGIO: Italiano casalingo, limpido e rassicurante. Zero gergo da chef (niente tartare, carpacci, julienne, bowl).

STRUTTURA:
🍽️ **[Nome Semplice del Piatto]**
⏱️ **Tempo:** [Minuti] | 🌡️ **Cottura:** [Temperatura in °C, fiamma, o 'A crudo'] | 🍳 **Metodo:** [Strumento]
💡 *[1 frase sul profilo di sapore]*

🛒 **Ingredienti:**
- [Carboidrato: indicare se a fette a lato, base o cotto]
- [Proteina e Verdura con taglio pratico: a dadini, a fettine, ecc.]
- [Solo i condimenti selezionati dalla dispensa per la combinazione vincente]

👨‍🍳 **Preparazione:** (Massimo 3 passaggi chiari e lineari)
1. [Passo 1: taglio e preparazione]
2. [Passo 2: cottura con minuti e temperatura, o condimento a crudo]
3. [Passo 3: unione e impiattamento]

🌿 **Alternative se ti manca qualcosa:**
- *[Aroma/condimento scelto]:* puoi sostituirlo con [Alternativa comune]
"""

            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
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
                                        "Selezioni solo i condimenti adatti senza mai fare intrugli caotici. "
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
                    
                    # Box rassicurante compatto posizionato prima della ricetta
                    st.info("💡 **Promemoria senza stress:** Spezie e passaggi sono solo uno spunto. Usa ciò che hai in casa e adatta le cotture come ti è più comodo: la cucina deve toglierti pensieri, non aggiungerne!")
                    
                    st.markdown(ricetta)
                else:
                    st.error(f"Nessun modello ha risposto: {ultimo_errore}")

            except Exception as e:
                st.error(f"Errore di connessione a Groq: {e}")
