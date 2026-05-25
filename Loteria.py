import streamlit as st
import itertools
import random
import json
import requests
from collections import Counter
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =====================================================================
# CONFIGURAÇÕES E PREÇOS - LOTOMATRIX PREMIUM 
# =====================================================================
st.set_page_config(page_title="LotoMatrix Premium", page_icon="🧬", layout="wide")

PRECO_15, PRECO_16 = 3.50, 56.00
PREMIOS = {11: 6.00, 12: 12.00, 13: 30.00, 14: 2000.00, 15: 1500000.00}

# --- INICIALIZAÇÃO DO ESTADO ---
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False
if 'historico_dados' not in st.session_state:
    st.session_state.historico_dados = []
if 'banca' not in st.session_state:
    st.session_state.banca = 0.0
if 'jogos_salvos' not in st.session_state:
    st.session_state.jogos_salvos = [] # Nova memória persistente

# =====================================================================
# FUNÇÕES DE MEMÓRIA E COFRE
# =====================================================================
def carregar_cofre_seguro(uploaded_file):
    try:
        data = json.load(uploaded_file)
        st.session_state.historico_dados = data.get("historico_dados", [])
        st.session_state.banca = data.get("banca", 200.0)
        # Carrega os jogos salvos que estavam aguardando sorteio
        st.session_state.jogos_salvos = data.get("jogos_salvos", []) 
        st.session_state.dados_carregados = True
        return True
    except Exception as e:
        st.error(f"Erro ao ler cofre: {e}")
        return False

def gerar_backup():
    return {
        "banca": st.session_state.banca,
        "historico_dados": st.session_state.historico_dados,
        "jogos_salvos": st.session_state.jogos_salvos
    }

# =====================================================================
# INTELIGÊNCIA BIOLÓGICA E FILTROS
# =====================================================================
def calcular_ciclo(historico):
    if not historico: return []
    dezenas_sorteadas = set()
    for sorteio in reversed(historico):
        dezenas_sorteadas.update(sorteio['dezenas'])
        if len(dezenas_sorteadas) == 25:
            break
    faltam = set(range(1, 26)) - dezenas_sorteadas
    return list(faltam)

def filtrar_jogo(jogo, ultimo_sorteio, historico_sets, volume_jogos):
    soma = sum(jogo)
    impares = sum(1 for n in jogo if n % 2 != 0)
    primos_lista = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    primos = sum(1 for n in jogo if n in primos_lista)
    
    # 1. Guilhotina Histórica (Inflexível)
    if set(jogo) in historico_sets: return False
    
    # 2. Repetição do Concurso Anterior (Inflexível: 8 a 10)
    if ultimo_sorteio:
        repetidas = len(set(jogo).intersection(ultimo_sorteio))
        if repetidas < 8 or repetidas > 10: return False

    # 3. Curva de Sino (Flexível com base no volume)
    if volume_jogos < 10:
        # Modo Sniper: Filtros Rígidos
        if not (180 <= soma <= 220): return False
        if not (7 <= impares <= 8): return False
        if not (5 <= primos <= 6): return False
    else:
        # Modo Cobertura: Permite anomalias para blindar (Zebras)
        if random.random() > 0.15: # 85% no padrão, 15% fora
            if not (170 <= soma <= 230): return False
            if not (6 <= impares <= 9): return False
            if not (4 <= primos <= 7): return False

    # 4. Filtro de Gap (Sem buracos gigantes)
    jogo_ordenado = sorted(jogo)
    for i in range(len(jogo_ordenado)-1):
        if jogo_ordenado[i+1] - jogo_ordenado[i] > 5:
            return False

    return True

