import streamlit as st
import pandas as pd

# Configuração simples
st.set_page_config(page_title="URBE", page_icon="🏙️")

st.title("🏙️ URBE")
st.write("Consulta de Legislação Urbana - Curitiba")

# Função para carregar os dados com segurança
@st.cache_data
def carregar_dados():
    try:
        # Lê o CSV e garante que tudo seja tratado como texto (string)
        df = pd.read_csv("leis.csv", dtype=str).fillna("")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar leis.csv: {e}")
        return pd.DataFrame(columns=["Categoria", "Artigo", "Descricao", "Link"])

df = carregar_dados()

# Barra de pesquisa
busca = st.text_input("Digite o que procura (ex: LED, Recuo, Altura):")

if busca:
    # Filtra em todas as colunas
    resultado = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)]
else:
    resultado = df

# Exibição dos resultados
st.write(f"Mostrando {len(resultado)} resultados:")

for i, linha in resultado.iterrows():
    with st.expander(f"📍 {linha['Artigo']} - {linha['Categoria']}"):
        st.info(linha['Descricao'])
        if linha['Link'] and "http" in linha['Link']:
            st.link_button("Abrir Lei Completa", linha['Link'])
