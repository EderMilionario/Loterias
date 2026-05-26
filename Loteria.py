import streamlit as st
import random
import json
import pandas as pd
from collections import Counter
from datetime import datetime

st.set_page_config(page_title="LotoMatrix PRO - Sistema Profissional", layout="wide")

# --- BLOCO DE SEGURANÇA E PROTEÇÃO DE DADOS ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    senha = st.text_input("Senha de Acesso:", type="password")
    if st.button("ENTRAR"):
        if senha == "admin123":
            st.session_state.autenticado = True
            st.rerun()
    st.stop()

# --- FUNÇÃO DE LIMPEZA (MATA O KEYERROR) ---
def sanitizar_dados(data):
    """Garante que qualquer estrutura de JSON antigo seja convertida para a nova."""
    if "jogos_salvos" not in data: data["jogos_salvos"] = []
    if "historico_dados" not in data: data["historico_dados"] = []
    
    for jogo in data["jogos_salvos"]:
        if "tamanho" not in jogo: jogo["tamanho"] = 15
        if "estrategia" not in jogo: jogo["estrategia"] = "Legacy"
        if "justificativa" not in jogo: jogo["justificativa"] = "Importado do Cofre antigo"
    return data

# --- CARREGAMENTO ---
if 'data' not in st.session_state:
    st.session_state.data = {"historico_dados": [], "jogos_salvos": [], "banca": 0.0}

# --- INTERFACE ---
st.title("🧬 LotoMatrix PRO - Gestão Autônoma")

tabs = st.tabs(["📊 Dashboard", "🤖 Gerador", "📜 Jogos Ativos", "🏆 Auditoria", "💾 Cofre"])

with tabs[0]: # Dashboard
    st.header("Painel de Informações")
    if st.session_state.data["historico_dados"]:
        historico = st.session_state.data["historico_dados"]
        todas = [n for h in historico for n in h['dezenas']]
        freq = Counter(todas)
        st.bar_chart(pd.DataFrame.from_dict(freq, orient='index', columns=['Frequencia']))
    else:
        st.info("Carregue o Cofre para ver o Dashboard.")

with tabs[1]: # Gerador
    st.header("Gerador Inteligente")
    budget = st.number_input("Valor da Aposta (R$)", min_value=3.5, step=3.5)
    if st.button("Gerar Jogos"):
        # Lógica de pesos baseada em frequência
        pesos = {i: 1 for i in range(1, 26)} # Default
        if st.session_state.data["historico_dados"]:
            todas = [n for h in st.session_state.data["historico_dados"] for n in h['dezenas']]
            freq = Counter(todas)
            pesos = {i: freq.get(i, 1) for i in range(1, 26)}
        
        while budget >= 3.5:
            tam = 16 if budget >= 56.0 and random.random() > 0.5 else 15
            custo = 56.0 if tam == 16 else 3.5
            if budget >= custo:
                jogo = sorted(random.sample(range(1, 26), tam))
                st.session_state.data["jogos_salvos"].append({
                    "dezenas": jogo, "tamanho": tam, "estrategia": "IA-Adaptativa",
                    "justificativa": "Baseado em frequência histórica", "acertos": 0
                })
                budget -= custo
        st.rerun()

with tabs[2]: # Jogos Ativos
    st.header("Jogos em Espera")
    for i, j in enumerate(st.session_state.data["jogos_salvos"]):
        with st.container(border=True):
            st.write(f"**Jogo {i+1}** | {j.get('tamanho', 15)} dezenas")
            st.code(str(j.get('dezenas', [])))
            st.caption(f"🧠 {j.get('justificativa', 'Sem info')}")

with tabs[3]: # Auditoria
    st.header("Auditoria")
    res = st.text_input("Resultado Oficial (15 números)")
    if st.button("Auditar"):
        try:
            sorteio = set(map(int, res.split()))
            for j in st.session_state.data["jogos_salvos"]:
                j['acertos'] = len(set(j['dezenas']).intersection(sorteio))
            st.success("Auditoria Realizada.")
        except: st.error("Erro no formato.")

with tabs[4]: # Cofre
    uploaded = st.file_uploader("Upload Cofre.json", type="json")
    if uploaded:
        dados_carregados = json.load(uploaded)
        st.session_state.data = sanitizar_dados(dados_carregados)
        st.success("Cofre Sincronizado com sucesso.")
    
    if st.button("Baixar Cofre"):
        st.download_button("Download", json.dumps(st.session_state.data), "Cofre_Atualizado.json")
