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
        carboidrati = st.text_input("Carboidrati:", placeholder="Es. Riso, patate, polenta precotta")
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

# --- GENERAZIONE CON LOGICA DI COTTURA REALISTICA ---
if invia:
    if not (proteine or carboidrati or verdure):
        st.error("Inserisci almeno uno o due alimenti del tuo pasto per procedere.")
    elif not metodi_scelti:
        st.error("Seleziona almeno un metodo di cottura che sei disposto a usare.")
    else:
        with st.spinner("🍳 Lo chef calcola tagli e tempi di cottura..."):
            
            prompt_utente = f"""
            DATI DEL PASTO:
            - Carboidrati: {carboidrati}
            - Proteine: {proteine}
            - Verdure: {verdure}
            - Tempo massimo totale: {tempo}
            - Voglia sensoriale: {voglia}
            - Strumenti ammessi: {', '.join(metodi_scelti)}

            VINCOLI CULINARI RIGIDI:
            1. REALISMO TERMICO E FISICA DI COTTURA:
               - MAI cuocere insieme alimenti con tempi e idratazione diversi (es. verdure crude ricche d'acqua e carboidrati precotti o carni magre).
               - Imposta cotture A SCAGLIONI: indica esattamente cosa inserire prima e cosa aggiungere solo negli ultimi minuti per non bruciare/seccare.
               - Specifica il TAGLIO FUNZIONALE: se il tempo è breve (10-15 min), verdure a rondelle millimetriche o alla julienne; carni a straccetti sottili.
               - In friggitrice ad aria: proteggi i carboidrati precotti (polenta, riso, gnocchi) con un velo d'olio o scottali solo per pochi minuti per non farli diventare pietre.
            2. CUCINA CONSAPEVOLE:
               - Nessun accostamento sgradevole (no pasta con pollo).
               - Nessun calcolo di calorie o grammature rigide.
               - Sfrutta acidità, spezie o emulsioni per dare succosità senza seccare le preparazioni.

            STRUTTURA:
            🍽️ **[Nome Invitante del Piatto]**
            ⏱️ [Tempo effettivo] | 🍳 Strumento: [Uno tra gli ammessi]
            💡 *[1 riga sul profilo aromatico/consistenza]*

            🛒 **Ingredienti e Tagli Consigliati:**
            - [Carboidrato, Proteina, Verdura con indicazione di taglio esatto per cuocere nei tempi]
            - [Spezie, erbe o grasso di cottura suggeriti]

            👨‍🍳 **Passaggi a Scaglioni:** (Max 3 passaggi cronologici con minuti precisi per ogni fase)
            1. [Minuto 0-X: prima preparazione/cottura elemento che richiede più tempo]
            2. [Minuto X-Y: inserimento secondo elemento / doratura]
            3. [Tocco finale: condimento, mantecatura o finitura a crudo]

            🌿 **Spezie & Sostituzioni Furbe:**
            - *[Spezia/erba usata]:* alternativa comune
            - *[Elemento umido/legante]:* alternativa comune
            """

            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                # Esclusione modelli non testuali
                modelli_disponibili = [
                    m.id for m in client.models.list().data 
                    if not any(escluso in m.id.lower() for escluso in ["whisper", "guard", "vision", "embed"])
                ]

                # Priorità ai modelli Llama stabili
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
                                        "Sei uno chef professionista e tecnologo alimentare italiano. "
                                        "Conosci alla perfezione la chimica della cottura, le rese della friggitrice ad aria, "
                                        "i tagli funzionali e la gestione
