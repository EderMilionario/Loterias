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

    # --- AVALIAÇÃO DE DESEMPENHO DE RECOMPENSA (4 ESTRATÉGIAS) ---
    perf = {}
    for est in ["Tendencia", "Reversao", "Ciclo", "Simetria"]:
        usos = memoria.get(est, {}).get("usos", 0)
        pontos = memoria.get(est, {}).get("pontos", 0)
        perf[est] = pontos / usos if usos > 0 else 11.0 # Peso neutro inicial de 11 pts
        
    melhor_est = max(perf, key=perf.get)

    # --- MUTAÇÃO DE PESOS DA IA CONFORME DECISÃO DE LINHA ---
    if melhor_est == "Ciclo" and len(faltam_ciclo) > 0:
        estrategia = "Ciclo Otimizado"
        pesos = {i: 100 if i in faltam_ciclo else freq.get(i, 0) for i in range(1, 26)}
        motivo_est = "A IA priorizou o Fechamento de Ciclo. Dezenas ausentes receberam força máxima de atração."
    elif melhor_est == "Simetria":
        estrategia = "Simetria de Borda"
        pesos = {i: freq.get(i, 0) + 30 if i in moldura_lista else freq.get(i, 0) for i in range(1, 26)}
        motivo_est = "A IA adotou o método de Simetria de Borda, focando o fechamento do volante nas extremidades."
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
tabs = st.tabs(["📂 1. Banco de Dados", "🧠 2. Cérebro Analítico (IA)", "🤖 3. Geração Autônoma", "📜 4. Fila de Sorteio (Cards)", "🏆 5. Sincronização & Auditoria"])

# --- TAB 1: BANCO DE DADOS ---
with tabs[0]:
    st.markdown("### 💾 Central de Dados e Ajuste Financeiro")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.file_uploader("📥 Carregar Arquivo Cofre.json", type="json", key="uploader_cofre", on_change=cb_carregar_cofre)
            st.info(f"📊 **Total de Registros Oficiais em Memória:** {len(st.session_state.data['historico_dados'])} concursos.")
            st.download_button("📤 Baixar e Atualizar Backup do Cofre", json.dumps(st.session_state.data), "Cofre.json", type="primary", use_container_width=True)
    with c2:
        with st.container(border=True):
            st.metric("💰 Saldo em Banca", f"R$ {st.session_state.data['banca']:.2f}")
            st.number_input("Valor para Depósito Imediato (R$):", min_value=0.0, step=10.0, key="input_aporte")
            st.button("AUTORIZAR DEPÓSITO", on_click=cb_depositar, use_container_width=True)

# --- TAB 2: CÉREBRO ANALÍTICO ---
with tabs[1]:
    if st.session_state.data["historico_dados"]:
        ia = raciocinio_total_ia(st.session_state.data["historico_dados"], st.session_state.data["ia_memoria"])
        st.session_state.data["matriz_viva_atual"] = ia["matriz_base"]
        
        st.markdown(f"### 🧠 Diagnóstico de Cenário da IA para o Concurso Alvo `{ia['alvo']}`")
        
        st.success(f"**⚡ LINHA TÁTICA ATIVADA:** {ia['estrategia']} \n\n**DIRETRIZ DA DECISÃO:** {ia['motivo_est']}")
        st.info(f"**🎯 GRUPO DE ELITE SELECIONADO ({ia['qtd_matriz']} DEZENAS):** {', '.join([f'{n:02d}' for n in ia['matriz_base']])}")

        st.markdown("#### 📊 Desempenho Histórico das 4 Inteligências Ativas")
        c_e1, c_e2, c_e3, c_e4 = st.columns(4)
        c_e1.metric("1. Frequência/Tendência", f"{ia['perf']['Tendencia']:.2f} pts")
        c_e2.metric("2. Reversão Estatística", f"{ia['perf']['Reversao']:.2f} pts")
        c_e3.metric("3. Fechamento de Ciclo", f"{ia['perf']['Ciclo']:.2f} pts")
        c_e4.metric("4. Simetria de Borda", f"{ia['perf']['Simetria']:.2f} pts")

        st.markdown("#### ⚙️ Parâmetros Volumétricos e de Massa do Sorteio")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Massa de Soma (Ideal: 195)", f"{ia['soma']:.1f}")
        c2.metric("Massa Ímpar (Ideal: 7.5)", f"{ia['impares']:.1f}")
        c3.metric("Massa Primos (Ideal: 5.5)", f"{ia['primos']:.1f}")
        c4.metric("Massa Moldura (Ideal: 10)", f"{ia['moldura']:.1f}")
        
        st.error(f"⏳ **Rastreamento de Ciclo:** Aberto há {ia['ciclo_tam']} concursos. Dezenas bloqueadas restantes: {ia['faltam_ciclo']}")
        st.bar_chart(pd.DataFrame.from_dict(ia['pesos'], orient='index', columns=['Vetor de Força']))
    else: st.warning("Aguardando inserção de dados do Cofre na Aba 1.")

