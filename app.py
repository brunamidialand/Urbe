import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# Configuração da página
st.set_page_config(page_title="Normas Curitiba", layout="wide")
st.title("🔍 Normas Curitiba - Arquitetura, Urbanismo & OOH")
st.caption("Descreva seu projeto e receba trechos das normas aplicáveis")

@st.cache_data
def carregar_normas():
    return pd.read_csv('leis.csv')

# Carrega normas
normas_df = carregar_normas()

# Interface
col1, col2 = st.columns([3,1])

with col1:
    projeto = st.text_area("Descreva seu projeto:", 
                          placeholder="Ex: prédio 5 andares com painel OOH 15m² na Av. Batel ZR-3",
                          height=120)

with col2:
    st.markdown("### Filtros")
    tipo_filtro = st.multiselect("Tipo:", 
                                ["Todas", "Decreto", "Lei"], 
                                default="Todas")
    relevancia = st.selectbox("Relevância:", ["Todas", "Alta", "Média"])

if st.button("🚀 Consultar Normas", type="primary") and projeto:
    with st.spinner("Analisando projeto e buscando normas..."):
        
        # Keywords do projeto
        keywords = re.findall(r'\b(painel|OOH|publicidade|fachada|recuo|andares|metros|ZR\d|zoneamento|lote|construção|reforma)\b', 
                             projeto.lower())
        
        resultados = []
        
        # Filtra normas relevantes
        normas_filtradas = normas_df[
            (normas_df['relevancia'] == relevancia) | (relevancia == "Todas")
        ].copy()
        
        for idx, norma in normas_filtradas.iterrows():
            score = 0
            
            # Pontuação por keywords
            if any(kw in projeto.lower() for kw in ['painel', 'OOH', 'publicidade']):
                if 'publicidade' in norma['nome'].lower() or 'posturas' in norma['nome'].lower():
                    score += 3
            if any(kw in projeto.lower() for kw in ['recuo', 'zoneamento', 'ZR']):
                if 'zoneamento' in norma['nome'].lower():
                    score += 3
            if any(kw in projeto.lower() for kw in ['construção', 'edificação', 'reforma']):
                if 'edificações' in norma['nome'].lower():
                    score += 3
                
            if score > 0:
                try:
                    # Busca real na página da norma
                    resp = requests.get(norma['url'], timeout=10)
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    texto = soup.get_text()
                    
                    # Extrai trechos relevantes
                    trecho = extrair_trecho_relevante(texto, projeto, norma['nome'])
                    
                    resultados.append({
                        'norma': norma['nome'],
                        'numero': norma['numero'],
                        'url': norma['url'],
                        'score': score,
                        'trecho': trecho
                    })
                except:
                    # Fallback com descrição genérica
                    resultados.append({
                        'norma': norma['nome'],
                        'numero': norma['numero'],
                        'url': norma['url'],
                        'score': score,
                        'trecho': f"Norma aplicável para {norma['nome'].lower()}. Consulte a legislação completa."
                    })
        
        # Ordena por relevância
        resultados = sorted(resultados, key=lambda x: x['score'], reverse=True)[:5]
        
        if resultados:
            st.success(f"✅ Encontradas {len(resultados)} normas relevantes!")
            
            for i, res in enumerate(resultados, 1):
                with st.expander(f"📋 {res['norma']} ({res['numero']}) - Score: {res['score']}/3"):
                    st.markdown(f"**Trecho relevante:**")
                    st.write(res['trecho'])
                    st.markdown(f"**[Leia norma completa]({res['url']})**")
                    st.caption(f"Fonte oficial: Prefeitura de Curitiba")
        else:
            st.warning("⚠️ Nenhuma norma com alta correspondência. Tente descrever com mais detalhes (recuos, OOH, zoneamento, etc.)")

def extrair_trecho_relevante(texto, projeto, norma_nome):
    """Extrai trecho mais relevante do texto da norma"""
    frases = re.split(r'[.!?]+', texto)
    
    pontuacoes = {}
    for frase in frases:
        frase = frase.strip().lower()
        score = 0
        
        if any(palavra in frase for palavra in projeto.lower().split()):
            score += 2
        if 'edifica' in norma_nome.lower() and any(termo in frase for termo in ['recuo', 'frente', 'lateral']):
            score += 1
        if 'publicidade' in norma_nome.lower() and any(termo in frase for termo in ['placa', 'fachada', 'm²']):
            score += 1
            
        if score > 0:
            pontuacoes[frase[:200]] = score
    
    if pontuacoes:
        melhor_frase = max(pontuacoes, key=pontuacoes.get)
        return melhor_frase.capitalize() + "..."
    
    return "Consulte a norma completa para detalhes específicos do seu projeto."

# Sidebar com informações
with st.sidebar:
    st.markdown("### 📖 Normas Incluídas")
    st.dataframe(normas_df[['nome', 'numero', 'relevancia']], use_container_width=True)
    
    st.markdown("---")
    st.markdown("**💡 Dica:** Use termos específicos como 'painel OOH 10m²', 'recuo frontal ZR-3', 'edificação 5 pavimentos'")
    
    st.markdown("**[Portal Urbanismo Curitiba](https://urbanismo.curitiba.pr.gov.br)**")

# Rodapé
st.markdown("---")
st.markdown("*App desenvolvido para consulta de normas de Curitiba/PR. Sempre valide com profissional habilitado.*")
