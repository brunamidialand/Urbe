import streamlit as st
import pandas as pd

st.set_page_config(page_title="URBE - Analista de Recortes", page_icon="🏙️", layout="wide")

@st.cache_data
def carregar_dados():
    try:
        # Carrega o CSV garantindo que links e descrições sejam textos
        df = pd.read_csv("leis.csv", dtype=str, keep_default_na=False)
        return df
    except:
        return pd.DataFrame()

df = carregar_dados()

st.title("🏙️ URBE: Inteligência Legislativa")
st.markdown("---")

if df.empty:
    st.error("⚠️ Base de dados não encontrada. Certifique-se de que o arquivo 'leis.csv' está no seu GitHub.")
else:
    tab1, tab2 = st.tabs(["🔍 Consulta por Termo", "🤖 Analista de Projetos"])

    with tab1:
        busca = st.text_input("Digite um termo ou número de artigo:")
        if busca:
            # Filtro que busca em todas as colunas
            mask = df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)
            res = df[mask]
            for _, row in res.iterrows():
                with st.expander(f"📌 {row['Artigo']} | {row['Categoria']}"):
                    st.info(f"**Trecho da Lei:** {row['Descricao']}")
                    st.caption(f"⚖️ Fonte: {row['Fonte']}")
                    if row['Link']: st.link_button("Conferir Lei Completa", row['Link'])

    with tab2:
        st.subheader("Análise Contextual de Projeto")
        contexto = st.text_area("Descreva o projeto para extrairmos os trechos das leis:", 
                                placeholder="Ex: Painel de LED em fachada comercial com avanço sobre o passeio...",
                                height=150)
        
        if st.button("Analisar e Extrair Trechos"):
            if contexto:
                ctx_low = contexto.lower()
                achou_algo = False
                
                st.write("### 📜 Recortes Legais Aplicáveis:")
                
                for _, row in df.iterrows():
                    # O código cruza as palavras do seu projeto com as tags da Categoria e Descrição
                    if any(palavra in ctx_low for palavra in row['Categoria'].lower().split()) or \
                       any(palavra in ctx_low for palavra in row['Descricao'].lower().split()):
                        
                        with st.chat_message("assistant"):
                            st.markdown(f"#### {row['Categoria']} - {row['Artigo']}")
                            # Exibe o recorte técnico da lei
                            st.success(f"**O que diz a norma:** {row['Descricao']}")
                            st.markdown(f"*Referência específica: {row['Fonte']}*")
                            if row['Link']:
                                st.link_button(f"🔗 Abrir Fonte Oficial ({row['Artigo']})", row['Link'])
                        achou_algo = True
                        st.markdown("---")
                
                if not achou_algo:
                    st.warning("Nenhum trecho específico foi encontrado para os termos digitados. Tente detalhar mais os elementos do projeto.")
