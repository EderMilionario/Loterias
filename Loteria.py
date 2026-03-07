import streamlit as st
import requests
import time
import json
import random
import re
import pandas as pd
from collections import Counter
from itertools import combinations
from fpdf import FPDF
import io

# --- 1. CONFIGURAÇÃO E ESTÉTICA ---
st.set_page_config(page_title="LOTERIAS - KADOSH ESTRATÉGICO", layout="wide")
st.markdown("""
    <style>
    .stApp {background-color: #ffffff !important;}
    p, label, span, div {color: #000000 !important; font-weight: bold !important;}
    code {font-size: 18px !important; color: black !important; font-weight: bold !important;}
    div.stButton > button {
        background: linear-gradient(45deg, #1e3799, #0984e3) !important;
        color: white !important; font-weight: bold !important; border-radius: 8px !important;
        width: 100% !important; text-transform: uppercase !important;
    }
    .status-backup { padding: 5px 10px; border-radius: 20px; font-size: 12px; float: right; background: #f0f2f6; border: 1px solid #d1d1d1; }
    </style>
""", unsafe_allow_html=True)

# --- 2. FUNÇÕES DE SUPORTE (LÓGICA KADOSH) ---

def mostrar_status_backup():
    total_jogos = len(st.session_state.get('jogos_salvos', []))
    total_res = sum(len(v) for v in st.session_state.get('ultimo_res', {}).values())
    st.markdown(f'<div class="status-backup">📁 Backup: {total_jogos} jogos | {total_res} resultados</div>', unsafe_allow_html=True)

def analisar_quadrantes(jogo):
    q1 = q2 = q3 = q4 = 0
    for n in jogo:
        linha = (n-1) // 5
        coluna = (n-1) % 5
        if linha <= 1 and coluna <= 2: q1 += 1
        elif linha <= 1 and coluna > 2: q2 += 1
        elif linha > 1 and coluna <= 2: q3 += 1
        else: q4 += 1
    return f"{q1}|{q2}|{q3}|{q4}"

