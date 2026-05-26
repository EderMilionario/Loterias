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
# CÉREBRA MULTI-ESTRATÉGICO DA IA (4 Linhas de Análise)
# =====================================================================
def raciocinio_total_ia(historico, memoria):
    if not historico: return None
    
    todas_dezenas = [n for h in historico for n in h['dezenas']]
    freq = Counter(todas_dezenas)
    freq_max = max(freq.values()) if freq else 1
    
    primos_lista = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    moldura_lista = [1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25]
    
    ultimos_10 = historico[-10:] if len(historico) >= 10 else historico
    media_soma = sum([sum(h['dezenas']) for h in ultimos_10]) / len(ultimos_10)
    media_impares = sum([sum(1 for n in h['dezenas'] if n % 2 != 0) for h in ultimos_10]) / len(ultimos_10)
    media_primos = sum([sum(1 for n in h['dezenas'] if n in primos_lista) for h in ultimos_10]) / len(ultimos_10)
    media_moldura = sum([sum(1 for n in h['dezenas'] if n in moldura_lista) for h in ultimos_10]) / len(ultimos_10)

    atrasos = {n: 0 for n in range(1, 26)}
    for h in reversed(historico):
        for n in range(1, 26):
            if n not in h['dezenas'] and atrasos[n] == 0: atrasos[n] += 1

    ciclo = set()
    jogos_ciclo = 0
    for h in reversed(historico):
        ciclo.update(h['dezenas'])
        jogos_ciclo += 1
        if len(ciclo) == 25: break
    faltam_ciclo = sorted(list(set(range(1, 26)) - ciclo))

    # --- TAMANHO DINÂMICO DA MATRIZ ---
    if len(faltam_ciclo) >= 9: qtd_matriz = 23
    elif len(faltam_ciclo) >= 6: qtd_matriz = 21
    elif len(faltam_ciclo) >= 3: qtd_matriz = 19
    else: qtd_matriz = 18

    # --- AVALIAÇÃO DE DESEMPENHO (MEMÓRIA) ---
    perf = {}
    for est in ["Tendencia", "Reversao", "Ciclo", "Simetria"]:
        usos = memoria.get(est, {}).get("usos", 0)
        pontos = memoria.get(est, {}).get("pontos", 0)
        perf[est] = pontos / usos if usos > 0 else 11.0 
        
    melhor_est = max(perf, key=perf.get)

    # --- MUTAÇÃO DE PESOS DA IA CONFORME DECISÃO ---
    if melhor_est == "Ciclo" and len(faltam_ciclo) > 0:
        estrategia = "Ciclo Otimizado"
        pesos = {i: 100 if i in faltam_ciclo else freq.get(i, 0) for i in range(1, 26)}
        motivo_est = "A IA priorizou o Fechamento de Ciclo. Dezenas ausentes receberam força máxima."
    elif melhor_est == "Simetria":
        estrategia = "Simetria de Borda"
        pesos = {i: freq.get(i, 0) + 30 if i in moldura_lista else freq.get(i, 0) for i in range(1, 26)}
        motivo_est = "A IA adotou o método de Simetria de Borda, focando nas extremidades do volante."
    elif melhor_est == "Reversao" or media_soma > 198:
        estrategia = "Reversão Estatística"
        pesos = {i: max(1, (freq_max - freq.get(i, 0)) + (atrasos.get(i, 0) * 5)) for i in range(1, 26)}
        motivo_est = "A IA ativou Reversão Estatística. Tendência forte de desaceleração de dezenas saturadas."
    else:
        estrategia = "Tendência de Frequência"
        pesos = {i: max(1, freq.get(i, 0) + 10) for i in range(1, 26)}
        motivo_est = "A IA escolheu seguir a Inércia de Frequência. Padrões quentes mantidos."

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
        
        if st.button("🧬 DISPARAR MOTOR DE GERAÇÃO INÉDITA", type="primary", use_container_width=True):
            if st.session_state.data['banca'] < orcamento:
                st.error("Banca insuficiente para a operação.")
            else:
                st.session_state.data['banca'] -= orcamento
                historico_sets = [set(h['dezenas']) for h in st.session_state.data["historico_dados"]]
                gasto = 0.0
                
                while (orcamento - gasto) >= 3.5:
                    tam = 16 if (orcamento - gasto) >= 56.0 and random.random() > 0.85 else 15
                    custo = 56.0 if tam == 16 else 3.5
                    
                    dezenas_disponiveis = ia['matriz_base']
                    pesos_sublista = [ia['pesos'][i] for i in dezenas_disponiveis]
                    
                    tentativas = 0
                    jogo_inedito = []
                    while tentativas < 1000:
                        candidato = sorted(list(set(random.choices(dezenas_disponiveis, weights=pesos_sublista, k=tam))))
                        while len(candidato) < tam:
                            sobra = list(set(dezenas_disponiveis) - set(candidato))
                            if not sobra: break
                            candidato.append(random.choice(sobra))
                            candidato = sorted(list(set(candidato)))
                        
                        if set(candidato) not in historico_sets:
                            jogo_inedito = candidato
                            break
                        tentativas += 1
                    
                    if not jogo_inedito: jogo_inedito = sorted(random.sample(dezenas_disponiveis, tam))
                        
                    st.session_state.data["jogos_salvos"].append({
                        "id": str(uuid.uuid4()), "concurso_alvo": ia['alvo'], "dezenas": jogo_inedito,
                        "tamanho": tam, "estrategia": ia['cod_estrategia'], 
                        "justificativa": f"Matriz adaptativa gerada sob influência direta do alvo {ia['alvo']}. Foco em {ia['cod_estrategia']} e pesos combinados.",
                        "status": "Aguardando Sorteio", "acertos": 0, "premio_valor": 0.0
                    })
                    gasto += custo
                st.success("Lote Inédito processado. O saldo foi deduzido.")
                st.rerun()
    else: st.warning("Suba o Cofre na Aba 1.")