# =====================================================================
# CÁLCULO DE PRÊMIOS MÚLTIPLOS (Para jogos de 16 dezenas)
# =====================================================================
def calcular_premiacao_multipla(acertos, tamanho_jogo):
    valor_total = 0.0
    if tamanho_jogo == 15:
        if acertos >= 11: valor_total = PREMIOS[acertos]
    elif tamanho_jogo == 16:
        if acertos == 11: valor_total = 5 * PREMIOS[11]
        elif acertos == 12: valor_total = 4 * PREMIOS[12] + 12 * PREMIOS[11]
        elif acertos == 13: valor_total = 3 * PREMIOS[13] + 13 * PREMIOS[12]
        elif acertos == 14: valor_total = 2 * PREMIOS[14] + 14 * PREMIOS[13]
        elif acertos == 15: valor_total = PREMIOS[15] + 15 * PREMIOS[14]
    return valor_total

# =====================================================================
# INTERFACE VISUAL
# =====================================================================
st.title("🧬 LotoMatrix Premium - IA Preditiva")

if not st.session_state.dados_carregados:
    st.warning("⚠️ Carregue seu arquivo Cofre.json na aba Sistema para iniciar.")

tabs = st.tabs(["🎯 Gerador Autônomo", "🏆 Conferência", "💾 Cofre & Sistema"])

