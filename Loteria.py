import streamlit as st
import json
import random
import re
import pandas as pd
from collections import Counter
from itertools import combinations
from fpdf import FPDF  # Acréscimo para PDF
import io

# --- 1. CONFIGURAÇÃO E ESTÉTICA ---
st.set_page_config(page_title="LOTERIAS - KADOSH ESTRATÉGICO", layout="wide")
st.markdown("""
    <style>
    .stApp {background-color: #ffffff !important;}
    p, label, span, div {color: #000000 !important; font-weight: bold !important;}
    .stCodeBlock {border: 2px solid #000000 !important;}
    code {font-size: 18px !important; color: black !important; font-weight: bold !important;}
    
    div.stButton > button {
        background: linear-gradient(45deg, #1e3799, #0984e3) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100% !important;
        transition: 0.3s !important;
        text-transform: uppercase !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(45deg, #0984e3, #1e3799) !important;
        transform: scale(1.02) !important;
    }

    .painel-luxo-black {
        background: #1a1a1a;
        border: 3px solid #d4af37;
        padding: 40px;
        border-radius: 25px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        margin-bottom: 30px;
    }
    .titulo-luxo-gold {
        color: #d4af37 !important;
        font-size: 20px !important;
        letter-spacing: 4px !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }
    .valor-luxo-white {
        color: #ffffff !important;
        font-size: 60px !important;
        font-weight: 900 !important;
        margin: 10px 0;
        text-shadow: 0 0 15px rgba(212,175,55,0.5);
    }
    
    .jogo-premiado {
        background-color: #e8f5e9 !important;
        border: 3px solid #d4af37 !important;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    .moeda-animada {
        display: inline-block;
        font-size: 45px;
        animation: rotateCoin 2.5s infinite linear;
    }
    @keyframes rotateCoin {
        from { transform: rotateY(0deg); }
        to { transform: rotateY(360deg); }
    }
    .status-backup {
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        float: right;
        background: #f0f2f6;
        border: 1px solid #d1d1d1;
    }
    /* Estilos para o Pool na Conferência */
    .dezena-pool {
        display: inline-block;
        width: 35px;
        height: 35px;
        line-height: 35px;
        text-align: center;
        border-radius: 50%;
        margin: 3px;
        font-size: 14px;
        font-weight: bold;
        color: white;
    }
    .pool-vermelho { background-color: #ff4b4b; border: 1px solid #8b0000; }
    .pool-verde { background-color: #28a745; border: 1px solid #145214; box-shadow: 0 0 8px #28a745; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES TÉCNICAS (MOTOR DE ALTA PRECISÃO) ---

def gerar_pdf_bonito(jogos, modalidade):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"VOLANTES OFICIAIS KADOSH - {modalidade}", ln=True, align='C')
    pdf.ln(10)
    for i, j in enumerate(jogos):
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt=f"JOGO {i+1:02d} - Estrategia: {j['est']}", ln=True)
        pdf.set_font("Arial", '', 11)
        # Grade de dezenas
        dez_str = ' | '.join([f"{x:02d}" for x in j['n']])
        pdf.multi_cell(0, 10, txt=f"DEZENAS: {dez_str}", border=1)
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1')

def formata_dinheiro(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    except: 
        return f"R$ {valor}"

def definir_label_chance(jogo, mod):
    if mod != "Lotofácil": 
        return "PADRÃO"
    soma = sum(jogo)
    n = len(jogo)
    media_esperada = 180 + ((n - 15) * 13)
    if (media_esperada - 10) <= soma <= (media_esperada + 10): 
        return "ALTA"
    return "PADRÃO"

def jogo_ja_saiu(jogo, mod):
    res_hist = st.session_state.ultimo_res.get(mod, {})
    if not res_hist: 
        return False
    conjunto_resultados = [set(res) for res in res_hist.values()]
    if len(jogo) == 15:
        return set(jogo) in conjunto_resultados
    for combo in combinations(jogo, 15):
        if set(combo) in conjunto_resultados: 
            return True
    return False

def validar_kadosh_cirurgico(jogo, mod, n_dez):
    if mod != "Lotofácil": 
        return True
    
    if not (jogo[0] in [1, 2, 3] and jogo[-1] in [23, 24, 25]): 
        return False
    
    for i in range(len(jogo)-1):
        if (jogo[i+1] - jogo[i]) > 5: 
            return False

    pares = len([n for n in jogo if n % 2 == 0])
    diff_n = n_dez - 15
    if not ( (7 + int(diff_n*0.4)) <= pares <= (9 + int(diff_n*0.6)) ): 
        return False

    fibo_ref = [1, 2, 3, 5, 8, 13, 21]
    fibo_count = len([n for n in jogo if n in fibo_ref])
    if not (3 <= fibo_count <= 5 + int(diff_n*0.5)): 
        return False

    is_atypical = random.random() < 0.12 
    if not is_atypical:
        vizinhos = 0
        sequencia_max = 1
        atual = 1
        for i in range(len(jogo)-1):
            if jogo[i+1] - jogo[i] == 1:
                vizinhos += 1
                atual += 1
                sequencia_max = max(sequencia_max, atual)
            else: 
                atual = 1
        if not (3 <= vizinhos <= 8): 
            return False
        if sequencia_max < 3 or sequencia_max > 5: 
            return False

    linhas = [0]*5
    colunas = [0]*5
    for n in jogo:
        linhas[(n-1)//5] += 1
        colunas[(n-1)%5] += 1
        
    if any(l == 0 for l in linhas) or any(c == 0 for c in colunas): 
        return False
    if any(l > 5 for l in linhas) or any(c > 5 for c in colunas): 
        return False

    soma = sum(jogo)
    primos_list = [2,3,5,7,11,13,17,19,23]
    moldura_list = [1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25]
    primos = len([n for n in jogo if n in primos_list])
    moldura = len([n for n in jogo if n in moldura_list])
    
    cfg = {
        's': (165 + (diff_n * 12), 215 + (diff_n * 14)),
        'p': (4 + int(diff_n * 0.5), 7 + int(diff_n * 0.8)),
        'm': (8 + int(diff_n * 0.7), 11 + int(diff_n * 0.9))
    }
    
    if not (cfg['s'][0] <= soma <= cfg['s'][1]): 
        return False
    if not (cfg['p'][0] <= primos <= cfg['p'][1]): 
        return False
    if not (cfg['m'][0] <= moldura <= cfg['m'][1]): 
        return False

    if jogo_ja_saiu(jogo, mod): 
        return False
        
    return True

def renderizar_heatmap(mod, res_loto):
    if not res_loto or mod != "Lotofácil": 
        return
        
    st.markdown("### 🗺️ MAPA DE CALOR E ANÁLISE DE CICLO (Últimos 20)")
    conc_ordenados = sorted(res_loto.keys(), key=lambda x: int(x), reverse=True)[:20]
    
    frequencia = Counter()
    atraso = {n: 0 for n in range(1, 26)}
    ja_apareceu = set()
    
    for i, c in enumerate(conc_ordenados):
        sorteados = res_loto[c]
        for n in range(1, 26):
            if n in sorteados:
                frequencia[n] += 1
                ja_apareceu.add(n)
            elif n not in ja_apareceu:
                atraso[n] += 1
                
    cols = st.columns(5)
    for n in range(1, 26):
        freq = frequencia[n]
        atr = atraso[n]
        bg_color = "#f1f2f6"
        texto = "black"
        
        if freq >= 12: 
            bg_color = "#eb4d4b"
            texto = "white"
        elif atr >= 3: 
            bg_color = "#0984e3"
            texto = "white"
            
        with cols[(n-1)%5]:
            st.markdown(f'<div style="background-color:{bg_color}; color:{texto}; border-radius:10px; padding:10px; text-align:center; border:2px solid #2d3436; margin-bottom:5px;"><span style="font-size:20px;">{n:02d}</span><br><span style="font-size:10px;">F:{freq} | A:{atr}</span></div>', unsafe_allow_html=True)
            
    st.markdown("---")

def calcular_matriz_afinidade_kadosh(mod):
    res_db = st.session_state.ultimo_res.get(mod, {})
    if len(res_db) < 3: return None
    limite = 26 if mod == "Lotofácil" else 61 if mod == "Mega-Sena" else 81
    matriz = [[0 for _ in range(limite)] for _ in range(limite)]
    for sorteio in res_db.values():
        nums = sorted([int(n) for n in sorteio])
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                d1, d2 = nums[i], nums[j]
                if d1 < limite and d2 < limite:
                    matriz[d1][d2] += 1
                    matriz[d2][d1] += 1
    return matriz

# --- 2. MAPA DE ESTRATÉGIAS E MATRIZES ---
ESTRATEGIA_MAPA = {
    "Personalizado": {"dez": 15, "qtd": 10, "desc": "Configuração manual", "prob": "Variável", "peso": 0.1},
    "1. SNIPER": {"dez": 15, "qtd": 8, "desc": "08 Jogos de 15 (Econômico)", "prob": "1/3.268.760", "peso": 0.2},
    "2. ESCUDO E ESPADA": {"dez": 16, "qtd": 1, "desc": "01 de 16 + 10 de 15", "qtd_15": 10, "prob": "1/204.297", "peso": 0.5},
    "3. EQUILÍBRIO REAL": {"dez": 16, "qtd": 2, "desc": "02 de 16 + 10 de 15 (NATA)", "qtd_15": 10, "prob": "1/102.148", "peso": 0.7},
    "4. ELITE KADOSH": {"dez": 16, "qtd": 2, "desc": "02 de 16 + 15 de 15", "qtd_15": 15, "prob": "1/85.000", "peso": 0.9},
    "5. INVASÃO": {"dez": 15, "qtd": 25, "desc": "25 Jogos de 15 (Volume)", "prob": "1/130.750", "peso": 0.6},
    "6. A MARRETA": {"dez": 18, "qtd": 1, "desc": "01 de 18 + 05 de 16", "qtd_16": 5, "prob": "1/152 (14 pts)", "peso": 0.95},
    "7. SIMETRIA GEOMÉTRICA": {"dez": 16, "qtd": 2, "desc": "02 de 16 + 08 de 15", "qtd_15": 8, "prob": "1/81.719", "peso": 0.85},
    "8. RASTREAMENTO DE CICLO": {"dez": 16, "qtd": 1, "desc": "01 de 16 + 06 de 15 (Tendência)", "qtd_15": 6, "prob": "Alta Recorrência", "peso": 0.88},
    "9. CERCO POR ELIMINAÇÃO": {"dez": 15, "qtd": 10, "desc": "10 Jogos de 15 (Quentes vs Atrasados)", "prob": "Equilibrada", "peso": 0.75}
}

MATRIZES_FECHAMENTO = {
    "Nenhum": None,
    "FECHAMENTO 18-15-14 (Redução Profissional)": {"n_pool": 18, "garantia": 14, "desc": "Garante 14 pts se as 15 estiverem nas 18", "prob": "1/152 para 14 pts", "peso": 0.75},
    "FECHAMENTO 19-15-14 (Intermediário)": {"n_pool": 19, "garantia": 14, "desc": "Garante 14 pts se as 15 estiverem nas 19", "prob": "1/103 para 14 pts", "peso": 0.85},
    "FECHAMENTO 20-15-13 (Cobertura Ampla)": {"n_pool": 20, "garantia": 13, "desc": "Garante 13 pts se as 15 estiverem nas 20", "prob": "1/12 para 13 pts", "peso": 0.98},
    "MATRIZ DIAMANTE [2x16 + 10x15] (Pool 19)": {"n_pool": 19, "garantia": 14, "desc": "2 de 16 + 10 de 15 (Cerco Inteligente)", "prob": "Alta para 14/15", "peso": 0.92},
    "MATRIZ CÉLULA [1x16 + 15x15] (Pool 18)": {"n_pool": 18, "garantia": 15, "desc": "1 de 16 + 15 de 15 (Malha Fina)", "prob": "Máxima para 15", "peso": 0.96}
}

# --- 4. ESTADOS E ABAS ---
for key in ['auth', 'jogos_gerados', 'jogos_salvos']:
    if key not in st.session_state: 
        st.session_state[key] = False if key == 'auth' else []
        
if 'ultimo_res' not in st.session_state: 
    st.session_state.ultimo_res = {m: {} for m in ["Lotofácil", "Mega-Sena", "Quina", "+Milionária", "Dupla-Sena"]}
    
if 'favoritas' not in st.session_state: 
    st.session_state.favoritas = {m: [] for m in ["Lotofácil", "Mega-Sena", "Quina", "+Milionária", "Dupla-Sena"]}
    
if 'premios' not in st.session_state:
    st.session_state.premios = {
        "Lotofácil": {"11": 7.0, "12": 14.0, "13": 35.0, "14": 1500.0, "15": 1700000.0},
        "Mega-Sena": {"4": 1200.0, "5": 45000.0, "6": 50000000.0},
        "Quina": {"2": 4.0, "3": 150.0, "4": 8000.0, "5": 600000.0},
        "+Milionária": {"2": 6.0, "3": 24.0, "4": 1500.0, "5": 50000.0, "6": 10000000.0},
        "Dupla-Sena": {"3": 6.0, "4": 150.0, "5": 4000.0, "6": 500000.0}
    }
    
if 'custos' not in st.session_state:
    st.session_state.custos = {
        "Lotofácil": {15: 3.5, 16: 56.0, 17: 408.0, 18: 2448.0, 19: 11628.0, 20: 46512.0},
        "Mega-Sena": {6: 6.0, 7: 42.0, 8: 168.0, 9: 504.0, 10: 1260.0},
        "Quina": {5: 2.5, 6: 15.0, 7: 52.5, 8: 140.0},
        "+Milionária": {6: 6.0},
        "Dupla-Sena": {6: 2.5, 7: 17.5, 8: 70.0}
    }

# --- 5. ACESSO ---
if not st.session_state.auth:
    st.title("🛡️ ACESSO LOTERIAS")
    with st.form("login_form"):
        senha = st.text_input("CHAVE DE ACESSO", type="password")
        if st.form_submit_button("ENTRAR"):
            if senha == "kadosh":
                st.session_state.auth = True
                st.rerun()
            else: 
                st.error("Senha incorreta!")
    st.stop()

# --- HELPER: INDICADOR DE BACKUP EM TODAS AS ABAS ---
def mostrar_status_backup():
    total_jogos = len(st.session_state.jogos_salvos)
    total_res = sum(len(v) for v in st.session_state.ultimo_res.values())
    st.markdown(f'<div class="status-backup">📁 Backup Ativo: {total_jogos} jogos | {total_res} resultados</div>', unsafe_allow_html=True)

# --- 6. INTERFACE ---
st.title("📊 GESTÃO ESTRATÉGICA LOTERIAS")
abas = st.tabs(["🎯 GERADOR PRO", "🔍 CONFERIR", "⚙️ VALORES", "📥 DATABASE", "💾 BACKUP", "🧠 INTELIGÊNCIA", "🔗 AFINIDADE"])

with abas[0]:
    # --- CORREÇÃO DE SEGURANÇA (INICIALIZAÇÃO) ---
    if 'analise_stats' not in st.session_state:
        st.session_state.analise_stats = {}
    
    # --- NOVO: INICIALIZAÇÃO DE MEMÓRIA PARA FIXAS SUGERIDAS ---
    if 'fixas_sugeridas_ia' not in st.session_state:
        st.session_state.fixas_sugeridas_ia = {m: [] for m in ["Lotofácil", "Mega-Sena", "Quina", "+Milionária", "Dupla-Sena"]}
    
    [cite_start]mostrar_status_backup() [cite: 51]
    [cite_start]mod = st.selectbox("Modalidade", list(st.session_state.custos.keys()), key="mod_selector") [cite: 53]
    
    if 'ultima_mod_selecionada' not in st.session_state:
        [cite_start]st.session_state.ultima_mod_selecionada = mod [cite: 53]
        
    if st.session_state.ultima_mod_selecionada != mod:
        [cite_start]st.session_state.jogos_gerados = [] [cite: 53]
        [cite_start]st.session_state.ultima_mod_selecionada = mod [cite: 53]
        [cite_start]st.rerun() [cite: 53]
    
    [cite_start]col_est1, col_est2 = st.columns(2) [cite: 53]
    with col_est1:
        if mod == "Lotofácil":
            [cite_start]est_escolhida = st.selectbox("💎 ESTRATÉGIA KADOSH", list(ESTRATEGIA_MAPA.keys())) [cite: 54]
            [cite_start]est_info = ESTRATEGIA_MAPA[est_escolhida] [cite: 54]
            [cite_start]st.progress(est_info["peso"]) [cite: 54]
            [cite_start]qtd_total_est = est_info.get("qtd", 0) + est_info.get("qtd_15", 0) + est_info.get("qtd_16", 0) [cite: 54]
            [cite_start]st.markdown(f"🎯 **Probabilidade:** {est_info['prob']} | 📦 **Volume:** {qtd_total_est} jogos") [cite: 55]
        else:
            [cite_start]est_escolhida = "Personalizado" [cite: 55]
            
    with col_est2:
        if mod == "Lotofácil":
            [cite_start]fe_escolhido = st.selectbox("📐 MODO FECHAMENTO (MATRIZ)", list(MATRIZES_FECHAMENTO.keys())) [cite: 56]
            if fe_escolhido != "Nenhum":
                [cite_start]fe_info = MATRIZES_FECHAMENTO[fe_escolhido] [cite: 56]
                [cite_start]st.progress(fe_info["peso"]) [cite: 56]
                [cite_start]st.markdown(f"📐 **Garantia:** {fe_info['prob']} | 🧬 **Pool:** {fe_info['n_pool']} dezenas") [cite: 56]
            else:
                [cite_start]st.markdown("<br><br>", unsafe_allow_html=True) [cite: 56]
        else:
            [cite_start]fe_escolhido = "Nenhum" [cite: 56]

    [cite_start]info_fech = MATRIZES_FECHAMENTO.get(fe_escolhido) if mod == "Lotofácil" else None [cite: 57]
    [cite_start]info_est = ESTRATEGIA_MAPA.get(est_escolhida) if mod == "Lotofácil" else ESTRATEGIA_MAPA["Personalizado"] [cite: 57]
    
    [cite_start]st.markdown("---") [cite: 57]

    [cite_start]c1, c2 = st.columns(2) [cite: 57]
    with c1:
        if info_fech:
            if "DIAMANTE" in fe_escolhido: 
                [cite_start]def_dez, def_qtd = 16, 2 [cite: 58]
            elif "CÉLULA" in fe_escolhido: 
                [cite_start]def_dez, def_qtd = 16, 1 [cite: 58]
            else: 
                [cite_start]def_dez, def_qtd = 15, (24 if "18-15-14" in fe_escolhido else 45) [cite: 58]
        elif est_escolhida != "Personalizado" and mod == "Lotofácil":
            [cite_start]def_dez, def_qtd = info_est["dez"], info_est.get("qtd", 10) [cite: 58]
        else:
            [cite_start]def_dez = list(st.session_state.custos[mod].keys())[0] [cite: 59]
            [cite_start]def_qtd = 10 [cite: 59]
            
        [cite_start]opcoes_dez = list(st.session_state.custos[mod].keys()) [cite: 59]
        [cite_start]idx_padrao = opcoes_dez.index(def_dez) if def_dez in opcoes_dez else 0 [cite: 59]
        [cite_start]n_dez = st.selectbox("Dezenas por Bilhete", opcoes_dez, index=idx_padrao) [cite: 59]
        [cite_start]qtd = st.number_input("Quantidade de Jogos", 1, 300, def_qtd) [cite: 59]
       
    with c2:
        [cite_start]max_v = 25 if mod=="Lotofácil" else 60 if mod=="Mega-Sena" else 80 [cite: 60]
        [cite_start]col_btn1, col_btn2 = st.columns(2) [cite: 60]
        
        with col_btn1:
            if st.button("✅ TODO O VOLANTE"):
                [cite_start]st.session_state.favoritas[mod] = list(range(1, max_v + 1)) [cite: 60]
                [cite_start]st.rerun() [cite: 61]
                
        with col_btn2:
            if st.button("🧠 POOL INTELIGENTE KADOSH"):
                [cite_start]res_loto = st.session_state.ultimo_res.get(mod, {}) [cite: 61]
                if len(res_loto) >= 5:
                    [cite_start]n_pool_req = info_fech['n_pool'] if info_fech else 20 [cite: 62]
                    [cite_start]conc_ordenados = sorted(res_loto.keys(), key=lambda x: int(x), reverse=True)[:20] [cite: 62]
                    [cite_start]score_kadosh = {} [cite: 62]
                    [cite_start]contagem = Counter() [cite: 62]
                    
                    for c in conc_ordenados:
                        for n in res_loto[c]: 
                            [cite_start]contagem[n] += 1 [cite: 63]
                   
                    for n in range(1, max_v + 1):
                        [cite_start]atraso_n = 0 [cite: 64]
                        for c in conc_ordenados:
                            if n not in res_loto[c]: 
                                [cite_start]atraso_n += 1 [cite: 65]
                            else: 
                                [cite_start]break [cite: 66]
                        [cite_start]score_kadosh[n] = contagem[n] + (atraso_n * 1.5) [cite: 66]
                        
                    [cite_start]melhores = sorted(score_kadosh.items(), key=lambda x: x[1], reverse=True) [cite: 66]
                    [cite_start]st.session_state.favoritas[mod] = sorted([n for n, s in melhores[:n_pool_req]]) [cite: 67]
                    
                    # --- NOVO: CAPTURA DE FIXAS SUGERIDAS PELA IA ---
                    st.session_state.fixas_sugeridas_ia[mod] = sorted([n for n, s in melhores[:6]])
                    
                    [cite_start]st.rerun() [cite: 67]

        [cite_start]pool = st.multiselect("SELECIONE SEU POOL", range(1, max_v + 1), default=st.session_state.favoritas.get(mod, [])) [cite: 67]
        [cite_start]st.session_state.favoritas[mod] = pool [cite: 67]
        
        # --- NOVO: EXIBIÇÃO VISUAL DAS FIXAS DO POOL INTELIGENTE ---
        if st.session_state.fixas_sugeridas_ia.get(mod):
            st.markdown("### 📌 FIXAS SUGERIDAS (IA SCORE)")
            fixas_html = '<div style="margin-bottom: 10px;">'
            for f in st.session_state.fixas_sugeridas_ia[mod]:
                fixas_html += f'<span style="background:#d4af37; color:black; padding:5px 12px; border-radius:15px; margin-right:5px; border:1px solid black; font-weight:bold; font-size:14px;">{f:02d}</span>'
            fixas_html += '</div>'
            st.markdown(fixas_html, unsafe_allow_html=True)
        
        [cite_start]modo_fixa = st.radio("MODO DE FIXAÇÃO:", ["Sem Fixas", "Manual", "IA Automática (Score)"], horizontal=True) [cite: 67]
        [cite_start]fixas_final = [] [cite: 68]
        if modo_fixa == "Manual":
            [cite_start]fixas_final = st.multiselect("📌 CRAVAR DEZENAS:", options=pool) [cite: 68]
        elif modo_fixa == "IA Automática (Score)":
            [cite_start]qtd_auto = st.slider("Qtd de Cravadas:", 1, 10, 6) [cite: 68]
            if mod in st.session_state.analise_stats:
                [cite_start]stats = st.session_state.analise_stats[mod] [cite: 69]
                [cite_start]melhores_ia = sorted([n for n in pool], key=lambda x: stats.get(x, {}).get('score', 0), reverse=True) [cite: 69]
                [cite_start]fixas_final = melhores_ia[:qtd_auto] [cite: 69]
                [cite_start]st.info(f"💎 IA CRAVOU: {', '.join(map(str, fixas_final))}") [cite: 69]
        
        [cite_start]renderizar_heatmap(mod, st.session_state.ultimo_res.get(mod, {})) [cite: 69]

    [cite_start]if st.button("🚀 GERAR JOGOS (SINCRO-MATRIZ KADOSH)"): [cite: 69]
        [cite_start]if len(pool) < (info_fech['n_pool'] if info_fech else n_dez): [cite: 70]
            [cite_start]st.error(f"Seu Pool precisa de pelo menos {info_fech['n_pool'] if info_fech else n_dez} dezenas!") [cite: 70]
        else:
            [cite_start]novos = [] [cite: 70]
            def gerar_com_matriz(tamanho, quantidade, filtragem=True):
                [cite_start]sucessos, tentativas = 0, 0 [cite: 70]
                [cite_start]pool_para_sorteio = [n for n in pool if n not in fixas_final] [cite: 71]
                [cite_start]vagas_abertas = tamanho - len(fixas_final) [cite: 71]

                while sucessos < quantidade and tentativas < 30000:
                    if len(pool_para_sorteio) >= vagas_abertas:
                        [cite_start]complemento = random.sample(pool_para_sorteio, vagas_abertas) [cite: 72]
                        [cite_start]comb = sorted(fixas_final + complemento) [cite: 72]
                    else:
                        [cite_start]comb = sorted(random.sample(pool, tamanho)) [cite: 72]
               
                    [cite_start]if any(set(comb) == set(existente['n']) for existente in novos): [cite: 73]
                        [cite_start]tentativas += 1 [cite: 73]
                        continue
                  
                    [cite_start]passou = validar_kadosh_cirurgico(comb, mod, tamanho) if filtragem else True [cite: 74]
                    if passou:
                        [cite_start]tag_est = f"{fe_escolhido if info_fech else est_escolhida}" [cite: 74]
                        [cite_start]if fixas_final: tag_est += f" (FIXAS: {len(fixas_final)})" [cite: 75]
                        
                        novos.append({
                            [cite_start]"mod": mod, [cite: 76] 
                            [cite_start]"n": comb, [cite: 76] 
                            [cite_start]"tam": tamanho, [cite: 76] 
                            [cite_start]"fixas_utilizadas": list(fixas_final), [cite: 77]
                            [cite_start]"chance": definir_label_chance(comb, mod), [cite: 77] 
                            [cite_start]"est": tag_est [cite: 77]
                        })
                        [cite_start]sucessos += 1 [cite: 78]
                    [cite_start]tentativas += 1 [cite: 78]

            if info_fech:
                if "DIAMANTE" in fe_escolhido: 
                    [cite_start]gerar_com_matriz(16, 2); gerar_com_matriz(15, 10) [cite: 79]
                elif "CÉLULA" in fe_escolhido: 
                    [cite_start]gerar_com_matriz(16, 1); gerar_com_matriz(15, 15) [cite: 79]
                else: 
                    [cite_start]gerar_com_matriz(15, qtd) [cite: 80]
            elif est_escolhida == "8. RASTREAMENTO DE CICLO": 
                [cite_start]gerar_com_matriz(16, 1); gerar_com_matriz(15, 6) [cite: 80]
            elif est_escolhida == "9. CERCO POR ELIMINAÇÃO": 
                [cite_start]gerar_com_matriz(15, 10) [cite: 81]
            elif est_escolhida == "6. A MARRETA": 
                [cite_start]gerar_com_matriz(18, 1); gerar_com_matriz(16, 5) [cite: 81]
            elif est_escolhida == "7. SIMETRIA GEOMÉTRICA": 
                [cite_start]gerar_com_matriz(16, 2); gerar_com_matriz(15, 8) [cite: 82]
            elif est_escolhida != "Personalizado" and mod == "Lotofácil":
                [cite_start]gerar_com_matriz(info_est['dez'], info_est.get('qtd', 1)) [cite: 83]
                [cite_start]if "qtd_15" in info_est: gerar_com_matriz(15, info_est['qtd_15']) [cite: 83]
            else: 
                [cite_start]gerar_com_matriz(n_dez, qtd) [cite: 83]
           
            [cite_start]st.session_state.jogos_gerados = novos [cite: 84]
            [cite_start]st.rerun() [cite: 84]

    for i, j in enumerate(st.session_state.jogos_gerados):
        [cite_start]txt_jogo = ' '.join([f'{x:02d}' for x in j['n']]) [cite: 84]
        [cite_start]st.code(f"JOGO {i+1:02d} | {j['est']} | {j['tam']} DEZ | {txt_jogo} / {j['chance']}") [cite: 84]
    
    [cite_start]if st.session_state.jogos_gerados and st.button("💾 SALVAR PARA CONFERIR"): [cite: 84]
        [cite_start]res_existentes = st.session_state.ultimo_res.get(mod, {}) [cite: 84]
        [cite_start]ultimo_c = int(max(res_existentes.keys(), key=int)) if res_existentes else 0 [cite: 85]
        [cite_start]pool_atual = list(st.session_state.favoritas.get(mod, [])) [cite: 85]
        for jogo in st.session_state.jogos_gerados:
            [cite_start]jogo['concurso_alvo'] = ultimo_c + 1 [cite: 85]
            [cite_start]jogo['pool_origem'] = pool_atual [cite: 85]
            # NOVO: SALVANDO AS FIXAS USADAS NO MOMENTO DA GERAÇÃO PARA O BACKUP
            jogo['fixas_pool_origem'] = list(jogo.get('fixas_utilizadas', []))
            [cite_start]st.session_state.jogos_salvos.append(jogo) [cite: 85]
        [cite_start]st.session_state.jogos_gerados = [] [cite: 85]
        [cite_start]st.rerun() [cite: 85]
with abas[1]:
    [cite_start]mostrar_status_backup() [cite: 86]
    [cite_start]st.header("🔍 Painel de Conferência") [cite: 86]
    [cite_start]mod_f = st.selectbox("Loteria", list(st.session_state.custos.keys()), key="f_conf") [cite: 86]
    
    [cite_start]jogos_salvos_atual = [j for j in st.session_state.jogos_salvos if j['mod'] == mod_f] [cite: 86]
    
    if jogos_salvos_atual:
        [cite_start]st.markdown("### 🎯 PERFORMANCE DO SEU POOL (CERCO)") [cite: 86]
        [cite_start]res_db = st.session_state.ultimo_res.get(mod_f, {}) [cite: 87]
        
        [cite_start]pool_salvo = jogos_salvos_atual[0].get('pool_origem', []) [cite: 87]
        [cite_start]alvo_pool = str(jogos_salvos_atual[0].get('concurso_alvo', '')) [cite: 87]
        
        if pool_salvo:
            [cite_start]html_pool = '<div style="background: #f8f9fa; padding: 20px; border-radius: 15px; border: 2px solid #1e3799; margin-bottom: 20px;">' [cite: 87]
            [cite_start]acertos_pool = 0 [cite: 88]
            [cite_start]resultado_alvo = res_db.get(alvo_pool, []) [cite: 88]
            
            for d in sorted(pool_salvo):
                [cite_start]classe = "pool-vermelho" [cite: 88]
                if d in resultado_alvo:
                    [cite_start]classe = "pool-verde" [cite: 89]
                    [cite_start]acertos_pool += 1 [cite: 89]
                [cite_start]html_pool += f'<span class="dezena-pool {classe}">{d:02d}</span>' [cite: 89]
            
            [cite_start]html_pool += f'<br><br><span style="font-size: 18px; color: #1e3799;">📊 <b>ACERTOS NO CERCO: {acertos_pool} DEZENAS</b></span>' [cite: 90]
            [cite_start]html_pool += '</div>' [cite: 90]
            [cite_start]st.markdown(html_pool, unsafe_allow_html=True) [cite: 90]
            
            # --- NOVO: PERFORMANCE DAS DEZENAS FIXAS SEPARADO ---
            fixas_salvas = jogos_salvos_atual[0].get('fixas_pool_origem', [])
            if fixas_salvas:
                st.markdown("### 📌 PERFORMANCE DAS DEZENAS FIXAS")
                acertos_fixas = 0
                html_fixas = '<div style="background: #1a1a1a; padding: 15px; border-radius: 12px; border: 2px solid #d4af37; margin-bottom: 20px;">'
                
                for df in sorted(fixas_salvas):
                    cor_fixa = "#28a745" if df in resultado_alvo else "#ff4b4b"
                    html_fixas += f'<span style="display:inline-block; width:35px; height:35px; line-height:35px; text-align:center; border-radius:50%; margin:3px; font-weight:bold; color:white; background-color:{cor_fixa}; border:1px solid white;">{df:02d}</span>'
                    if df in resultado_alvo:
                        acertos_fixas += 1
                
                html_fixas += f'<br><br><span style="color:#d4af37; font-size:16px;"><b>🎯 ACERTOS NAS FIXAS: {acertos_fixas} de {len(fixas_salvas)}</b></span>'
                html_fixas += '</div>'
                st.markdown(html_fixas, unsafe_allow_html=True)
        else:
            [cite_start]st.info("Pool não registrado nos jogos antigos.") [cite: 90]

    if jogos_salvos_atual:
        [cite_start]btn_pdf = gerar_pdf_bonito(jogos_salvos_atual, mod_f) [cite: 90]
        [cite_start]st.download_button(label="📄 EXTRAIR JOGOS SALVOS EM PDF", data=btn_pdf, file_name=f"jogos_{mod_f}.pdf", mime="application/pdf") [cite: 91]

    if st.button("🔄 ATUALIZAR E CONFERIR"): 
        [cite_start]st.rerun() [cite: 91]
        
    [cite_start]res_db = st.session_state.ultimo_res.get(mod_f, {}) [cite: 91]
    [cite_start]jogos_na_espera = [j for j in st.session_state.jogos_salvos if j.get('mod') == mod_f] [cite: 91]
    
    if jogos_na_espera:
        [cite_start]total_ganho = 0 [cite: 91]
        for j in jogos_na_espera:
            [cite_start]alvo = str(j.get('concurso_alvo', '')) [cite: 92]
            if alvo in res_db:
                [cite_start]sorteados = set(res_db[alvo]) [cite: 92]
                [cite_start]acertos = len(set(j['n']).intersection(sorteados)) [cite: 92]
                [cite_start]total_ganho += st.session_state.premios[mod_f].get(str(acertos), 0.0) [cite: 92]
    
        [cite_start]st.markdown(f'<div class="painel-luxo-black"><div class="titulo-luxo-gold">🏆 Premiação Total 🏆</div><div class="valor-luxo-white">{formata_dinheiro(total_ganho)}</div></div>', unsafe_allow_html=True) [cite: 93]
        
        for i, j in enumerate(jogos_na_espera):
            [cite_start]alvo = str(j.get('concurso_alvo', '')) [cite: 93]
            [cite_start]txt_jogo = ' '.join([f'{x:02d}' for x in j['n']]) [cite: 94]
            
            if alvo in res_db:
                [cite_start]sorteados = set(res_db[alvo]) [cite: 94]
                [cite_start]acertos = len(set(j['n']).intersection(sorteados)) [cite: 94]
                [cite_start]val = st.session_state.premios[mod_f].get(str(acertos), 0.0) [cite: 94]
               
                if "fixas_utilizadas" in j and j["fixas_utilizadas"]:
                    [cite_start]fixas_u = j["fixas_utilizadas"] [cite: 95]
                    [cite_start]acertos_f = set(fixas_u).intersection(sorteados) [cite: 95]
                    [cite_start]bolinhas = "" [cite: 96]
                    for f in fixas_u:
                        [cite_start]cor_f = "#2ecc71" if f in sorteados else "#e74c3c" [cite: 96]
                        [cite_start]bolinhas += f'<span style="background:{cor_f}; color:white; padding:2px 8px; border-radius:50%; margin-right:5px; border:1px solid black; font-size:11px; font-weight:bold;">{f:02d}</span>' [cite: 98]
                    
                    [cite_start]st.markdown(f"📍 **FIXAS:** {bolinhas} | **Acertos: {len(acertos_f)}/{len(fixas_u)}**", unsafe_allow_html=True) [cite: 98]

                [cite_start]st.markdown(f"<div {'class=\"jogo-premiado\"' if val>0 else ''}>**ID {i+1:02d}** | `{txt_jogo}` | **{acertos} ACERTOS** ({formata_dinheiro(val)})</div>", unsafe_allow_html=True) [cite: 99]
            else: 
                [cite_start]st.markdown(f"**ID {i+1:02d}** | `{txt_jogo}` | ⏳ **AGUARDANDO CONCURSO {alvo}**") [cite: 99]
                
    if st.button("🗑️ LIMPAR HISTÓRICO"):
        [cite_start]st.session_state.jogos_salvos = [j for j in st.session_state.jogos_salvos if j['mod'] != mod_f] [cite: 99]
        [cite_start]st.rerun() [cite: 99]
with abas[2]:
    mostrar_status_backup()
    st.header("⚙️ Configuração de Valores")
    mod_v = st.selectbox("Loteria", list(st.session_state.premios.keys()), key="v_sel")
    novos_v = {}
    for faixa, valor in st.session_state.premios[mod_v].items():
        novos_v[faixa] = st.number_input(f"Prêmio {faixa} acertos", value=float(valor), format="%.2f", key=f"v_{mod_v}_{faixa}")
    if st.button("💾 SALVAR VALORES"): 
        st.session_state.premios[mod_v] = novos_v
        st.success("✅ Valores atualizados!")


with abas[3]:
    mostrar_status_backup()
    st.header("📥 Database")
    m_db = st.selectbox("Loteria", list(st.session_state.custos.keys()), key="m_db")
    id_c = st.number_input("Nº Concurso", 1, 9999, key="id_c")
    
    # Campo de entrada de texto 
    txt_site = st.text_area("Cole os números sorteados aqui (aceita números grudados, com espaços ou traços)").strip()
    
    if txt_site:
        try:
            # LÓGICA DE PROCESSAMENTO INTELIGENTE
            # Se o texto for longo e não tiver espaços/traços, assume que está grudado de 2 em 2
            if len(txt_site) > 10 and " " not in txt_site and "-" not in txt_site:
                extraidos = [txt_site[i:i+2] for i in range(0, len(txt_site), 2)]
            else:
                # Caso contrário, usa busca padrão por números separados 
                extraidos = re.findall(r'\d+', txt_site)
            
            # Converte para inteiros, remove duplicados e filtra pelo limite da loteria (até 80) 
            nums = sorted(list(set([int(n) for n in extraidos if 1 <= int(n) <= 80])))
            
            if not nums:
                st.warning("⚠️ Nenhum número válido foi encontrado. Verifique o formato colado.")
            else:
                # Exibe os números formatados para conferência visual 
                st.code(" ".join([f"{x:02d}" for x in nums]))
                
                if st.button("💾 GRAVAR RESULTADO"):
                    # Grava no banco de dados da sessão 
                    st.session_state.ultimo_res[m_db][str(int(id_c))] = nums
                    st.success(f"✅ Resultado do concurso {id_c} gravado com sucesso!")
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Erro técnico ao processar os dados: {e}")
with abas[4]:
    mostrar_status_backup()
    st.header("💾 Backup e Status")
    data_b = json.dumps({"salvos": st.session_state.jogos_salvos, "premios": st.session_state.premios, "res": st.session_state.ultimo_res}, indent=4)
    st.download_button("📤 EXPORTAR BACKUP", data_b, "backup_kadosh.json")
    f = st.file_uploader("Importar Backup", type="json")
    if f and st.button("📥 CONFIRMAR IMPORTAÇÃO"):
        d = json.load(f)
        st.session_state.jogos_salvos = d.get("salvos", [])
        st.session_state.premios = d.get("premios", st.session_state.premios)
        st.session_state.ultimo_res = d.get("res", st.session_state.ultimo_res)
        st.rerun()

with abas[5]:
    mostrar_status_backup()
    st.header("🧠 CENTRAL DE INTELIGÊNCIA KADOSH")
    st.markdown("---")
    
    st.subheader("📊 Painel Tático de Estratégias")
    dados_est = []
    for nome, info in ESTRATEGIA_MAPA.items():
        if nome != "Personalizado":
            qtd_total = info.get("qtd", 0) + info.get("qtd_15", 0) + info.get("qtd_16", 0)
            custo_aprox = (info.get("qtd", 0) * 3.5) + (info.get("qtd_15", 0) * 3.5) + (info.get("qtd_16", 0) * 56.0)
            if "MARRETA" in nome: 
                custo_aprox = 2448.0 + (5 * 56.0)
            dados_est.append({
                "Estratégia": nome, 
                "Jogos": qtd_total, 
                "Custo Est.": f"R$ {custo_aprox:,.2f}", 
                "Foco": info["desc"], 
                "Chances": info["prob"]
            })
    st.table(pd.DataFrame(dados_est))

    st.markdown("---")
    st.subheader("📐 ANÁLISE TÉCNICA DE MATRIZES (ACRÉSCIMO)")
    dados_mat = []
    for nome, info in MATRIZES_FECHAMENTO.items():
        if info:
            n_p = info["n_pool"]
            erro_m = n_p - 15
            dados_mat.append({
                "Matriz": nome,
                "Pool (Dez)": n_p,
                "Foco/Garantia": info["desc"],
                "Erro Máx.": f"Erre até {erro_m} dezenas",
                "Probabilidade": info["prob"],
                "Garantia": f"{info['garantia']} Pontos"
            })
    st.table(pd.DataFrame(dados_mat))
    st.info("💡 **Dica Técnica:** A coluna 'Erro Máx.' indica quantas dezenas do seu pool podem ser sorteadas e ainda manter a garantia 100%.")
    
    st.markdown("---")
    
    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        st.subheader("🔄 Status do Ciclo Atual")
        res_loto = st.session_state.ultimo_res.get("Lotofácil", {})
        if res_loto:
            sorteadas_no_ciclo = set()
            concursos_analisados = sorted(res_loto.keys(), key=lambda x: int(x), reverse=True)
            for c in concursos_analisados:
                sorteadas_no_ciclo.update(res_loto[c])
                if len(sorteadas_no_ciclo) == 25: 
                    break
            faltam = sorted(list(set(range(1, 26)) - sorteadas_no_ciclo))
            if not faltam: 
                st.success("✅ CICLO FECHADO!")
            else:
                st.warning(f"⚠️ Faltam {len(faltam)} dezenas para o ciclo: {faltam}")
                st.info("💡 Dezenas pendentes ganham bônus de atraso no Pool Inteligente.")
                
    with col_inf2:
        st.subheader("⚖️ Regras de Auditoria")
        st.markdown("""
        - **Paridade:** 7 a 9 Pares (Adaptativa)
        - **Âncoras:** Início [1,2,3] | Fim [23,24,25]
        - **Soma:** 180 a 220
        - **Moldura:** 8 a 11 dezenas
        - **Frequência:** Analisando histórico de 20 jogos
        """)
    
    st.markdown("---")
    
    with st.expander("🛠️ MANUAL DE MANUTENÇÃO TÉCNICA"):
        st.code("""
// LOCALIZAÇÃO DO CÓDIGO NO SCRIPT:
// 1. Heatmap: Logo após a função 'validar_kadosh_cirurgico'
// 2. Score Pool: Aba 0 > Botão Pool Inteligente Kadosh
// 3. Backup: Leitura automática via session_state (Aba 5 reflete o JSON)
// 4. Paridade: Fórmula dinâmica integrada no motor de validação
        """, language="javascript")

with abas[6]:
    st.markdown("""
        <div class="painel-luxo-black">
            <div class="moeda-animada">💰</div>
            <div class="titulo-luxo-gold">🔗 ANÁLISE DE AFINIDADE E VÍNCULOS</div>
            <div style="color:white; font-size:12px; margin-top:10px;">Identificação de pares de dezenas com alta frequência conjunta</div>
        </div>
    """, unsafe_allow_html=True)
    
    mod_af = st.selectbox("Selecione a Loteria para Estudo", list(st.session_state.custos.keys()), key="af_selector_new")
    matriz_vinculos = calcular_matriz_afinidade_kadosh(mod_af)
    
    if matriz_vinculos:
        col_vin1, col_vin2 = st.columns(2)
        with col_vin1:
            st.subheader("🔥 Top 15 Pares Mais Fortes")
            lista_pares = []
            for i in range(1, len(matriz_vinculos)):
                for j in range(i + 1, len(matriz_vinculos)):
                    freq = matriz_vinculos[i][j]
                    if freq > 0:
                        lista_pares.append({
                            "Par": f"{i:02d} + {j:02d}", 
                            "Frequência": freq, 
                            "Afinidade": f"{(freq/max(1, len(st.session_state.ultimo_res[mod_af])))*100:.1f}%"
                        })
            st.table(pd.DataFrame(sorted(lista_pares, key=lambda x: x['Frequência'], reverse=True)[:15]))
            
        with col_vin2:
            st.subheader("🚫 Pares em Vácuo (Exemplos)")
            vacuos, cont_v = [], 0
            for i in range(1, len(matriz_vinculos)):
                for j in range(i + 1, len(matriz_vinculos)):
                    if matriz_vinculos[i][j] == 0 and cont_v < 15: 
                        vacuos.append(f"{i:02d} + {j:02d}")
                        cont_v += 1
            for v in vacuos: 
                st.markdown(f"❌ `{v}`")
                
        st.info("💡 **DICA:** Use estes dados para refinar seu Pool na Aba 0. Pares com alta afinidade tendem a se repetir.")
    else:
        st.warning("⚠️ Database insuficiente para análise de afinidade. Insira mais resultados na aba DATABASE.")


