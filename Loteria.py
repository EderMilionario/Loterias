import streamlit as st
import itertools
import json

# =====================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E MEMÓRIA
# =====================================================================
st.set_page_config(page_title="LotoEstratégia Pro", page_icon="📊", layout="wide")

# Inicialização do Estado da Sessão (Memória do Sistema)
if 'banca_saldo' not in st.session_state: st.session_state.banca_saldo = 500.0
if 'jogos_otimizados' not in st.session_state: st.session_state.jogos_otimizados = []

# =====================================================================
# 2. MOTOR DE FILTROS MATEMÁTICOS (A "Peneira" Inteligente)
# =====================================================================
def validar_jogo(jogo):
    """
    Esta função avalia cada bilhete gerado.
    Se o bilhete não cumprir as estatísticas mais comuns, é descartado.
    """
    soma = sum(jogo)
    impares = len([x for x in jogo if x % 2 != 0])
    
    # Filtro 1: Soma das dezenas (Historicamente, 80% dos sorteios caem entre 180 e 220)
    if soma < 180 or soma > 220:
        return False
        
    # Filtro 2: Quantidade de Ímpares (Geralmente saem 7, 8 ou 9 ímpares)
    if impares < 6 or impares > 9:
        return False
        
    # Poderá adicionar mais filtros aqui futuramente (Primos, Moldura, etc.)
    return True

# =====================================================================
# 3. INTERFACE DO UTILIZADOR (ECRÃ PRINCIPAL)
# =====================================================================
st.title("📊 LotoEstratégia Pro — Otimizador Matemático")
st.caption("Arquitetura baseada em Desdobramentos Combinatórios, Filtros de Probabilidade e Backtesting.")

# Menu Lateral (Separadores)
menu = st.sidebar.radio(
    "Navegação do Sistema", 
    ["1. Matriz de Desdobramento", "2. Conferidor e Backtesting", "3. Gestão e Backup (JSON)"]
)

# ---------------------------------------------------------------------
# SEPARADOR 1: Geração de Jogos
# ---------------------------------------------------------------------
if menu == "1. Matriz de Desdobramento":
    st.header("⚙️ Motor de Combinações")
    st.write("Selecione um grupo maior de dezenas. O sistema criará todas as combinações possíveis de 15 números e aplicará filtros para eliminar apostas de baixo potencial.")
    
    todas_dezenas = list(range(1, 26))
    
    # O utilizador escolhe o seu grupo de risco (ex: 18 números)
    dezenas_escolhidas = st.multiselect(
        "Selecione as suas dezenas estratégicas (Recomendado: 17 a 19 dezenas):", 
        todas_dezenas, 
        default=[1,2,3,4,5,7,8,10,11,13,15,16,17,19,20,22,23,24]
    )
    
    if len(dezenas_escolhidas) >= 15:
        if st.button("Executar Motor de Otimização", type="primary"):
            
            with st.spinner("A calcular matrizes matemáticas..."):
                # Gera TODAS as combinações possíveis de 15 dentro do grupo escolhido
                todas_combinacoes = list(itertools.combinations(sorted(dezenas_escolhidas), 15))
                total_bruto = len(todas_combinacoes)
                
                # Aplica a peneira inteligente
                jogos_filtrados = [jogo for jogo in todas_combinacoes if validar_jogo(jogo)]
                total_liquido = len(jogos_filtrados)
                
                # Guarda os jogos na memória
                st.session_state.jogos_otimizados = jogos_filtrados
            
            st.success("✅ Processamento Concluído!")
            
            # Exibição de Resultados e Economia
            col1, col2, col3 = st.columns(3)
            col1.metric("Combinações Possíveis (Bruto)", total_bruto)
            col2.metric("Jogos Aprovados (Líquido)", total_liquido)
            col3.metric("Jogos Descartados (Poupança)", total_bruto - total_liquido)
            
            st.write("### Amostra do Pool Otimizado")
            st.dataframe(jogos_filtrados[:10]) # Mostra os primeiros 10 jogos
    else:
        st.warning("Por favor, selecione pelo menos 15 dezenas para iniciar o desdobramento.")

