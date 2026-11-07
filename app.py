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
   - Se 'Nessuna cottura', crea un piatto
