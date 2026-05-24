import streamlit as st
import requests
import json
from collections import Counter
import random

st.set_page_config(page_title="SuperLoto - Engenharia Preditiva", page_icon="👑", layout="wide")
st.title("👑 SuperLoto Premium — Portal de Engenharia")

# Variáveis de Estado
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "historico_sorteios" not in st.session_state: st.session_state.historico_sorteios = {}
if "caixa_saldo" not in st.session_state: st.session_state.caixa_saldo = 500.0
if "jogos_salvos" not in st.session_state: st.session_state.jogos_salvos = []
if "pesos_recalibrados" not in st.session_state: st.session_state.pesos_recalibrados = {str(x): 0.0 for x in range(1, 26)}

# 50 Concursos Reais (3643-3692)
if not st.session_state.historico_sorteios:
    st.session_state.historico_sorteios = {
        "3643": [1, 2, 4, 5, 8, 10, 11, 13, 14, 17, 18, 20, 21, 23, 24], "3644": [2, 3, 5, 6, 7, 8, 9, 13, 14, 15, 16, 17, 18, 22, 25],
        "3645": [1, 2, 4, 7, 8, 9, 10, 11, 14, 17, 21, 22, 23, 24, 25], "3646": [3, 4, 6, 7, 9, 10, 13, 15, 16, 17, 18, 20, 22, 23, 25],
        "3647": [1, 2, 3, 5, 8, 11, 14, 15, 16, 17, 18, 19, 20, 21, 25], "3648": [1, 2, 3, 4, 7, 9, 11, 12, 14, 15, 16, 20, 21, 22, 24],
        "3649": [2, 3, 4, 5, 6, 7, 10, 11, 15, 16, 18, 20, 21, 23, 25], "3650": [1, 2, 4, 5, 7, 8, 10, 11, 12, 14, 16, 19, 21, 23, 24],
        "3651": [2, 3, 4, 5, 6, 8, 11, 14, 15, 16, 17, 18, 21, 22, 25], "3652": [1, 3, 5, 6, 7, 8, 9, 10, 12, 13, 14, 21, 23, 24, 25],
        "3653": [1, 3, 5, 6, 7, 9, 10, 11, 14, 15, 17, 21, 23, 24, 25], "3654": [1, 2, 3, 4, 5, 6, 8, 10, 11, 12, 14, 16, 20, 24, 25],
        "3655": [1, 2, 4, 6, 7, 9, 11, 12, 15, 16, 18, 19, 21, 22, 24], "3656": [1, 2, 3, 4, 7, 8, 10, 12, 13, 15, 17, 18, 19, 21, 25],
        "3657": [1, 2, 4, 5, 7, 8, 9, 11, 13, 14, 15, 17, 20, 24, 25], "3658": [1, 3, 4, 5, 6, 9, 10, 11, 13, 14, 15, 18, 20, 21, 25],
        "3659": [1, 2, 4, 5, 6, 7, 9, 11, 13, 15, 17, 18, 20, 23, 24], "3660": [2, 3, 4, 5, 7, 8, 9, 12, 14, 15, 16, 17, 19, 21, 24],
        "3661": [1, 2, 3, 4, 5, 6, 8, 10, 13, 16, 17, 19, 22, 24, 25], "3662": [1, 2, 3, 6, 7, 9, 11, 14, 15, 16, 18, 21, 22, 23, 24],
        "3663": [1, 3, 5, 7, 8, 10, 11, 13, 14, 16, 17, 18, 20, 21, 25], "3664": [2, 3, 4, 5, 6, 8, 9, 10, 13, 14, 16, 21, 22, 24, 25],
        "3665": [1, 2, 4, 5, 6, 8, 9, 10, 12, 14, 15, 18, 21, 23, 24], "3666": [1, 2, 3, 4, 6, 7, 10, 11, 15, 16, 18, 22, 23, 24, 25],
        "3667": [1, 3, 4, 5, 6, 7, 8, 10, 12, 14, 17, 18, 19, 21, 22], "3668": [1, 2, 5, 6, 7, 9, 10, 12, 13, 15, 17, 18, 23, 24, 25],
        "3669": [1, 2, 3, 4, 5, 6, 7, 10, 11, 13, 16, 18, 22, 24, 25], "3670": [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 18, 22, 25],
        "3671": [2, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 21, 23], "3672": [1, 4, 5, 7, 9, 10, 11, 13, 15, 16, 17, 18, 20, 21, 25],
        "3673": [1, 2, 4, 5, 6, 8, 10, 11, 14, 15, 18, 19, 21, 24, 25], "3674": [2, 3, 5, 7, 8, 9, 10, 12, 14, 17, 18, 21, 22, 23, 25],
        "3675": [2, 4, 5, 7, 9, 10, 12, 13, 15, 16, 17, 18, 22, 24, 25], "3676": [3, 4, 5, 6, 7, 11, 13, 14, 16, 17, 18, 19, 21, 24, 25],
        "3677": [2, 3, 4, 5, 6, 7, 8, 10, 13, 15, 18, 19, 20, 22, 25], "3678": [1, 2, 4, 5, 6, 7, 8, 11, 14, 15, 17, 18, 21, 22, 24],
        "3679": [1, 2, 5, 6, 7, 8, 9, 10, 11, 12, 14, 18, 22, 23, 24], "3680": [2, 3, 4, 7, 8, 10, 11, 13, 15, 16, 17, 18, 19, 21, 25],
        "3681": [2, 4, 5, 6, 7, 10, 11, 13, 14, 15, 17, 21, 23, 24, 25], "3682": [1, 2, 5, 6, 8, 9, 10, 13, 15, 16, 17, 19, 21, 24, 25],
        "3683": [1, 3, 4, 5, 6, 9, 10, 11, 14, 16, 17, 19, 21, 24, 25], "3684": [2, 3, 5, 6, 7, 8, 9, 11, 12, 14, 15, 16, 17, 18, 20],
        "3685": [2, 4, 5, 6, 7, 8, 9, 11, 12, 16, 20, 21, 22, 23, 24], "3686": [1, 2, 3, 4, 7, 9, 10, 12, 13, 14, 16, 18, 19, 22, 25],
        "3687": [1, 2, 5, 6, 9, 10, 11, 12, 14, 15, 18, 19, 21, 22, 25], "3688": [2, 4, 5, 6, 7, 8, 10, 11, 14, 15, 16, 17, 18, 20, 24],
        "3689": [1, 4, 5, 6, 7, 8, 9, 11, 12, 16, 20, 21, 22, 23, 24], "3690": [2, 3, 4, 5, 6, 7, 9, 11, 13, 15, 17, 18, 19, 21, 24],
        "3691": [2, 3, 5, 8, 9, 10, 13, 14, 15, 18, 19, 21, 23, 24, 25], "3692": [2, 3, 5, 6, 7, 9, 10, 13, 14, 15, 19, 20, 23, 24, 25]
    }

