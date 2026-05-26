import streamlit as st
import pandas as pd
import requests
import json
import random
from collections import Counter
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="LotoMatrix PRO - Sistema de Gestão", layout="wide")

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    senha = st.text_input("Senha de Acesso:", type="password")
    if st.button("ENTRAR"):
        if senha == "admin123":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- ESTADO CENTRAL ---
if 'data' not in st.session_state:
    st.session_state.data = {"banca": 0.0, "historico_dados": [], "jogos_salvos": []}

# --- FUNÇÕES DE ANÁLISE PROFISSIONAL ---
def calcular_metricas(historico):
    if not historico: return None
    todas = [n for h in historico for n in h['dezenas']]
    contagem = Counter(todas)
    
    # Calcular atrasos (Concursos sem sair)
    atrasos = {n: 0 for n in range(1, 26)}
    for h in reversed(historico):
        for n in range(1, 26):
            if n not in h['dezenas'] and atrasos[n] == 0: atrasos[n] += 1
    
    # Calcular Ciclo
    ciclo = set()
    jogos_ciclo = 0
    for h in reversed(historico):
        ciclo.update(h['dezenas'])
        jogos_ciclo += 1
        if len(ciclo) == 25: break
    
    return {"freq": contagem, "atrasos": atrasos, "ciclo_tamanho": jogos_ciclo}

# --- INTERFACE ---
st.title("🧬 LotoMatrix PRO - Gestão Autônoma")
tabs = st.tabs(["📂 Cofre", "📊 Painéis", "🤖 Motor IA", "🏆 Auditoria Real"])

with tabs[0]: # COFRE
    file = st.file_uploader("Upload Cofre.json", type="json")
    if file:
        st.session_state.data = json.load(file)
        st.success("Dados carregados.")
    if st.button("Exportar Backup"):
        st.download_button("Baixar JSON", json.dumps(st.session_state.data), "Cofre_Atualizado.json")

with tabs[1]: # PAINÉIS
    if st.session_state.data["historico_dados"]:
        m = calcular_metricas(st.session_state.data["historico_dados"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Ciclo Atual", f"{m['ciclo_tamanho']} concursos")
        c2.write("### Dezenas Mais Frequentes")
        c2.bar_chart(pd.Series(m['freq']).sort_values(ascending=False).head(10))
        c3.write("### Dezenas Atrasadas")
        c3.bar_chart(pd.Series(m['atrasos']).sort_values(ascending=False).head(10))
    else: st.warning("Suba o Cofre.")

with tabs[2]: # IA
    budget = st.number_input("Budget (R$)", value=3.5)
    if st.button("Gerar Jogos Inteligentes"):
        m = calcular_metricas(st.session_state.data["historico_dados"])
        # IA escolhe baseada no atraso
        pesos = {n: (m['atrasos'][n] + 1) for n in range(1, 26)}
        while budget >= 3.5:
            tam = 16 if budget >= 56.0 else 15
            custo = 56.0 if tam == 16 else 3.5
            if budget < custo: break
            
            jogo = sorted(random.choices(range(1, 26), weights=[pesos[i] for i in range(1, 26)], k=tam))
            st.session_state.data["jogos_salvos"].append({
                "dezenas": list(set(jogo)), "tamanho": tam, "justificativa": "Foco em atrasadas"
            })
            budget -= custo
        st.rerun()

    for j in st.session_state.data["jogos_salvos"]:
        with st.container(border=True):
            st.write(f"Jogo: {j['dezenas']} | Motivo: {j['justificativa']}")

with tabs[3]: # AUDITORIA CAIXA
    if st.button("Sincronizar com Caixa"):
        res = requests.get("https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest").json()
        st.write(f"### Concurso {res['concurso']}")
        st.write(f"Dezenas: {res['dezenas']}")
        st.write("### Rateio Oficial")
        df_premio = pd.DataFrame(res['premiacoes'])
        st.table(df_premio)
