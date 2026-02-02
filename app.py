import streamlit as st
import pandas as pd

st.set_page_config(page_title="URBE - Diagnóstico Técnico", page_icon="🏙️", layout="wide")

@st.cache_data
def carregar_dados():
    try:
        # Força a leitura correta do CSV
        df = pd.read_csv("leis.csv", sep=',', dtype=str, keep_default_na=False)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar banco de dados: {e}")
        return pd.DataFrame()

df = carregar_dados()

st.title("🏙️ URBE - Diagnóstico Técnico")
st.markdown("### Analista Inteligente de Normas e Artigos de Curitiba")
st.divider()

if df.empty:
    st.warning("⚠️ O banco de dados está vazio. Verifique o arquivo leis.csv no GitHub.")
else:
    projeto = st.text_area("Descreva o seu projeto:", placeholder="Ex: Painel de LED em fachada comercial com rampa de acesso...", height=150)

    if st.button("🔍 ANALISAR TUDO"):
        if projeto:
            # Quebra a descrição em palavras e limpa o texto
            termos = projeto.lower().replace(".", " ").replace(",", " ").split()
            # Filtra palavras pequenas para focar no que importa
            filtros = [t for t in termos if len(t) > 3]
            
            encontrou = False
            st.markdown("---")
            
            # Procura cada linha do banco de dados
            for _, row in df.iterrows():
                # Junta todo o texto da lei para facilitar a busca
                conteudo_completo = (row['Categoria'] + " " + row['Artigo'] + " " + row['Descricao']).lower()
                
                # Se qualquer palavra da pesquisa bater com a lei, mostra o resultado
                if any(f in conteudo_completo for f in filtros):
                    with st.container():
                        c1, c2 = st.columns([1, 4])
                        with c1:
                            st.info(f"**{row['Artigo']}**")
                            st.caption(f"Área: {row['Categoria']}")
                        with c2:
                            st.markdown(f"**Regra:** {row['Descricao']}")
                            st.caption(f"📍 Fonte: {row['Fonte']}")
                            if row['Link']:
                                st.link_button("Ver Documento Oficial", row['Link'])
                        st.divider()
                        encontrou = True
            
            if not encontrou:
                st.warning("Nenhum detalhe específico encontrado. Tente termos como: LED, Rampa, Recuo, Vaga, Incêndio.")
