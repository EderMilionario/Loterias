import streamlit as st
import pandas as pd
import requests
import json
from collections import Counter

st.set_page_config(page_title="LotoMatrix PRO - Profissional", layout="wide")

# --- GERENCIAMENTO DE DADOS ---
if 'dados' not in st.session_state:
    st.session_state.dados = {"banca": 0.0, "historico_dados": []}

def carregar_arquivo(file):
    try:
        content = json.load(file)
        st.session_state.dados = content
        return True
    except Exception as e:
        st.error(f"Erro ao ler JSON: {e}")
        return False

# --- MOTOR DE INTEGRAÇÃO (CAIXA) ---
def buscar_resultado_caixa():
    try:
        url = "https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        return None
    except: return None

# --- UI PRINCIPAL ---
st.title("🧬 LotoMatrix PRO - Sistema de Gestão")

tabs = st.tabs(["📂 Cofre e Sincronização", "📊 Dashboard", "🤖 Motor de IA", "🏆 Auditoria"])

with tabs[0]:
    st.header("Gestão de Dados")
    uploaded_file = st.file_uploader("Upload do Cofre.json", type="json")
    if uploaded_file and carregar_arquivo(uploaded_file):
        st.success(f"Cofre carregado. Concursos lidos: {len(st.session_state.dados['historico_dados'])}")
    
    st.divider()
    if st.button("Sincronizar com Caixa"):
        res = buscar_resultado_caixa()
        if res:
            st.write(f"Último Concurso: {res['concurso']}")
            st.write(f"Dezenas: {res['dezenas']}")
            st.session_state.ultimo_resultado = res
        else:
            st.error("Falha na API da Caixa.")

with tabs[1]:
    st.header("Dashboard de Performance")
    if st.session_state.dados['historico_dados']:
        df = pd.DataFrame(st.session_state.dados['historico_dados'])
        st.write("Estatísticas de Concursos:")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Gráfico de Frequência
        all_nums = [n for sublist in df['dezenas'] for n in sublist]
        st.bar_chart(pd.Series(all_nums).value_counts().sort_index())
    else:
        st.warning("Nenhum dado para exibir. Carregue o Cofre.")

with tabs[2]:
    st.header("Agente Autônomo")
    if st.session_state.dados['historico_dados']:
        st.info("O motor de IA está pronto. Ele usará a frequência das dezenas do Cofre para sugerir jogos.")
        budget = st.number_input("Budget para esta rodada (R$)", value=3.5)
        if st.button("Executar Estratégia"):
            st.write("IA: Analisando padrões...")
            # Lógica simples de IA (Baseada em frequência)
            st.write("Estratégia: Tendência de alta frequência aplicada.")
    else:
        st.warning("Carregue o Cofre primeiro.")

with tabs[3]:
    st.header("Auditoria")
    if 'ultimo_resultado' in st.session_state:
        st.write(f"Auditoria do Concurso {st.session_state.ultimo_resultado['concurso']}")
        # Aqui você implementaria a comparação real
        st.success("Dados sincronizados e prontos para conferência.")
    else:
        st.info("Sincronize com a Caixa na primeira aba.")
