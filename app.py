import streamlit as st
import pandas as pd

# 1. Configuração Visual do App (O nome que aparece no navegador)
st.set_page_config(
    page_title="URBE - Legislação Curitiba", 
    page_icon="🏙️",
    layout="centered"
)

# Estilo customizado para parecer um App profissional
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .st-emotion-cache-1cv0aru {
        border-radius: 15px;
        border: 1px solid #ddd;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_index=True)

# 2. Título e Cabeçalho
st.title("🏙️ URBE")
st.caption("Consulta Rápida de Legislação de Arquitetura e Painéis de LED (Curitiba)")

# 3. Função para carregar os dados do arquivo leis.csv
@st.cache_data
def load_data():
    try:
        # Carrega o arquivo e remove espaços extras
        data = pd.read_csv("leis.csv")
        return data
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo de leis: {e}")
        return pd.DataFrame(columns=["Categoria", "Artigo", "Descricao", "Link"])

df = load_data()

# 4. Campo de Busca
st.subheader("O que você deseja consultar?")
search_query = st.text_input("", placeholder="Ex: LED, Recuo, Altura, Fachada...")

# 5. Filtro por Categoria (Opcional)
categorias = ["Todas"] + sorted(df["Categoria"].unique().tolist())
filtro_cat = st.selectbox("Filtrar por Tema:", categorias)

# 6. Lógica de Pesquisa
filtered_df = df.copy()

if search_query:
    filtered_df = filtered_df[
        filtered_df['Descricao'].str.contains(search_query, case=False, na=False) |
        filtered_df['Artigo'].str.contains(search_query, case=False, na=False) |
        filtered_df['Categoria'].str.contains(search_query, case=False, na=False)
    ]

if filtro_cat != "Todas":
    filtered_df = filtered_df[filtered_df['Categoria'] == filtro_cat]

# 7. Exibição dos Resultados
st.write(f"---")
st.write(f"Encontrados **{len(filtered_df)}** itens.")

if len(filtered_df) > 0:
    for index, row in filtered_df.iterrows():
        with st.expander(f"📍 {row['Artigo']} ({row['Categoria']})"):
            st.info(row['Descricao'])
            if 'Link' in row and str(row['Link']) != 'nan':
                st.link_button("Ver Lei Completa", row['Link'])
else:
    st.warning("Nenhum resultado encontrado. Tente outra palavra-chave.")

# 8. Rodapé
st.markdown("---")
st.markdown("⚠️ *Sempre confirme os dados na Guia Amarela da Prefeitura de Curitiba.*")
