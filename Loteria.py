import streamlit as st
import pandas as pd
import requests
import json
import random
import uuid
import re
from collections import Counter
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def salvar_dados(dados):
    """Força a gravação silenciosa da memória da IA no arquivo local do PC"""
    try:
        import json
        with open("Cofre.json", "w", encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
    except Exception as e:
        pass

def render_performance_grid(dezenas_lista, titulo):
    contagem = Counter(dezenas_lista)
    # Criar DataFrame para visualizar melhor
    df = pd.DataFrame.from_dict(contagem, orient='index', columns=['Frequência']).sort_index()
    st.markdown(f"#### {titulo}")
    # Usar um gráfico de barras simples e elegante
    st.bar_chart(df)

# =====================================================================
# CONFIGURAÇÃO E LOGIN
# =====================================================================
st.set_page_config(page_title="LotoMatrix PRO - Agente Autônomo", page_icon="🧬", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #006644;'>🔐 Acesso Restrito - LotoMatrix PRO</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            senha = st.text_input("Digite a Senha para Acessar a IA:", type="password")
            if st.button("ENTRAR NO SISTEMA", type="primary", use_container_width=True):
                if senha == "777":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Acesso Negado.")
    st.stop()

# =====================================================================
# MÓDULO MATEMÁTICO: PREMIAÇÃO MÚLTIPLA DA CAIXA
# =====================================================================
def calcular_premio_multiplo(tamanho, acertos, v11=7.0, v12=14.0, v13=35.0, v14=1500.0, v15=1500000.0):
    """Calcula o rateio exato para apostas simples e múltiplas com os novos valores base."""
    if acertos < 11: return 0.0
    premio = 0.0
    
    # Regra oficial da Caixa Econômica
    if tamanho == 15:
        if acertos == 11: premio = v11
        elif acertos == 12: premio = v12
        elif acertos == 13: premio = v13
        elif acertos == 14: premio = v14
        elif acertos == 15: premio = v15
    elif tamanho == 16:
        if acertos == 11: premio = 5 * v11
        elif acertos == 12: premio = (4 * v12) + (12 * v11)
        elif acertos == 13: premio = (3 * v13) + (13 * v12)
        elif acertos == 14: premio = (2 * v14) + (14 * v13)
        elif acertos == 15: premio = (1 * v15) + (15 * v14)
    
    return premio
# =====================================================================
# SENSOR DE DNA QUÂNTICO DA LOTOFÁCIL (FUNÇÃO DE APTIDÃO)
# =====================================================================
# =====================================================================
# SENSOR DE DNA QUÂNTICO DA LOTOFÁCIL (FUNÇÃO DE APTIDÃO)
# =====================================================================
def avaliar_dna_lotofacil(dezenas_geradas, dezenas_ultimo_sorteio):
    primos_set = {2, 3, 5, 7, 11, 13, 17, 19, 23}
    fibo_set = {1, 2, 3, 5, 8, 13, 21}
    mult3_set = {3, 6, 9, 12, 15, 18, 21, 24}

    pares = sum(1 for n in dezenas_geradas if n % 2 == 0)
    impares = len(dezenas_geradas) - pares
    primos = sum(1 for n in dezenas_geradas if n in primos_set)
    fibos = sum(1 for n in dezenas_geradas if n in fibo_set)
    mult3 = sum(1 for n in dezenas_geradas if n in mult3_set)
    repetidas = len(set(dezenas_geradas).intersection(set(dezenas_ultimo_sorteio)))

    tamanho = len(dezenas_geradas)
    score_padrao = 0

    # 🎯 1. ALVOS DINÂMICOS (Estrutura Base)
    if tamanho == 15:
        if impares in [7, 8]: score_padrao += 10
        if primos in [4, 5, 6]: score_padrao += 10
        if fibos in [4, 5]: score_padrao += 10
        if mult3 in [4, 5, 6]: score_padrao += 10
        if repetidas in [8, 9, 10]: score_padrao += 15 
    elif tamanho >= 16:
        if impares in [7, 8, 9]: score_padrao += 10
        if primos in [5, 6, 7]: score_padrao += 10
        if fibos in [4, 5, 6]: score_padrao += 10
        if mult3 in [5, 6, 7]: score_padrao += 10
        if repetidas in [9, 10, 11]: score_padrao += 15

    # 🕸️ 2. TEIA DE CORRELAÇÃO (Bônus Magnético Apriori)
    par_ouro = st.session_state.get('par_ouro', None)
    if par_ouro and par_ouro[0] in dezenas_geradas and par_ouro[1] in dezenas_geradas:
        score_padrao += 25 

    # 🚫 3. VAZIOS DE LINHA E COLUNA (Filtro Cartesiano)
    # Lapeia o volante de 5x5 e identifica anomalias geométricas de abismos.
    linhas = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    colunas = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for n in dezenas_geradas:
        linhas[(n - 1) // 5 + 1] += 1
        colunas[(n - 1) % 5 + 1] += 1
    
    linhas_vazias = sum(1 for v in linhas.values() if v == 0)
    colunas_vazias = sum(1 for v in colunas.values() if v == 0)
    # Punição matemática letal: a IA vai expurgar jogos que deixam corredores vazios
    if linhas_vazias > 0: score_padrao -= (linhas_vazias * 80)
    if colunas_vazias > 0: score_padrao -= (colunas_vazias * 80)

    # 🚫 4. BLOQUEIO DE SEQUENCIAMENTO EXTREMO (Filtro Anti-Escadinha)
    maior_seq = 1
    seq_atual = 1
    dezenas_ordenadas = sorted(dezenas_geradas)
    for i in range(1, len(dezenas_ordenadas)):
        if dezenas_ordenadas[i] == dezenas_ordenadas[i-1] + 1:
            seq_atual += 1
            if seq_atual > maior_seq: maior_seq = seq_atual
        else:
            seq_atual = 1
    # Punição severa se o bilhete formar uma "cobra" de 7 ou mais números grudados
    if maior_seq >= 7: score_padrao -= 100

    # ⚖️ 5. MASSA GRAVITACIONAL (Curva de Gauss da Soma)
    soma_total = sum(dezenas_geradas)
    media_soma = soma_total / tamanho
    # Normalizamos o intervalo Gaussiano: se 180~215 é o ideal para 15 dezenas, 
    # a média perfeita por dezena é de 12.0 a 14.33. Isso faz a IA funcionar perfeitamente
    # mesmo se você decidir gerar bilhetes múltiplos (16+ dezenas).
    if 12.0 <= media_soma <= 14.33:
        score_padrao += 15
    else:
        # Se a soma estourar a normalidade estatística, corta a força do bilhete
        score_padrao -= 30

    # 🏷️ CARIMBO VISUAL DO DNA (Agora mostrando Soma Total e Alertas)
    dna_texto = f"🧬 {impares} Ímp • {pares} Par • {primos} Pri • {fibos} Fib • {mult3} Múlt • {repetidas} Rep • Σ {soma_total}"
    
    # Flags visuais inseridas no bilhete gerado, caso a IA (num caso extremo sem saída) seja obrigada a usar um desses padrões.
    if maior_seq >= 7: 
        dna_texto += " ⚠️ SeqExtrema"
    if linhas_vazias > 0 or colunas_vazias > 0: 
        dna_texto += " ⚠️ VaziosNoVolante"

    return score_padrao, dna_texto
# =====================================================================
# BLINDAGEM DE MEMÓRIA E SANITIZAÇÃO ABSOLUTA
# =====================================================================
def sanitizar_dados(d):
    if "banca" not in d: d["banca"] = 0.0
    if "historico_dados" not in d: d["historico_dados"] = []
    if "jogos_salvos" not in d: d["jogos_salvos"] = []
    if "matriz_viva_atual" not in d: d["matriz_viva_atual"] = []
    if "ia_memoria" not in d: 
        d["ia_memoria"] = {
            "Tendencia": {"usos": 0, "pontos": 0}, 
            "Reversao": {"usos": 0, "pontos": 0},
            "Ciclo": {"usos": 0, "pontos": 0},
            "Simetria": {"usos": 0, "pontos": 0}
        }
    
    for j in d["jogos_salvos"]:
        if "id" not in j: j["id"] = str(uuid.uuid4())
        if "concurso_alvo" not in j: j["concurso_alvo"] = "Legado"
        if "tamanho" not in j: j["tamanho"] = len(j.get("dezenas", []))
        if "status" not in j: j["status"] = "Aguardando Sorteio"
        if "acertos" not in j: j["acertos"] = 0
        if "estrategia" not in j: j["estrategia"] = "Tendencia"
        if "justificativa" not in j: j["justificativa"] = "Jogo recuperado."
    return d

if 'data' not in st.session_state:
    st.session_state.data = sanitizar_dados({})

# =====================================================================
# FUNÇÕES DE CALLBACK (Ações Dinâmicas)
# =====================================================================
def cb_depositar():
    valor = st.session_state.get("input_aporte", 0.0)
    if valor > 0:
        st.session_state.data['banca'] += valor
        st.toast(f"R$ {valor:.2f} creditados na banca!", icon="💰")

def cb_excluir_jogo(jogo_id):
    st.session_state.data['jogos_salvos'] = [j for j in st.session_state.data['jogos_salvos'] if j.get('id') != jogo_id]
    st.toast("Bilhete deletado.", icon="🗑️")

def cb_excluir_todos():
    st.session_state.data['jogos_salvos'] = []
    st.toast("Fila de espera limpa.", icon="🧹")

def cb_carregar_cofre():
    file = st.session_state.uploader_cofre
    if file:
        try:
            st.session_state.data = sanitizar_dados(json.load(file))
            st.toast("Cofre sincronizado com sucesso!", icon="✅")
        except Exception as e: st.error(f"Erro ao ler JSON: {e}")

# =====================================================================
# CÉREBRA MULTI-ESTRATÉGICO DA IA (4 Linhas de Análise Evoluídas)
# =====================================================================
def raciocinio_total_ia(historico, memoria):
    if not historico: return None
    
    # 🧠 JANELA DE ESQUECIMENTO (A base para curar a Inércia Estatística)
    # A IA agora enxerga a frequência global para fins de log, mas usa o horizonte recente para decisão.
    historico_recente = historico[-50:] if len(historico) >= 50 else historico
    todas_dezenas_recentes = [n for h in historico_recente for n in h['dezenas']]
    freq_recente = Counter(todas_dezenas_recentes)
    freq_recente_max = max(freq_recente.values()) if freq_recente else 1
    
    # Frequência Absoluta (Mantida para não quebrar outras leituras do painel)
    todas_dezenas = [n for h in historico for n in h['dezenas']]
    freq = Counter(todas_dezenas)
    
    primos_lista = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    moldura_lista = [1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25]
    
    # Fragmentação Temporal para o Viés Direcional
    ultimos_10 = historico[-10:] if len(historico) >= 10 else historico
    penultimos_10 = historico[-20:-10] if len(historico) >= 20 else historico[-10:]
    
    freq_ult_10 = Counter([n for h in ultimos_10 for n in h['dezenas']])
    freq_pen_10 = Counter([n for h in penultimos_10 for n in h['dezenas']])

    media_soma = sum([sum(h['dezenas']) for h in ultimos_10]) / len(ultimos_10)
    media_impares = sum([sum(1 for n in h['dezenas'] if n % 2 != 0) for h in ultimos_10]) / len(ultimos_10)
    media_primos = sum([sum(1 for n in h['dezenas'] if n in primos_lista) for h in ultimos_10]) / len(ultimos_10)
    media_moldura = sum([sum(1 for n in h['dezenas'] if n in moldura_lista) for h in ultimos_10]) / len(ultimos_10)

    atrasos = {n: 0 for n in range(1, 26)}
    for h in reversed(historico):
        for n in range(1, 26):
            if n not in h['dezenas'] and atrasos[n] == 0: atrasos[n] += 1

    # --- CÉREBRO DE CICLO INTELIGENTE (CÁLCULO PROGRESSIVO PERFEITO) ---
    ciclo_atual = set()
    jogos_ciclo = 0
    
    # A IA varre a história do concurso 1 até hoje. Sempre que dá 25, ela reseta.
    for h in historico:
        ciclo_atual.update(h['dezenas'])
        jogos_ciclo += 1
        if len(ciclo_atual) == 25:
            ciclo_atual = set() # O Ciclo fechou! Reseta para o próximo.
            jogos_ciclo = 0
            
    # O que sobrar na variável é o estado real e absoluto do ciclo hoje.
    faltam_ciclo = sorted(list(set(range(1, 26)) - ciclo_atual))
    
    # Se faltam_ciclo tem 25 dezenas (len == 25), a IA vai ativar o Modo Caos e Matriz 23.
    # Inteligência de Reset: Se o ciclo fechou (faltam 0), iniciamos um novo agora
    if len(faltam_ciclo) == 0:
        ciclo = set(historico[-1]['dezenas'])
        faltam_ciclo = sorted(list(set(range(1, 26)) - ciclo))
        jogos_ciclo = 1
    # [FIM DA SUBSTITUIÇÃO]

    # --- TAMANHO DINÂMICO DA MATRIZ ---
    if len(faltam_ciclo) >= 9: qtd_matriz = 23
    elif len(faltam_ciclo) >= 6: qtd_matriz = 21
    elif len(faltam_ciclo) >= 3: qtd_matriz = 19
    else: qtd_matriz = 18

    # --- AVALIAÇÃO DE DESEMPENHO (MEMÓRIA BLINDADA CONTRA OVERFITTING) ---
    perf = {}
    for est in ["Tendencia", "Reversao", "Ciclo", "Simetria"]:
        usos = memoria.get(est, {}).get("usos", 0)
        pontos = memoria.get(est, {}).get("pontos", 0)
        # Taxa de Decaimento virtual: Impede que uma estratégia fique congelada no topo por ter 500 usos passados.
        if usos > 30: 
            pontos = (pontos / usos) * 30
            usos = 30
        perf[est] = pontos / usos if usos > 0 else 11.0 
        
    melhor_est = max(perf, key=perf.get)

    # --- MUTAÇÃO DE PESOS DA IA CONFORME DECISÃO (CORE ATUALIZADO) ---
    if melhor_est == "Ciclo" and len(faltam_ciclo) > 0:
        estrategia = "Ciclo Otimizado"
        # Ciclo usa freq_recente como base secundária
        pesos = {i: 100 if i in faltam_ciclo else freq_recente.get(i, 0) for i in range(1, 26)}
        motivo_est = "A IA priorizou o Fechamento de Ciclo. Dezenas ausentes receberam força máxima."
        
    elif melhor_est == "Simetria":
        estrategia = "Simetria de Borda"
        pesos = {}
        for i in range(1, 26):
            # SIMETRIA REAL (Espelhamento Direcionado): i e (26-i). 
            # Se o espelho de 'i' está saindo POUCO, a dezena 'i' recebe peso alto para COMPENSAR o eixo.
            espelho = 26 - i
            peso_compensacao = freq_recente_max - freq_recente.get(espelho, 0)
            bonus_borda = 15 if i in moldura_lista else 0
            pesos[i] = peso_compensacao + bonus_borda + freq_recente.get(i, 0)
        motivo_est = "A IA adotou Simetria Analítica. Compensando quadrantes fracos através de espelhamento."
        
    elif melhor_est == "Reversao" or media_soma > 198:
        estrategia = "Reversão Estatística"
        # Agora usando ESTRITAMENTE a Janela de Esquecimento para não ser sufocada pelo passado
        pesos = {i: max(1, (freq_recente_max - freq_recente.get(i, 0)) + (atrasos.get(i, 0) * 5)) for i in range(1, 26)}
        motivo_est = "A IA ativou Reversão Estatística focada no curto prazo (Janela de Esquecimento)."
        
    else:
        estrategia = "Tendência de Frequência"
        pesos = {}
        for i in range(1, 26):
            # VIÉS DIRECIONAL (Momentum de Aceleração vs Desaceleração)
            aceleracao = freq_ult_10.get(i, 0) - freq_pen_10.get(i, 0) 
            peso_base = freq_recente.get(i, 0)
            pesos[i] = max(1, peso_base + (aceleracao * 3))
        motivo_est = "A IA escolheu Tendência com Viés Direcional. Dezenas em aceleração no momento foram priorizadas."

    dezenas_ordenadas = sorted(range(1, 26), key=lambda x: pesos[x], reverse=True)
    matriz_base = sorted(dezenas_ordenadas[:qtd_matriz])
    
    alvo = (historico[-1]['concurso'] + 1) if historico else 1

    return {
        "estrategia": estrategia, "cod_estrategia": melhor_est, "motivo_est": motivo_est, "pesos": pesos, "freq": freq, 
        "atrasos": atrasos, "ciclo_tam": jogos_ciclo, "faltam_ciclo": faltam_ciclo,
        "soma": media_soma, "impares": media_impares, "primos": media_primos, 
        "moldura": media_moldura, "alvo": alvo, "qtd_matriz": qtd_matriz, 
        "matriz_base": matriz_base, "perf": perf
    }

# =====================================================================
# INTERFACE PRINCIPAL
# =====================================================================
st.markdown("<h2 style='text-align: center; color: #1f77b4;'>🧬 LotoMatrix PRO - Agente Autônomo</h2>", unsafe_allow_html=True)
tabs = st.tabs(["📂 1. Banco de Dados", "🧠 2. Cérebro Analítico (IA)", "🤖 3. Geração Autônoma", "📜 4. Fila de Sorteio", "🏆 5. Sincronização e Entrada"])

# --- TAB 1: BANCO DE DADOS E BANCA ---
with tabs[0]:
    st.markdown("### 💾 Central de Dados e Ajuste Financeiro")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.file_uploader("📥 Carregar Arquivo Cofre.json", type="json", key="uploader_cofre", on_change=cb_carregar_cofre)
            st.info(f"📊 **Concursos Oficiais Salvos:** {len(st.session_state.data['historico_dados'])}.")
            st.download_button("📤 Baixar Backup Consolidado", json.dumps(st.session_state.data), "Cofre.json", type="primary", use_container_width=True)
    with c2:
        with st.container(border=True):
            st.metric("💰 Saldo na Banca", f"R$ {st.session_state.data['banca']:.2f}")
            st.number_input("Depositar Valor (R$):", min_value=0.0, step=10.0, key="input_aporte")
            st.button("AUTORIZAR DEPÓSITO", on_click=cb_depositar, use_container_width=True)

# --- TAB 2: CÉREBRO ANALÍTICO ---
with tabs[1]:
    if st.session_state.data["historico_dados"]:
        ia = raciocinio_total_ia(st.session_state.data["historico_dados"], st.session_state.data["ia_memoria"])
        st.session_state.data["matriz_viva_atual"] = ia["matriz_base"]
        
        st.markdown(f"### 🧠 Diagnóstico Autônomo — Concurso Alvo `{ia['alvo']}`")

        # =====================================================================
        # SUPER PAINEL INSTITUCIONAL: RAIO-X, RISCO E CORRELAÇÃO
        # =====================================================================
        historico_painel = st.session_state.data.get("historico_dados", [])
        if len(historico_painel) >= 2:
            ultimo_sort = historico_painel[-1]
            penultimo_sort = historico_painel[-2]
            dez_ult = ultimo_sort['dezenas']
            dez_pen = penultimo_sort['dezenas']
            
            # 1. EXPANSÃO BIOMÉTRICA (DNA do Sorteio)
            primos_set = {2, 3, 5, 7, 11, 13, 17, 19, 23}
            fibo_set = {1, 2, 3, 5, 8, 13, 21}
            mult3_set = {3, 6, 9, 12, 15, 18, 21, 24}

            pares_ult = sum(1 for n in dez_ult if n % 2 == 0)
            impares_ult = 15 - pares_ult
            primos_ult = sum(1 for n in dez_ult if n in primos_set)
            fibo_ult = sum(1 for n in dez_ult if n in fibo_set)
            mult3_ult = sum(1 for n in dez_ult if n in mult3_set)
            repetidas_ult = len(set(dez_ult).intersection(set(dez_pen)))
            
            dezenas_ult_formatadas = " - ".join([f"{n:02d}" for n in dez_ult])
            st.info(f"**🎯 Último Sorteio Oficial (Concurso {ultimo_sort['concurso']}):** {dezenas_ult_formatadas}")
            
            # 6 Cartões com a nova leitura do Universo Lotofácil
            col_rx1, col_rx2, col_rx3, col_rx4, col_rx5, col_rx6 = st.columns(6)
            col_rx1.metric("Ímpares", impares_ult)
            col_rx2.metric("Pares", pares_ult)
            col_rx3.metric("Primos", primos_ult)
            col_rx4.metric("Fibonacci", fibo_ult)
            col_rx5.metric("Múltiplos 3", mult3_ult)
            col_rx6.metric("Repetidas", repetidas_ult)
            
            st.divider()

            # 2. MOTOR APRIORI (Cálculo Restrito à Matriz de Elite - Rota A)
            amostra_corr = historico_painel[-100:] if len(historico_painel) > 100 else historico_painel
            pares_count = {}
            matriz_atual_set = set(ia['matriz_base']) # O filtro matemático que você percebeu faltar

            for sorteio in amostra_corr:
                # Intersecção: cruza a história oficial com a matriz eleita pela IA
                d_sort = [n for n in sorteio['dezenas'] if n in matriz_atual_set]
                for i in range(len(d_sort)):
                    for j in range(i+1, len(d_sort)):
                        par = tuple(sorted((d_sort[i], d_sort[j])))
                        pares_count[par] = pares_count.get(par, 0) + 1
            
            top_par = max(pares_count, key=pares_count.get) if pares_count else (0,0)
            st.session_state.par_ouro = top_par # Salva a dupla magnética real para o DNA!

            # 3. TERMÔMETRO DE RISCO E CORRELAÇÃO
            col_risk, col_corr = st.columns(2)
            
            with col_risk:
                st.markdown("#### 🌡️ Termômetro de Risco (Critério de Kelly)")
                qtd_m = ia.get('qtd_matriz', 18)
                if qtd_m >= 21:
                    n_risco = "ALTO (Início de Ciclo / Caos Aleatório)"
                    c_risco = "#dc3545"; d_banca = "Recomendação: Operar com orçamento defensivo."
                elif qtd_m == 19:
                    n_risco = "MÉDIO (Meio de Ciclo / Transição)"
                    c_risco = "#ffcc00"; d_banca = "Recomendação: Operar com orçamento padrão."
                else:
                    n_risco = "BAIXO (Fim de Ciclo / Alta Previsibilidade)"
                    c_risco = "#28a745"; d_banca = "Recomendação: Janela de Ataque. Risco Mínimo."

                st.markdown(f"""
                <div style='background-color: #f8f9fa; border-left: 5px solid {c_risco}; padding: 15px; border-radius: 6px;'>
                    <span style='color: {c_risco}; font-weight: bold; font-size: 15px;'>Nível Atual: {n_risco}</span><br>
                    <span style='color: #4d5156; font-size: 13px;'><b>Diretriz Institucional:</b> {d_banca}</span>
                </div>
                """, unsafe_allow_html=True)

            with col_corr:
                st.markdown("#### 🕸️ Teia de Correlação (Matriz Filtrada)")
                st.markdown(f"""
                <div style='background-color: #f8f9fa; border-left: 5px solid #1a73e8; padding: 15px; border-radius: 6px;'>
                    <span style='color: #1a73e8; font-weight: bold; font-size: 15px;'>Par Magnético da Elite: {top_par[0]:02d} e {top_par[1]:02d}</span><br>
                    <span style='color: #4d5156; font-size: 13px;'>Esta é a dupla mais quente <b>possível de ser gerada</b> pela matriz atual. O Motor DNA vai garantir a recompensa quântica por agrupá-las.</span>
                </div>
                """, unsafe_allow_html=True)

            st.divider()
            
            # =====================================================================
            # PAINEL DE GESTÃO DE CICLO (Layout Limpo - Nível Profissional)
            # =====================================================================
            st.subheader("📐 Gestão de Ciclo e Matriz")
        
            qtd_em_falta = len(ia['faltam_ciclo'])
        
            # Exibição das métricas principais
            col_c1, col_c2 = st.columns(2)
            col_c1.metric("Ciclo aberto há", f"{ia['ciclo_tam']} concursos")
            col_c2.metric("Dezenas faltando", qtd_em_falta)
        
            # Identificação inteligente do modo de operação
            if qtd_em_falta >= 9:
                modo = "Modo Caos (Defensivo)"
                matriz = "23 Dezenas"
                tipo = "error"
            elif 6 <= qtd_em_falta <= 8:
                modo = "Modo Transição"
                matriz = "21 Dezenas"
                tipo = "warning"
            elif 3 <= qtd_em_falta <= 5:
                modo = "Modo Ataque"
                matriz = "19 Dezenas"
                tipo = "info"
            else:
                modo = "Modo Sniper (Baixo Risco)"
                matriz = "18 Dezenas"
                tipo = "success"
            
            # Exibição do Status atual (sem HTML bagunçado)
            if tipo == "error": st.error(f"**Inteligência:** {modo} | **Matriz Selecionada:** {matriz}")
            elif tipo == "warning": st.warning(f"**Inteligência:** {modo} | **Matriz Selecionada:** {matriz}")
            elif tipo == "info": st.info(f"**Inteligência:** {modo} | **Matriz Selecionada:** {matriz}")
            else: st.success(f"**Inteligência:** {modo} | **Matriz Selecionada:** {matriz}")
        
            # Regras explicativas (Apenas se o usuário quiser ler)
            with st.expander("Ver critérios de dimensionamento (Regras)"):
                st.write("A matriz é ajustada automaticamente baseada na entropia do ciclo:")
                st.write("- 9+ faltando: Matriz 23 (Caos)")
                st.write("- 6-8 faltando: Matriz 21 (Transição)")
                st.write("- 3-5 faltando: Matriz 19 (Ataque)")
                st.write("- 0-2 faltando: Matriz 18 (Sniper)")

            st.divider()
        
        # =====================================================================
        
        st.success(f"**⚡ LINHA TÁTICA ATIVADA:** {ia['estrategia']} \n\n**DIRETRIZ DA DECISÃO:** {ia['motivo_est']}")
        st.info(f"**🎯 GRUPO DE ELITE ({ia['qtd_matriz']} DEZENAS COMPILADAS):** {', '.join([f'{n:02d}' for n in ia['matriz_base']])}")

        # --- NOVAS ANÁLISES EXTRAS SOLICITADAS ---
        st.markdown("#### 📈 Parâmetros Volumétricos e Distribuição Espacial")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Massa de Soma", f"{ia['soma']:.1f}", delta="Equilíbrio: ~195")
        c2.metric("Massa Ímpar", f"{ia['impares']:.1f}", delta="Equilíbrio: ~7.5")
        c3.metric("Massa Primos", f"{ia['primos']:.1f}", delta="Equilíbrio: ~5.5")
        c4.metric("Massa Moldura", f"{ia['moldura']:.1f}", delta="Equilíbrio: ~10")

        # Análise de Quadrantes/Linhas/Colunas e Taxa de Repetição
        linhas_count = {i: 0 for i in range(1, 6)}
        colunas_count = {i: 0 for i in range(1, 6)}
        for n in ia['matriz_base']:
            l = (n - 1) // 5 + 1
            c = (n - 1) % 5 + 1
            linhas_count[l] += 1
            colunas_count[c] += 1
        
        ultimo_sorteio = st.session_state.data["historico_dados"][-1]["dezenas"]
        repetidas_previstas = len(set(ia['matriz_base']).intersection(set(ultimo_sorteio)))

        c_an1, c_an2, c_an3 = st.columns(3)
        with c_an1:
            st.info(f"📋 **Dezenas por Linha (Grupo Elite):**<br>" + " | ".join([f"L{k}: **{v}**" for k, v in linhas_count.items()]), icon="📊")
        with c_an2:
            st.info(f"📋 **Dezenas por Coluna (Grupo Elite):**<br>" + " | ".join([f"C{k}: **{v}**" for k, v in colunas_count.items()]), icon="📊")
        with c_an3:
            st.info(f"🔄 **Repetição do Concurso Anterior:** A Matriz de Elite carrega **{repetidas_previstas} dezenas** do concurso nº {st.session_state.data['historico_dados'][-1]['concurso']}.", icon="🔮")

        # --- NOVO BLOCO: DESEMPENHO HISTÓRICO DAS DEZENAS ESCOLHIDAS PELA IA ---
        st.markdown("#### 🎯 Retrospectiva Crítica do Grupo de Elite (Últimos 30 Concursos)")
        ultimos_30 = st.session_state.data["historico_dados"][-30:]
        acertos_grupo = []
        for h in ultimos_30:
            hits = len(set(ia['matriz_base']).intersection(set(h['dezenas'])))
            acertos_grupo.append(hits)
        
        avg_hits = sum(acertos_grupo) / len(acertos_grupo) if acertos_grupo else 0
        t11 = sum(1 for x in acertos_grupo if x == 11)
        t12 = sum(1 for x in acertos_grupo if x == 12)
        t13 = sum(1 for x in acertos_grupo if x == 13)
        t14 = sum(1 for x in acertos_grupo if x == 14)
        t15 = sum(1 for x in acertos_grupo if x == 15)

        cd_1, cd_2, cd_3, cd_4 = st.columns(4)
        cd_1.metric("Média Geral de Acertos", f"{avg_hits:.2f} / 15", help="Média de dezenas sorteadas dentro do seu grupo atual de elite nos últimos 30 concursos.")
        cd_2.metric("Simulações com 11-12 Pts", f"{t11 + t12} vezes", delta=f"11 Pts: {t11} | 12 Pts: {t12}", delta_color="off")
        cd_3.metric("Simulações com 13 Pts", f"{t13} vezes", help="Quantidade de vezes que o grupo capturou 13 acertos.")
        cd_4.metric("Altas Premiações (14-15 Pts)", f"{t14 + t15} acertos", delta=f"14 Pts: {t14} | 15 Pts: {t15}", delta_color="inverse")

        st.markdown("#### 📊 Desempenho Histórico das Inteligências Ativas")
        c_e1, c_e2, c_e3, c_e4 = st.columns(4)
        c_e1.metric("1. Frequência/Tendência", f"{ia['perf']['Tendencia']:.2f} pts")
        c_e2.metric("2. Reversão Estatística", f"{ia['perf']['Reversao']:.2f} pts")
        c_e3.metric("3. Fechamento de Ciclo", f"{ia['perf']['Ciclo']:.2f} pts")
        c_e4.metric("4. Simetria de Borda", f"{ia['perf']['Simetria']:.2f} pts")
        
        st.markdown("#### 🔍 Dossiê Completo da Inteligência Artificial")
        top5_quentes = sorted(ia['freq'].items(), key=lambda x: x[1], reverse=True)[:5]
        str_quentes = ", ".join([f"{k:02d} ({v}x)" for k, v in top5_quentes])
        
        top5_atrasos = sorted(ia['atrasos'].items(), key=lambda x: x[1], reverse=True)[:5]
        str_atrasos = ", ".join([f"{k:02d} ({v} conc.)" for k, v in top5_atrasos])
        
        html_dossie = f"""
        <div style="background-color: #e8f4f8; border-left: 6px solid #1f77b4; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #1a1a1a;">
            <div style="margin-bottom: 8px;"><strong>🔥 Top 5 Dezenas mais Quentes:</strong> <span style="color: #d62728; font-weight: 500;">{str_quentes}</span></div>
            <div style="margin-bottom: 8px;"><strong>🧊 Top 5 Maiores Atrasos:</strong> <span style="color: #2ca02c; font-weight: 500;">{str_atrasos}</span></div>
            <div><strong>⏳ Status do Ciclo:</strong> Aberto há {ia['ciclo_tam']} concursos. <span style="color: #ff7f0e; font-weight: 500;">Faltam {len(ia['faltam_ciclo'])} dezenas para fechar: {ia['faltam_ciclo']}</span></div>
        </div>
        """
        st.markdown(html_dossie, unsafe_allow_html=True)

        # --- PAINEL DE DESEMPENHO DOS JOGOS ATIVOS (Aba 2) ---
        jogos_ativos = [j for j in st.session_state.data["jogos_salvos"] if j.get('status') == "Aguardando Sorteio"]
        if jogos_ativos:
            st.markdown("---")
            dezenas_ativos = [n for j in jogos_ativos for n in j["dezenas"]]
            render_performance_grid(dezenas_ativos, "🧬 Dezenas que a IA selecionou para os seus Jogos Ativos")
        else:
            st.info("Nenhum jogo ativo na fila no momento.")

        # --- NOVO PAINEL DE PESOS ESTILIZADO EM BADGES GIGANTES ---
        st.markdown("#### ⚖️ Grade Dinâmica de Pesos Absolutos (Heatmap de Atração da IA)")
        
        # Correção da Quebra de Markdown: Gerado em uma linha contínua para o Streamlit renderizar o HTML perfeitamente
        html_pesos = "<div style='display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; font-family: sans-serif; margin-bottom: 25px;'>"
        for n in range(1, 26):
            p_val = ia['pesos'].get(n, 0.0)
            no_grupo = n in ia['matriz_base']
            bg_color = "#d1e7dd" if no_grupo else "#f8f9fa"
            border_color = "#0f5132" if no_grupo else "#dee2e6"
            label_elite = "<span style='background-color:#0f5132; color:white; padding:2px 6px; font-size:10px; border-radius:4px; margin-left:5px;'>ELITE</span>" if no_grupo else ""
            
            html_pesos += f"<div style='background-color: {bg_color}; border: 2px solid {border_color}; border-radius: 8px; padding: 12px; text-align: center; color: #1a1a1a;'><span style='font-size: 20px; font-weight: bold; color: #111;'>{n:02d}</span>{label_elite}<br><span style='font-size: 13px; color: #444;'>Peso: <b>{p_val:.1f}</b></span></div>"
        
        html_pesos += "</div>"
        st.markdown(html_pesos, unsafe_allow_html=True)

    else: st.warning("Aguardando inserção de dados do Cofre na Aba 1.")
# --- TAB 3: GERADOR AUTÔNOMO ---
with tabs[2]:
    st.markdown("### 🚀 Engenharia Combinatória por Verba")
    if st.session_state.data["historico_dados"]:
        ia = raciocinio_total_ia(st.session_state.data["historico_dados"], st.session_state.data["ia_memoria"])
        st.write(f"Concurso Alvo Sincronizado: **{ia['alvo']}**")
        
        orcamento = st.number_input("Defina a verba máxima para geração (R$):", min_value=3.5, max_value=max(3.5, st.session_state.data['banca']), step=3.5)
        
        if st.button("🧬 DISPARAR MOTOR DE GERAÇÃO INÉDITA E ORTOGONAL", type="primary", use_container_width=True):
            if st.session_state.data['banca'] < orcamento:
                st.error("Banca insuficiente para a operação.")
            else:
                st.session_state.data['banca'] -= orcamento
                
                # Bloqueio histórico (Inteligência original mantida)
                # ESCUDO HISTÓRICO QUÂNTICO (Tabela Hash para velocidade na luz)
                historico_sets = {frozenset(h['dezenas']) for h in st.session_state.data['historico_dados']}
                jogos_neste_lote = [] # Armazena os jogos criados AGORA para a matemática Ortogonal
                gasto = 0.0
                
                while (orcamento - gasto) >= 3.5:
                    # Lógica financeira original (Trava de 16 e dinheiro)
                    tam = 16 if (orcamento - gasto) >= 56.0 and random.random() > 0.85 else 15
                    custo = 56.0 if tam == 16 else 3.5
                    
                    dezenas_disponiveis = ia['matriz_base']
                    pesos_sublista = [ia['pesos'][i] for i in dezenas_disponiveis]
                    
                    melhor_candidato = []
                    melhor_score = -999999
                    
                    # MÁQUINA ORTOGONAL: Gera 150 simulações internas para encontrar o jogo perfeito da rodada
                    for _ in range(150):
                        # 1. Cria protótipo puxando os pesos da IA
                        candidato = sorted(list(set(random.choices(dezenas_disponiveis, weights=pesos_sublista, k=tam))))
                        while len(candidato) < tam:
                            sobra = list(set(dezenas_disponiveis) - set(candidato))
                            if not sobra: break
                            candidato.append(random.choice(sobra))
                            candidato = sorted(list(set(candidato)))
                    
                        # 2. INTELIGÊNCIA DE INEDITISMO: Bloqueia na mesma hora se já saiu na história
                        if frozenset(candidato) in historico_sets: continue
                        
                        # 3. TEORIA DOS JOGOS: Impede o que o público joga. Rejeita 8 ou mais dezenas grudadas.
                        max_c = 1
                        atual_c = 1
                        for i in range(1, len(candidato)):
                            if candidato[i] == candidato[i-1] + 1:
                                atual_c += 1
                                max_c = max(max_c, atual_c)
                            else: atual_c = 1
                        if max_c > 7: continue # Prevenção contra rateio dividido (evita prêmio pequeno)

                        # 4. AVALIAÇÃO ORTOGONAL: Pontuação baseada na Força da IA menos a Repetição
                        score_ia = sum(ia['pesos'][n] for n in candidato)
                        penalidade_ortogonal = 0
                        
                        for jogo_ja_feito in jogos_neste_lote:
                            intersecao = len(set(candidato).intersection(jogo_ja_feito))
                            # Se bater 11 ou mais dezenas com um jogo que a IA acabou de gerar no mesmo lote, penaliza duro
                            if intersecao >= 11:
                                penalidade_ortogonal += (intersecao ** 3)
                        
                        ultimo_sorteio = st.session_state.data["historico_dados"][-1]["dezenas"] if st.session_state.data["historico_dados"] else []
                        score_dna, dna_texto_candidato = avaliar_dna_lotofacil(candidato, ultimo_sorteio)
                        score_final = score_ia + score_dna - penalidade_ortogonal
                        
                        # A IA seleciona apenas a combinação que tiver o maior Score Final
                        if score_final > melhor_score:
                            melhor_score = score_final
                            melhor_candidato = candidato
                            melhor_dna = dna_texto_candidato
                        
                    
                    # Fallback de proteção (Gatilho de segurança raríssimo)
                    if not melhor_candidato: melhor_candidato = sorted(random.sample(dezenas_disponiveis, tam))
                    
                    jogos_neste_lote.append(set(melhor_candidato))
                        
                    # Agora o jogo já nasce com o "DNA" da matriz que o criou
                    st.session_state.data["jogos_salvos"].append({
                        "id": str(uuid.uuid4()), 
                        "concurso_alvo": ia['alvo'], 
                        "dezenas": melhor_candidato,
                        "tamanho": tam, 
                        "estrategia": ia['cod_estrategia'], 
                        "justificativa": f"Matriz {ia['cod_estrategia']}. Cobertura Ortogonal Ativada. Sobreposição com outros bilhetes evitada (Teoria dos Jogos).",
                        "status": "Aguardando Sorteio", 
                        "acertos": 0, 
                        "premio_valor": 0.0,
                        "matriz_origem": st.session_state.data["matriz_viva_atual"], # <--- AQUI ESTÁ O DNA DO JOGO
                        "dna": melhor_dna if 'melhor_dna' in locals() else "🧬 DNA Não Biometrado"
                    })
                    gasto += custo
                st.success("Lote Inédito processado com Teoria dos Jogos e Matriz Ortogonal.")
                st.rerun()
    else: st.warning("Suba o Cofre na Aba 1.")
# --- TAB 4: FILA DE SORTEIO ---
with tabs[3]:
    st.markdown("### 🎫 Cartões Ativos e Auditados")
    
    # --- MÉTRICAS DE RESUMO DA FILA ---
    jogos_em_espera = [j for j in st.session_state.data["jogos_salvos"] if j.get('status') == "Aguardando Sorteio"]
    total_premio = sum(j.get("premio_valor", 0) for j in st.session_state.data["jogos_salvos"] if j.get('status') == "Premiado")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("🎫 Jogos em Espera", len(jogos_em_espera))
    c2.metric("💰 Premiação Total Acumulada", f"R$ {total_premio:.2f}")
    c3.metric("📊 Bilhetes Auditados", len([j for j in st.session_state.data["jogos_salvos"] if j.get('status') != "Aguardando Sorteio"]))
    
    # =====================================================================
    # MATRIZ QUE GEROU OS JOGOS (SEM GRÁFICOS, MOSTRA O RESULTADO REAL)
    # =====================================================================
    st.markdown("---")
    st.markdown("#### 🎯 A Matriz de Origem vs Sorteio Alvo")
    
    if st.session_state.data.get("jogos_salvos") and st.session_state.data.get("historico_dados"):
        num_ultimo_oficial = int(st.session_state.data["historico_dados"][-1]["concurso"])
        
        # Pega o alvo do ÚLTIMO jogo salvo na base (esteja ele em espera ou já auditado)
        ultimo_jogo_criado = st.session_state.data["jogos_salvos"][-1]
        alvo_foco = ultimo_jogo_criado.get("concurso_alvo")
        matriz_usada = ultimo_jogo_criado.get("matriz_origem")
        
        if matriz_usada:
            elite_group = set(matriz_usada)
            tamanho_matriz = len(elite_group)
            
            col_a1, col_a2 = st.columns([1, 2])
            
            # SE O SORTEIO ALVO JÁ ACONTECEU (E VOCÊ JÁ AUDITOU)
            if alvo_foco <= num_ultimo_oficial:
                resultado_oficial = next((h for h in st.session_state.data["historico_dados"] if int(h["concurso"]) == int(alvo_foco)), None)
                
                if resultado_oficial:
                    sorteio_real = set(resultado_oficial["dezenas"])
                    acertos_elite = len(elite_group.intersection(sorteio_real))
                    
                    with col_a1:
                        st.metric(label=f"Acertos da Matriz (Sorteio {alvo_foco})", value=f"{acertos_elite} / {tamanho_matriz}")
                    with col_a2:
                        st.write(f"**Matriz de {tamanho_matriz} dezenas usada para gerar os jogos:**")
                        st.code(", ".join([f"{n:02d}" for n in sorted(list(elite_group))]))
                    
                    if acertos_elite >= 11:
                        st.success(f"🎯 A Matriz de {tamanho_matriz} dezenas acertou {acertos_elite} pontos no concurso {alvo_foco}!")
                    else:
                        st.warning(f"A Matriz de {tamanho_matriz} dezenas não atingiu 11 pontos no concurso {alvo_foco}.")
            
            # SE O SORTEIO ALVO AINDA NÃO ACONTECEU (ESTÁ ESPERANDO)
            else:
                with col_a1:
                    st.metric(label=f"Sorteio Alvo", value=f"{alvo_foco}", delta="Aguardando Resultado...", delta_color="off")
                with col_a2:
                    st.write(f"**Matriz de {tamanho_matriz} dezenas que gerou seus jogos:**")
                    st.code(", ".join([f"{n:02d}" for n in sorted(list(elite_group))]))
        else:
            st.info("Os jogos atuais são antigos e não têm a Matriz salva.")
    else:
        st.info("Gere jogos na Aba 3 para visualizar a matriz de origem.")

    # =====================================================================
    # BOTÕES DE LIMPAR E EXPORTAR
    # =====================================================================
    if st.session_state.data["jogos_salvos"]:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.button("🗑️ LIMPAR ABSOLUTAMENTE TODOS OS JOGOS", on_click=cb_excluir_todos, type="secondary", use_container_width=True)
        with col_btn2:
            linhas_export = []
            for i, j in enumerate(st.session_state.data["jogos_salvos"], 1):
                dezenas = j.get('dezenas', [])
                qtd = len(dezenas)
                dezenas_formatadas = " - ".join([f"{n:02d}" for n in dezenas])
                linhas_export.append(f"📌 JOGO {i:02d} • ({qtd} Dezenas)\n{dezenas_formatadas}\n")
    
            conteudo_export = "\n".join(linhas_export)   
            st.download_button("📤 EXPORTAR JOGOS PARA APOSTA (TXT)", data=conteudo_export, file_name="Meus_Jogos_Loto.txt", type="primary", use_container_width=True)
        st.divider()
        
        for j in st.session_state.data["jogos_salvos"]:
            alvo = j.get('concurso_alvo')
            
            if j.get('status') == "Premiado":
                html_card = f"""
                <div style="border-top: 5px solid #28a745; background-color: #f8f9fa; border-left: 1px solid #dadce0; border-right: 1px solid #dadce0; border-bottom: 1px solid #dadce0; border-radius: 6px; padding: 15px; margin-bottom: 10px;">
                    <span style="color: #28a745; font-weight: bold; font-size: 14px;">✅ PREMIADO ({j.get('acertos')} Acertos) - R$ {j.get('premio_valor'):.2f}</span><br>
                    <span style="color: #4d5156; font-size: 13px; font-weight: 500;">Concurso Alvo: {alvo} | Grade: {j.get('tamanho')} Dezenas</span><br>
                    <span style="color: #5f6368; font-size: 12px;">Estratégia Operante: {j.get('estrategia')}</span><br>
                    <span style="color: #5f6368; font-size: 12px; font-style: italic;">Especificações da estratégia: {j.get('justificativa', 'Padrão autônomo.')}</span><br>
                    <span style="color: #006644; font-size: 13px; font-weight: bold;">{j.get('dna', '🧬 DNA Padrão Pós-Atualização')}</span>
                </div>
                """
            elif j.get('status') == "Não Premiado":
                html_card = f"""
                <div style="border-top: 5px solid #dc3545; background-color: #f8f9fa; border-left: 1px solid #dadce0; border-right: 1px solid #dadce0; border-bottom: 1px solid #dadce0; border-radius: 6px; padding: 15px; margin-bottom: 10px;">
                    <span style="color: #dc3545; font-weight: bold; font-size: 14px;">❌ NÃO PREMIADO ({j.get('acertos')} Acertos)</span><br>
                    <span style="color: #4d5156; font-size: 13px; font-weight: 500;">Concurso Alvo: {alvo} | Grade: {j.get('tamanho')} Dezenas</span><br>
                    <span style="color: #5f6368; font-size: 12px;">Estratégia Operante: {j.get('estrategia')}</span><br>
                    <span style="color: #5f6368; font-size: 12px; font-style: italic;">Especificações da estratégia: {j.get('justificativa', 'Padrão autônomo.')}</span><br>
                    <span style="color: #006644; font-size: 13px; font-weight: bold;">{j.get('dna', '🧬 DNA Padrão Pós-Atualização')}</span>
                </div>
                """
            else:
                html_card = f"""
                <div style="border-top: 5px solid #ffcc00; background-color: #f8f9fa; border-left: 1px solid #dadce0; border-right: 1px solid #dadce0; border-bottom: 1px solid #dadce0; border-radius: 6px; padding: 15px; margin-bottom: 10px;">
                    <span style="color: #1a73e8; font-weight: bold; font-size: 14px;">⏳ AGUARDANDO SORTEIO</span><br>
                    <span style="color: #4d5156; font-size: 13px; font-weight: 500;">Espera do Concurso Alvo: {alvo} | Grade: {j.get('tamanho')} Dezenas</span><br>
                    <span style="color: #5f6368; font-size: 12px;">Estratégia Operante: {j.get('estrategia')}</span><br>
                    <span style="color: #5f6368; font-size: 12px; font-style: italic;">Especificações da estratégia: {j.get('justificativa', 'Padrão autônomo.')}</span><br>
                    <span style="color: #006644; font-size: 13px; font-weight: bold;">{j.get('dna', '🧬 DNA Padrão Pós-Atualização')}</span>
                </div>
                """
            
            st.markdown(html_card, unsafe_allow_html=True)
            with st.container():
                st.code(" - ".join([f"{n:02d}" for n in j.get('dezenas', [])]))
                st.button("Apagar", key=f"del_{j['id']}", on_click=cb_excluir_jogo, args=(j['id'],))
                st.markdown("<br>", unsafe_allow_html=True)
    else: st.info("Sem bilhetes registrados na fila atual.")

# --- TAB 5: SINCRONIZAÇÃO E ENTRADA ---
with tabs[4]:
    st.markdown("### 🏆 Sincronização Oficial e Auditoria Pericial")
    
    col_sync1, col_sync2 = st.columns(2)
    
    with col_sync1:
        with st.container(border=True):
            st.markdown("#### 🌐 Sincronização Automática (API Caixa)")
            st.write("Conecta aos servidores da Caixa para baixar o último sorteio, atualizar o banco de dados e conferir todos os bilhetes na fila.")
            
            if st.button("🔄 Buscar Resultado e Auditar Bilhetes", type="primary", use_container_width=True):
                with st.spinner("Conectando à API da Caixa..."):
                    try:
                        resp = requests.get("https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest", verify=False, timeout=15)
                        if resp.status_code == 200:
                            ultimo_resultado = resp.json()
                            dezenas_oficiais = [int(x) for x in ultimo_resultado['dezenas']]
                            concurso_oficial = int(ultimo_resultado['concurso'])
                            
                            # Prepara pacote de dados
                            novo_dado = {
                                "concurso": concurso_oficial,
                                "data": ultimo_resultado['data'],
                                "dezenas": dezenas_oficiais,
                                "premiacoes": ultimo_resultado['premiacoes']
                            }
                            
                            # Verifica se já existe no histórico
                            existe = any(h['concurso'] == concurso_oficial for h in st.session_state.data["historico_dados"])
                            if not existe:
                                st.session_state.data["historico_dados"].append(novo_dado)
                                st.session_state.caixa_latest = novo_dado
                            else:
                                st.session_state.caixa_latest = novo_dado
                            
                            # Identifica valores de premiação oficiais
                            v11 = 7.0; v12 = 14.0; v13 = 35.0; v14 = 1500.0; v15 = 1500000.0
                            for p in ultimo_resultado['premiacoes']:
                                if p['acertos'] == 11: v11 = p['premio']
                                elif p['acertos'] == 12: v12 = p['premio']
                                elif p['acertos'] == 13: v13 = p['premio']
                                elif p['acertos'] == 14: v14 = p['premio']
                                elif p['acertos'] == 15: v15 = p['premio']
                                
                            # =========================================================
                            # AUDITORIA E APRENDIZADO DA IA (AUTOMÁTICO)
                            # =========================================================
                            relatorio_aprendizado = []
                            sorteio_set = set(dezenas_oficiais)
                            lucro_total = 0.0
                            
                            for j in st.session_state.data.get("jogos_salvos", []):
                                alvo_do_jogo = j.get('concurso_alvo')
                                pode_auditar = False
                                
                                # Lógica para auditar apenas jogos elegíveis
                                if str(alvo_do_jogo) == str(concurso_oficial) or (isinstance(alvo_do_jogo, int) and alvo_do_jogo <= concurso_oficial):
                                    pode_auditar = True
                                elif str(alvo_do_jogo) == "Legado":
                                    pode_auditar = True
                                    
                                if j.get('status') == "Aguardando Sorteio" and pode_auditar:
                                    pontos = len(set(j.get('dezenas', [])).intersection(sorteio_set))
                                    j['acertos'] = pontos
                                    j['premio_valor'] = calcular_premio_multiplo(j.get('tamanho', 15), pontos, v11, v12, v13, v14, v15)
                                    
                                    # --- O CÉREBRO APRENDE AQUI ---
                                    mapa_estrategias = {
                                        "Ciclo Otimizado": "Ciclo",
                                        "Tendência de Frequência": "Tendencia",
                                        "Reversão Estatística": "Reversao",
                                        "Simetria de Borda": "Simetria"
                                    }
                                    
                                    est_raw = j.get('estrategia', '')
                                    est_usada = mapa_estrategias.get(est_raw, est_raw)
                                    
                                    if est_usada in st.session_state.data["ia_memoria"]:
                                        st.session_state.data["ia_memoria"][est_usada]["pontos"] += pontos
                                        st.session_state.data["ia_memoria"][est_usada]["usos"] += 1
                                        relatorio_aprendizado.append(f"A métrica para **{est_usada}** aprendeu e calibrou pesos (Concurso API {concurso_oficial}: {pontos} pts).")
                                        
                                    if pontos >= 11:
                                        j['status'] = "Premiado"
                                        lucro_total += j['premio_valor']
                                        st.session_state.data["banca"] += j['premio_valor']
                                    else:
                                        j['status'] = "Não Premiado"
                            
                            # Salvar logs e dados forçadamente
                            if relatorio_aprendizado: 
                                st.session_state.ultimo_aprendizado = list(set(relatorio_aprendizado))
                                
                            salvar_dados(st.session_state.data) # O HD É ATUALIZADO AQUI
                            
                            if 'ia_memoria' in st.session_state: 
                                del st.session_state.ia_memoria # Força reload visual na Aba 2
                                
                            st.success(f"✅ Sincronização Automática Concluída! Inteligência treinada. Lucro creditado: R$ {lucro_total:.2f}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Erro na API da Caixa. Tente a inserção manual ao lado.")
                    except Exception as e:
                        st.error(f"Falha de conexão com a API: {e}")

    with col_sync2:
        with st.container(border=True):
            st.markdown("#### 🛠️ Inserção e Conferência Manual")
            st.write("Em caso de instabilidade na API, insira os dados do sorteio oficial manualmente para auditar seus bilhetes.")
            
            concurso_manual = st.number_input("Número do Concurso:", min_value=1, step=1, key="num_conc_manual")
            dezenas_texto = st.text_input("Dezenas Sorteadas (separadas por espaço ou vírgula):", key="dez_manual_input")
            
            if st.button("✅ Confirmar e Processar Conferência Manual", use_container_width=True):
                # Limpeza e extração das dezenas
                nums_str = dezenas_texto.replace(",", " ").split()
                try:
                    dezenas_oficiais = sorted([int(n) for n in nums_str])
                    if len(dezenas_oficiais) != 15:
                        st.error(f"Erro: Você digitou {len(dezenas_oficiais)} dezenas. É obrigatório inserir exatamente 15 dezenas.")
                    elif len(set(dezenas_oficiais)) != 15:
                        st.error("Erro: Existem dezenas repetidas. Verifique sua digitação.")
                    elif not all(1 <= n <= 25 for n in dezenas_oficiais):
                        st.error("Erro: As dezenas devem estar entre 01 e 25.")
                    else:
                        # =========================================================
                        # AUDITORIA E APRENDIZADO DA IA (MANUAL)
                        # =========================================================
                        sorteio_set = set(dezenas_oficiais)
                        lucro_total = 0.0
                        relatorio_aprendizado = []
                        
                        # Simula valores de prêmio padrão (já que a Caixa não envia na forma manual)
                        v11 = 7.0; v12 = 14.0; v13 = 35.0; v14 = 1500.0; v15 = 1500000.0
                        
                        for j in st.session_state.data.get("jogos_salvos", []):
                            alvo_do_jogo = j.get('concurso_alvo')
                            pode_auditar = False
                            
                            if str(alvo_do_jogo) == str(concurso_manual) or (isinstance(alvo_do_jogo, int) and alvo_do_jogo <= concurso_manual):
                                pode_auditar = True
                            elif str(alvo_do_jogo) == "Legado":
                                pode_auditar = True

                            if j.get('status') == "Aguardando Sorteio" and pode_auditar:
                                pontos = len(set(j.get('dezenas', [])).intersection(sorteio_set))
                                j['acertos'] = pontos
                                j['premio_valor'] = calcular_premio_multiplo(j.get('tamanho', 15), pontos, v11, v12, v13, v14, v15)
                                
                                # --- O CÉREBRO APRENDE AQUI ---
                                mapa_estrategias = {
                                    "Ciclo Otimizado": "Ciclo",
                                    "Tendência de Frequência": "Tendencia",
                                    "Reversão Estatística": "Reversao",
                                    "Simetria de Borda": "Simetria"
                                }
                                
                                est_raw = j.get('estrategia', '')
                                est_usada = mapa_estrategias.get(est_raw, est_raw)
                                
                                if est_usada in st.session_state.data["ia_memoria"]:
                                    st.session_state.data["ia_memoria"][est_usada]["pontos"] += pontos
                                    st.session_state.data["ia_memoria"][est_usada]["usos"] += 1
                                    relatorio_aprendizado.append(f"A métrica para **{est_usada}** aprendeu e calibrou pesos (Concurso Manual {concurso_manual}: {pontos} pts).")
                                
                                if pontos >= 11:
                                    j['status'] = "Premiado"
                                    lucro_total += j['premio_valor']
                                else: 
                                    j['status'] = "Não Premiado"
                        
                        # Insere no histórico se não existir
                        existe = any(h['concurso'] == concurso_manual for h in st.session_state.data["historico_dados"])
                        if not existe:
                            novo_dado = {
                                "concurso": concurso_manual,
                                "data": datetime.now().strftime("%d/%m/%Y"),
                                "dezenas": dezenas_oficiais,
                                "premiacoes": []
                            }
                            st.session_state.data["historico_dados"].append(novo_dado)
                            st.session_state.caixa_latest = novo_dado
                        
                        # Salvar logs e banca
                        st.session_state.data["banca"] += lucro_total
                        if relatorio_aprendizado: 
                            st.session_state.ultimo_aprendizado = list(set(relatorio_aprendizado))
                            
                        salvar_dados(st.session_state.data) # O HD É ATUALIZADO AQUI
                        
                        if 'ia_memoria' in st.session_state: 
                            del st.session_state.ia_memoria
                            
                        st.success(f"✅ Operação Manual Concluída. O banco de dados aprendeu as dezenas e R$ {lucro_total:.2f} foram creditados.")
                        st.rerun()
                        
                except ValueError:
                    st.error("Erro: Digite apenas números separados por espaço ou vírgula.")

    st.divider()

    # --- EXIBIÇÃO DE APRENDIZADO APÓS QUALQUER UMA DAS CONFERÊNCIAS ---
    if 'ultimo_aprendizado' in st.session_state and st.session_state.ultimo_aprendizado:
        st.markdown("#### 🧠 Informações absorvidas pela IA com o último resultado:")
        for aprendizado in st.session_state.ultimo_aprendizado:
            st.info(f"🧬 {aprendizado}")

    if 'caixa_latest' in st.session_state:
        r = st.session_state.caixa_latest
        st.markdown(f"#### 🏛️ Último Extrato Salvo da Caixa: Concurso {r['concurso']} ({r.get('data', '')})")
        st.code(" - ".join([f"{n:02d}" for n in r['dezenas']]))
        if r.get('premiacoes'):
            st.markdown("#### 💰 Tabela do Rateio Registrada")
            st.table(pd.DataFrame(r['premiacoes']))
