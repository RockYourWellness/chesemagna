import streamlit as st
import google.generativeai as genai
from openai import OpenAI

# Configurazione chiavi API salvate nei Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
client_img = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Svoltagusto", page_icon="🥗", layout="centered")

st.title("🥗 Svoltagusto")
st.markdown("Componi il tuo pasto con gli alimenti del piano: trasformeremo la solita routine in una ricetta veloce, aromatica e su misura.")

# --- MODULO FISSO SENZA CHAT ---
with st.form("modulo_ricetta"):
    st.subheader("1. Gli ingredienti del tuo pasto")
    col_c, col_p, col_v = st.columns(3)
    with col_c:
        carboidrati = st.text_input("Carboidrati:", placeholder="Es. Riso, patate, couscous")
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

    st.subheader("3. Come vuoi cucinare oggi?")
    st.caption("Spunta solo gli strumenti che hai a disposizione e che HAI VOGLIA di usare oggi:")
    metodi_scelti = st.multiselect(
        "Strumenti ammessi per oggi:",
        ["Padella / Fornelli", "Friggitrice ad aria", "Forno", "Microonde", "Vaporiera", "Frullatore / Minipimer"],
        default=["Padella / Fornelli"]
    )

    invia = st.form_submit_button("✨ Svolta la mia cena")

# --- GENERAZIONE RICETTA E FOTO ---
if invia:
    if not (proteine or carboidrati or verdure):
        st.error("Inserisci almeno uno o due alimenti del tuo pasto per procedere.")
    elif not metodi_scelti:
        st.error("Seleziona almeno un metodo di cottura che sei disposto a usare.")
    else:
        with st.spinner("Creazione della ricetta aromatica e della foto in corso..."):
            
            prompt_ricetta = f"""
            Sei uno chef specializzato in nutrizione sana, sostenibile e priva di paranoie.
            
            DATI DEL PASTO FORNITI DAL PAZIENTE:
            - Carboidrati: {carboidrati}
            - Proteine: {proteine}
            - Verdure: {verdure}
            - Tempo a disposizione: {tempo}
            - Voglia sensoriale: {voglia}
            - Metodi di cottura tassativamente ammessi: {', '.join(metodi_scelti)}

            VINCOLI E LINEE GUIDA:
            1. Usa SOLO i metodi di cottura indicati ({', '.join(metodi_scelti)}). Se l'utente non ha spuntato il forno, non proporre cotture al forno.
            2. Se il tempo è '10-15 minuti', ipotizza riso/cereali precotti o tagli ultra-sottili.
            3. Valorizza il piatto suggerendo attivamente spezie, erbe aromatiche e condimenti furbi (limone, yogurt, aceto, salsa di soia, semi) per assecondare la voglia richiesta.
            4. Inserisci sempre una sezione finale con SOSTITUZIONI pratiche per le spezie e i condimenti suggeriti, così che il paziente non si blocchi se gli manca qualcosa.
            5. Nessun tabù sgradevole (no pasta con il pollo) e nessun conteggio o paranoia calorica.

            FORMATO DI RISPOSTA:
            TITOLO: [Nome invitante del piatto]
            ⏱️ [Tempo] | 🍳 Strumento: [Solo uno tra {', '.join(metodi_scelti)}]
            💡 [1 frase breve su come questa combinazione appaga la voglia del giorno]

            🛒 **Ingredienti del pasto:**
            - [Carboidrati, Proteine, Verdure dosati/tagliati]
            - [Spezie ed erbette consigliate per dare sapore]

            👨‍🍳 **Passaggi Facili:**
            1. [Passo 1: taglio/aromatizzazione]
            2. [Passo 2: cottura con lo strumento ammesso]
            3. [Passo 3: mantecatura, emulsione o tocco finale]

            🌿 **Spezie, Erbette e Sostituzioni Furbe:**
            - *[Erba/Spezia consigliata]:* se non ce l'hai, usa [Alternativa comune]
            - *[Elemento cremoso/legante]:* se non ce l'hai, usa [Alternativa pratica]
            """

            model = genai.GenerativeModel("gemini-1.5-flash")
            risposta = model.generate_content(prompt_ricetta).text

            # Separazione del titolo per il prompt fotografico
            linee = risposta.split("\n")
            titoli = [l.replace("TITOLO:", "").strip() for l in linee if "TITOLO:" in l]
            nome_piatto = titoli[0] if titoli else "Piatto Sano e Gustoso"
            testo_pulito = "\n".join([l for l in linee if "TITOLO:" not in l])

            # Creazione immagine coordinata
            img_prompt = f"Professional food photography of {nome_piatto}, beautifully served in a ceramic bowl, fresh herbs garnish, natural sunlight, restaurant quality, appetizing top view."
            img_res = client_img.images.generate(
                model="dall-e-3",
                prompt=img_prompt,
                size="1024x1024",
                n=1
            )

            # Visualizzazione a schermo
            st.divider()
            st.image(img_res.data[0].url, caption=nome_piatto, use_container_width=True)
            st.markdown(testo_pulito)