def validar_kadosh_cirurgico(jogo, mod, n_dez):
    if mod != "Lotofácil": return True
    diff_n = n_dez - 15
    # Âncoras e Saltos
    if not (jogo[0] in [1, 2, 3] and jogo[-1] in [23, 24, 25]): return False
    for i in range(len(jogo)-1):
        if (jogo[i+1] - jogo[i]) > 5: return False
    # Geometria Real (Máximo 5 por linha/coluna)
    linhas = [0]*5
    colunas = [0]*5
    for n in jogo:
        linhas[(n-1)//5] += 1
        colunas[(n-1)%5] += 1
    if any(l > 5 for l in linhas) or any(c > 5 for c in colunas): return False
    # Soma Adaptativa
    soma = sum(jogo)
    if not (165 + (diff_n * 12) <= soma <= 215 + (diff_n * 14)): return False
    return True

# --- 3. INICIALIZAÇÃO DE ESTADOS ---
ESTRATEGIA_MAPA = {"SNIPER": {"dez": 15}, "ELITE": {"dez": 16}, "MARRETA": {"dez": 18}}
MATRIZES_FECHAMENTO = {"Nenhum": None, "18-15-14": {"n": 18}, "20-15-13": {"n": 20}}
custos_globais = {"Lotofácil": {15: 3.5, 16: 56.0, 17: 408.0, 18: 2448.0}}

if 'jogos_gerados' not in st.session_state: st.session_state.jogos_gerados = []
if 'jogos_salvos' not in st.session_state: st.session_state.jogos_salvos = []
if 'ultimo_res' not in st.session_state: st.session_state.ultimo_res = {m: {} for m in custos_globais.keys()}
if 'favoritas' not in st.session_state: st.session_state.favoritas = {m: [] for m in custos_globais.keys()}
if 'analise_stats' not in st.session_state: st.session_state.analise_stats = {m: {} for m in custos_globais.keys()}
# --- 4. INTERFACE ---
st.title("📊 GESTÃO ESTRATÉGICA LOTERIAS")
abas = st.tabs(["🎯 GERADOR PRO", "🔍 CONFERIR", "📥 DATABASE", "💾 BACKUP"])

with abas[0]:
    mostrar_status_backup()
    mod = st.selectbox("Modalidade", list(custos_globais.keys()), key="mod_principal")
    
    # --- RADAR DE TENDÊNCIAS (QUADRANTES & SCORE) ---
    stats_temp = st.session_state.analise_stats.get(mod, {})
    if stats_temp:
        c_q, c_f = st.columns(2)
        quentes = sorted(stats_temp.items(), key=lambda x: x[1].get('score', 0), reverse=True)[:6]
        with c_q: st.success(f"🔥 QUENTES: {' '.join([f'**{n:02d}**' for n, s in quentes])}")

    # --- CONFIGURAÇÃO E MATRIZES ---
    c_cfg1, c_cfg2 = st.columns(2)
    with c_cfg1:
        fe_escolhido = st.selectbox("📐 MATRIZ", list(MATRIZES_FECHAMENTO.keys()))
        est_escolhida = st.selectbox("💎 ESTRATÉGIA", list(ESTRATEGIA_MAPA.keys()))
    with c_cfg2:
        n_dez = st.selectbox("Dezenas/Bilhete", list(custos_globais[mod].keys()))
        qtd = st.number_input("Qtd de Jogos", 1, 1000, 20)

    # --- POOL E BOTÃO TODO O VOLANTE ---
    st.markdown("### 🎯 POOL (O CERCO)")
    if st.button("✅ SELECIONAR TODO O VOLANTE"):
        st.session_state.favoritas[mod] = list(range(1, 26 if mod=="Lotofácil" else 61))
        st.rerun()
            
    pool = st.multiselect("SEU POOL:", range(1, 26 if mod=="Lotofácil" else 61), default=st.session_state.favoritas.get(mod, []))
    st.session_state.favoritas[mod] = pool

    # --- FIXAS (IA E MANUAL) ---
    st.markdown("### 📌 FIXAS OBRIGATÓRIAS")
    c_fx1, c_fx2 = st.columns([1, 2])
    with c_fx1:
        modo_fixa = st.radio("SISTEMA:", ["Sem Fixas", "Manual", "IA Automática"])
    
    fixas_final = []
    with c_fx2:
        if modo_fixa == "Manual":
            fixas_final = st.multiselect("Fixas do Pool:", options=pool)
        elif modo_fixa == "IA Automática":
            num_f = st.slider("Qtd Fixas IA:", 1, 12, 6)
            if stats_temp:
                melhores_pool = sorted([n for n in pool], key=lambda x: stats_temp.get(x, {}).get('score', 0), reverse=True)
                fixas_final = melhores_pool[:num_f]
                st.warning(f"💎 IA TRAVOU: {', '.join([f'{x:02d}' for x in fixas_final])}")

    st.markdown("---")

    # --- MOTOR KADOSH COM FILTROS DE QUADRANTE ---
    if st.button("🚀 EXECUTAR MOTOR KADOSH", use_container_width=True):
        if len(pool) < n_dez:
            st.error("Pool insuficiente!")
        else:
            novos = []
            p_sorteio = [n for n in pool if n not in fixas_final]
            tentativas = 0
            while len(novos) < qtd and tentativas < 40000:
                vagas = n_dez - len(fixas_final)
                if len(p_sorteio) < vagas: break
                comb = sorted(fixas_final + random.sample(p_sorteio, vagas))
                
                # VALIDAÇÃO GEOMÉTRICA E QUADRANTES (SUA INTELIGÊNCIA)
                if validar_kadosh_cirurgico(comb, mod, n_dez):
                    quad_result = analisar_quadrantes(comb)
                    novos.append({
                        "mod": mod, "n": comb, "tam": n_dez, "est": est_escolhida, 
                        "quad": quad_result, "fixas": list(fixas_final)
                    })
                tentativas += 1
            st.session_state.jogos_gerados = novos
            st.rerun()

    # --- LISTAGEM COM SCANNER DE QUADRANTES ---
    if st.session_state.jogos_gerados:
        for i, j in enumerate(st.session_state.jogos_gerados):
            st.code(f"ID {i+1:02d} | {' '.join([f'{x:02d}' for x in j['n']])} | QUAD: {j['quad']}")
        if st.button("💾 CONFIRMAR E SALVAR TUDO"):
            st.session_state.jogos_salvos.extend(st.session_state.jogos_gerados)
            st.session_state.jogos_gerados = []
            st.success("Salvo com sucesso!")
            st.rerun()

# --- ABA DATABASE (INPUT DE RESULTADOS) ---
with abas[2]:
    st.header("📥 Database")
    m_db = st.selectbox("Loteria", list(custos_globais.keys()), key="m_db_final")
    txt_man = st.text_area("Cole o resultado (Ex: 01 02...)")
    id_c = st.number_input("Concurso", 1, 9999)
    if st.button("💾 GRAVAR RESULTADO"):
        numeros = sorted([int(n) for n in re.findall(r'\d+', txt_man)])
        if len(numeros) > 0:
            st.session_state.ultimo_res[m_db][str(id_c)] = numeros
            # ATUALIZA RADAR
            contagem = Counter()
            res_list = list(st.session_state.ultimo_res[m_db].values())
            for r in res_list:
                for n in r: contagem[n] += 1
            st.session_state.analise_stats[m_db] = {n: {'score': contagem[n]} for n in range(1, 26)}
            st.success(f"Concurso {id_c} gravado!")
        else:
            st.error("Nenhum número detectado!")
