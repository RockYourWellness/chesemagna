import streamlit as st
import google.generativeai as genai

st.title("Verifica Modelli Abilitati")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Chiede a Google quali modelli sono utilizzabili con la tua chiave
    modelli_attivi = [
        m.name for m in genai.list_models() 
        if 'generateContent' in m.supported_generation_methods
    ]
    
    if modelli_attivi:
        st.success("Connessione riuscita! Ecco i modelli che puoi usare subito:")
        for m in modelli_attivi:
            st.write(f"- `{m}`")
    else:
        st.warning("La chiave è valida, ma non ha ancora modelli di testo abilitati.")
except Exception as e:
    st.error(f"Errore: {e}")
