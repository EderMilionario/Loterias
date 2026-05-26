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
# BLINDAGEM DE DADOS E ESTADO
# =====================================================================
def sanitizar_dados(d):
    if "banca" not in d: d["banca"] = 0.0
    if "historico_dados" not in d: d["historico_dados"] = []
    if "jogos_salvos" not in d: d["jogos_salvos"] = []
    if "ia_memoria" not in d: 
        d["ia_memoria"] = {"Tendencia": {"usos": 0, "pontos": 0}, "Reversao": {"usos": 0, "pontos": 0}}
    
    for j in d["jogos_salvos"]:
        if "id" not in j: j["id"] = str(uuid.uuid4())
        if "justificativa" not in j: j["justificativa"] = "Jogo legado."
        if "estrategia" not in j: j["estrategia"] = "Padrão"
        if "acertos" not in j: j["acertos"] = 0
        if "tamanho" not in j: j["tamanho"] = len(j.get("dezenas", []))
        if "status" not in j: j["status"] = "Aguardando"
        if "concurso_alvo" not in j: j["concurso_alvo"] = "N/A"
    return d

if 'data' not in st.session_state:
    st.session_state.data = sanitizar_dados({})

# Função de exclusão de jogo
def excluir_jogo(jogo_id):
    st.session_state.data['jogos_salvos'] = [j for j in st.session_state.data['jogos_salvos'] if j['id'] != jogo_id]

# =====================================================================
# CÉREBRO DA IA (Análise Profunda)
# =====================================================================
def raciocinio_completo_ia(historico):
    if not historico: return None
    todas_dezenas = [n for h in historico for n in h['dezenas']]
    freq = Counter(todas_dezenas)
    
    # Parâmetros Específicos
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
            elif n in h['dezenas'] and atrasos[n] == 0: pass

    ciclo = set()
    jogos_ciclo = 0
    for h in reversed(historico):
        ciclo.update(h['dezenas'])
        jogos_ciclo += 1
        if len(ciclo) == 25: break
    faltam_ciclo = sorted(list(set(range(1, 26)) - ciclo))

    ultimo_concurso = historico[-1]['concurso'] if historico else 0
    concurso_alvo = ultimo_concurso + 1

    # Veredito da IA
    if media_soma > 195:
        estrategia = "Reversão para Baixa"
        pesos = {i: 100 - freq.get(i, 1) for i in range(1, 26)}
        motivo = f"A média de SOMA está alta ({media_soma:.1f}). A IA forçará dezenas menores e atrasadas para equilibrar."
    else:
        estrategia = "Tendência de Alta"
        pesos = {i: freq.get(i, 1) + atrasos.get(i, 0) for i in range(1, 26)}
        motivo = f"Soma equilibrada ({media_soma:.1f}). A IA vai mesclar dezenas quentes com dezenas da moldura."

    return {
        "estrategia": estrategia, "motivo": motivo, "pesos": pesos, "freq": freq, 
        "atrasos": atrasos, "ciclo_tam": jogos_ciclo, "faltam_ciclo": faltam_ciclo,
        "soma": media_soma, "impares": media_impares, "primos": media_primos, 
        "moldura": media_moldura, "alvo": concurso_alvo, "total_dados": len(historico)
    }

# =====================================================================
# INTERFACE (5 ABAS PROFISSIONAIS)
# =====================================================================
st.markdown("<h2 style='text-align: center; color: #1f77b4;'>🧬 LotoMatrix PRO - Agente Autônomo</h2>", unsafe_allow_html=True)
tabs = st.tabs(["📂 1. Gestão e Cofre", "📊 2. Painel da IA", "🤖 3. Gerador", "📜 4. Jogos em Espera", "🏆 5. Auditoria & Caixa"])

# --- ABA 1: GESTÃO ---
with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### 💾 Cofre de Dados")
            file = st.file_uploader("Upload do Cofre.json", type="json")
            if file:
                try:
                    st.session_state.data = sanitizar_dados(json.load(file))
                    st.success("✅ Cofre carregado com sucesso!")
                except: st.error("Erro ao ler o arquivo.")
            
            total = len(st.session_state.data['historico_dados'])
            st.info(f"📊 **Dados Oficiais Lidos:** {total} concursos no histórico.")
            
            st.download_button("📥 Baixar Cofre Atualizado", json.dumps(st.session_state.data), "Cofre.json", type="primary", use_container_width=True)

    with c2:
        with st.container(border=True):
            st.markdown("### 💰 Gestão de Banca")
            st.metric("Saldo Disponível", f"R$ {st.session_state.data['banca']:.2f}")
            novo_aporte = st.number_input("Aportar Dinheiro (R$)", min_value=0.0, step=10.0)
            if st.button("Depositar na Banca", use_container_width=True):
                st.session_state.data['banca'] += novo_aporte
                st.success(f"R$ {novo_aporte:.2f} adicionados à banca!")
                st.rerun()

