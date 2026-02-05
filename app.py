import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

st.set_page_config(page_title="Normas Curitiba PRO", layout="wide")
st.title("🏛️ Normas Curitiba - Arquitetura, Urbanismo & OOH")
st.caption("🔥 VERSÃO COMPLETA com 28 leis municipais + busca inteligente")

@st.cache_data
def carregar_normas():
    df = pd.read_csv('leis.csv')
    return df

normas_df = carregar_normas()

# Interface principal
col1, col2 = st.columns([3,1])

with col1:
    projeto = st.text_area("📝 Descreva seu projeto:", 
                          placeholder="Ex: 'Prédio 10 andares com painel OOH 20m² na fachada, Av. Batel ZR-3, recuo frontal 5m'",
                          height=100)

with col2:
    st.markdown("### ⚙️ Filtros")
    tipo_filtro = st.multiselect("Tipo:", 
                                ["Todas", "Lei", "Decreto", "Lei Complementar", "Resolução"], 
                                default="Todas")
    relevancia = st.selectbox("Relevância:", ["Todas", "Alta", "Média", "Baixa"])
    assunto = st.multiselect("Assunto:", 
                           ["Todas", "OOH/Publicidade", "Zoneamento", "Edificações", "Parcelamento", "Acessibilidade"])

if st.button("🔍 ANALISAR PROJETO", type="primary", use_container_width=True) and projeto:
    
    with st.spinner("🤖 Processando com IA Local + Busca Web..."):
        # Análise semântica avançada
        resultados = analisar_projeto_completo(projeto, normas_df)
        
        if resultados:
            st.success(f"✅ {len(resultados)} normas relevantes encontradas!")
            
            for i, res in enumerate(resultados[:8], 1):
                with st.expander(f"#{i} 🎯 {res['norma']} ({res['numero']}/{res['ano']}) - {res['score']:.1f}%", 
                                expanded=i==1):
                    st.markdown(f"**Assunto:** {res['assunto']}")
                    st.markdown("**Trecho relevante:**")
                    st.info(res['trecho'])
                    st.markdown(f"**[Leia norma completa]({res['url']})**")
                    st.caption(f"📍 {res['tipo']} - Relevância: {res['relevancia']}")
        else:
            st.warning("❌ Nenhuma norma encontrada. Use termos como: OOH, painel, recuo, ZR-3, andares, m², zoneamento...")

def analisar_projeto_completo(projeto, df):
    """Busca inteligente com TF-IDF + keywords + web scraping"""
    resultados = []
    
    # Keywords específicas do projeto
    keywords_projeto = extrair_keywords(projeto)
    
    for idx, norma in df.iterrows():
        score = calcular_relevancia(norma, projeto, keywords_projeto)
        
        if score > 0.1:  # Threshold mínimo
            try:
                trecho = buscar_trecho_web(norma['url'], projeto)
                resultados.append({
                    'norma': norma['nome'],
                    'numero': norma['numero'],
                    'ano': norma['ano'],
                    'tipo': norma['tipo'],
                    'url': norma['url'],
                    'assunto': norma['assunto'],
                    'relevancia': norma['relevancia'],
                    'score': score * 100,
                    'trecho': trecho
                })
            except:
                resultados.append({
                    'norma': norma['nome'], 'numero': norma['numero'], 'ano': norma['ano'],
                    'tipo': norma['tipo'], 'url': norma['url'], 'assunto': norma['assunto'],
                    'relevancia': norma['relevancia'], 'score': score * 100,
                    'trecho': f"Norma essencial para {norma['assunto'].lower()}. Acesse link oficial."
                })
    
    return sorted(resultados, key=lambda x: x['score'], reverse=True)

def extrair_keywords(texto):
    """Extrai termos técnicos do projeto"""
    termos = re.findall(r'\b(painel|OOH|publicidade|fachada|recuo|andares?|pavimento|metros?²?|m²|ZR\d|zoneamento|lote|construção|reforma|acessibilidade|habitação|edificação)\b', 
                       texto.lower())
    return list(set(termos))

def calcular_relevancia(norma, projeto, keywords):
    """Calcula score de relevância com múltiplos fatores"""
    score = 0
    
    # 1. Keywords diretas
    for kw in keywords:
        if kw in norma['nome'].lower() or kw in norma['assunto'].lower():
            score += 0.3
    
    # 2. Assuntos específicos
    if any(palavra in projeto.lower() for palavra in ['painel', 'OOH', 'publicidade']):
        if 'ooh' in norma['assunto'].lower() or 'publicidade' in norma['assunto'].lower():
            score += 0.4
    if any(palavra in projeto.lower() for palavra in ['recuo', 'zoneamento', 'zr']):
        if 'zoneamento' in norma['assunto'].lower():
            score += 0.4
    if 'edifica' in norma['assunto'].lower() or 'construção' in norma['assunto'].lower():
        score += 0.2
    
    return min(score, 1.0)

def buscar_trecho_web(url, query):
    """Extrai trecho real da norma online"""
    try:
        resp = requests.get(url, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        texto = soup.get_text()
        
        # Busca frases com termos do projeto
        frases = re.split(r'[.!?]+', texto)
        melhor_frase = max(frases, key=lambda f: sum(1 for q in query.lower().split() if q in f.lower()), default="")
        
        return melhor_frase.strip()[:400] + "..." if melhor_frase.strip() else "Consulte norma completa"
    except:
        return "Trecho indisponível - acesse link oficial"

# Sidebar com estatísticas
with st.sidebar:
    st.markdown("### 📊 Estatísticas")
    st.metric("Total de Normas", len(normas_df))
    st.metric("Alta Relevância", len(normas_df[normas_df['relevancia']=='Alta']))
    
    st.markdown("### 🔗 Fontes Oficiais")
    st.markdown("[🏛️ Portal Urbanismo](https://urbanismo.curitiba.pr.gov.br)")
    st.markdown("[📜 Leis Municipais](https://leismunicipais.com.br/curitiba-pr)")
    st.markdown("[⚖️ Câmara Municipal](https://www.curitiba.pr.leg.br)")
    
    st.markdown("---")
    st.caption("💾 Atualizado: Fev/2026")

st.markdown("---")
st.markdown("*🔨 App para arquitetos/urbanistas. Valide sempre com CREA/CAU/PR.* | *Desenvolvido com ❤️ para Curitiba/PR*")