# --- TAB 3: GERADOR ---
with tabs[2]:
    st.markdown("### 🚀 Engenharia Combinatória por Verba")
    if st.session_state.data["historico_dados"]:
        ia = raciocinio_total_ia(st.session_state.data["historico_dados"], st.session_state.data["ia_memoria"])
        st.write(f"Preparando matriz para o Concurso Alvo: **{ia['alvo']}**")
        
        orcamento = st.number_input("Defina a verba máxima para este processamento (R$):", min_value=3.5, max_value=max(3.5, st.session_state.data['banca']), step=3.5)
        
        if st.button("🧬 DISPARAR MOTOR DE GERAÇÃO INÉDITA", type="primary", use_container_width=True):
            if st.session_state.data['banca'] < orcamento:
                st.error("Banca insuficiente.")
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
                    while tentatives < 1000:
                        candidato = sorted(list(set(random.choices(dezenas_disponiveis, weights=pesos_sublista, k=tam))))
                        while len(candidato) < tam:
                            sobra = list(set(dezenas_disponiveis) - set(candidato))
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
                        "justificativa": f"Abordagem: {ia['estrategia']} dentro de matriz compacta.",
                        "status": "Aguardando Sorteio", "acertos": 0
                    })
                    gasto += custo
                st.success("Lote gerado sem repetições históricas.")
                st.rerun()
    else: st.warning("Suba o Cofre na Aba 1.")

