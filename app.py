import streamlit as st
import pandas as pd

# Configuração com layout expandido para facilitar a leitura técnica
st.set_page_config(page_title="URBE", page_icon="🏙️", layout="wide")

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("leis.csv", dtype=str, keep_default_na=False)
        return df
    except:
        return pd.DataFrame()

df = carregar_dados()

# Interface Profissional
st.title("🏙️ URBE - Diagnóstico Técnico")
st.markdown("### Análise de Conformidade: Arquitetura, Urbanismo e Publicidade")
st.divider()

if df.empty:
    st.error("⚠️ Erro: Banco de dados (leis.csv) não localizado.")
else:
    # Área de entrada de dados
    st.subheader("Descrição do Projeto")
    projeto = st.text_area(
        "Insira os detalhes do projeto para identificação de normas:", 
        placeholder="Ex: Instalação de painel de LED em fachada comercial no bairro Centro...",
        height=150
    )

    if st.button("🔍 ANALISAR NORMAS E ARTIGOS"):
        if projeto:
            p_low = projeto.lower()
            encontrou = False
            
            st.markdown("---")
            st.subheader("📋 Artigos e Dispositivos Legais Identificados")
            
            for _, row in df.iterrows():
                # Busca inteligente cruzando Categoria e Descrição
                if any(termo in p_low for termo in row['Categoria'].lower().split()) or \
                   any(termo in p_low for termo in row['Descricao'].lower().split()):
                    
                    # Box visual para cada item da lei
                    with st.container():
                        c1, c2 = st.columns([1, 4])
                        
                        with c1:
                            st.info(f"**{row['Artigo']}**")
                            st.caption(f"Tópico: {row['Categoria']}")
                        
                        with c2:
                            # O Trecho exato da lei que você solicitou
                            st.markdown(f"**Dispositivo:** {row['Descricao']}")
                            st.caption(f"📍 Fonte específica: {row['Fonte']}")
                            
                            if row['Link']:
                                st.link_button("Acessar Texto Integral", row['Link'])
                        
                        st.divider()
                        encontrou = True
            
            if not encontrou:
                st.warning("Nenhum artigo correspondente foi encontrado para a descrição fornecida.")
        else:
            st.error("Por favor, descreva o projeto antes de analisar.")
