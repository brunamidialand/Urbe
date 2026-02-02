import streamlit as st
import pandas as pd

st.set_page_config(page_title="URBE - Inteligência Urbana", page_icon="🏙️", layout="wide")

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("leis.csv", dtype=str, keep_default_na=False)
        return df
    except:
        return pd.DataFrame()

# DICIONÁRIO ESTRUTURAL (O "Cérebro" do App)
# Relaciona grandes áreas da arquitetura a termos técnicos que estarão no seu CSV
MAPEAMENTO = {
    "habitação": ["residencial", "casa", "sobrado", "apartamento", "unifamiliar", "multifamiliar", "loteamento"],
    "comercial": ["loja", "comércio", "serviço", "alvará", "vagas", "estacionamento", "restaurante"],
    "mídia": ["painel", "led", "outdoor", "publicidade", "letreiro", "fachada", "luminosidade", "propaganda"],
    "estrutura": ["recuo", "afastamento", "altura", "pavimento", "saliência", "beiral", "muro", "divisa"],
    "acessibilidade": ["rampa", "calçada", "passeio", "rebaixo", "piso tátil", "guarda-corpo", "sanitário"],
    "sustentabilidade": ["permeabilidade", "árvore", "vegetação", "telhado verde", "drenagem"]
}

df = carregar_dados()

st.title("🏙️ URBE: Sistema Unificado de Leis")
st.markdown("---")

if df.empty:
    st.error("⚠️ Base de dados (leis.csv) não encontrada. Verifique seu GitHub.")
else:
    # Barra lateral com estatísticas para a equipe
    st.sidebar.header("Status do Banco")
    st.sidebar.write(f"📚 {len(df)} regras cadastradas")
    
    aba1, aba2 = st.tabs(["🔍 Consulta Rápida", "🧠 Analista de Viabilidade"])

    with aba1:
        termo = st.text_input("Busca global (Ex: 'Art. 30', 'LED', 'Calçadas')")
        if termo:
            resultado = df[df.apply(lambda row: row.astype(str).str.contains(termo, case=False).any(), axis=1)]
            for i, row in resultado.iterrows():
                with st.expander(f"📌 {row['Artigo']} - {row['Categoria']}"):
                    st.warning(row['Descricao'])
                    st.caption(f"📍 Fonte: {row['Fonte']}")
                    if row['Link']: st.link_button("Documento Oficial", row['Link'])

    with aba2:
        st.subheader("Diagnóstico do Projeto")
        texto_projeto = st.text_area("Descreva os detalhes do projeto aqui:", 
                                     placeholder="Ex: Instalação de painel digital em fachada de prédio comercial com recuo de 5m...",
                                     height=150)
        
        if st.button("Executar Análise Completa"):
            if texto_projeto:
                projeto_lower = texto_projeto.lower()
                # Cria uma lista de termos para buscar no CSV
                termos_finais = set(projeto_lower.split())
                
                # Adiciona termos técnicos baseados no mapeamento
                for categoria, palavras in MAPEAMENTO.items():
                    if any(p in projeto_lower for p in palavras) or categoria in projeto_lower:
                        termos_finais.update(palavras)

                st.write("### 🛠️ Parâmetros Técnicos Detectados:")
                achou = False
                
                # Busca profunda no CSV
                for i, row in df.iterrows():
                    alvo = (row['Categoria'] + " " + row['Descricao'] + " " + row['Artigo']).lower()
                    if any(t in alvo for t in termos_finais if len(t) > 3):
                        with st.container():
                            st.markdown(f"#### {row['Categoria']} | {row['Artigo']}")
                            st.info(row['Descricao'])
                            st.caption(f"⚖️ **Referência:** {row['Fonte']}")
                            if row['Link']: st.caption(f"[Link para conferência]({row['Link']})")
                            st.markdown("---")
                            achou = True
                
                if not achou:
                    st.warning("Nenhuma norma específica encontrada. Tente descrever com mais termos técnicos.")
