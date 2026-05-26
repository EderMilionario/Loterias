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
# BLINDAGEM DE MEMÓRIA E SANITIZAÇÃO
# =====================================================================
def sanitizar_dados(d):
    if "banca" not in d: d["banca"] = 0.0
    if "historico_dados" not in d: d["historico_dados"] = []
    if "jogos_salvos" not in d: d["jogos_salvos"] = []
    if "matriz_viva_atual" not in d: d["matriz_viva_atual"] = []
    if "ia_memoria" not in d: 
        d["ia_memoria"] = {"Tendencia": {"usos": 0, "pontos": 0}, "Reversao": {"usos": 0, "pontos": 0}}
    
    for j in d["jogos_salvos"]:
        if "id" not in j: j["id"] = str(uuid.uuid4())
        if "status" not in j: j["status"] = "Aguardando Sorteio"
        if "acertos" not in j: j["acertos"] = 0
    return d

if 'data' not in st.session_state:
    st.session_state.data = sanitizar_dados({})

# =====================================================================
# FUNÇÕES DE CALLBACK (Botões sem bugs)
# =====================================================================
def cb_depositar():
    valor = st.session_state.get("input_aporte", 0.0)
    if valor > 0:
        st.session_state.data['banca'] += valor
        st.toast(f"R$ {valor:.2f} creditados com sucesso!", icon="💰")

def cb_excluir_jogo(jogo_id):
    st.session_state.data['jogos_salvos'] = [j for j in st.session_state.data['jogos_salvos'] if j['id'] != jogo_id]
    st.toast("Jogo excluído permanentemente.", icon="🗑️")

def cb_excluir_todos():
    st.session_state.data['jogos_salvos'] = []
    st.toast("Fila de espera apagada.", icon="🧹")

def cb_carregar_cofre():
    file = st.session_state.uploader_cofre
    if file:
        try:
            st.session_state.data = sanitizar_dados(json.load(file))
            st.toast("Cofre sincronizado e higienizado com sucesso!", icon="✅")
        except: st.error("Erro crítico ao ler o arquivo JSON.")

# =====================================================================
# CÉREBRO DA IA (Análise Total, Livre e Protegida)
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

    # Atrasos e Ciclos
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

    # --- LIBERDADE DA IA: TAMANHO DA MATRIZ DINÂMICO ---
    # A IA analisa o "caos" do ciclo para definir o tamanho da rede.
    if len(faltam_ciclo) >= 9: qtd_matriz = 23
    elif len(faltam_ciclo) >= 6: qtd_matriz = 21
    elif len(faltam_ciclo) >= 3: qtd_matriz = 19
    else: qtd_matriz = 17

    # --- APRENDIZADO E PESOS (Blindados contra valores negativos) ---
    pts_tend = memoria["Tendencia"]["pontos"] / max(1, memoria["Tendencia"]["usos"])
    pts_rev = memoria["Reversao"]["pontos"] / max(1, memoria["Reversao"]["usos"])
    
    # Decide baseado na memória e na soma recente
    if media_soma > 198 or pts_rev > pts_tend:
        estrategia = "Reversão Estatística"
        # max(1, x) garante que o peso NUNCA seja zero ou negativo
        pesos = {i: max(1, (freq_max - freq.get(i, 0)) + (atrasos.get(i, 0) * 5)) for i in range(1, 26)}
        motivo_est = f"Memória de Reversão alta ({pts_rev:.1f} pts) ou Soma Estourada ({media_soma:.1f}). Focando em atrasadas."
    else:
        estrategia = "Tendência de Frequência"
        pesos = {i: max(1, freq.get(i, 0) + 10) for i in range(1, 26)}
        motivo_est = f"Soma equilibrada ({media_soma:.1f}) e/ou Memória favorável. Aproveitando a inércia das dezenas quentes."

    # Seleciona o Grupo de Elite baseado na liberdade de qtd_matriz
    dezenas_ordenadas = sorted(range(1, 26), key=lambda x: pesos[x], reverse=True)
    matriz_base = sorted(dezenas_ordenadas[:qtd_matriz])
    
    motivo_qtd = f"Como faltam {len(faltam_ciclo)} dezenas para o ciclo, a IA estabeleceu dinamicamente a Matriz em {qtd_matriz} dezenas."

    alvo = (historico[-1]['concurso'] + 1) if historico else 1

    return {
        "estrategia": estrategia, "motivo_est": motivo_est, "pesos": pesos, "freq": freq, 
        "atrasos": atrasos, "ciclo_tam": jogos_ciclo, "faltam_ciclo": faltam_ciclo,
        "soma": media_soma, "impares": media_impares, "primos": media_primos, 
        "moldura": media_moldura, "alvo": alvo, "qtd_matriz": qtd_matriz, 
        "motivo_qtd": motivo_qtd, "matriz_base": matriz_base, "pts_tend": pts_tend, "pts_rev": pts_rev
    }