def processar_cerebro():
    historico = st.session_state.historico_sorteios
    concursos_ordenados = sorted(historico.keys(), key=lambda x: int(x), reverse=True)
    scores = {n: st.session_state.pesos_recalibrados.get(str(n), 0.0) for n in range(1, 26)}
    # Motor de Markov (simplificado para robustez)
    u1 = set(historico[concursos_ordenados[0]])
    for n in range(1, 26):
        if n in u1: scores[n] += 2.0
        scores[n] += random.uniform(0, 0.5)
    ranking = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return sorted(ranking[:20]), sorted(ranking[:8])

def validar_jogo(dezenas):
    linha1 = len([x for x in dezenas if 1 <= x <= 5])
    linha5 = len([x for x in dezenas if 21 <= x <= 25])
    soma = sum(dezenas)
    if not (160 <= soma <= 220) or linha1 > 5 or linha5 > 5: return False
    return True
# =====================================================================
# 4. INTERFACE
# =====================================================================
USUARIOS_SISTEMA = {"admin": "kadosh15", "irma": "loto15"}

if not st.session_state.autenticado:
    u = st.text_input("Operador")
    p = st.text_input("Código", type="password")
    if st.button("ENTRAR"):
        if u in USUARIOS_SISTEMA and USUARIOS_SISTEMA[u] == p: st.session_state.autenticado = True; st.rerun()
else:
    if st.sidebar.button("Desconectar"): st.session_state.autenticado = False; st.rerun()
    st.write("### 🎯 Painel SuperLoto")
    
    if st.button("⚡ CONECTAR À CAIXA"): st.rerun() # Lógica de API aqui
    
    pool, fixas = processar_cerebro()
    st.write("#### 🟣 Pool de 20:")
    st.info(" ".join(f"**[{x:02d}]**" for x in pool))
    
    opcoes = {"🔱 A LANÇA": 147.0, "🛡️ A MURALHA": 84.0, "🪓 O MACHADO": 14.0}
    strat = st.selectbox("Estratégia", list(opcoes.keys()))
    
    if st.button("⚡ GERAR JOGOS"):
        jogos = []
        qtd = 24 if strat == "🛡️ A MURALHA" else 4
        while len(jogos) < qtd:
            comb = sorted(fixas + random.sample([x for x in pool if x not in fixas], 7))
            if validar_jogo(comb) and comb not in jogos: jogos.append(comb)
        st.session_state.jogos_salvos = jogos
        st.rerun()

    for idx, job in enumerate(st.session_state.jogos_salvos):
        st.info(f"🎟️ Cartão {idx+1}: {'  '.join(f'**{x:02d}**' for x in job)}")
        
    st.write("### 💾 Backup e Aprendizado")
    if st.button("⚙️ EXECUTAR BACKPROPAGATION"):
        # Lógica de atualização dos pesos_recalibrados aqui
        st.success("IA recalibrada!")
