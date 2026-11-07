import streamlit as st
from groq import Groq

st.set_page_config(page_title="chesemagna", page_icon="🥗", layout="centered")

st.title("Che se magna")
st.markdown("Componi il tuo pasto con gli alimenti del piano: trasformeremo la solita routine in una ricetta veloce, saporita e senza complicazioni.")

# Lista delle aggiunte consentite
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

    # Menu a tendina multiplo per aromi e condimenti
    aggiunte_scelte = st.multiselect(
        "Aggiunte consentite che hai in casa (facoltativo - seleziona pure più elementi):",
        options=OPZIONI_AGGIUNTE,
        default=[],
        placeholder="Scegli erbe, spezie o condimenti da valorizzare..."
    )

    st.subheader("2. Tempo e Voglia del momento")
    col_t, col_m = st.columns(2)
    with col_t:
        tempo = st.selectbox("Quanto tempo hai?", ["10-15 minuti (Ultra rapido)", "20-30 minuti", "Oltre 30 minuti"])
    with col_m:
        voglia = st.selectbox("Cosa ti andrebbe oggi?", [
            "Fresco e semplice", 
            "Croccante e dorato", 
            "Morbido e saporito", 
            "Profumato alle erbe", 
            "Speziato ed etnico",
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

# --- GENERAZIONE RICETTA CON SELEZIONE DINAMICA DEL MODELLO ---
if invia:
    if not (proteine or carboidrati or verdure):
        st.error("Inserisci almeno uno o due alimenti del tuo pasto per procedere.")
    elif not metodi_scelti:
        st.error("Seleziona almeno un'opzione tra i metodi di cottura.")
    else:
        with st.spinner("🍳 Preparo una ricetta calibrata sui tuoi ingredienti..."):
            
            stringa_aggiunte = ", ".join(aggiunte_scelte) if aggiunte_scelte else "Nessuna specifica (usa solo olio, sale e condimenti base da dispensa)"
            
            prompt_utente = f"""
SELEZIONE DEL PAZIENTE:
- Carboidrato: {carboidrati if carboidrati else "Nessuno (non aggiungerne altri)"}
- Proteina: {proteine if proteine else "Nessuna (non aggiungerne altre)"}
- Verdura: {verdure if verdure else "Nessuna (non aggiungerne altre)"}
- Aggiunte/Aromi scelti in dispensa: {stringa_aggiunte}
- Tempo a disposizione: {tempo}
- Voglia di oggi: {voglia}
- Metodi concessi: {', '.join(metodi_scelti)}

DIRETTIVE DI PREPARAZIONE:
1. FEDELTÀ AGLI INGREDIENTI BASE: Usa ESCLUSIVAMENTE la proteina, il carboidrato e la verdura indicati. Se l'utente ha indicato ceci, usa solo ceci; se ha scritto tofu, usa solo tofu; se ha scritto uova, usa solo uova. Non introdurre MAI altre proteine inventate.
2. VALORIZZAZIONE AGGIUNTE E VOGLIA: Se l'utente seleziona 'Speziato ed etnico' o seleziona spezie/condimenti specifici ({stringa_aggiunte}), sfrutta quegli elementi per dare sapore (es. tostatura del curry con le verdure, marinatura a freddo con soia, emulsione allo yogurt, semi tostati croccanti). Non usare mai aglio.
3. PRATICITÀ DEL CARBOIDRATO: Se il carboidrato è pane, crostini, friselle o gallette, va servito fresco a fette a lato o come base; non metterlo a cuocere negli elettrodomestici.
4. CALORE E TEMPI:
   - Se il metodo è 'Nessuna cottura', crea un piatto freddo senza alcuna fonte di calore.
   - Se usi elettrodomestici, specifica minuti e temperatura o intensità di calore esatta (es. 180°C in friggitrice, o fiamma media in padella).
   - Inserisci prima le verdure crude a fette sottili e solo alla fine gli ingredienti già cotti o in scatola per scaldarli.
5. LINGUAGGIO: Italiano casalingo, limpido e rassicurante. Nessun termine tecnico da ristorante (niente brunoise, julienne, tartare, sashimi, bowl).

STRUTTURA DI RISPOSTA:
🍽️ **[Nome Semplice del Piatto]**
⏱️ **Tempo:** [Minuti] | 🌡️ **Cottura:** [Temperatura in gradi °C, fiamma, oppure 'A crudo'] | 🍳 **Metodo:** [Strumento]
💡 *[1 frase accattivante sul sapore]*

🛒 **Ingredienti:**
- [Carboidrato: indicare se a fette a lato, base o cotto]
- [Proteina e Verdura con taglio pratico: a dadini, a fettine sottili, ecc.]
- [Aromi e condimenti scelti utilizzati]

👨‍🍳 **Preparazione:** (Massimo 3 passaggi chiari e lineari)
1. [Passo 1: taglio e preparazione]
2. [Passo 2: cottura con minuti e temperatura, oppure emulsione/condimento a freddo]
3. [Passo 3: unione e impiattamento]

🌿 **Alternative se ti manca qualcosa:**
- *[Aroma/spezia usata]:* puoi sostituirla con [Altra opzione comune]
- *[Condimento usato]:* puoi sostituirlo con [Altro condimento comune]
"""

            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                # 1. Filtra solo i modelli di testo escludendo audio e moderazione
                modelli_disponibili = [
                    m.id for m in client.models.list().data 
                    if not any(escluso in m.id.lower() for escluso in ["whisper", "guard", "vision", "embed", "tts"])
                ]

                # 2. Ordina dando priorità ai modelli di testo per chat
                modelli_prioritari = sorted(
                    modelli_disponibili, 
                    key=lambda x: ("llama" in x.lower() or "mixtral" in x.lower() or "gemma" in x.lower() or "qwen" in x.lower()), 
                    reverse=True
                )

                ricetta = None
                ultimo_errore = ""

                # 3. Prova sequenziale del primo modello testuale funzionante
                for mod in modelli_prioritari:
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "Sei un cuoco casalingo italiano e biologo nutrizionista. "
                                        "Parli un italiano impeccabile, semplice e familiare. "
                                        "Rispetti alla lettera gli ingredienti e gli aromi selezionati dall'utente senza inventarne altri."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": prompt_utente
                                }
                            ],
                            model=mod,
                            temperature=0.45,
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
                    st.error(f"Nessun modello ha risposto. Modelli provati: {modelli_prioritari}. Errore: {ultimo_errore}")

            except Exception as e:
                st.error(f"Errore di connessione a Groq: {e}")