# ---------------------------------------------------------------------
# SEPARADOR 2: Backtesting e Conferência
# ---------------------------------------------------------------------
elif menu == "2. Conferidor e Backtesting":
    st.header("🔍 Auditoria de Jogos (Backtesting)")
    st.write("Simule o desempenho do seu Pool de jogos contra sorteios reais ou hipotéticos.")
    
    if not st.session_state.jogos_otimizados:
        st.info("O seu Pool está vazio. Regresse ao separador de Desdobramento para gerar os jogos.")
    else:
        st.write(f"Temos **{len(st.session_state.jogos_otimizados)}** jogos otimizados em memória.")
        
        resultado_oficial = st.text_input(
            "Introduza as 15 dezenas do sorteio (separadas por vírgula):", 
            "1,2,4,5,7,8,10,13,15,16,17,19,20,23,24"
        )
        
        if st.button("Conferir Bilhetes"):
            try:
                # Transforma o texto inserido num conjunto (set) de inteiros
                dezenas_sorteadas = set([int(x.strip()) for x in resultado_oficial.split(",")])
                
                if len(dezenas_sorteadas) != 15:
                    st.error("Tem de introduzir exatamente 15 dezenas únicas.")
                else:
                    acertos = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
                    custo_total = len(st.session_state.jogos_otimizados) * 3.00 # Considerando 3,00 por aposta
                    retorno_financeiro = 0.0
                    
                    # Tabela de prémios (estimativa conservadora)
                    premios = {11: 6.00, 12: 12.00, 13: 30.00, 14: 1500.00, 15: 1000000.00}
                    
                    for jogo in st.session_state.jogos_otimizados:
                        pontos = len(set(jogo).intersection(dezenas_sorteadas))
                        if pontos >= 11:
                            acertos[pontos] += 1
                            retorno_financeiro += premios[pontos]
                    
                    lucro = retorno_financeiro - custo_total
                    
                    st.markdown("---")
                    st.write("### 🏆 Relatório de Desempenho do Pool")
                    
                    colA, colB, colC = st.columns(3)
                    colA.metric("Custo do Desdobramento", f"R$ {custo_total:.2f}")
                    colB.metric("Retorno Bruto", f"R$ {retorno_financeiro:.2f}")
                    colC.metric("Lucro / Prejuízo Líquido", f"R$ {lucro:.2f}", delta=lucro)
                    
                    st.write("#### Distribuição de Acertos:")
                    st.write(f"- **15 Pontos:** {acertos[15]}")
                    st.write(f"- **14 Pontos:** {acertos[14]}")
                    st.write(f"- **13 Pontos:** {acertos[13]}")
                    st.write(f"- **12 Pontos:** {acertos[12]}")
                    st.write(f"- **11 Pontos:** {acertos[11]}")
            except:
                st.error("Formato inválido. Certifique-se de usar apenas números separados por vírgula.")

# ---------------------------------------------------------------------
# SEPARADOR 3: Sistema de Ficheiros / Backup
# ---------------------------------------------------------------------
elif menu == "3. Gestão e Backup (JSON)":
    st.header("💾 Gestão de Ficheiros e Banca")
    
    st.write(f"### Saldo em Banca: R$ {st.session_state.banca_saldo:.2f}")
    
    st.markdown("---")
    st.write("### 📥 Descarregar Pool Atual")
    st.write("Exporte os seus jogos otimizados e saldo para não os perder quando fechar a aplicação.")
    
    # Preparar dados para exportação
    dados_exportacao = {
        "banca_saldo": st.session_state.banca_saldo,
        "jogos_otimizados": st.session_state.jogos_otimizados
    }
    
    # Converter para JSON
    json_string = json.dumps(dados_exportacao)
    
    st.download_button(
        label="Descarregar Backup .json",
        data=json_string,
        file_name="meu_backup_estrategico.json",
        mime="application/json"
    )
    
    st.markdown("---")
    st.write("### 📤 Carregar Backup")
    arquivo_importacao = st.file_uploader("Selecione o seu ficheiro .json", type=["json"])
    
    if arquivo_importacao is not None:
        try:
            conteudo = json.load(arquivo_importacao)
            st.session_state.banca_saldo = conteudo.get("banca_saldo", 500.0)
            st.session_state.jogos_otimizados = conteudo.get("jogos_otimizados", [])
            st.success("✅ Dados restaurados com sucesso! O seu saldo e Pool de jogos estão de volta.")
        except:
            st.error("Erro ao ler o ficheiro JSON. Certifique-se de que é um backup válido.")