# --- ABA 2: PAINEL DA IA (O "TUDO") ---
with tabs[1]:
    if st.session_state.data["historico_dados"]:
        ia = raciocinio_completo_ia(st.session_state.data["historico_dados"])
        
        st.markdown("### 🧠 Relatório de Análise Profunda da IA")
        st.info(f"**Veredito Oficial para o Concurso Alvo {ia['alvo']}:**\n\n{ia['motivo']}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média de Soma (10 conc)", f"{ia['soma']:.1f}")
        c2.metric("Ímpares por jogo", f"{ia['impares']:.1f}")
        c3.metric("Primos por jogo", f"{ia['primos']:.1f}")
        c4.metric("Moldura por jogo", f"{ia['moldura']:.1f}")

        st.markdown("---")
        colA, colB, colC = st.columns(3)
        with colA:
            st.markdown("#### ⏳ Status do Ciclo")
            st.write(f"Aberta há **{ia['ciclo_tam']}** concursos.")
            if ia['faltam_ciclo']: st.warning(f"Faltam: {ia['faltam_ciclo']}")
            else: st.success("Ciclo acabou de fechar.")
        with colB:
            st.markdown("#### 🔥 Top Quentes")
            st.dataframe(pd.DataFrame.from_dict(ia['freq'], orient='index', columns=['Frequência']).sort_values('Frequência', ascending=False).head(5), use_container_width=True)
        with colC:
            st.markdown("#### ❄️ Maiores Atrasos")
            st.dataframe(pd.DataFrame.from_dict(ia['atrasos'], orient='index', columns=['Concursos']).sort_values('Concursos', ascending=False).head(5), use_container_width=True)
    else: st.warning("Suba o Cofre na Aba 1.")

# --- ABA 3: GERADOR ---
with tabs[2]:
    st.markdown("### 🚀 Gerador Inteligente")
    if st.session_state.data["historico_dados"]:
        ia = raciocinio_completo_ia(st.session_state.data["historico_dados"])
        st.write(f"🎯 **Gerando para o Concurso Alvo:** {ia['alvo']}")
        
        orcamento = st.number_input("Valor para apostar agora (R$)", min_value=3.5, max_value=max(3.5, st.session_state.data['banca']), step=3.5)
        
        if st.button("🧬 GERAR JOGOS", type="primary"):
            if st.session_state.data['banca'] < orcamento:
                st.error("Saldo insuficiente! Vá na Aba 1 e aporte dinheiro na banca.")
            else:
                st.session_state.data['banca'] -= orcamento
                gasto = 0.0
                while (orcamento - gasto) >= 3.5:
                    tam = 16 if (orcamento - gasto) >= 56.0 and random.random() > 0.8 else 15
                    custo = 56.0 if tam == 16 else 3.5
                    
                    numeros = list(range(1, 26))
                    pesos_lista = [ia['pesos'][i] for i in numeros]
                    jogo = sorted(list(set(random.choices(numeros, weights=pesos_lista, k=tam))))
                    while len(jogo) < tam:
                        faltantes = list(set(numeros) - set(jogo))
                        jogo.append(random.choice(faltantes))
                        jogo = sorted(jogo)

                    st.session_state.data["jogos_salvos"].append({
                        "id": str(uuid.uuid4()),
                        "concurso_alvo": ia['alvo'],
                        "dezenas": jogo, "tamanho": tam, "estrategia": ia['estrategia'],
                        "justificativa": ia['motivo'], "status": "Aguardando Sorteio", "acertos": 0
                    })
                    gasto += custo
                st.success(f"Jogos gerados! R$ {gasto:.2f} deduzidos da banca.")
                st.rerun()
    else: st.warning("Suba o Cofre na Aba 1.")

# --- ABA 4: JOGOS EM ESPERA ---
with tabs[3]:
    st.markdown("### 🎫 Meus Jogos (Cards)")
    if st.button("🗑️ Excluir Todos", type="secondary"):
        st.session_state.data["jogos_salvos"] = []
        st.rerun()

    if not st.session_state.data["jogos_salvos"]: st.info("Nenhum jogo na fila.")
    
    for j in st.session_state.data["jogos_salvos"]:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                cor = "green" if j['status'] == "Premiado" else "blue" if j['status'] == "Aguardando Sorteio" else "gray"
                st.markdown(f"🎯 **Alvo:** {j['concurso_alvo']} | **{j['tamanho']} Dezenas** | Status: :{cor}[{j['status']}]")
                st.code(" - ".join([f"{n:02d}" for n in j['dezenas']]))
                st.caption(f"🧠 {j['justificativa']}")
            with col2:
                # BOTAO DE EXCLUIR INDIVIDUAL
                if st.button("🗑️ Excluir Jogo", key=f"del_{j['id']}"):
                    excluir_jogo(j['id'])
                    st.rerun()

# --- ABA 5: AUDITORIA ---
with tabs[4]:
    st.markdown("### 🏆 Sincronização e Auditoria")
    if st.button("🔄 Puxar Resultado da Caixa", type="primary"):
        with st.spinner("Conectando Caixa Econômica Federal..."):
            try:
                res = requests.get("https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest", verify=False, timeout=10).json()
                st.session_state.ultimo_resultado = res
                sorteio = set(map(int, res['dezenas']))
                
                ganho = 0.0
                for j in st.session_state.data["jogos_salvos"]:
                    if j['status'] == "Aguardando Sorteio":
                        acertos = len(set(j['dezenas']).intersection(sorteio))
                        j['acertos'] = acertos
                        premio = {11: 6.0, 12: 12.0, 13: 30.0, 14: 2000.0, 15: 1500000.0}.get(acertos, 0.0)
                        
                        if acertos >= 11:
                            j['status'] = "Premiado"
                            ganho += premio
                        else: j['status'] = "Não Premiado"
                
                st.session_state.data["banca"] += ganho
                st.success(f"Conferência concluída! Lucro: R$ {ganho:.2f} adicionados à banca.")
            except: st.error("Erro ao conectar com a API da Caixa.")

    if 'ultimo_resultado' in st.session_state:
        res = st.session_state.ultimo_resultado
        st.markdown(f"#### 🏛️ Concurso Oficial: {res['concurso']} ({res['data']})")
        st.code(" - ".join(res['dezenas']))
        st.markdown("#### 💰 Rateio Oficial")
        st.table(pd.DataFrame(res['premiacoes']))
