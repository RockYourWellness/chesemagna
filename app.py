import streamlit as st
import google.generativeai as genai

st.title("Test Connessione")

if "GEMINI_API_KEY" not in st.secrets:
    st.error("ERRORE: Non hai ancora salvato la voce GEMINI_API_KEY nei Secrets di Streamlit!")
else:
    st.write("Chiave trovata nei Secrets. Provo a contattare Google...")
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        testo = model.generate_content("Rispondi solo con: OK FUNZIONA").text
        st.success(f"Risultato: {testo}")
    except Exception as e:
        st.error(f"Dettaglio errore da Google: {e}")
