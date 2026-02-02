import streamlit as st
import pandas as pd

st.set_page_config(page_title="URBE - Analista Técnico", page_icon="🏙️")

@st.cache_data
def carregar_dados():
    try:
        # keep_default_na=False evita erros com campos vazios
        df = pd.read_csv("leis.csv", dtype=str, keep_default_na=False)
        return df
    except:
        return pd.DataFrame(columns=["Categoria", "Artigo", "Descricao", "Fonte", "Link"])

df = carregar_dados()

st.title("🏙️ URBE")
st.caption("Foco na regra técnica com fonte para conferência")

aba1, aba2 = st.tabs(["🔍 Busca Rápida", "🤖 Analista de Viabilidade"])

with aba1:
    busca = st.text_input("O que deseja consultar? (ex: Brilho, Calçada)")
    if busca:
        resultado = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)]
        for i, linha in resultado.iterrows():
            with st.expander(f"📌 {linha['Artigo']}"):
                st.warning(f"**Regra Direta:** {linha['Descricao']}")
                st.code(f"Fonte: {linha['Fonte']}", language=None)
                if linha['Link']:
                    st.link_button("Verificar na Lei Integral", linha['Link'])

with aba2:
    st.subheader("Análise de Texto do Projeto")
    desc = st.text_area("Descreva o que será feito no projeto:")
    
    if st.button("Identificar Regras e Fontes"):
        if desc:
            palavras_chave = desc.lower()
            encontradas = False
            
            for i, linha in df.iterrows():
                # Verifica se termos da descrição ou categoria aparecem no texto do usuário
                if any(p in palavras_chave for p in linha['Categoria'].lower().split()) or \
                   any(p in palavras_chave for p in linha['Descricao'].lower().split()):
                    
                    with st.chat_message("assistant"):
                        st.write(f"### Item identificado: {linha['Categoria']}")
                        st.success(f"**O que deve ser feito:** {linha['Descricao']}")
                        # Exibe a fonte de forma clara para conferência
                        st.info(f"⚖️ **Fonte para conferir:** {linha['Fonte']}")
                        if linha['Link']:
                            st.caption(f"[Abrir documento oficial]({linha['Link']})")
                    encontradas = True
            
            if not encontradas:
                st.info("Nenhum termo técnico identificado. Tente: LED, Recuo, Altura, Calçada, etc.")
