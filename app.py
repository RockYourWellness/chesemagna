import streamlit as st
from groq import Groq

st.set_page_config(page_title="chesemagna", page_icon="🥗", layout="centered")

st.title("Che se magna")
st.markdown("Componi il tuo pasto con gli alimenti del piano: trasformeremo la solita routine in una ricetta veloce, saporita e senza complicazioni.")

# --- MODULO FISSO ---
with st.form("modulo_ricetta"):
    st.subheader("1. Gli alimenti del tuo pasto")
    col_c, col_p, col_v = st.columns(3)
    with col_c:
        carboidrati = st.text_input("Carboidrati:", placeholder="Es. Pane, crostini, mais, riso precotto, friselle")
    with col_p:
        proteine = st.text_input("Proteine:", placeholder="Es. Tofu, ceci in scatola, tonno, uova, feta, pollo")
    with col_v:
        verdure = st.text_input("Verdure:", placeholder="Es. Zucchine, carote, pomodori, insalata, spinaci")

    st.subheader("2. Tempo e Voglia del momento")
    col_t, col_m = st.columns(2)
    with col_t:
        tempo = st.selectbox("Quanto tempo hai?", ["10-15 minuti (Ultra rapido)", "20-30 minuti", "Oltre 30 minuti"])
    with col_m:
        voglia = st.selectbox("Cosa ti andrebbe oggi?", [
            "Fresco e semplice", 
            "Croccante e sfizioso", 
            "Morbido e saporito", 
            "Profumato con erbe", 
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

# --- GENERAZIONE RICETTA CON FOOTER DI RASSICURAZIONE ---
if invia:
    if not (proteine or carboidrati or verdure):
        st.error("Inserisci almeno uno o due alimenti del tuo pasto per procedere.")
    elif not metodi_scelti:
        st.error("Seleziona almeno un'opzione tra i metodi di cottura (anche solo 'A crudo').")
    else:
        with st.spinner("🍳 Preparo una ricetta semplice e appetitosa..."):
            
            prompt_utente = f"""
            DATI DEL PASTO:
            - Carboidrati: {carboidrati}
            - Proteine: {proteine}
            - Verdure: {verdure}
            - Tempo massimo: {tempo}
            - Voglia: {voglia}
            - Metodi ammessi: {', '.join(metodi_scelti)}

            VINCOLI TASSATIVI:
            1. LINGUAGGIO SEMPLICE E CASALINGO (TARGET: TUTTI, ANCHE ANZIANI):
               - VIETATO IL GERGO GOURMET: niente sashimi, tartare, carpaccio, bowl, dressing, julienne, brunoise.
               - Solo parole comuni: "a fettine sottili", "a dadini", "a striscioline", "insalatona", "piatto freddo".
               - Titoli semplici e chiari (es. "Insalata fresca con ceci e pomodori", "Zucchine in padella con pollo e pane").
            2. DIVIETO TOTALE DELL'AGLIO:
               - Nessun tipo di aglio. Usa basilico, origano, rosmarino, limone, prezzemolo, timo o spezie dolci.
            3. CARBOIDRATI COME PANE O CROSTINI:
               - Se l'utente scrive pane, fette, gallette o crostini, NON metterli a cuocere negli elettrodomestici. Servili a fette a lato per accompagnare.
            4. OPZIONE "NESSUNA COTTURA / PIATTO FREDDO":
               - Se selezionata, non accendere nulla: taglia le verdure e uniscile alle proteine condendo con olio, limone ed erbe.
            5. ORDINE TERMICO (SE SI ACCENDE QUALCOSA):
               - Verdure crude o carne entrano per prime tagliate piccole. Ingredienti precotti (ceci, polenta pronta) entrano solo negli ultimi minuti per scaldarli.
            6. ZERO CALORIE, zero pasta con pollo, massimo 120 parole.

            FORMATO DI RISPOSTA:
            🍽️ **[Nome Semplice e Familiare del Piatto]**
            ⏱️ [Tempo] | 🍳 Strumento: [Strumento usato o "Nessuna cottura"]
            💡 *[1 frase rassicurante sul sapore]*

            🛒 **Ingredienti da preparare:**
            - [Carboidrato: indicare se va a fette nel piatto a lato o cotto]
            - [Proteina e Verdura con taglio pratico: a dadini, a fettine, ecc.]
            - [Condimento semplice: olio, limone, erbe a piacere]

            👨‍🍳 **Come prepararlo:** (Massimo 3 passaggi chiarissimi)
            1. [Passo 1: taglio]
            2. [Passo 2: cottura o unione a freddo]
            3. [Passo 3: come servire a tavola]

            🌿 **Alternative pratiche se manca qualcosa:**
            - *[Erba usata]:* se non ce l'hai, usa [Alternativa comunissima]
            - *[Condimento]:* se non ce l'hai, usa [Alternativa comunissima]
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
                                        "Sei un cuoco di casa italiano, pratico e rassicurante. "
                                        "Spieghi tutto con parole semplici e familiari. Non usi mai l'aglio. Rispondi in italiano."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": prompt_utente
                                }
                            ],
                            model=mod,
                            temperature=0.2,
                            max_tokens=420,
                        )
                        ricetta = chat_completion.choices[0].message.content
                        if ricetta:
                            break
                    except Exception:
                        continue

                if ricetta:
                    st.divider()
                    st.markdown(ricetta)
                    
                    # --- FOOTER DI RASSICURAZIONE FISSO ---
                    st.info("""
                    💡 **Promemoria senza stress:**
                    * **Spezie ed erbe:** sono solo un suggerimento. Usa pure quello che hai già a casa o che ti piace di più; se non ne hai, bastano un goccio d'olio e un pizzico di sale.
                    * **Massima libertà:** se un passaggio ti sembra scomodo o complicato, prendi solo quello che ti serve. Puoi cuocere le verdure come consigliato e fare il resto nel modo più comodo per te (come scaldare la polenta o il riso in un semplice pentolino, o mangiare il pane così com'è). La cucina deve toglierti pensieri, non aggiungerne!
                    """)
                else:
                    st.error("Errore temporaneo. Riprova tra un istante.")

            except Exception as e:
                st.error(f"Errore di connessione a Groq: {e}")
