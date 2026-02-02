import streamlit as st
import pandas as pd

st.set_page_config(page_title="URBE - Analista Inteligente", page_icon="🏙️")

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("leis.csv", dtype=str, keep_default_na=False)
        return df
    except:
        return pd.DataFrame()

# DICIONÁRIO DE SINÔNIMOS (Expanda conforme a necessidade da equipe)
# Isso faz o app entender que 'casa' exige ver 'recuo', 'afastamento', etc.
SINONIMOS = {
    "casa": ["recuo", "afastamento", "altura", "taxa de ocupação", "zoneamento", "residencial"],
    "residência": ["recuo", "afastamento", "altura", "zoneamento"],
    "painel": ["led", "publicidade", "luminosidade", "fachada"],
    "outdoor": ["led", "publicidade", "propaganda"],
    "comércio": ["vagas", "acessibilidade", "calçada", "alvará"],
    "prédio": ["coeficiente", "altura", "rebaixo", "incêndio"]
}

df = carregar_dados()

st.title("🏙️ URBE")
st.caption("Analista de Viabilidade Técnica - Curitiba")

if df.empty:
    st.warning("Configure seu arquivo leis.csv para começar.")
else:
    aba1, aba2 = st.tabs(["🔍 Consulta Direta", "🤖 Analista de Projeto"])

    with aba1:
        busca = st.text_input("Busca rápida por termo:")
        if busca:
            resultado = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)]
            for i, linha in resultado.iterrows():
                with st.expander(f"📌 {linha.get('Artigo', 'S/A')}"):
                    st.success(linha.get('Descricao', ''))
                    st.caption(f"Fonte: {linha.get('Fonte', '')}")

    with aba2:
        st.subheader("O que você está projetando?")
        desc = st.text_area("Ex: Projeto de uma casa de dois pavimentos no bairro Batel.")
        
        if st.button("Analisar Requisitos Legais"):
            if desc:
                texto_usuario = desc.lower()
                termos_para_buscar = set()
                
                # 1. Adiciona termos que o usuário digitou
                palavras_digitadas = texto_usuario.split()
                for p in palavras_digitadas:
                    termos_para_buscar.add(p)
                
                # 2. Adiciona sinônimos técnicos baseados no que o usuário digitou
                for chave, lista_sinonimos in SINONIMOS.items():
                    if chave in texto_usuario:
                        for s in lista_sinonimos:
                            termos_para_buscar.add(s)
                
                st.write("### 📋 Itens obrigatórios para conferir:")
                encontrado = False
                
                # 3. Varre o banco de dados buscando esses termos
                for i, linha in df.iterrows():
                    conteudo_lei = (linha.get('Categoria', '') + " " + linha.get('Descricao', '')).lower()
                    
                    if any(termo in conteudo_lei for termo in termos_para_buscar):
                        with st.chat_message("assistant"):
                            st.write(f"**{linha.get('Categoria')}** ({linha.get('Artigo')})")
                            st.info(linha.get('Descricao'))
                            if 'Fonte' in linha: st.caption(f"⚖️ {linha['Fonte']}")
                        encontrado = True
                
                if not encontrado:
                    st.warning("Não encontrei leis específicas. Tente detalhar mais (ex: mencionar se tem muro, calçada ou letreiro).")
