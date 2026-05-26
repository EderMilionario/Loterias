import streamlit as st
import random
import json
import pandas as pd
from collections import Counter
from datetime import datetime

# --- CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="LotoMatrix PRO - Agente Autônomo", layout="wide")

# Senha Hardcoded para acesso
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    senha = st.text_input("Senha de Acesso:", type="password")
    if st.button("ENTRAR"):
        if senha == "admin123":
            st.session_state.autenticado = True
            st.rerun()
    st.stop()

# --- ESTADO DO SISTEMA (LIMPO) ---
def inicializar_sistema():
    st.session_state.historico_dados = []
    st.session_state.jogos_salvos = []
    st.session_state.banca = 0.0

if 'historico_dados' not in st.session_state: inicializar_sistema()

# --- MOTOR DE INTELIGÊNCIA (O CÉREBRO) ---
class LotoEngine:
    @staticmethod
    def analisar(historico):
        if not historico: return {"tipo": "Neutro", "peso": {i: 1 for i in range(1, 26)}}
        
        todas = [n for h in historico for n in h['dezenas']]
        contagem = Counter(todas)
        # Define estratégia baseada na média de frequência
        if sum(contagem.values()) / 25 > 50:
            return {"tipo": "Tendência", "pesos": {i: contagem[i] + 1 for i in range(1, 26)}}
        return {"tipo": "Reversão", "pesos": {i: 100 - contagem[i] for i in range(1, 26)}}

    @staticmethod
    def gerar_jogo(tipo, pesos, tam=15):
        numeros = list(range(1, 26))
        pesos_list = [pesos[i] for i in numeros]
        jogo = sorted(random.choices(numeros, weights=pesos_list, k=tam))
        return list(set(jogo)) # Garante unicidade

# --- UI PROFISSIONAL ---
st.title("🧬 LotoMatrix PRO")

# Sidebar - Gestão de Dados
with st.sidebar:
    st.header("Gestão de Cofre")
    uploaded = st.file_uploader("Upload Cofre.json", type="json")
    if uploaded:
        data = json.load(uploaded)
        st.session_state.historico_dados = data.get("historico_dados", [])
        st.session_state.jogos_salvos = data.get("jogos_salvos", [])
        st.session_state.banca = data.get("banca", 0.0)
        st.success("Cofre Sincronizado.")
    
    st.metric("Banca", f"R$ {st.session_state.banca:.2f}")
    if st.button("Download Backup"):
        dados = {"historico_dados": st.session_state.historico_dados, "jogos_salvos": st.session_state.jogos_salvos, "banca": st.session_state.banca}
        st.download_button("Baixar JSON", json.dumps(dados), "Cofre.json")

# Tabs Principais
tab1, tab2, tab3 = st.tabs(["📊 Dashboard de IA", "🤖 Gerador Inteligente", "🏆 Auditoria"])

with tab1:
    st.subheader("Painel de Raciocínio")
    if st.session_state.historico_dados:
        analise = LotoEngine.analisar(st.session_state.historico_dados)
        st.info(f"Modo Atual: **{analise['tipo']}**")
        st.write("A IA está priorizando números baseada na frequência histórica.")
    else:
        st.warning("Carregue o Cofre.")

with tab2:
    st.subheader("Geração Autônoma por Orçamento")
    orcamento = st.number_input("Valor para esta rodada (R$)", min_value=3.5, step=3.5)
    
    if st.button("Gerar Jogos"):
        analise = LotoEngine.analisar(st.session_state.historico_dados)
        budget_left = orcamento
        
        while budget_left >= 3.5:
            # IA decide se gera 16 ou 15 baseado no budget
            tam = 16 if budget_left >= 56.0 and random.random() > 0.7 else 15
            custo = 56.0 if tam == 16 else 3.5
            
            if budget_left >= custo:
                jogo = LotoEngine.gerar_jogo(analise['tipo'], analise['pesos'], tam)
                st.session_state.jogos_salvos.append({
                    "dezenas": jogo,
                    "tamanho": tam,
                    "estrategia": analise['tipo'],
                    "justificativa": f"IA usou modo {analise['tipo']} devido ao histórico."
                })
                budget_left -= custo
        st.session_state.banca -= (orcamento - budget_left)
        st.rerun()

    # Cards de Jogos
    for i, j in enumerate(st.session_state.jogos_salvos):
        with st.container(border=True):
            cols = st.columns([3, 1])
            cols[0].write(f"**Jogo {i+1}** ({j['tamanho']} dezenas) - Estratégia: {j['estrategia']}")
            cols[0].code(str(j['dezenas']))
            cols[1].write(f"🧠 IA: {j['justificativa']}")

with tab3:
    st.subheader("Auditoria de Resultados")
    sorteio_str = st.text_input("Resultado Oficial (espaço entre números)")
    if st.button("Auditar Lote"):
        try:
            sorteio = set(map(int, sorteio_str.split()))
            for j in st.session_state.jogos_salvos:
                acertos = len(set(j['dezenas']).intersection(sorteio))
                j['acertos'] = acertos # Aqui a IA "aprende" o resultado
            st.success("Auditoria concluída. O histórico foi atualizado com os acertos.")
        except: st.error("Erro no formato.")
