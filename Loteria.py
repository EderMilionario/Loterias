import streamlit as st
import pandas as pd
import requests
import json
import random
import uuid
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
            senha = st.text_input("Digite a Senha (admin123):", type="password")
            if st.button("ENTRAR NO SISTEMA", type="primary", use_container_width=True):
                if senha == "admin123":
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
# CÉREBRO MULTI-ESTRATÉGICO DA IA (4 Linhas de Análise)
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
    
    # Sincronização Absoluta do Concurso Alvo Baseado no Banco de Dados
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
tabs = st.tabs(["📂 1. Banco de Dados", "🧠 2. Cérebro Analítico (IA)", "🤖 3. Geração Autônoma", "📜 4. Fila de Sorteio", "🏆 5. Sincronização da Base"])

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
        st.info(f"**🎯 GRUPO DE ELITE ({ia['qtd_matriz']} DEZENAS):** {', '.join([f'{n:02d}' for n in ia['matriz_base']])}")

        st.markdown("#### 📊 Desempenho Histórico (Inteligências Ativas)")
        c_e1, c_e2, c_e3, c_e4 = st.columns(4)
        c_e1.metric("1. Frequência/Tendência", f"{ia['perf']['Tendencia']:.2f} pts")
        c_e2.metric("2. Reversão Estatística", f"{ia['perf']['Reversao']:.2f} pts")
        c_e3.metric("3. Fechamento de Ciclo", f"{ia['perf']['Ciclo']:.2f} pts")
        c_e4.metric("4. Simetria de Borda", f"{ia['perf']['Simetria']:.2f} pts")

        st.markdown("#### ⚙️ Parâmetros Volumétricos Oficiais (Últimos 10)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Massa de Soma", f"{ia['soma']:.1f}", delta="Equilíbrio: ~195")
        c2.metric("Massa Ímpar", f"{ia['impares']:.1f}", delta="Equilíbrio: ~7.5")
        c3.metric("Massa Primos", f"{ia['primos']:.1f}", delta="Equilíbrio: ~5.5")
        c4.metric("Massa Moldura", f"{ia['moldura']:.1f}", delta="Equilíbrio: ~10")
        
        st.error(f"⏳ **Rastreamento de Ciclo:** Aberto há {ia['ciclo_tam']} concursos. Dezenas restantes: {ia['faltam_ciclo']}")
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
                    # O erro de digitação ("tentatives") foi corrigido aqui:
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
                        "justificativa": f"Matriz adaptativa. Estratégia mestre: {ia['cod_estrategia']}.",
                        "status": "Aguardando Sorteio", "acertos": 0
                    })
                    gasto += custo
                st.success("Lote Inédito processado. O saldo foi deduzido.")
                st.rerun()
    else: st.warning("Suba o Cofre na Aba 1.")