# =====================================================================
# ABAS DE OPERAÇÃO
# =====================================================================
st.markdown("<h2 style='text-align: center; color: #1f77b4;'>🧬 LotoMatrix PRO - Agente Autônomo</h2>", unsafe_allow_html=True)
tabs = st.tabs(["📂 1. Banco de Dados", "🧠 2. Cérebro Analítico (IA)", "🤖 3. Geração Autônoma", "📜 4. Fila de Espera", "🏆 5. Sincronização & Rateio"])

# --- TAB 1: GESTÃO ---
with tabs[0]:
    st.markdown("### 💾 Gestão Central e Banca")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.file_uploader("📥 Carregar Cofre.json (Ativar Inteligência)", type="json", key="uploader_cofre", on_change=cb_carregar_cofre)
            st.info(f"📊 **Dados Oficiais na Memória:** {len(st.session_state.data['historico_dados'])} concursos.")
            st.download_button("📤 Fazer Backup do Cofre", json.dumps(st.session_state.data), "Cofre_Atualizado.json", type="primary", use_container_width=True)
    with c2:
        with st.container(border=True):
            st.metric("💰 Saldo em Banca", f"R$ {st.session_state.data['banca']:.2f}")
            st.number_input("Adicionar Saldo (R$):", min_value=0.0, step=10.0, key="input_aporte")
            st.button("CONFIRMAR APORTE", on_click=cb_depositar, use_container_width=True)

# --- TAB 2: CÉREBRO ANALÍTICO (TUDO) ---
with tabs[1]:
    if st.session_state.data["historico_dados"]:
        ia = raciocinio_total_ia(st.session_state.data["historico_dados"], st.session_state.data["ia_memoria"])
        st.session_state.data["matriz_viva_atual"] = ia["matriz_base"]
        
        st.markdown(f"### 🧠 O Raio-X da Inteligência — Preparação Concurso `{ia['alvo']}`")
        
        # O que ela aprendeu
        st.markdown("#### 1️⃣ Memória de Aprendizado (O que funcionou no passado)")
        c_m1, c_m2 = st.columns(2)
        c_m1.info(f"**Performance da Estratégia TENDÊNCIA:** {ia['pts_tend']:.1f} pontos de média.")
        c_m2.warning(f"**Performance da Estratégia REVERSÃO:** {ia['pts_rev']:.1f} pontos de média.")
        
        # A Decisão da Matriz
        st.markdown("#### 2️⃣ Decisão e Matriz Dinâmica")
        st.success(f"**Decisão da IA:** {ia['estrategia']} | {ia['motivo_est']}")
        st.success(f"**Liberdade de Matriz:** {ia['motivo_qtd']} \n\n**Dezenas Escolhidas:** {', '.join([f'{n:02d}' for n in ia['matriz_base']])}")

        # Painel Profundo
        st.markdown("#### 3️⃣ Leitura do Comportamento Global (Últimos 10 concursos)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Soma Global", f"{ia['soma']:.1f}", delta="Ideal: 195", delta_color="off")
        c2.metric("Ímpares", f"{ia['impares']:.1f}", delta="Ideal: 7.5", delta_color="off")
        c3.metric("Primos", f"{ia['primos']:.1f}", delta="Ideal: 5.5", delta_color="off")
        c4.metric("Moldura", f"{ia['moldura']:.1f}", delta="Ideal: 10", delta_color="off")
        
        st.markdown("#### 4️⃣ O Caos do Ciclo Atual")
        st.error(f"O ciclo está aberto há **{ia['ciclo_tam']}** sorteios. Faltam {len(ia['faltam_ciclo'])} dezenas para fechar: {ia['faltam_ciclo']}")

        st.markdown("#### 5️⃣ O Mapa de Pesos Internos da IA")
        st.write("*(Esta tabela mostra os pesos matemáticos exatos gerados agora. Bolas com peso maior são sugadas para a matriz).*")
        df_pesos = pd.DataFrame.from_dict(ia['pesos'], orient='index', columns=['Peso Atribuído']).sort_index()
        st.bar_chart(df_pesos)
    else: st.warning("Por favor, carregue o Cofre na Aba 1 para ativar o Cérebro.")

