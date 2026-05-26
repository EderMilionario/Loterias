import streamlit as st
import random
import json
import requests
from collections import Counter
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONFIGURAÇÕES
st.set_page_config(page_title="LotoMatrix PRO - Agente Autônomo", layout="wide")

# --- MÓDULO DE INTELIGÊNCIA E RACIOCÍNIO ---
def analisar_contexto_ia(historico):
    if not historico: return {"estrategia": "Inicial", "motivo": "Sem dados", "pesos": {}}
    
    todas = [n for h in historico for n in h['dezenas']]
    contagem = Counter(todas)
    ultimos = historico[-5:]
    ultimas_dezenas = [n for h in ultimos for n in h['dezenas']]
    contagem_recente = Counter(ultimas_dezenas)
    
    # Decisão de Estratégia (A IA "Raciocina")
    # Se bolas muito quentes estão saindo muito, focar nelas. Se estão raras, focar em reversão.
    score_quentes = sum([contagem[i] for i in range(1, 26)]) / 25
    
    if contagem_recente.most_common(1)[0][1] > 3:
        estrategia = "Tendência Agressiva"
        motivo = "O sistema identificou um padrão de repetição forte em dezenas quentes."
    else:
        estrategia = "Reversão de Frias"
        motivo = "O sistema identificou um ciclo de instabilidade e está forçando dezenas atrasadas."

    # Criar pesos para seleção
    pesos = {i: contagem[i] if estrategia == "Tendência Agressiva" else (100 - contagem[i]) for i in range(1, 26)}
    
    return {"estrategia": estrategia, "motivo": motivo, "pesos": pesos}

# --- FUNÇÕES DE PERSISTÊNCIA E API ---
def carregar_dados(uploaded_file):
    try:
        data = json.load(uploaded_file)
        st.session_state.historico_dados = data.get("historico_dados", [])
        st.session_state.jogos_salvos = data.get("jogos_salvos", [])
        st.session_state.banca = data.get("banca", 0.0)
        return True
    except: return False

def sincronizar_caixa():
    try:
        url = "https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest"
        r = requests.get(url, verify=False, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- INICIALIZAÇÃO DO ESTADO ---
if 'historico_dados' not in st.session_state: st.session_state.historico_dados = []
if 'jogos_salvos' not in st.session_state: st.session_state.jogos_salvos = []
if 'banca' not in st.session_state: st.session_state.banca = 100.0

# --- INTERFACE ---
st.title("🧬 LotoMatrix PRO - Agente Autônomo")

tab1, tab2, tab3, tab4 = st.tabs(["🧠 Raciocínio da IA", "🚀 Gerador Vivo", "🏆 Auditoria Inteligente", "💾 Cofre"])

# TAB 1: RACIOCÍNIO
with tab1:
    st.subheader("Painel de Raciocínio")
    if st.session_state.historico_dados:
        analise = analisar_contexto_ia(st.session_state.historico_dados)
        st.info(f"**Estratégia Atual:** {analise['estrategia']}")
        st.write(f"**Decisão da IA:** {analise['motivo']}")
    else:
        st.warning("Injete dados no Cofre para a IA começar a raciocinar.")

# TAB 2: GERADOR
with tab2:
    if st.button("🚀 Gerar Jogos com IA"):
        analise = analisar_contexto_ia(st.session_state.historico_dados)
        numeros = list(range(1, 26))
        pesos = [analise['pesos'][i] for i in numeros]
        
        novo_jogo = sorted(random.choices(numeros, weights=pesos, k=15))
        
        # Salvando com o DNA do Jogo
        st.session_state.jogos_salvos.append({
            "data": datetime.now().strftime("%d/%m/%Y"),
            "dezenas": novo_jogo,
            "estrategia": analise['estrategia'],
            "justificativa": analise['motivo'],
            "acertos": 0,
            "premio": 0.0
        })
        st.success("Jogo gerado e memória atualizada!")
        st.rerun()

    for j in st.session_state.jogos_salvos:
        with st.expander(f"Jogo: {j['dezenas']}"):
            st.write(f"**IA Justificou:** {j['justificativa']}")
            st.write(f"**Estratégia:** {j['estrategia']}")

# TAB 3: AUDITORIA
with tab3:
    if st.button("🔄 Sincronizar com Caixa e Auditar"):
        resultado = sincronizar_caixa()
        if resultado:
            dezenas_sorteadas = set(map(int, resultado['dezenas']))
            st.success(f"Concurso {resultado['concurso']} processado.")
            
            # IA audita seus próprios jogos
            for j in st.session_state.jogos_salvos:
                acertos = len(set(j['dezenas']).intersection(dezenas_sorteadas))
                j['acertos'] = acertos
                # Lógica simples de premiação
                if acertos >= 11: j['premio'] = 5.0 * (acertos - 10) 
            st.rerun()

# TAB 4: COFRE
with tab4:
    uploaded = st.file_uploader("Upload Cofre.json", type="json")
    if uploaded and carregar_dados(uploaded): st.success("Cofre Carregado")
    
    dados = {
        "historico_dados": st.session_state.historico_dados,
        "jogos_salvos": st.session_state.jogos_salvos,
        "banca": st.session_state.banca
    }
    st.download_button("💾 Baixar Backup Inteligente", json.dumps(dados), "Cofre.json")
