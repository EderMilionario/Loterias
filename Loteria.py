import streamlit as st
import random
import json
import pandas as pd
from collections import Counter
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURAÇÃO PROFISSIONAL ---
st.set_page_config(page_title="LotoMatrix PRO - Sistema Autônomo", layout="wide")

SENHA_ACESSO = "admin123"  # Mantenha sua senha aqui

# --- SEGURANÇA E AUTENTICAÇÃO ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center; color: #006644;'>🔐 LotoMatrix PRO - Acesso Restrito</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            senha_digitada = st.text_input("Digite a Senha:", type="password")
            if st.button("ENTRAR", type="primary", use_container_width=True):
                if senha_digitada == SENHA_ACESSO:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Acesso Negado.")
    st.stop()

# --- INICIALIZAÇÃO E MIGRAÇÃO ---
if 'historico_dados' not in st.session_state: st.session_state.historico_dados = []
if 'jogos_salvos' not in st.session_state: st.session_state.jogos_salvos = []
if 'banca' not in st.session_state: st.session_state.banca = 100.0

def migrar_estrutura(data):
    if "jogos_salvos" not in data: data["jogos_salvos"] = []
    for jogo in data["jogos_salvos"]:
        if "justificativa" not in jogo: jogo["justificativa"] = "Jogo legado"
        if "estrategia" not in jogo: jogo["estrategia"] = "Manual"
    return data

def carregar_dados(uploaded_file):
    try:
        data = json.load(uploaded_file)
        data = migrar_estrutura(data)
        st.session_state.historico_dados = data.get("historico_dados", [])
        st.session_state.jogos_salvos = data.get("jogos_salvos", [])
        st.session_state.banca = data.get("banca", 100.0)
        return True
    except: return False

# --- MÓDULO DE INTELIGÊNCIA ---
def analisar_cenario(historico):
    if not historico: return None
    todas = [n for h in historico for n in h['dezenas']]
    contagem = Counter(todas)
    
    # Lógica simples de atraso baseada no histórico
    atrasos = {n: 0 for n in range(1, 26)}
    for h in reversed(historico):
        for n in range(1, 26):
            if n not in h['dezenas'] and atrasos[n] == 0: atrasos[n] += 1
            elif n in h['dezenas'] and atrasos[n] == 0: pass 
            
    estilo = "Reversão" if any(v > 5 for v in atrasos.values()) else "Tendência"
    
    return {
        "frequencia": contagem,
        "atrasos": atrasos,
        "estilo": estilo,
        "motivo": f"O sistema analisou os últimos {len(historico)} sorteios e optou por estratégia de {estilo}."
    }

# --- INTERFACE PRINCIPAL ---
st.title("🧬 LotoMatrix PRO - Agente Autônomo")

# Sidebar - Painel de Controle
st.sidebar.metric("Banca Atual", f"R$ {st.session_state.banca:.2f}")
if st.sidebar.button("💾 Exportar Cofre Atualizado"):
    dados = {"historico_dados": st.session_state.historico_dados, "jogos_salvos": st.session_state.jogos_salvos, "banca": st.session_state.banca}
    st.sidebar.download_button("Baixar JSON", json.dumps(dados), "Cofre_Backup.json")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard de IA", "🤖 Agente de Geração", "💾 Gestão do Cofre"])

with tab1:
    st.subheader("Painel de Diagnóstico")
    if st.session_state.historico_dados:
        stats = analisar_cenario(st.session_state.historico_dados)
        col1, col2 = st.columns(2)
        col1.bar_chart(pd.DataFrame.from_dict(stats['frequencia'], orient='index', columns=['Frequencia']))
        col2.info(f"**Estratégia Ativa:** {stats['estilo']}")
        col2.write(f"**Justificativa Técnica:** {stats['motivo']}")
    else:
        st.warning("Carregue dados na aba de Gestão.")

with tab2:
    st.subheader("Gerador Autônomo")
    if st.button("🚀 Gerar Lote com IA"):
        analise = analisar_cenario(st.session_state.historico_dados)
        pesos = [analise['frequencia'][i] if analise['estilo'] == "Tendência" else (100 - analise['frequencia'][i]) for i in range(1, 26)]
        
        novo_jogo = sorted(random.choices(range(1, 26), weights=pesos, k=15))
        
        st.session_state.jogos_salvos.append({
            "dezenas": novo_jogo,
            "estrategia": analise['estilo'],
            "justificativa": analise['motivo'],
            "data": datetime.now().strftime("%d/%m/%Y")
        })
        st.rerun()

    # Cards Profissionais
    for idx, j in enumerate(st.session_state.jogos_salvos):
        with st.container(border=True):
            col_a, col_b = st.columns([3, 1])
            col_a.markdown(f"**Jogo {idx+1}** • Estratégia: `{j.get('estrategia', 'N/A')}`")
            col_a.code(" ".join(map(str, j['dezenas'])))
            col_b.caption(f"🧠 Justificativa IA:")
            col_b.write(j.get('justificativa', 'Sem info'))

with tab3:
    st.subheader("Cofre Central")
    uploaded = st.file_uploader("Upload de Backup (JSON)", type="json")
    if uploaded and carregar_dados(uploaded):
        st.success("Dados carregados e migrados com sucesso.")