# --- TAB 3: GERAÇÃO AUTÔNOMA ---
with tabs[2]:
    st.markdown("### 🚀 Algoritmo Combinatório Seguro")
    if st.session_state.data["historico_dados"]:
        ia = raciocinio_total_ia(st.session_state.data["historico_dados"], st.session_state.data["ia_memoria"])
        
        orcamento = st.number_input("Autorizar orçamento para gerar jogos (R$):", min_value=3.5, max_value=max(3.5, st.session_state.data['banca']), step=3.5)
        
        if st.button("🧬 GERAR JOGOS (SEM REPETIÇÃO)", type="primary", use_container_width=True):
            if st.session_state.data['banca'] < orcamento:
                st.error("Banca insuficiente. Aporte dinheiro na Aba 1.")
            else:
                st.session_state.data['banca'] -= orcamento
                historico_sets = [set(h['dezenas']) for h in st.session_state.data["historico_dados"]]
                gasto = 0.0
                
                while (orcamento - gasto) >= 3.5:
                    tam = 16 if (orcamento - gasto) >= 56.0 and random.random() > 0.85 else 15
                    custo = 56.0 if tam == 16 else 3.5
                    
                    dezenas_disponiveis = ia['matriz_base']
                    # Garante extração de pesos sem erro
                    pesos_sublista = [ia['pesos'][i] for i in dezenas_disponiveis]
                    
                    tentativas = 0
                    jogo_inedito = []
                    while tentativas < 500:
                        candidato = sorted(list(set(random.choices(dezenas_disponiveis, weights=pesos_sublista, k=tam))))
                        while len(candidato) < tam:
                            sobra = list(set(dezenas_disponiveis) - set(candidato))
                            candidato.append(random.choice(sobra))
                            candidato = sorted(list(set(candidato)))
                        
                        if set(candidato) not in historico_sets:
                            jogo_inedito = candidato
                            break
                        tentativas += 1
                    
                    if not jogo_inedito: 
                        jogo_inedito = sorted(random.sample(dezenas_disponiveis, tam))
                        
                    st.session_state.data["jogos_salvos"].append({
                        "id": str(uuid.uuid4()), "concurso_alvo": ia['alvo'], "dezenas": jogo_inedito,
                        "tamanho": tam, "estrategia": ia['estrategia'], 
                        "justificativa": f"Matriz {ia['qtd_matriz']} | {ia['estrategia']}",
                        "status": "Aguardando Sorteio", "acertos": 0
                    })
                    gasto += custo
                st.success(f"Geração concluída! R$ {gasto:.2f} investidos. Veja na Aba 4.")
                st.rerun()
    else: st.warning("Por favor, carregue o Cofre na Aba 1.")

