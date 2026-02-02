import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="URBE - Inteligência Técnica", page_icon="🏙️", layout="wide")

@st.cache_data
def carregar_dados():
    try:
        # Pula linhas com erro e garante leitura de texto puro
        df = pd.read_csv("leis.csv", on_bad_lines='skip', engine='python', dtype=str).fillna("")
        return df
    except Exception as e:
        st.error(f"Erro ao ler banco de dados: {e}")
        return pd.DataFrame()

def calcular_relevancia(texto_usuario, linha_lei):
    """Calcula quantos termos do projeto batem com a lei, dando pesos diferentes."""
    score = 0
    # Limpa o texto e separa em palavras significativas (mais de 3 letras)
    termos_projeto = re.findall(r'\w{4,}', texto_usuario.lower())
    conteudo_lei = " ".join(linha_lei.values).lower()
    
    for termo in termos_projeto:
        # Se a palavra exata está na lei
        if termo in conteudo_lei:
            score += 2
        # Se parte da palavra está na lei (ex: 'manuten' em 'manutenção')
        elif termo[:5] in conteudo_lei:
            score += 1
            
    return score

df = carregar_dados()

st.title("🏙️ URBE - Diagnóstico de Projetos Complexos")
st.markdown("---")

if df.empty:
    st.error("Banco de dados 'leis.csv' não encontrado ou vazio.")
else:
    projeto = st.text_area("Descreva seu projeto com todos os detalhes técnicos:", 
                          placeholder="Ex: Instalação de painéis eletrônicos de grande porte em estrutura metálica sobreposta à fachada com acesso para manutenção e aterramento...",
                          height=200)

    if st.button("🔍 GERAR ANÁLISE TÉCNICA"):
        if projeto:
            # Aplica o cálculo de relevância em cada linha
            df['relevancia'] = df.apply(lambda row: calcular_relevancia(projeto, row), axis=1)
            
            # Filtra apenas o que tem alguma ligação e ordena pelo mais relevante
            resultados = df[df['relevancia'] > 0].sort_values(by='relevancia', ascending=False)
            
            if not resultados.empty:
                st.success(f"Encontramos {len(resultados)} dispositivos legais relacionados ao seu projeto.")
                
                for _, res in resultados.iterrows():
                    with st.expander(f"📍 {res['Artigo']} - {res['Categoria']} (Relevância: {res['relevancia']})"):
                        st.markdown(f"**TRECHO DA LEI:** {res['Descricao']}")
                        st.caption(f"⚖️ Fonte: {res['Fonte']}")
                        if res['Link']:
                            st.link_button("Abrir Documento Oficial", res['Link'])
            else:
                st.warning("Nenhum detalhe técnico correspondente foi encontrado. Tente detalhar mais os materiais ou tipos de estrutura.")
        else:
            st.error("Por favor, descreva o projeto para análise.")
