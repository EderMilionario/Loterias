import streamlit as st, pandas as pd, requests as rq, json, random, uuid
st.set_page_config(layout="wide")
if not st.session_state.get('auth'):
    if st.text_input("Senha:", type="password") == "admin123": st.session_state.auth = True; st.rerun()
    st.stop()
def s(d): 
    d.setdefault("banca",0.0); d.setdefault("historico_dados",[]); d.setdefault("jogos_salvos",[]); d.setdefault("mem", {"Tendencia": [0,0], "Reversao": [0,0]})
    for j in d["jogos_salvos"]: j.setdefault("id", str(uuid.uuid4())); j.setdefault("status", "Aguardando")
    return d
if 'data' not in st.session_state: st.session_state.data = s({})
def ia_engine(h, m):
    f = Counter([n for j in h for n in j['dezenas']]); at = {n: sum(1 for j in reversed(h) if n not in j['dezenas'] and j['concurso'] > h[-1]['concurso']-5) for n in range(1,26)}
    strat = "Tendencia" if (m["Tendencia"][1]/max(1,m["Tendencia"][0])) >= (m["Reversao"][1]/max(1,m["Reversao"][0])) else "Reversao"
    pesos = {i: (f[i]+10 if strat=="Tendencia" else max(1, 100-f[i]+at[i]*5)) for i in range(1,26)}
    return strat, pesos, f, at
# --- TABS ---
t1, t2, t3, t4, t5 = st.tabs(["📂 Dados", "🧠 Cérebro", "🤖 Gerador", "📜 Fila", "🏆 Auditoria"])
with t1:
    f = st.file_uploader("JSON", type="json")
    if f: st.session_state.data = s(json.load(f)); st.rerun()
    st.metric("Banca", f"R$ {st.session_state.data['banca']:.2f}"); v = st.number_input("Depósito:", step=10.0)
    if st.button("Depositar"): st.session_state.data['banca'] += v; st.rerun()
with t2:
    if st.session_state.data["historico_dados"]:
        strat, p, f, at = ia_engine(st.session_state.data["historico_dados"], st.session_state.data["mem"])
        st.write(f"Estratégia: **{strat}**"); st.bar_chart(pd.Series(f)); st.bar_chart(pd.Series(at))
with t3:
    orc = st.number_input("Orçamento:", step=3.5)
    if st.button("Gerar") and st.session_state.data['banca'] >= orc:
        st.session_state.data['banca'] -= orc; strat, p, _, _ = ia_engine(st.session_state.data["historico_dados"], st.session_state.data["mem"])
        while orc >= 3.5:
            tam = 16 if orc >= 56 else 15; custo = 56 if tam==16 else 3.5
            st.session_state.data["jogos_salvos"].append({"id":str(uuid.uuid4()), "dezenas":sorted(random.choices(range(1,26), weights=[p[i] for i in range(1,26)], k=tam)), "status":"Aguardando", "estrategia":strat, "acertos":0})
            orc -= custo
        st.rerun()
with t4:
    for j in st.session_state.data["jogos_salvos"]:
        with st.container(border=True):
            st.write(f"Estratégia: {j['estrategia']} | Acertos: {j['acertos']}"); st.code(list(set(j['dezenas'])))
            if st.button("🗑️", key=j['id']): st.session_state.data["jogos_salvos"].remove(j); st.rerun()
with t5:
    if st.button("Sincronizar Caixa"):
        r = rq.get("https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest", verify=False).json()
        sorteio = set(map(int, r['dezenas']))
        if not any(h['concurso'] == r['concurso'] for h in st.session_state.data['historico_dados']): st.session_state.data['historico_dados'].append({"concurso": r['concurso'], "dezenas": sorted(list(sorteio))})
        for j in st.session_state.data["jogos_salvos"]:
            if j['status'] == "Aguardando":
                pts = len(set(j['dezenas']).intersection(sorteio)); j['acertos'] = pts; j['status'] = "Premiado" if pts>=11 else "Não"
                m = st.session_state.data["mem"][j['estrategia']]; m[0]+=1; m[1]+=pts
                if pts >= 11: st.session_state.data['banca'] += {11:7, 12:14, 13:35, 14:1500, 15:1500000}[pts]
        st.rerun()
    st.table(pd.DataFrame(st.session_state.data.get("historico_dados", [])[-1:]))