# --- TAB 4: FILA DE SORTEIO (CARDS SEPARADOS) ---
with tabs[3]:
    st.markdown("### 🎫 Cartões Ativos em Fila")
    if st.session_state.data["jogos_salvos"]:
        st.button("🗑️ LIMPAR ABSOLUTAMENTE TODOS OS JOGOS", on_click=cb_excluir_todos, type="secondary")
        st.divider()
        
        for j in st.session_state.data["jogos_salvos"]:
            status = j.get('status', 'Aguardando Sorteio')
            acertos = j.get('acertos', 0)
            
            # SEPARAÇÃO VISUAL DE ACORDO COM O STATUS DO BILHETE
            if status == "Premiado":
                # CARD PREMIUM (Vencedores): Fundo verde suave, borda verde-escura, destaque dourado
                html_card = f"""
                <div style="background-color: #e6f4ea; border: 2px solid #137333; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
                    <span style="color: #137333; font-weight: bold; font-size: 14px;">🏆 BILHETE PREMIADO — {acertos} ACERTOS</span><br>
                    <span style="color: #5f6368; font-size: 12px;">Concurso Alvo: {j.get('concurso_alvo')} | Estratégia: {j.get('estrategia')}</span>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                with st.container():
                    st.code(" - ".join([f"{n:02d}" for n in j.get('dezenas', [])]))
                    st.caption(f"💡 Raciocínio Aplicado: {j.get('justificativa')}")
                    st.button("Remover Bilhete", key=f"del_{j['id']}", on_click=cb_excluir_jogo, args=(j['id'],))
                    st.markdown("<br>", unsafe_allow_html=True)
            
            elif status == "Não Premiado":
                # CARD SIMPLES (Perdedores): Fundo cinza opaco, bordas apagadas, sem destaques visuais
                html_card = f"""
                <div style="background-color: #f1f3f4; border: 1px solid #dadce0; border-radius: 6px; padding: 10px; margin-bottom: 5px; opacity: 0.75;">
                    <span style="color: #5f6368; font-weight: normal; font-size: 13px;">❌ Sem Premiação ({acertos} acertos)</span><br>
                    <span style="color: #70757a; font-size: 11px;">Alvo: {j.get('concurso_alvo')}</span>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                with st.container():
                    st.text(" - ".join([f"{n:02d}" for n in j.get('dezenas', [])]))
                    st.button("Descartar", key=f"del_{j['id']}", on_click=cb_excluir_jogo, args=(j['id'],))
                    st.markdown("<br>", unsafe_allow_html=True)
                    
            else:
                # CARD PADRÃO: Bilhetes ainda aguardando a extração oficial (Borda azul)
                html_card = f"""
                <div style="background-color: #f8f9fa; border-left: 5px solid #1a73e8; border-top: 1px solid #dadce0; border-right: 1px solid #dadce0; border-bottom: 1px solid #dadce0; border-radius: 4px; padding: 12px; margin-bottom: 10px;">
                    <span style="color: #1a73e8; font-weight: bold; font-size: 13px;">⏳ AGUARDANDO EXTRAÇÃO OFICIAL</span><br>
                    <span style="color: #5f6368; font-size: 11px;">Concurso Alvo: {j.get('concurso_alvo')} | Grade: {j.get('tamanho')} Dezenas</span>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                with st.container():
                    st.code(" - ".join([f"{n:02d}" for n in j.get('dezenas', [])]))
                    st.button("Remover da Fila", key=f"del_{j['id']}", on_click=cb_excluir_jogo, args=(j['id'],))
                    st.markdown("<br>", unsafe_allow_html=True)
    else: st.info("Sem bilhetes registrados na fila atual.")

# --- TAB 5: AUDITORIA REAL & INTEGRAÇÃO ---
with tabs[4]:
    st.markdown("### 🏆 Sincronização Pericial da Rede de Dados")
    
    if st.button("🔄 EXECUTAR SINCRONIZAÇÃO COMPLETA DA CAIXA", type="primary", use_container_width=True):
        with st.spinner("Processando teias de dados oficiais..."):
            try:
                res = requests.get("https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest", verify=False, timeout=10).json()
                st.session_state.caixa_latest = res
                
                concurso_oficial = int(res['concurso'])
                sorteio_oficial = set(map(int, res['dezenas']))
                
                # --- CORREÇÃO DA SINCRONIZAÇÃO DA BASE DE DADOS (ABAS INTEGRADAS) ---
                historico = st.session_state.data.get("historico_dados", [])
                ultimo_concurso_salvo = int(historico[-1]["concurso"]) if historico else 0
                
                if concurso_oficial > ultimo_concurso_salvo:
                    novo_concurso = {
                        "concurso": concurso_oficial,
                        "dezenas": sorted(list(sorteio_oficial)),
                        "data": res['data']
                    }
                    st.session_state.data["historico_dados"].append(novo_concurso)
                    st.toast(f"Banco de Dados integrado para {concurso_oficial} concursos!", icon="🔄")
                
                # Apuração e processamento financeiro
                lucro = 0.0
                for j in st.session_state.data.get("jogos_salvos", []):
                    if j.get('status') == "Aguardando Sorteio":
                        pontos = len(set(j.get('dezenas', [])).intersection(sorteio_oficial))
                        j['acertos'] = pontos
                        
                        est_usada = j.get('estrategia', 'Tendencia')
                        if est_usada in st.session_state.data["ia_memoria"]:
                            st.session_state.data["ia_memoria"][est_usada]["usos"] += 1
                            st.session_state.data["ia_memoria"][est_usada]["points"] = st.session_state.data["ia_memoria"][est_usada].get("points", 0) + pontos
                            st.session_state.data["ia_memoria"][est_usada]["pontos"] = st.session_state.data["ia_memoria"][est_usada]["points"]
                        
                        premio = {11: 6.0, 12: 12.0, 13: 30.0, 14: 2000.0, 15: 1500000.0}.get(pontos, 0.0)
                        if pontos >= 11:
                            j['status'] = "Premiado"
                            lucro += premio
                        else: j['status'] = "Não Premiado"
                
                st.session_state.data["banca"] += lucro
                st.success(f"Sincronização executada. O histórico geral da base foi estendido para {len(st.session_state.data['historico_dados'])} resultados!")
                st.rerun()
            except Exception as e: st.error(f"Erro na conexão pericial: {e}")

    if 'caixa_latest' in st.session_state:
        r = st.session_state.caixa_latest
        st.markdown(f"#### 🏛️ Último Registro Gravado da Caixa: Concurso {r['concurso']} ({r['data']})")
        st.code(" - ".join(r['dezenas']))
        st.markdown("#### 💰 Tabela do Rateio Oficial")
        st.table(pd.DataFrame(r['premiacoes']))
