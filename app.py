import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="URBE - Inteligência Técnica", page_icon="🏙️", layout="wide")

@st.cache_data
def carregar_dados():
    try:
        # Lê o CSV garantindo que linhas com vírgulas extras sejam tratadas
        df = pd.read_csv("leis.csv", on_bad_lines='skip', engine='python', dtype=str).fillna("")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o cérebro de dados: {e}")
        return pd.DataFrame()

df = carregar_dados()

st.title("🏙️ URBE - Analista de Projetos Complexos")
st.markdown("### Diagnóstico Integral de Normas e Dispositivos Legais")
st.divider()

if df.empty:
    st.error("⚠️ Banco de dados 'leis.csv' não encontrado ou mal formatado.")
else:
    projeto = st.text_area("Descreva o projeto completo (ex: estrutura, uso, manutenção, localização):", 
                          placeholder="Detalhe os sistemas envolvidos...", height=200)

    if st.button("🔍 GERAR DIAGNÓSTICO INTEGRAL"):
        if projeto:
            # Limpeza e extração de termos técnicos (palavras com mais de 3 letras)
            termos_projeto = re.findall(r'\w{4,}', projeto.lower())
            
            encontrou = False
            st.markdown("---")
            st.subheader("📋 Relatório de Conformidade Técnica")
            
            # O motor de busca agora analisa a linha da lei como um todo
            for _, row in df.iterrows():
                universo_lei = (row['Categoria'] + " " + row['Artigo'] + " " + row['Descricao']).lower()
                
                # Sistema de Pontuação: Verifica a densidade de termos técnicos no projeto
                matches = [t for t in termos_projeto if t in universo_lei]
                
                if matches:
                    with st.container():
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            st.info(f"**{row['Artigo']}**")
                            st.caption(f"Categoria: {row['Categoria']}")
                        with col2:
                            # Exibe a descrição detalhada (fundamental para projetos complexos)
                            st.markdown(f"**Dispositivo Técnico:** {row['Descricao']}")
                            st.caption(f"📍 Fonte: {row['Fonte']}")
                            if row['Link']:
                                st.link_button("Texto Integral da Lei", row['Link'])
                        st.divider()
                        encontrou = True
            
            if not encontrou:
                st.warning("A descrição não acionou nenhuma norma conhecida. Detalhe os materiais ou a finalidade do projeto.")
