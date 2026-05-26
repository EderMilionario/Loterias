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
# BLINDAGEM DE MEMÓRIA E SANITIZAÇÃO (Mata o KeyError)
# =====================================================================
def sanitizar_dados(d):
    if "banca" not in d: d["banca"] = 0.0
    if "historico_dados" not in d: d["historico_dados"] = []
    if "jogos_salvos" not in d: d["jogos_salvos"] = []
    if "matriz_viva_atual" not in d: d["matriz_viva_atual"] = []
    
    for j in d["jogos_salvos"]:
        if "id" not in j: j["id"] = str(uuid.uuid4())
        if "justificativa" not in j: j["justificativa"] = "Jogo legado."
        if "estrategia" not in j: j["estrategia"] = "Padrão"
        if "acertos" not in j: j["acertos"] = 0
        if "tamanho" not in j: j["tamanho"] = len(j.get("dezenas", []))
        if "status" not in j: j["status"] = "Aguardando Sorteio"
        if "concurso_alvo" not in j: j["concurso_alvo"] = "N/A"
    return d

if 'data' not in st.session_state:
    st.session_state.data = sanitizar_dados({})

# =====================================================================
# FUNÇÕES DE CALLBACK (Ações dos Botões Sem Erros)
# =====================================================================
def cb_depositar():
    st.session_state.data['banca'] += st.session_state.input_aporte
    st.toast(f"R$ {st.session_state.input_aporte:.2f} depositados!", icon="💰")

def cb_excluir_jogo(jogo_id):
    st.session_state.data['jogos_salvos'] = [j for j in st.session_state.data['jogos_salvos'] if j['id'] != jogo_id]
    st.toast("Jogo excluído com sucesso.", icon="🗑️")

def cb_excluir_todos():
    st.session_state.data['jogos_salvos'] = []
    st.toast("Fila de espera limpa.", icon="🧹")

def cb_carregar_cofre():
    if st.session_state.uploader_cofre:
        try:
            raw = json.load(st.session_state.uploader_cofre)
            st.session_state.data = sanitizar_dados(raw)
            st.toast("Cofre sincronizado e higienizado!", icon="✅")
        except:
            st.error("Erro crítico ao decodificar JSON.")

# =====================================================================
# MOTOR DE INTELIGÊNCIA PERICIAL (Cérebro Avançado)
# =====================================================================
def raciocinio_pericial_ia(historico):
    if not historico: return None
    
    todas_dezenas = [n for h in historico for n in h['dezenas']]
    freq = Counter(todas_dezenas)
    
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

    # --- DECISÃO DINÂMICA DA QUANTIDADE DA MATRIZ BASE ---
    # Se faltam muitas dezenas no ciclo, a IA expande a rede. Se faltam poucas, condensa.
    if len(faltam_ciclo) >= 4:
        qtd_matriz = 20
        motivo_qtd = f"A IA escolheu uma Matriz Base expandida de {qtd_matriz} dezenas porque o ciclo atual está aberto há {jogos_ciclo} concursos e necessita de maior cobertura de dezenas ausentes."
    else:
        qtd_matriz = 18
        motivo_qtd = f"A IA reduziu a Matriz Base para {qtd_matriz} dezenas. O ciclo está na reta final (faltam apenas {len(faltam_ciclo)}), permitindo focar o investimento nas tendências mais quentes."

    # Ordenação de Pesos para construir a Matriz de Elite
    if media_soma > 195:
        estrategia = "Reversão Estatística"
        pesos = {i: (100 - freq.get(i, 1)) + (atrasos.get(i, 0) * 2) for i in range(1, 26)}
        motivo_est = "Soma recente elevada. Modulando pesos para favorecer dezenas frias e baixas."
    else:
        estrategia = "Frequência Corrente"
        pesos = {i: freq.get(i, 1) + 10 for i in range(1, 26)}
        motivo_est = "Equilíbrio termodinâmico detectado. Priorizando blocos de alta frequência histórica."

    # Seleção das N dezenas da Matriz Base
    dezenas_ordenadas = sorted(range(1, 26), key=lambda x: pesos[x], reverse=True)
    matriz_base = sorted(dezenas_ordenadas[:qtd_matriz])

    ultimo_concurso = historico[-1]['concurso'] if historico else 0
    concurso_alvo = ultimo_concurso + 1

    return {
        "estrategia": estrategia, "motivo_est": motivo_est, "pesos": pesos, "freq": freq, 
        "atrasos": atrasos, "ciclo_tam": jogos_ciclo, "faltam_ciclo": faltam_ciclo,
        "soma": media_soma, "impares": media_impares, "primos": media_primos, 
        "moldura": media_moldura, "alvo": concurso_alvo, "total_dados": len(historico),
        "qtd_matriz": qtd_matriz, "motivo_qtd": motivo_qtd, "matriz_base": matriz_base
    }

