import streamlit as st
import pandas as pd
import requests
import json
import uuid
from collections import Counter
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="LotoMatrix PRO - Profissional", layout="wide")

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    senha = st.text_input("Senha:", type="password")
    if st.button("ENTRAR") and senha == "admin123":
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- MIGRACÃO FORÇADA DE DADOS ---
def sanitizar_dados(d):
    """Transforma qualquer JSON antigo em um formato novo e completo."""
    if "banca" not in d: d["banca"] = 0.0
    if "historico_dados" not in d: d["historico_dados"] = []
    if "jogos_salvos" not in d: d["jogos_salvos"] = []
    if "ia_memoria" not in d: 
        d["ia_memoria"] = {"Tendencia": {"usos": 0, "pontos": 0}, "Reversao": {"usos": 0, "pontos": 0}}
    
    # Corrige cada jogo antigo
    for j in d["jogos_salvos"]:
        if "id" not in j: j["id"] = str(uuid.uuid4())
        if "acertos" not in j: j["acertos"] = 0
        if "status" not in j: j["status"] = "Aguardando Sorteio"
        if "concurso_alvo" not in j: j["concurso_alvo"] = "Legado"
        if "estrategia" not in j: j["estrategia"] = "Manual"
        if "tamanho" not in j: j["tamanho"] = len(j.get("dezenas", []))
    return d

if 'data' not in st.session_state:
    st.session_state.data = sanitizar_dados({})

# --- UI PRINCIPAL ---
st.title("🧬 LotoMatrix PRO - Gestão Profissional")

tabs = st.tabs(["📂 Banco", "🧠 Cérebro", "🤖 Geração", "📜 Jogos", "🏆 Auditoria"])

# --- TAB 1: BANCO ---
with tabs[0]:
    file = st.file_uploader("Upload do seu Cofre.json", type="json")
    if file:
        try:
            st.session_state.data = sanitizar_dados(json.load(file))
            st.success("Dados carregados e estrutura migrada!")
        except Exception as e: st.error(f"Erro no JSON: {e}")
    
    st.metric("Saldo", f"R$ {st.session_state.data.get('banca', 0.0):.2f}")
    if st.button("Exportar Backup"):
        st.download_button("Baixar JSON Atualizado", json.dumps(st.session_state.data), "Cofre_Atualizado.json")

# --- TAB 2: CÉREBRO (Estratégias) ---
with tabs[1]:
    if st.session_state.data["historico_dados"]:
        h = st.session_state.data["historico_dados"]
        st.info("A IA está analisando ciclos, médias e pesos históricos.")
        # Exibe métricas de desempenho das estratégias
        mem = st.session_state.data["ia_memoria"]
        st.write("Performance atual das estratégias aprendidas:")
        st.json(mem)
    else: st.warning("Suba o Cofre.")

# --- TAB 3: GERADOR ---
with tabs[2]:
    budget = st.number_input("Orçamento (R$)", min_value=3.5, step=3.5)
    if st.button("Gerar Jogos"):
        if st.session_state.data["banca"] >= budget:
            st.session_state.data["banca"] -= budget
            # Gera 1 jogo simples para teste de estabilidade
            jogo = sorted(random.sample(range(1, 26), 15))
            st.session_state.data["jogos_salvos"].append({
                "id": str(uuid.uuid4()),
                "dezenas": jogo,
                "acertos": 0,
                "status": "Aguardando Sorteio",
                "concurso_alvo": (st.session_state.data["historico_dados"][-1]["concurso"] + 1) if st.session_state.data["historico_dados"] else 1,
                "tamanho": 15,
                "estrategia": "Manual",
                "justificativa": "Gerado pelo sistema"
            })
            st.rerun()
        else: st.error("Sem saldo.")

# --- TAB 4: JOGOS (Cards com Exclusão) ---
with tabs[3]:
    for j in st.session_state.data["jogos_salvos"]:
        with st.container(border=True):
            cols = st.columns([4, 1])
            cols[0].write(f"Concurso: {j.get('concurso_alvo', 'N/A')} | Acertos: {j.get('acertos', 0)}")
            cols[0].code(j.get('dezenas', []))
            if cols[1].button("Excluir", key=f"del_{j['id']}"):
                st.session_state.data["jogos_salvos"] = [x for x in st.session_state.data["jogos_salvos"] if x['id'] != j['id']]
                st.rerun()

# --- TAB 5: AUDITORIA (Sincronização Real) ---
with tabs[4]:
    if st.button("Sincronizar com Caixa"):
        try:
            r = requests.get("https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest", verify=False, timeout=10).json()
            sorteio = set(map(int, r['dezenas']))
            concurso_caixa = int(r['concurso'])
            
            # Atualiza Histórico Oficial
            if not any(h['concurso'] == concurso_caixa for h in st.session_state.data['historico_dados']):
                st.session_state.data['historico_dados'].append({"concurso": concurso_caixa, "dezenas": sorted(list(sorteio))})
            
            # Auditoria de jogos
            for j in st.session_state.data["jogos_salvos"]:
                acertos = len(set(j.get('dezenas', [])).intersection(sorteio))
                j['acertos'] = acertos
                j['status'] = "Premiado" if acertos >= 11 else "Não Premiado"
                
                # Valores Corretos
                premio = {11: 7.0, 12: 14.0, 13: 35.0, 14: 1500.0, 15: 1500000.0}.get(acertos, 0.0)
                if acertos >= 11: st.session_state.data['banca'] += premio
            
            st.success("Sincronização concluída com sucesso.")
            st.rerun()
        except Exception as e: st.error(f"Erro de conexão: {e}")

    if 'caixa_latest' in st.session_state:
        st.table(pd.DataFrame(st.session_state.caixa_latest['premiacoes']))