# --- TAB 4: FILA DE SORTEIO (CARDS SEPARADOS) ---
with tabs[3]:
    st.markdown("### 🎫 Cartões Ativos e Auditados")
    if st.session_state.data["jogos_salvos"]:
        st.button("🗑️ LIMPAR ABSOLUTAMENTE TODOS OS JOGOS", on_click=cb_excluir_todos, type="secondary")
        st.divider()
        
        for j in reversed(st.session_state.data["jogos_salvos"]):
            status = j.get('status', 'Aguardando Sorteio')
            acertos = j.get('acertos', 0)
            alvo = j.get('concurso_alvo', 'N/A')
            
            if status == "Premiado":
                html_card = f"""
                <div style="background-color: #e6f4ea; border: 2px solid #137333; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
                    <span style="color: #137333; font-weight: bold; font-size: 14px;">🏆 PREMIADO: {acertos} ACERTOS</span><br>
                    <span style="color: #5f6368; font-size: 12px;">Alvo: {alvo} | Estratégia Operante: {j.get('estrategia')}</span>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                with st.container():
                    st.code(" - ".join([f"{n:02d}" for n in j.get('dezenas', [])]))
                    st.button("Remover Bilhete", key=f"del_{j['id']}", on_click=cb_excluir_jogo, args=(j['id'],))
                    st.markdown("<br>", unsafe_allow_html=True)
            
            elif status == "Não Premiado":
                html_card = f"""
                <div style="background-color: #f1f3f4; border: 1px solid #dadce0; border-radius: 6px; padding: 10px; margin-bottom: 5px; opacity: 0.75;">
                    <span style="color: #5f6368; font-weight: normal; font-size: 13px;">❌ Sem Premiação ({acertos} acertos)</span><br>
                    <span style="color: #70757a; font-size: 11px;">Alvo: {alvo}</span>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                with st.container():
                    st.text(" - ".join([f"{n:02d}" for n in j.get('dezenas', [])]))
                    st.button("Descartar", key=f"del_{j['id']}", on_click=cb_excluir_jogo, args=(j['id'],))
                    st.markdown("<br>", unsafe_allow_html=True)
                    
            else:
                html_card = f"""
                <div style="background-color: #f8f9fa; border-left: 5px solid #1a73e8; border-top: 1px solid #dadce0; border-right: 1px solid #dadce0; border-bottom: 1px solid #dadce0; border-radius: 4px; padding: 12px; margin-bottom: 10px;">
                    <span style="color: #1a73e8; font-weight: bold; font-size: 13px;">⏳ AGUARDANDO SORTEIO</span><br>
                    <span style="color: #5f6368; font-size: 11px;">Alvo: {alvo} | Grade: {j.get('tamanho')} Dezenas</span>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                with st.container():
                    st.code(" - ".join([f"{n:02d}" for n in j.get('dezenas', [])]))
                    st.button("Apagar", key=f"del_{j['id']}", on_click=cb_excluir_jogo, args=(j['id'],))
                    st.markdown("<br>", unsafe_allow_html=True)
    else: st.info("Sem bilhetes registrados na fila atual.")

# --- TAB 5: AUDITORIA REAL E ATUALIZAÇÃO DA BASE ---
with tabs[4]:
    st.markdown("### 🏆 Extração de Resultados, Pagamentos e Atualização do Banco")
    
    if st.button("🔄 SINCRONIZAR BASE COM A CAIXA ECONÔMICA", type="primary", use_container_width=True):
        with st.spinner("Conectando ao sistema de dados oficiais..."):
            try:
                res = requests.get("https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest", verify=False, timeout=10).json()
                st.session_state.caixa_latest = res
                
                concurso_oficial = int(res['concurso'])
                sorteio_oficial = set(map(int, res['dezenas']))
                
                # 1. EXPANSÃO DA BASE DE DADOS (Interligação)
                historico = st.session_state.data.get("historico_dados", [])
                ultimo_concurso_salvo = int(historico[-1]["concurso"]) if historico else 0
                
                if concurso_oficial > ultimo_concurso_salvo:
                    novo_concurso = {
                        "concurso": concurso_oficial,
                        "dezenas": sorted(list(sorteio_oficial)),
                        "data": res['data']
                    }
                    st.session_state.data["historico_dados"].append(novo_concurso)
                    st.toast(f"Concurso {concurso_oficial} anexado à sua base de dados histórica!", icon="🔄")
                
                # 2. AUDITORIA FINANCEIRA (Apostas Múltiplas + API Dinâmica)
                lucro_total = 0.0
                
                # Extraindo o valor exato pago pela Caixa na data de hoje
                v11, v12, v13, v14, v15 = 7.0, 14.0, 35.0, 1500.0, 1500000.0
                if 'premiacoes' in res:
                    for p in res['premiacoes']:
                        if p['acertos'] == 11: v11 = p['premio']
                        elif p['acertos'] == 12: v12 = p['premio']
                        elif p['acertos'] == 13: v13 = p['premio']
                        elif p['acertos'] == 14: v14 = p['premio']
                        elif p['acertos'] == 15: v15 = p['premio']
                
                for j in st.session_state.data.get("jogos_salvos", []):
                    # Só audita se o jogo estava aguardando e se o concurso oficial for o alvo ou mais novo
                    alvo_do_jogo = j.get('concurso_alvo')
                    pode_auditar = isinstance(alvo_do_jogo, int) and alvo_do_jogo <= concurso_oficial
                    if not isinstance(alvo_do_jogo, int): pode_auditar = True # Jogos antigos legados
                    
                    if j.get('status') == "Aguardando Sorteio" and pode_auditar:
                        pontos = len(set(j.get('dezenas', [])).intersection(sorteio_oficial))
                        j['acertos'] = pontos
                        tamanho_jogo = j.get('tamanho', 15)
                        
                        # Cálculo pericial incluindo múltiplas garantias se tiver 16 dezenas
                        premio_bilhete = calcular_premio_multiplo(tamanho_jogo, pontos, v11, v12, v13, v14, v15)
                        
                        # 3. O APRENDIZADO DA IA
                        est_usada = j.get('estrategia', 'Tendencia')
                        if est_usada in st.session_state.data["ia_memoria"]:
                            st.session_state.data["ia_memoria"][est_usada]["usos"] += 1
                            st.session_state.data["ia_memoria"][est_usada]["pontos"] += pontos
                        
                        if pontos >= 11:
                            j['status'] = "Premiado"
                            lucro_total += premio_bilhete
                        else: j['status'] = "Não Premiado"
                
                # 4. FECHAMENTO DO CAIXA E REINÍCIO FORÇADO DE INTEGRAÇÃO
                st.session_state.data["banca"] += lucro_total
                st.success(f"Operação Finalizada. A base foi atualizada, a IA aprendeu as lições e R$ {lucro_total:.2f} caíram na sua banca.")
                st.rerun() # <--- O SEGREDO: ISSO ATUALIZA TODAS AS ABAS NA MESMA HORA
                
            except Exception as e: st.error(f"Erro na conexão com os servidores da Caixa: {e}")

    if 'caixa_latest' in st.session_state:
        r = st.session_state.caixa_latest
        st.markdown(f"#### 🏛️ Extrato Oficial da Caixa: Concurso {r['concurso']} ({r['data']})")
        st.code(" - ".join(r['dezenas']))
        st.markdown("#### 💰 Tabela do Rateio Registrada")
        st.table(pd.DataFrame(r['premiacoes']))