# ----------------- ABA 1: GERADOR -----------------
with tabs[0]:
    if st.session_state.dados_carregados:
        st.markdown("### 🧠 Cérebro Preditivo e Matriz de Risco")
        
        col1, col2 = st.columns(2)
        orcamento_alocado = col1.number_input("Orçamento para esta operação (R$)", min_value=3.5, max_value=st.session_state.banca, value=20.0)
        tamanho_bilhete = col2.selectbox("Formato do Bilhete", [15, 16], format_func=lambda x: f"{x} Dezenas")
        
        custo_unitario = PRECO_15 if tamanho_bilhete == 15 else PRECO_16
        qtd_jogos_possivel = int(orcamento_alocado // custo_unitario)
        
        st.info(f"O sistema pode gerar **{qtd_jogos_possivel} jogos** com este orçamento.")

        if st.button("🚀 INICIAR GERAÇÃO IA", type="primary"):
            if qtd_jogos_possivel < 1:
                st.error("Orçamento insuficiente para o formato escolhido.")
            else:
                with st.spinner("Analisando Ciclos, Histórico e Padrões..."):
                    historico = st.session_state.historico_dados
                    ultimo_sorteio = historico[-1]['dezenas'] if historico else []
                    historico_sets = [set(h['dezenas']) for h in historico]
                    
                    # Inteligência de Ciclos e Frequência
                    faltam_ciclo = calcular_ciclo(historico)
                    todas_dezenas = [n for h in historico for n in h['dezenas']]
                    contagem = Counter(todas_dezenas)
                    dezenas_ordenadas = [k for k, v in contagem.most_common()]
                    
                    # Construindo a Matriz Base (18 a 20 dezenas)
                    matriz_base = set(faltam_ciclo) # Força dezenas do ciclo atual
                    for dezena in dezenas_ordenadas:
                        if len(matriz_base) >= 19: break
                        matriz_base.add(dezena)
                    matriz_base = sorted(list(matriz_base))
                    
                    jogos_aprovados = []
                    tentativas = 0
                    
                    while len(jogos_aprovados) < qtd_jogos_possivel and tentativas < 50000:
                        tentativas += 1
                        candidato = sorted(random.sample(matriz_base, tamanho_bilhete))
                        if filtrar_jogo(candidato, ultimo_sorteio, historico_sets, qtd_jogos_possivel):
                            if candidato not in jogos_aprovados:
                                jogos_aprovados.append(candidato)
                    
                    # Salva os jogos no cofre
                    st.session_state.jogos_salvos.extend([{"tamanho": tamanho_bilhete, "dezenas": j} for j in jogos_aprovados])
                    st.session_state.banca -= (len(jogos_aprovados) * custo_unitario)
                    st.success(f"✅ Lote de {len(jogos_aprovados)} jogos gerado e salvo com sucesso!")

        # Exibição dos Jogos Salvos Pendentes
        if st.session_state.jogos_salvos:
            st.markdown("---")
            st.markdown("### 🎫 Bilhetes na Espera do Sorteio (Salvos no Backup)")
            
            for i, j in enumerate(st.session_state.jogos_salvos):
                dezenas_str = " - ".join([f"{n:02d}" for n in j['dezenas']])
                st.markdown(f"""
                <div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #00ffcc;">
                    <h4 style="margin:0; color: #00ffcc;">Jogo {i+1} [{j['tamanho']} Dezenas]</h4>
                    <p style="font-size: 18px; letter-spacing: 2px; margin-top: 10px;">{dezenas_str}</p>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("🗑️ Excluir Todos os Jogos Pendentes"):
                st.session_state.jogos_salvos = []
                st.rerun()

# ----------------- ABA 2: CONFERÊNCIA -----------------
with tabs[1]:
    if st.session_state.dados_carregados:
        st.markdown("### 🏆 Auditoria de Bilhetes")
        
        if not st.session_state.jogos_salvos:
            st.info("Nenhum jogo salvo na espera. Vá ao Gerador primeiro.")
        else:
            col_resultado = st.text_input("Insira as 15 dezenas do Sorteio (separadas por espaço):")
            
            if st.button("🔍 CONFERIR PREMIAÇÃO", type="primary"):
                try:
                    resultado_oficial = [int(x) for x in col_resultado.split()]
                    if len(resultado_oficial) != 15:
                        st.error("Por favor, insira exatamente 15 números válidos.")
                    else:
                        resultado_set = set(resultado_oficial)
                        total_ganho = 0.0
                        
                        for i, j in enumerate(st.session_state.jogos_salvos):
                            acertos = len(set(j['dezenas']).intersection(resultado_set))
                            premio = calcular_premiacao_multipla(acertos, j['tamanho'])
                            total_ganho += premio
                            
                            dezenas_str = " - ".join([
                                f"<span style='color: {'#00ff00' if n in resultado_set else '#ffffff'}; font-weight: {'bold' if n in resultado_set else 'normal'};'>{n:02d}</span>" 
                                for n in j['dezenas']
                            ])
                            
                            # Card Estilizado
                            if acertos >= 11:
                                border_color = "#00ff00" if acertos >= 14 else "#ffcc00"
                                status_txt = f"🎉 PREMIADO! {acertos} Acertos (R$ {premio:.2f})"
                            else:
                                border_color = "#ff4444"
                                status_txt = f"❌ {acertos} Acertos"

                            st.markdown(f"""
                            <div style="background-color: #2b2b2b; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 6px solid {border_color};">
                                <h4 style="margin:0; color: {border_color};">Bilhete {i+1} - {status_txt}</h4>
                                <p style="font-size: 16px; margin-top: 10px; background: #111; padding: 8px; border-radius: 4px;">{dezenas_str}</p>
                                <p style="font-size: 12px; color: #888; margin: 0;">Formato: {j['tamanho']} dezenas | O cálculo considera prêmios múltiplos.</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.session_state.banca += total_ganho
                        st.success(f"💰 Lucro Total da Operação: R$ {total_ganho:.2f} (Adicionado à Banca)")
                        
                except ValueError:
                    st.error("Formato inválido. Use apenas números e espaços.")

# ----------------- ABA 3: SISTEMA -----------------
with tabs[2]:
    st.markdown("### 💾 Gestão do Sistema e Cofre")
    colA, colB = st.columns(2)
    
    with colA:
        st.metric("Banca Atual", f"R$ {st.session_state.banca:.2f}")
        
    with colB:
        st.markdown("#### 📥 Restaurar Sistema")
        uploaded_file = st.file_uploader("Selecione o arquivo Cofre.json:", type=["json"])
        if st.button("🚀 CARREGAR DADOS"):
            if uploaded_file and carregar_cofre_seguro(uploaded_file):
                st.success("✅ Sistema Restaurado e Inteligência Carregada!")
                st.rerun()

    st.markdown("---")
    if st.session_state.dados_carregados:
        estado_json = json.dumps(gerar_backup())
        st.download_button(
            "📤 Baixar Cofre de Segurança Atualizado (.json)", 
            estado_json, 
            "Cofre.json", 
            "application/json", 
            type="primary",
            help="Baixe este arquivo para não perder sua banca e os jogos gerados que estão aguardando sorteio."
        )
