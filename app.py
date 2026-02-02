import streamlit as st
import pandas as pd

st.set_page_config(page_title="URBE - Analista", page_icon="🏙️")

# --- FUNÇÃO DE DADOS ---
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("leis.csv", dtype=str).fillna("")
        return df
    except:
        return pd.DataFrame(columns=["Categoria", "Artigo", "Descricao", "Link"])

df = carregar_dados()

# --- INTERFACE ---
st.title("🏙️ URBE")
aba1, aba2 = st.tabs(["🔍 Consulta Direta", "🤖 Analista de Projeto"])

# ABA 1: BUSCA MANUAL
with aba1:
    busca = st.text_input("Buscar por termo (ex: LED, Recuo):")
    if busca:
        resultado = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)]
        for i, linha in resultado.iterrows():
            with st.expander(f"📍 {linha['Artigo']}"):
                st.info(linha['Descricao'])

# ABA 2: ANALISTA AUTOMÁTICO (SEM COTA/GRATUITO)
with aba2:
    st.subheader("Descreva o projeto abaixo:")
    descricao_projeto = st.text_area("Ex: Vou instalar um painel de LED na fachada com 20m2 e preciso saber sobre o brilho e recuo.")
    
    if st.button("Analisar Viabilidade"):
        if descricao_projeto:
            st.write("### 📋 Leis que você deve observar:")
            
            # Lógica de identificação de palavras-chave
            palavras = descricao_projeto.lower()
            leis_encontradas = []
            
            for i, linha in df.iterrows():
                # Se a descrição do projeto cita termos da categoria ou da descrição da lei
                if linha['Categoria'].lower() in palavras or any(termo in palavras for termo in linha['Descricao'].lower().split()):
                    leis_encontradas.append(linha)
            
            if leis_encontradas:
                for lei in leis_encontradas:
                    with st.chat_message("assistant"):
                        st.write(f"**Atenção ao {lei['Artigo']}** ({lei['Categoria']})")
                        st.write(lei['Descricao'])
                        if lei['Link']:
                            st.caption(f"[Clique aqui para ler a lei completa]({lei['Link']})")
            else:
                st.warning("Nenhum termo técnico específico foi identificado. Tente usar palavras como: LED, Recuo, Altura, Calçada, etc.")
        else:
            st.error("Por favor, descreva o projeto primeiro.")