# =====================================================================
# ABAS DE OPERAÇÃO
# =====================================================================
tabs = st.tabs(["📂 1. Banco de Dados & Caixa", "📊 2. Raciocínio & Matriz Base", "🤖 3. Engenharia de Lotes", "📜 4. Jogos Ativos (Fila)", "🏆 5. Auditoria Pericial"])

# --- TAB 1: GESTÃO ---
with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### 📥 Sincronização do Cofre")
            st.file_uploader("Arraste o seu Cofre.json para ativar a inteligência:", type="json", key="uploader_cofre", on_change=cb_carregar_cofre)
            st.info(f"📊 **Concursos Indexados no Histórico:** {len(st.session_state.data['historico_dados'])} resultados.")
            st.download_button("📤 Baixar Cópia Segura do Cofre", json.dumps(st.session_state.data), "Cofre.json", type="primary", use_container_width=True)
    with c2:
        with st.container(border=True):
            st.markdown("### 💳 Fluxo de Caixa / Banca")
            st.metric("Saldo Disponível para Operações", f"R$ {st.session_state.data['banca']:.2f}")
            st.number_input("Valor para Aporte / Depósito (R$):", min_value=0.0, step=10.0, key="input_aporte")
            st.button("CONFIRMAR DEPÓSITO", on_click=cb_depositar, use_container_width=True, type="secondary")

# --- TAB 2: PAINEL DA IA & MATRIZ ---
with tabs[1]:
    if st.session_state.data["historico_dados"]:
        ia = raciocinio_pericial_ia(st.session_state.data["historico_dados"])
        st.session_state.data["matriz_viva_atual"] = ia["matriz_base"] # Atualiza persistência
        
        st.markdown(f"### 🧠 Auditoria de Raciocínio da IA — Concurso Alvo: `{ia['alvo']}`")
        
        # Bloco da quantidade dinâmica exigida
        with st.chat_message("assistant"):
            st.markdown(f"**🎯 QUANTIDADE DE DEZENAS ESCOLHIDAS:** O sistema selecionou **{ia['qtd_matriz']} Dezenas** como Grupo de Elite.")
            st.caption(ia['motivo_qtd'])
            st.markdown(f"**🧬 MATRIZ VIVA SELECIONADA:**")
            st.subheader(f" {', '.join([f'{n:02d}' for n in ia['matriz_base']])}")

        st.markdown("---")
        st.markdown("#### ⚙️ Diretrizes Estatísticas Calculadas")
        st.info(f"**Filosofia do Lote:** {ia['estrategia']} | {ia['motivo_est']}")
        
        colA, colB, colC, colD = st.columns(4)
        colA.metric("Média Volumetria Soma", f"{ia['soma']:.1f}")
        colB.metric("Média Ímpares/Jogo", f"{ia['impares']:.1f}")
        colC.metric("Média Primos/Jogo", f"{ia['primos']:.1f}")
        colD.metric("Média Borda/Moldura", f"{ia['moldura']:.1f}")
    else: st.warning("Por favor, injete os dados do seu Cofre na Aba 1.")

# --- TAB 3: GERADOR ---
with tabs[2]:
    st.markdown("### 🚀 Algoritmo Combinatório por Orçamento")
    if st.session_state.data["historico_dados"]:
        ia = raciocinio_pericial_ia(st.session_state.data["historico_dados"])
        st.write(f"Operação dimensionada para o Concurso: **{ia['alvo']}**")
        
        orcamento = st.number_input("Orçamento Máximo Autorizado para esta Rodada (R$):", min_value=3.5, max_value=max(3.5, st.session_state.data['banca']), step=3.5)
        
        if st.button("PROCESSAR FILTROS E GERAR JOGOS", type="primary", use_container_width=True):
            if st.session_state.data['banca'] < orcamento:
                st.error("Saldo em banca insuficiente para cobrir o orçamento solicitado.")
            else:
                st.session_state.data['banca'] -= orcamento
                historico_sets = [set(h['dezenas']) for h in st.session_state.data["historico_dados"]]
                gasto = 0.0
                
                while (orcamento - gasto) >= 3.5:
                    tam = 16 if (orcamento - gasto) >= 56.0 and random.random() > 0.85 else 15
                    custo = 56.0 if tam == 16 else 3.5
                    
                    # Filtro Supremo: Puxa apenas os números de dentro da Matriz Viva da IA
                    dezenas_disponiveis = ia['matriz_base']
                    pesos_sublista = [ia['pesos'][i] for i in dezenas_disponiveis]
                    
                    # Laço de validação anti-repetição histórica
                    tentativas = 0
                    jogo_inedito = []
                    while tentativas < 1000:
                        candidato = sorted(list(set(random.choices(dezenas_disponiveis, weights=pesos_sublista, k=tam))))
                        while len(candidato) < tam:
                            sobra = list(set(dezenas_disponiveis) - set(candidato))
                            if not sobra: break
                            candidato.append(random.choice(sobra))
                            candidato = sorted(candidato)
                        
                        if set(candidato) not in historico_sets:
                            jogo_inedito = candidato
                            break
                        tentativas += 1
                    
                    if not jogo_inedito: 
                        jogo_inedito = sorted(random.sample(dezenas_disponiveis, tam)) # Fallback caso sature
                        
                    st.session_state.data["jogos_salvos"].append({
                        "id": str(uuid.uuid4()), "concurso_alvo": ia['alvo'], "dezenas": jogo_inedito,
                        "tamanho": tam, "estrategia": ia['estrategia'], "justificativa": ia['motivo_est'],
                        "status": "Aguardando Sorteio", "acertos": 0
                    })
                    gasto += custo
                
                st.success(f"Lote Processado! R$ {gasto:.2f} liquidados do saldo.")
                st.rerun()
    else: st.warning("Suba o Cofre na Aba 1.")

