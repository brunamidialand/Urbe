import streamlit as st
import pandas as pd

st.title("🏛️ Normas Curitiba - TESTE")

# Testa se leis.csv existe
try:
    df = pd.read_csv('leis.csv')
    st.success(f"✅ {len(df)} normas carregadas!")
    st.write(df.head())
except:
    st.error("❌ leis.csv não encontrado!")
    st.stop()

projeto = st.text_area("Descreva seu projeto:")
if st.button("Testar") and projeto:
    st.write("✅ Funcionando! App OK.")
