# ... (mantenha o início do código igual)

    if st.button("🔍 ANALISAR NORMAS E ARTIGOS"):
        if projeto:
            # Transforma sua descrição em uma lista de palavras para busca ampla
            palavras_usuario = set(projeto.lower().replace(",", " ").split())
            encontrou = False
            
            st.markdown("---")
            st.subheader("📋 Artigos e Dispositivos Legais Identificados")
            
            for _, row in df.iterrows():
                # Texto onde o app vai procurar (Categoria + Descrição + Artigo)
                conteudo_lei = (row['Categoria'] + " " + row['Descricao'] + " " + row['Artigo']).lower()
                
                # Se QUALQUER palavra que você digitou (com mais de 3 letras) estiver na lei, ele mostra
                if any(palavra in conteudo_lei for palavra in palavras_usuario if len(palavra) > 3):
                    with st.container():
                        c1, c2 = st.columns([1, 4])
                        with c1:
                            st.info(f"**{row['Artigo']}**")
                            st.caption(f"Tópico: {row['Categoria']}")
                        with c2:
                            st.markdown(f"**Dispositivo:** {row['Descricao']}")
                            st.caption(f"📍 Fonte específica: {row['Fonte']}")
                            if row['Link']:
                                st.link_button("Acessar Texto Integral", row['Link'])
                        st.divider()
                        encontrou = True