# --- TAB 4: FILA DE JOGOS ---
with tabs[3]:
    st.markdown("### 🎫 Cartões na Fila de Sorteio")
    if st.session_state.data["jogos_salvos"]:
        st.button("🚨 EXCLUIR TODO O LOTE", on_click=cb_excluir_todos, type="secondary")
        st.divider()
        
        for j in st.session_state.data["jogos_salvos"]:
            with st.container(border=True):
                c_card, c_del = st.columns([5, 1])
                with c_card:
                    cor = "green" if j['status'] == "Premiado" else "blue" if j['status'] == "Aguardando Sorteio" else "gray"
                    st.markdown(f"🎯 **Alvo:** `{j['concurso_alvo']}` | **{j['tamanho']} Dezenas** | Status: :{cor}[{j['status']}]")
                    st.code(" - ".join([f"{n:02d}" for n in j['dezenas']]))
                    st.caption(f"💡 *{j['justificativa']}*")
                with c_del:
                    st.button("🗑️ Apagar", key=f"del_{j['id']}", on_click=cb_excluir_jogo, args=(j['id'],), use_container_width=True)
    else: st.info("Sem jogos na fila.")

# --- TAB 5: AUDITORIA E APRENDIZADO ---
with tabs[4]:
    st.markdown("### 🏆 Sincronização e Ensino da IA")
    
    if st.button("🔄 SINCRONIZAR CAIXA E ENSINAR IA", type="primary", use_container_width=True):
        with st.spinner("Conectando à Caixa e calculando matrizes..."):
            try:
                res = requests.get("https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest", verify=False, timeout=10).json()
                st.session_state.caixa_latest = res
                sorteio_oficial = set(map(int, res['dezenas']))
                
                lucro = 0.0
                for j in st.session_state.data["jogos_salvos"]:
                    if j['status'] == "Aguardando Sorteio":
                        pontos = len(set(j['dezenas']).intersection(sorteio_oficial))
                        j['acertos'] = pontos
                        
                        # IA APRENDENDO O RESULTADO DA ESTRATÉGIA!
                        estr_nome = "Tendencia" if "Tendência" in j['estrategia'] else "Reversao"
                        st.session_state.data["ia_memoria"][estr_nome]["usos"] += 1
                        st.session_state.data["ia_memoria"][estr_nome]["pontos"] += pontos
                        
                        premio = {11: 6.0, 12: 12.0, 13: 30.0, 14: 2000.0, 15: 1500000.0}.get(pontos, 0.0)
                        if pontos >= 11:
                            j['status'] = "Premiado"
                            lucro += premio
                        else: j['status'] = "Não Premiado"
                
                st.session_state.data["banca"] += lucro
                st.success(f"Conferência concluída. Lucro: R$ {lucro:.2f}. A IA registrou as notas na Memória!")
            except: st.error("Erro ao conectar na Caixa.")

    if 'caixa_latest' in st.session_state:
        r = st.session_state.caixa_latest
        if st.session_state.data["matriz_viva_atual"]:
            mv = set(st.session_state.data["matriz_viva_atual"])
            sorteio_set = set(map(int, r['dezenas']))
            acertos_mv = len(mv.intersection(sorteio_set))
            st.markdown(f"""
            <div style="background: #ebf8ff; padding: 15px; border-left: 5px solid #2b6cb0; margin-bottom: 15px;">
                <h4 style="margin:0; color:#2b6cb0;">📊 Auditoria da Matriz da IA</h4>
                A IA havia escolhido <b>{len(mv)} dezenas</b>. No concurso oficial, <b>{acertos_mv} foram sorteadas</b> dentro dessa matriz.
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"#### 🏛️ Concurso Oficial: {r['concurso']} ({r['data']})")
        st.code(" - ".join(r['dezenas']))
        st.markdown("#### 💰 Rateio Oficial")
        st.table(pd.DataFrame(r['premiacoes']))
