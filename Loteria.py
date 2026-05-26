import streamlit as st, pandas as pd, requests, json, random, uuid, urllib3
from collections import Counter
urllib3.disable_warnings()

st.set_page_config(layout="wide")

# --- LOGIN & ESTADO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    if st.text_input("Senha:", type="password") == "admin123": st.session_state.auth = True; st.rerun()
    st.stop()

def sanitizar(d):
    d.setdefault("banca", 0.0); d.setdefault("historico_dados", []); d.setdefault("jogos_salvos", [])
    d.setdefault("ia_memoria", {"Tendencia": {"usos": 0, "pontos": 0}, "Reversao": {"usos": 0, "pontos": 0}})
    for j in d["jogos_salvos"]:
        j.setdefault("id", str(uuid.uuid4())); j.setdefault("status", "Aguardando"); j.setdefault("acertos", 0)
        j.setdefault("concurso_alvo", "N/A"); j.setdefault("tamanho", len(j.get("dezenas", [])))
    return d

if 'data' not in st.session_state: st.session_state.data = sanitizar({})

# --- CALLBACKS (Botões) ---
def cb_deposito(): st.session_state.data['banca'] += st.session_state.v_dep
def cb_del(id): st.session_state.data['jogos_salvos'] = [j for j in st.session_state.data['jogos_salvos'] if j['id'] != id]
def cb_del_all(): st.session_state.data['jogos_salvos'] = []

# --- LÓGICA IA ---
def analisar(h):
    f = Counter([n for j in h for n in j['dezenas']])
    at = {n: 0 for n in range(1, 26)}
    for j in reversed(h):
        for n in range(1, 26):
            if n not in j['dezenas'] and at[n] == 0: at[n] += 1
    m = st.session_state.data["ia_memoria"]
    strat = "Tendencia" if (m['Tendencia']['pontos']/max(1,m['Tendencia']['usos'])) >= (m['Reversao']['pontos']/max(1,m['Reversao']['usos'])) else "Reversao"
    pesos = {i: (f.get(i,1)+10 if strat=="Tendencia" else max(1, 100-f.get(i,0)+at.get(i,0)*5)) for i in range(1, 26)}
    return {"strat": strat, "pesos": pesos, "freq": f, "atrasos": at, "alvo": (h[-1]['concurso']+1) if h else 1}

# --- UI ---
st.title("🧬 LotoMatrix PRO")
t1, t2, t3, t4, t5 = st.tabs(["📂 Dados", "🧠 Cérebro", "🤖 Gerador", "📜 Fila", "🏆 Auditoria"])

with t1:
    f = st.file_uploader("JSON", type="json")
    if f: st.session_state.data = sanitizar(json.load(f)); st.rerun()
    st.metric("Banca", f"R$ {st.session_state.data['banca']:.2f}")
    st.number_input("Depósito:", key="v_dep", step=10.0); st.button("Depositar", on_click=cb_deposito)

with t2:
    if st.session_state.data["historico_dados"]:
        ia = analisar(st.session_state.data["historico_dados"])
        st.write(f"### Estratégia: {ia['strat']}"); st.info(f"Concurso Alvo: {ia['alvo']}")
        c1, c2 = st.columns(2)
        c1.bar_chart(pd.Series(ia['freq']))
        c2.bar_chart(pd.Series(ia['atrasos']))
    else: st.warning("Suba o Cofre.")

with t3:
    orc = st.number_input("Orçamento (R$):", step=3.5)
    if st.button("Gerar Jogos") and st.session_state.data['banca'] >= orc:
        st.session_state.data['banca'] -= orc
        ia = analisar(st.session_state.data["historico_dados"])
        while orc >= 3.5:
            tam = 16 if orc >= 56 else 15
            jogo = sorted(random.choices(range(1, 26), weights=[ia['pesos'][i] for i in range(1,26)], k=tam))
            st.session_state.data["jogos_salvos"].append({"id": str(uuid.uuid4()), "dezenas": list(set(jogo)), "status": "Aguardando", "concurso_alvo": ia['alvo'], "estrategia": ia['strat']})
            orc -= (56 if tam==16 else 3.5)
        st.rerun()

with t4:
    if st.button("Apagar Todos", on_click=cb_del_all): pass
    for j in st.session_state.data["jogos_salvos"]:
        with st.container(border=True):
            st.write(f"Alvo: {j['concurso_alvo']} | {j['status']}"); st.code(j['dezenas'])
            st.button("🗑️", key=j['id'], on_click=cb_del, args=[j['id']])

with t5:
    if st.button("Sincronizar"):
        res = requests.get("https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest", verify=False).json()
        sorteio = set(map(int, res['dezenas']))
        if not any(h['concurso'] == res['concurso'] for h in st.session_state.data['historico_dados']):
            st.session_state.data['historico_dados'].append({"concurso": res['concurso'], "dezenas": sorted(list(sorteio))})
        for j in st.session_state.data["jogos_salvos"]:
            if j['status'] == "Aguardando":
                pts = len(set(j['dezenas']).intersection(sorteio))
                j['acertos'] = pts; j['status'] = "Premiado" if pts>=11 else "Não Premiado"
                if pts >= 11: st.session_state.data['banca'] += {11:7, 12:14, 13:35, 14:1500, 15:1500000}[pts]
        st.rerun()
