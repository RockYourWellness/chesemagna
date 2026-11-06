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
               - Focus totale sull'EMULSIONE del condimento: consiglia una vinaigrette o salsa veloce (olio, acidità come limone/aceto/soia, senape o yogurt