# --- TAB 4: FILA DE SORTEIO ---
with tabs[3]:
    st.markdown("### 🎫 Cartões Ativos e Auditados")
    if st.session_state.data["jogos_salvos"]:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.button("🗑️ LIMPAR ABSOLUTAMENTE TODOS OS JOGOS", on_click=cb_excluir_todos, type="secondary", use_container_width=True)
        with col_btn2:
            conteudo_export = "\n".join([" ".join([f"{n:02d}" for n in j.get('dezenas', [])]) for j in st.session_state.data["jogos_salvos"]])
            st.download_button("📤 EXPORTAR JOGOS PARA APOSTA (TXT)", data=conteudo_export, file_name="Meus_Jogos_Loto.txt", type="primary", use_container_width=True)
            
        st.divider()
        
        for j in reversed(st.session_state.data["jogos_salvos"]):
            status = j.get('status', 'Aguardando Sorteio')
            acertos = j.get('acertos', 0)
            alvo = j.get('concurso_alvo', 'N/A')
            premio_ganho = j.get('premio_valor', 0.0)
            
            if status == "Premiado":
                html_card = f"""
                <div style="background-color: #e6f4ea; border: 2px solid #137333; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
                    <span style="color: #137333; font-weight: bold; font-size: 15px;">🏆 PREMIADO: {acertos} ACERTOS | Valor do Rateio: R$ {premio_ganho:.2f}</span><br>
                    <span style="color: #4d5156; font-size: 13px; font-weight: 500;">Espera do Concurso Alvo: {alvo}</span><br>
                    <span style="color: #5f6368; font-size: 12px;">Estratégia Operante: {j.get('estrategia')}</span><br>
                    <span style="color: #5f6368; font-size: 12px; font-style: italic;">Especificações da estratégia: {j.get('justificativa', 'Padrão autônomo.')}</span>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                with st.container():
                    st.code(" - ".join([f"{n:02d}" for n in j.get('dezenas', [])]))
                    st.button("Remover Bilhete", key=f"del_{j['id']}", on_click=cb_excluir_jogo, args=(j['id'],))
                    st.markdown("<br>", unsafe_allow_html=True)
            
            elif status == "Não Premiado":
                html_card = f"""
                <div style="background-color: #f1f3f4; border: 1px solid #dadce0; border-radius: 6px; padding: 12px; margin-bottom: 5px; opacity: 0.75;">
                    <span style="color: #5f6368; font-weight: normal; font-size: 14px;">❌ Sem Premiação ({acertos} acertos)</span><br>
                    <span style="color: #70757a; font-size: 12px; font-weight: 500;">Espera do Concurso Alvo: {alvo}</span><br>
                    <span style="color: #70757a; font-size: 11px;">Estratégia: {j.get('estrategia')}</span>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                with st.container():
                    st.text(" - ".join([f"{n:02d}" for n in j.get('dezenas', [])]))
                    st.button("Descartar", key=f"del_{j['id']}", on_click=cb_excluir_jogo, args=(j['id'],))
                    st.markdown("<br>", unsafe_allow_html=True)
                    
            else:
                html_card = f"""
                <div style="background-color: #f8f9fa; border-left: 5px solid #1a73e8; border-top: 1px solid #dadce0; border-right: 1px solid #dadce0; border-bottom: 1px solid #dadce0; border-radius: 6px; padding: 15px; margin-bottom: 10px;">
                    <span style="color: #1a73e8; font-weight: bold; font-size: 14px;">⏳ AGUARDANDO SORTEIO</span><br>
                    <span style="color: #4d5156; font-size: 13px; font-weight: 500;">Espera do Concurso Alvo: {alvo} | Grade: {j.get('tamanho')} Dezenas</span><br>
                    <span style="color: #5f6368; font-size: 12px;">Estratégia Operante: {j.get('estrategia')}</span><br>
                    <span style="color: #5f6368; font-size: 12px; font-style: italic;">Especificações da estratégia: {j.get('justificativa', 'Padrão autônomo.')}</span>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                with st.container():
                    st.code(" - ".join([f"{n:02d}" for n in j.get('dezenas', [])]))
                    st.button("Apagar", key=f"del_{j['id']}", on_click=cb_excluir_jogo, args=(j['id'],))
                    st.markdown("<br>", unsafe_allow_html=True)
    else: st.info("Sem bilhetes registrados na fila atual.")

# --- TAB 5: AUDITORIA REAL, ATUALIZAÇÃO DA BASE E ENTRADA MANUAL ---
with tabs[4]:
    st.markdown("### 🏆 Extração de Resultados, Pagamentos e Aprendizado da IA")
    
    # Módulos Colunados para Separação Clara das Funcionalidades
    col_sync1, col_sync2 = st.columns(2)
    
    with col_sync1:
        with st.container(border=True):
            st.markdown("#### 🔄 Captura Oficial da Caixa")
            st.write("Consulta automatizada em tempo real via servidores da API pública.")
            btn_caixa = st.button("🔄 SINCRONIZAR BASE COM A CAIXA ECONÔMICA", type="primary", use_container_width=True)
            
    with col_sync2:
        with st.container(border=True):
            st.markdown("#### ✍️ Entrada Manual de Resultados (Restaurado)")
            next_num = 1
            if st.session_state.data["historico_dados"]:
                next_num = int(st.session_state.data["historico_dados"][-1]["concurso"]) + 1
            
            c_m1, c_m2 = st.columns([1, 2])
            with c_m1:
                num_concurso_man = st.number_input("Nº Concurso", min_value=1, step=1, value=next_num, key="num_man")
            with c_m2:
                dezenas_man_str = st.text_input("15 Dezenas Sorteadas", placeholder="Ex: 01 02 03 05...", key="dez_man")
            
            btn_manual = st.button("📥 INSERIR RESULTADO MANUALMENTE E ATUALIZAR IA", type="secondary", use_container_width=True)

    # -----------------------------------------------------------------
    # PROCESSAMENTO 1: BOTÃO AUTOMÁTICO DA CAIXA
    # -----------------------------------------------------------------
    if btn_caixa:
        with st.spinner("Conectando ao sistema de dados oficiais..."):
            try:
                res = requests.get("https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest", verify=False, timeout=10).json()
                st.session_state.caixa_latest = res
                concurso_oficial = int(res['concurso'])
                sorteio_oficial = set(map(int, res['dezenas']))
                
                historico = st.session_state.data.get("historico_dados", [])
                ultimo_concurso_salvo = int(historico[-1]["concurso"]) if historico else 0
                
                if concurso_oficial > ultimo_concurso_salvo:
                    st.session_state.data["historico_dados"].append({
                        "concurso": concurso_oficial, "dezenas": sorted(list(sorteio_oficial)), "data": res['data']
                    })
                    st.toast(f"Concurso {concurso_oficial} anexado à base histórica!", icon="🔄")
                
                lucro_total = 0.0
                relatorio_aprendizado = []
                v11, v12, v13, v14, v15 = 7.0, 14.0, 35.0, 1500.0, 1500000.0
                if 'premiacoes' in res:
                    for p in res['premiacoes']:
                        if p['acertos'] == 11: v11 = p['premio']
                        elif p['acertos'] == 12: v12 = p['premio']
                        elif p['acertos'] == 13: v13 = p['premio']
                        elif p['acertos'] == 14: v14 = p['premio']
                        elif p['acertos'] == 15: v15 = p['premio']
                
                for j in st.session_state.data.get("jogos_salvos", []):
                    alvo_do_jogo = j.get('concurso_alvo')
                    pode_auditar = isinstance(alvo_do_jogo, int) and alvo_do_jogo <= concurso_oficial
                    if not isinstance(alvo_do_jogo, int): pode_auditar = True
                    
                    if j.get('status') == "Aguardando Sorteio" and pode_auditar:
                        pontos = len(set(j.get('dezenas', [])).intersection(sorteio_oficial))
                        j['acertos'] = pontos
                        premio_bilhete = calcular_premio_multiplo(j.get('tamanho', 15), pontos, v11, v12, v13, v14, v15)
                        j['premio_valor'] = premio_bilhete
                        
                        est_usada = j.get('estrategia', 'Tendencia')
                        if est_usada in st.session_state.data["ia_memoria"]:
                            st.session_state.data["ia_memoria"][est_usada]["usos"] += 1
                            st.session_state.data["ia_memoria"][est_usada]["pontos"] += pontos
                            relatorio_aprendizado.append(f"A métrica para **{est_usada}** foi calibrada (+1 simulação real com {pontos} pontos verificados).")
                        
                        if pontos >= 11:
                            j['status'] = "Premiado"
                            lucro_total += premio_bilhete
                        else: j['status'] = "Não Premiado"
                
                st.session_state.data["banca"] += lucro_total
                if relatorio_aprendizado: st.session_state.ultimo_aprendizado = list(set(relatorio_aprendizado))
                st.success(f"Operação Automatizada Concluída. Creditado R$ {lucro_total:.2f}")
                st.rerun()
            except Exception as e: st.error(f"Erro na conexão com os servidores da Caixa: {e}")

    # -----------------------------------------------------------------
    # PROCESSAMENTO 2: BOTÃO MANUAL RESTAURADO E INTEGRADO
    # -----------------------------------------------------------------
    if btn_manual:
        tokens = re.findall(r'\d+', dezenas_man_str)
        dezenas_man = sorted(list(set([int(t) for t in tokens if 1 <= int(t) <= 25])))
        
        if len(dezenas_man) != 15:
            st.error(f"Erro Crítico: Identificadas {len(dezenas_man)} dezenas exclusivas. Forneça exatamente 15 números válidos de 01 a 25.")
        else:
            concurso_oficial = int(num_concurso_man)
            sorteio_oficial = set(dezenas_man)
            
            historico = st.session_state.data.get("historico_dados", [])
            # Evita sobreposições idênticas
            if any(h['concurso'] == concurso_oficial for h in historico):
                st.warning(f"O concurso {concurso_oficial} já constava na base de dados. Os bilhetes associados pendentes serão reauditados.")
            else:
                st.session_state.data["historico_dados"].append({
                    "concurso": concurso_oficial, "dezenas": dezenas_man, "data": datetime.now().strftime("%d/%m/%Y")
                })
                st.toast(f"Concurso {concurso_oficial} inserido manualmente com sucesso!", icon="📥")
            
            lucro_total = 0.0
            relatorio_aprendizado = []
            v11, v12, v13, v14, v15 = 7.0, 14.0, 35.0, 1500.0, 1500000.0 # Valores base oficiais
            
            for j in st.session_state.data.get("jogos_salvos", []):
                alvo_do_jogo = j.get('concurso_alvo')
                pode_auditar = isinstance(alvo_do_jogo, int) and alvo_do_jogo <= concurso_oficial
                if not isinstance(alvo_do_jogo, int): pode_auditar = True
                
                if j.get('status') == "Aguardando Sorteio" and pode_auditar:
                    pontos = len(set(j.get('dezenas', [])).intersection(sorteio_oficial))
                    j['acertos'] = pontos
                    premio_bilhete = calcular_premio_multiplo(j.get('tamanho', 15), pontos, v11, v12, v13, v14, v15)
                    j['premio_valor'] = premio_bilhete
                    
                    est_usada = j.get('estrategia', 'Tendencia')
                    if est_usada in st.session_state.data["ia_memoria"]:
                        st.session_state.data["ia_memoria"][est_usada]["usos"] += 1
                        st.session_state.data["ia_memoria"][est_usada]["pontos"] += pontos
                        relatorio_aprendizado.append(f"A métrica para **{est_usada}** aprendeu e calibrou seus pesos com base no concurso manual {concurso_oficial} (+1 simulação com {pontos} acertos).")
                    
                    if pontos >= 11:
                        j['status'] = "Premiado"
                        lucro_total += premio_bilhete
                    else: j['status'] = "Não Premiado"
            
            st.session_state.data["banca"] += lucro_total
            if relatorio_aprendizado: st.session_state.ultimo_aprendizado = list(set(relatorio_aprendizado))
            st.success(f"Operação Pericial Manual Concluída. O banco de dados aprendeu as dezenas e R$ {lucro_total:.2f} foram computados na banca.")
            st.rerun()

    # --- EXIBIÇÃO DE APRENDIZADO APÓS QUALQUER UMA DAS CONFERÊNCIAS ---
    if 'ultimo_aprendizado' in st.session_state and st.session_state.ultimo_aprendizado:
        st.markdown("#### 🧠 Informações absorvidas pela IA com o novo resultado:")
        for aprendizado in st.session_state.ultimo_aprendizado:
            st.info(f"🧬 {aprendizado}")

    if 'caixa_latest' in st.session_state:
        r = st.session_state.caixa_latest
        st.markdown(f"#### 🏛️ Último Extrato Salvo da Caixa: Concurso {r['concurso']} ({r['data']})")
        st.code(" - ".join(r['dezenas']))
        st.markdown("#### 💰 Tabela do Rateio Registrada")
        st.table(pd.DataFrame(r['premiacoes']))
