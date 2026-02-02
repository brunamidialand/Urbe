import streamlit as st
import pandas as pd

st.set_page_config(page_title="URBE - Analista Técnico", page_icon="🏙️")

@st.cache_data
def carregar_dados():
    try:
        # keep_default_na=False evita que campos vazios virem erros de leitura
        df = pd.read_csv("leis.csv", dtype=str, keep_default_na=False)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return pd.DataFrame()

df = carregar_dados()

st.title("🏙️ URBE")
st.caption("Foco na regra técnica e fonte oficial")

if df.empty:
    st.warning("Aguardando carregamento do arquivo leis.csv...")
else:
    aba1, aba2 = st.tabs(["🔍 Busca Rápida", "🤖 Analista de Projeto"])

    with aba1:
        busca = st.text_input("O que deseja consultar? (ex: LED, Recuo)")
        if busca:
            # Busca em todas as colunas existentes
            resultado = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)]
            for i, linha in resultado.iterrows():
                # O comando .get('Coluna', 'Padrao') evita o KeyError
                with st.expander(f"📌 {linha.get('Artigo', 'S/A')}"):
                    st.warning(f"**Regra:** {linha.get('Descricao', 'Sem descrição')}")
                    if 'Fonte' in linha and linha['Fonte']:
                        st.code(f"Fonte: {linha['Fonte']}", language=None)
                    if 'Link' in linha and linha['Link']:
                        st.link_button("Abrir Lei", linha['Link'])

    with aba2:
        st.subheader("Análise do Projeto")
        desc = st.text_area("Descreva o projeto (termos técnicos):")
        
        if st.button("Identificar Regras"):
            if desc:
                palavras_chave = desc.lower()
                encontrado = False
                for i, linha in df.iterrows():
                    # Verifica se o termo está na categoria ou descrição
                    cat = str(linha.get('Categoria', '')).lower()
                    if cat and cat in palavras_chave:
                        with st.chat_message("assistant"):
                            st.success(f"**Regra:** {linha.get('Descricao', '')}")
                            if 'Fonte' in linha and linha['Fonte']:
                                st.info(f"⚖️ Fonte oficial: {linha['Fonte']}")
                        encontrado = True
                if not encontrado:
                    st.info("Nenhum termo técnico identificado. Tente: LED, Recuo, Fachada.")