# --- TAB 4: FILA DE JOGOS (Cards Bonitos com Exclusão Real) ---
with tabs[3]:
    st.markdown("### 🎫 Cartões Prontos na Fila de Espera")
    if st.session_state.data["jogos_salvos"]:
        st.button("🚨 EXCLUIR TODO O LOTE ATUAL", on_click=cb_excluir_todos, type="secondary")
        st.divider()
        
        for j in st.session_state.data["jogos_salvos"]:
            with st.container(border=True):
                c_card, c_action = st.columns([5, 1])
                with c_card:
                    badge_cor = "green" if j['status'] == "Premiado" else "blue" if j['status'] == "Aguardando Sorteio" else "gray"
                    st.markdown(f"🎯 **Concurso Alvo:** `{j['concurso_alvo']}` | Volante de **{j['tamanho']} Dezenas** | Status: :{badge_cor}[{j['status']}]")
                    st.code(" - ".join([f"{n:02d}" for n in j['dezenas']]))
                    st.caption(f"💡 *Diretriz:* {j['justificativa']}")
                with c_action:
                    # O uso do on_click com o ID do jogo resolve o travamento
                    st.button("🗑️ Apagar", key=f"btn_del_{j['id']}", on_click=cb_excluir_jogo, args=(j['id'],), use_container_width=True)
    else: st.info("Não existem bilhetes pendentes de sorteio na memória.")

# --- TAB 5: AUDITORIA REAL ---
with tabs[4]:
    st.markdown("### 🏆 Sincronização Pericial e Performance da Matriz")
    
    if st.button("🔄 CONECTAR À CAIXA E AUDITAR", type="primary", use_container_width=True):
        with st.spinner("Conectando aos servidores oficiais..."):
            try:
                res = requests.get("https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest", verify=False, timeout=10).json()
                st.session_state.caixa_latest = res
                sorteio_oficial = set(map(int, res['dezenas']))
                
                # Conferência dos jogos e apuração de lucro
                retorno_financeiro = 0.0
                for j in st.session_state.data["jogos_salvos"]:
                    if j['status'] == "Aguardando Sorteio":
                        pontos = len(set(j['dezenas']).intersection(sorteio_oficial))
                        j['acertos'] = pontos
                        val_premio = {11: 6.0, 12: 12.0, 13: 30.0, 14: 2000.0, 15: 1500000.0}.get(pontos, 0.0)
                        
                        if pontos >= 11:
                            j['status'] = "Premiado"
                            retorno_financeiro += val_premio
                        else: j['status'] = "Não Premiado"
                
                st.session_state.data["banca"] += retorno_financeiro
                st.success(f"Auditoria Realizada! R$ {retorno_financeiro:.2f} inseridos no seu saldo.")
            except: st.error("Servidor da Caixa indisponível temporariamente.")

    if 'caixa_latest' in st.session_state:
        r = st.session_state.caixa_latest
        sorteio_set = set(map(int, r['dezenas']))
        
        # --- DESEMPENHO DA MATRIZ ESCOLHIDA ---
        if st.session_state.data["matriz_viva_atual"]:
            mv = set(st.session_state.data["matriz_viva_atual"])
            acertos_mv = len(mv.intersection(sorteio_set))
            st.markdown(f"""
            <div style="background-color: #ebf8ff; padding: 15px; border-radius: 5px; border-left: 5px solid #2b6cb0; margin-bottom: 15px;">
                <h4 style="margin:0; color:#2b6cb0;">📊 Desempenho do Grupo de Elite (Matriz Escolhida)</h4>
                <p style="margin:5px 0 0 0;">A IA separou <b>{len(mv)} dezenas</b> para trabalhar. Destas, <b>{acertos_mv} estavam entre as 15 sorteadas</b> oficiais.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"#### 🏛️ Resultado Oficial Caixa: Concurso {r['concurso']} ({r['data']})")
        st.code(" - ".join(r['dezenas']))
        st.markdown("#### 💰 Tabela Geral de Rateio Oficial")
        st.table(pd.DataFrame(r['premiacoes']))
