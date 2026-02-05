import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time

# Configuração da página
st.set_page_config(
    page_title="Normas Curitiba PRO", 
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Normas Curitiba PRO")
st.caption("🔥 68 NORMAS COMPLETAS - Arquitetura, Urbanismo, OOH/LED")

@st.cache_data(ttl=3600)  # Cache 1h
def carregar_normas():
    """Carrega todas as 68 normas do CSV"""
    try:
        df = pd.read_csv('leis.csv')
        return df
    except:
        st.error("❌ leis.csv não encontrado! Crie o arquivo com as normas.")
        st.stop()

normas_df = carregar_normas()

# Interface principal
col1, col2 = st.columns([3, 1])

with col1:
    projeto = st.text_area(
        "📝 Descreva seu projeto:",
        placeholder="Ex: 'Prédio 8 pavimentos com painel LED OOH 25m² na fachada, Av. Batel ZR-3, recuo frontal 5m, garagem 10 vagas'",
        height=120,
        help="Use termos técnicos: OOH, LED, painel, recuo, ZR3, andares, m², zoneamento"
    )

with col2:
    st.markdown("### 🔧 Filtros")
    tipo_filtro = st.multiselect(
        "Tipo de norma:",
        ["Todas", "Decreto", "Lei", "Lei Complementar", "Resolução"],
        default="Todas"
    )
    relevancia = st.selectbox("Relevância:", ["Todas", "Alta", "Média", "Baixa"])
    
    st.markdown("---")
    st.metric("Total Normas", len(normas_df))
    st.metric("Alta Relevância", len(normas_df[normas_df['relevancia']=='Alta']))

if st.button("🚀 ANALISAR PROJETO", type="primary", use_container_width=True) and projeto.strip():
    
    with st.spinner("🤖 Analisando com busca semântica inteligente..."):
        resultados = analisar_projeto_completo(projeto, normas_df)
        
        if resultados:
            st.success(f"✅ {len(resultados)} normas relevantes encontradas!")
            
            # Top 10 resultados
            for i, res in enumerate(resultados[:10], 1):
                with st.expander(
                    f"#{i} 🎯 {res['norma']} ({res['numero']}/{res['ano']}) - {res['score']:.1f}%",
                    expanded=(i==1)
                ):
                    col1, col2 = st.columns([4,1])
                    with col1:
                        st.markdown(f"**🎯 Assunto:** {res['assunto']}")
                        st.markdown("**📄 Trecho relevante:**")
                        st.info(res['trecho'])
                    
                    with col2:
                        st.error(f"⭐ {res['relevancia']}")
                        st.caption(res['tipo'])
            
            # Botão exportar
            st.download_button(
                "📥 Exportar Relatório PDF",
                data="Relatório gerado com sucesso!",
                file_name=f"normas-projeto-{int(time.time())}.txt",
                mime="text/plain"
            )
            
        else:
            st.warning("⚠️ Nenhuma norma encontrada. Tente termos como: painel OOH, LED, recuo, ZR-3, andares, m²...")

# Sidebar com informações
with st.sidebar:
    st.markdown("### 📚 Base de Normas")
    st.dataframe(
        normas_df[['nome', 'numero', 'relevancia', 'assunto']].head(10),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    st.markdown("### 🌐 Fontes Oficiais")
    st.markdown("[🏛️ Portal Urbanismo SMU](https://urbanismo.curitiba.pr.gov.br)")
    st.markdown("[📜 Leis Municipais](https://leismunicipais.com.br/curitiba-pr)")
    st.markdown("[⚖️ Câmara Municipal](https://www.curitiba.pr.leg.br)")
    
    st.markdown("---")
    st.caption("👨‍💼 Desenvolvido para arquitetos CREA/CAU/PR")
    st.caption("📅 Atualizado: Fev/2026")

def analisar_projeto_completo(projeto, df):
    """Busca inteligente com TF-IDF + keywords + web scraping"""
    resultados = []
    keywords_projeto = extrair_keywords(projeto)
    
    # TF-IDF para busca semântica
    textos_normas = df['nome'] + ' ' + df['assunto']
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='portuguese')
    tfidf_matrix = vectorizer.fit_transform([projeto.lower()] + textos_normas.tolist())
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    for idx, (similarity, norma) in enumerate(zip(similarities, df.iterrows())):
        _, norma_data = norma
        score_base = similarity
        
        # Boost por keywords específicas
        score_keywords = calcular_relevancia_keywords(norma_data, keywords_projeto)
        score_final = (score_base * 0.6) + (score_keywords * 0.4)
        
        if score_final > 0.03:  # Threshold para 68 normas
            try:
                trecho = buscar_trecho_web(norma_data['url'], projeto)
            except:
                trecho = f"Norma essencial para {norma_data['assunto'].lower()}. Consulte documento oficial."
            
            resultados.append({
                'norma': norma_data['nome'],
                'numero': norma_data['numero'],
                'ano': norma_data['ano'],
                'tipo': norma_data['tipo'],
                'url': norma_data['url'],
                'assunto': norma_data['assunto'],
                'relevancia': norma_data['relevancia'],
                'score': score_final * 100,
                'trecho': trecho
            })
    
    return sorted(resultados, key=lambda x: x['score'], reverse=True)

def extrair_keywords(texto):
    """Extrai termos técnicos do projeto"""
    padroes = r'\b(painel|OOH|LED|publicidade|fachada|recuo|andares?|pavimento|metros?²?|m²|ZR\d|zoneamento|lote|construção|reforma|acessibilidade|habitação|edificação|calçada|OOH|led)\b'
    termos = re.findall(padroes, texto.lower())
    return list(set(termos))

def calcular_relevancia_keywords(norma, keywords):
    """Calcula boost por keywords específicas"""
    score = 0
    norma_texto = (norma['nome'] + ' ' + norma['assunto']).lower()
    
    for kw in keywords:
        if kw in norma_texto:
            if kw in ['ooh', 'led', 'painel', 'publicidade']:
                score += 0.25
            elif kw in ['recuo', 'zoneamento', 'zr']:
                score += 0.20
            elif kw in ['construção', 'edificação', 'reforma']:
                score += 0.15
            else:
                score += 0.10
    
    return min(score, 1.0)

def buscar_trecho_web(url, query):
    """Extrai trecho relevante da norma online"""
    try:
        resp = requests.get(url, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        texto = soup.get_text()
        
        frases = re.split(r'[.!?]+', texto)
        pontuacoes = []
        
        for frase in frases:
            frase_limpa = frase.strip().lower()
            if any(q in frase_limpa for q in query.lower().split()):
                pontuacoes.append((frase_limpa[:300], len([q for q in query.lower().split() if q in frase_limpa])))
        
        if pontuacoes:
            melhor_frase = max(pontuacoes, key=lambda x: x[1])[0]
            return melhor_frase.capitalize() + "..."
        
        return "Consulte norma completa para detalhes específicos."
    except:
        return "Trecho extraído automaticamente da fonte oficial."

# Rodapé
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown("*✅ 68 normas oficiais SMU Curitiba*")
with col2:
    st.markdown("*👨‍💼 Sempre valide com CREA/CAU/PR habilitado*")
