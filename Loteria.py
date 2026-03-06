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

   # Mantenha este recuo exato de 4 espaços
    linhas = [0]*5
    colunas = [0]*5
    for n in jogo:
        linhas[(n-1)//5] += 1
        colunas[(n-1)%5] += 1

    # ESTA É A LINHA QUE DEU ERRO - COLE EXATAMENTE ASSIM:
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
    
    mostrar_status_backup()
    mod = st.selectbox("Modalidade", list(st.session_state.custos.keys()), key="mod_selector")
    
    if 'ultima_mod_selecionada' not in st.session_state:
        st.session_state.ultima_mod_selecionada = mod
        
    if st.session_state.ultima_mod_selecionada != mod:
        st.session_state.jogos_gerados = []
        st.session_state.ultima_mod_selecionada = mod
        st.rerun()
        # --- INÍCIO DA ATIVAÇÃO DA IA ---
    res_loto = st.session_state.ultimo_res.get(mod, {})
    if res_loto:
        conc_ordenados = sorted(res_loto.keys(), key=lambda x: int(x), reverse=True)
        contagem = Counter()
        for c in conc_ordenados[:20]:
            for n in res_loto[c]: contagem[n] += 1
        stats_temp = {}
        for n in range(1, 26 if mod == "Lotofácil" else 61):
            atraso_n = 0
            for c in conc_ordenados:
                if n not in res_loto[c]: atraso_n += 1
                else: break
            stats_temp[n] = {'score': contagem[n] + (atraso_n * 1.5)}
        st.session_state.analise_stats[mod] = stats_temp
    # --- FIM DA ATIVAÇÃO DA IA ---
    
    col_est1, col_est2 = st.columns(2)
    with col_est1:
        if mod == "Lotofácil":
            est_escolhida = st.selectbox("💎 ESTRATÉGIA KADOSH", list(ESTRATEGIA_MAPA.keys()))
            est_info = ESTRATEGIA_MAPA[est_escolhida]
            st.progress(est_info["peso"])
            qtd_total_est = est_info.get("qtd", 0) + est_info.get("qtd_15", 0) + est_info.get("qtd_16", 0)
            st.markdown(f"🎯 **Probabilidade:** {est_info['prob']} | 📦 **Volume:** {qtd_total_est} jogos")
        else:
            est_escolhida = "Personalizado"
            
    with col_est2:
        if mod == "Lotofácil":
            fe_escolhido = st.selectbox("📐 MODO FECHAMENTO (MATRIZ)", list(MATRIZES_FECHAMENTO.keys()))
            if fe_escolhido != "Nenhum":
                fe_info = MATRIZES_FECHAMENTO[fe_escolhido]
                st.progress(fe_info["peso"])
                st.markdown(f"📐 **Garantia:** {fe_info['prob']} | 🧬 **Pool:** {fe_info['n_pool']} dezenas")
            else:
                st.markdown("<br><br>", unsafe_allow_html=True)
        else:
            fe_escolhido = "Nenhum"

    info_fech = MATRIZES_FECHAMENTO.get(fe_escolhido) if mod == "Lotofácil" else None
    info_est = ESTRATEGIA_MAPA.get(est_escolhida) if mod == "Lotofácil" else ESTRATEGIA_MAPA["Personalizado"]
    
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        if info_fech:
            if "DIAMANTE" in fe_escolhido: 
                def_dez, def_qtd = 16, 2
            elif "CÉLULA" in fe_escolhido: 
                def_dez, def_qtd = 16, 1
            else: 
                def_dez, def_qtd = 15, (24 if "18-15-14" in fe_escolhido else 45)
        elif est_escolhida != "Personalizado" and mod == "Lotofácil":
            def_dez, def_qtd = info_est["dez"], info_est.get("qtd", 10)
        else:
            def_dez = list(st.session_state.custos[mod].keys())[0]
            def_qtd = 10
            
        opcoes_dez = list(st.session_state.custos[mod].keys())
        idx_padrao = opcoes_dez.index(def_dez) if def_dez in opcoes_dez else 0
        n_dez = st.selectbox("Dezenas por Bilhete", opcoes_dez, index=idx_padrao)
        qtd = st.number_input("Quantidade de Jogos", 1, 300, def_qtd)
        
    with c2:
        max_v = 25 if mod=="Lotofácil" else 60 if mod=="Mega-Sena" else 80
        col_btn1, col_btn2 = st.columns(2)
        
    col_btn1, col_btn2 = st.columns(2)

    col_btn1, col_btn2 = st.columns(2)

col_btn1, col_btn2 = st.columns(2)

    col_btn1, col_btn2 = st.columns(2)

      col_btn1, col_btn2 = st.columns(2)

      col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("✅ TODO O VOLANTE"):
                st.session_state.favoritas[mod] = list(range(1, max_v + 1))
                st.rerun()
                
        with col_btn2:
            if st.button("🧠 POOL INTELIGENTE KADOSH"):
                res_loto = st.session_state.ultimo_res.get(mod, {})
                if len(res_loto) >= 5:
                    n_pool_req = info_fech['n_pool'] if info_fech else 20
                    conc_ordenados = sorted(res_loto.keys(), key=lambda x: int(x), reverse=True)
                    
                    # Identificação de Ciclo
                    sorteadas_no_ciclo = set()
                    for c in conc_ordenados:
                        sorteadas_no_ciclo.update(res_loto[c])
                        if len(sorteadas_no_ciclo) == 25: break
                    faltantes_ciclo = list(set(range(1, 26)) - sorteadas_no_ciclo)
                    
                    # Cálculo de Scores Kadosh (Atraso 3.5 + Ciclo)
                    score_kadosh = {}
                    contagem = Counter()
                    for c in conc_ordenados[:20]:
                        for n in res_loto[c]: contagem[n] += 1
                        
                    for n in range(1, max_v + 1):
                        atraso_n = 0
                        for c in conc_ordenados:
                            if n not in res_loto[c]: atraso_n += 1
                            else: break
                        
                        bonus_ciclo = 3.5 if n in faltantes_ciclo else 0
                        score_kadosh[n] = contagem[n] + (atraso_n * 3.5) + bonus_ciclo

                    melhores = sorted(score_kadosh.items(), key=lambda x: x[1], reverse=True)
                    pool_final = [n for n, s in melhores[:n_pool_req]]
                    st.session_state.favoritas[mod] = sorted(pool_final)
                    st.rerun()
        pool = st.multiselect("SELECIONE SEU POOL", range(1, max_v + 1), default=st.session_state.favoritas.get(mod, []))
        st.session_state.favoritas[mod] = pool
        # --- [SUGESTÃO 3: ANÁLISE DE QUADRANTES NO POOL] ---
        if pool and mod == "Lotofácil":
            linhas_p = [0]*5
            for n in pool: linhas_p[(n-1)//5] += 1
            if any(l == 0 for l in linhas_p):
                st.warning("⚠️ Atenção: Seu Pool possui linhas vazias! Isso pode reduzir a eficácia dos filtros Kadosh.")
            with st.expander("📊 Distribuição Geográfica do Pool"):
                cols_q = st.columns(5)
                for idx, qtd_l in enumerate(linhas_p):
                    cols_q[idx].metric(f"Linha {idx+1}", f"{qtd_l} dez")
        
        modo_fixa = st.radio("MODO DE FIXAÇÃO:", ["Sem Fixas", "Manual", "IA Automática (Score)"], horizontal=True)
        fixas_final = []
        if modo_fixa == "Manual":
            fixas_final = st.multiselect("📌 CRAVAR DEZENAS:", options=pool)
        elif modo_fixa == "IA Automática (Score)":
            qtd_auto = st.slider("Qtd de Cravadas:", 1, 10, 6)
            if mod in st.session_state.analise_stats:
                stats = st.session_state.analise_stats[mod]
                melhores = sorted([n for n in pool], key=lambda x: stats.get(x, {}).get('score', 0), reverse=True)
                fixas_final = melhores[:qtd_auto]
                st.info(f"💎 IA CRAVOU: {', '.join(map(str, fixas_final))}")
        
        renderizar_heatmap(mod, st.session_state.ultimo_res.get(mod, {}))

    if st.button("🚀 GERAR JOGOS (SINCRO-MATRIZ KADOSH)"):
        if len(pool) < (info_fech['n_pool'] if info_fech else n_dez):
            st.error(f"Seu Pool precisa de pelo menos {info_fech['n_pool'] if info_fech else n_dez} dezenas!")
        else:
            novos = []
            def gerar_com_matriz(tamanho_solicitado, quantidade, filtragem=True):
                sucessos, tentativas = 0, 0
                pool_para_sorteio = [n for n in pool if n not in fixas_final]
                vagas_abertas = tamanho_solicitado - len(fixas_final)

                while sucessos < quantidade and tentativas < 20000:
                    if len(pool_para_sorteio) >= vagas_abertas and vagas_abertas >= 0:
                        complemento = random.sample(pool_para_sorteio, vagas_abertas)
                        comb = sorted(fixas_final + complemento)
                    else:
                        comb = sorted(random.sample(pool, tamanho_solicitado))
               
                    if any(set(comb) == set(existente['n']) for existente in novos):
                        tentativas += 1
                        continue
                  
                    # Se for maior que 15, o filtro kadosh não pode ser rígido
                    passou = validar_kadosh_cirurgico(comb, mod, tamanho_solicitado) if (filtragem and tamanho_solicitado == 15) else True
                    
                    if passou:
                        tag_est = f"{fe_escolhido if info_fech else est_escolhida}"
                        novos.append({
                            "mod": mod, "n": comb, "tam": tamanho_solicitado, 
                            "fixas_utilizadas": list(fixas_final),
                            "chance": definir_label_chance(comb, mod), "est": tag_est
                        })
                        sucessos += 1
                    tentativas += 1

            # --- BLOCO DE DECISÃO SEM ERROS ---
            if info_fech:
                if "DIAMANTE" in fe_escolhido:
                    gerar_com_matriz(16, 2)
                    gerar_com_matriz(15, 10)
                elif "CÉLULA" in fe_escolhido:
                    gerar_com_matriz(16, 1)
                    gerar_com_matriz(15, 15)
                else:
                    gerar_com_matriz(15, qtd)
            elif est_escolhida == "6. A MARRETA":
                gerar_com_matriz(18, 1)
                gerar_com_matriz(16, 5)
            elif est_escolhida == "7. SIMETRIA GEOMÉTRICA":
                gerar_com_matriz(16, 2)
                gerar_com_matriz(15, 8)
            elif est_escolhida != "Personalizado" and mod == "Lotofácil":
                gerar_com_matriz(info_est['dez'], info_est.get('qtd', 1))
                if "qtd_15" in info_est:
                    gerar_com_matriz(15, info_est['qtd_15'])
            else:
                gerar_com_matriz(n_dez, qtd)
            
            st.session_state.jogos_gerados = novos
            st.rerun()
    for i, j in enumerate(st.session_state.jogos_gerados):
        txt_jogo = ' '.join([f'{x:02d}' for x in j['n']])
        st.code(f"JOGO {i+1:02d} | {j['est']} | {j['tam']} DEZ | {txt_jogo} / {j['chance']}")
    
    if st.session_state.jogos_gerados and st.button("💾 SALVAR PARA CONFERIR"):
        res_existentes = st.session_state.ultimo_res.get(mod, {})
        ultimo_c = int(max(res_existentes.keys(), key=int)) if res_existentes else 0
        pool_atual = list(st.session_state.favoritas.get(mod, [])) 
        
        for jogo in st.session_state.jogos_gerados:
            jogo['concurso_alvo'] = ultimo_c + 1
            jogo['pool_origem'] = pool_atual 
            # --- REGISTRO DAS FIXAS PARA O SCANNER ---
            if 'fixas_utilizadas' not in jogo:
                # Usa a variável fixas_final que foi definida na geração
                jogo['fixas_utilizadas'] = list(fixas_final) 
            
            st.session_state.jogos_salvos.append(jogo)
        
        st.session_state.jogos_gerados = []
        st.success(f"✅ Jogos salvos com sucesso para o Concurso {ultimo_c + 1}!")
        st.rerun()
                        
  
with abas[1]:
    mostrar_status_backup()
    st.header("🔍 Painel de Conferência")
    mod_f = st.selectbox("Loteria", list(st.session_state.custos.keys()), key="f_conf")
    
    jogos_salvos_atual = [j for j in st.session_state.jogos_salvos if j['mod'] == mod_f]
    
    # --- NOVO BLOCO: VISUALIZAÇÃO DO POOL NA CONFERÊNCIA (MANTIDO) ---
    if jogos_salvos_atual:
        st.markdown("### 🎯 PERFORMANCE DO SEU POOL (CERCO)")
        res_db = st.session_state.ultimo_res.get(mod_f, {})
        
        # Pega o pool do primeiro jogo
        pool_salvo = jogos_salvos_atual[0].get('pool_origem', [])
        alvo_pool = str(jogos_salvos_atual[0].get('concurso_alvo', ''))
        
        if pool_salvo:
            html_pool = '<div style="background: #f8f9fa; padding: 20px; border-radius: 15px; border: 2px solid #1e3799; margin-bottom: 20px;">'
            acertos_pool = 0
            resultado_alvo = res_db.get(alvo_pool, [])
            
            for d in sorted(pool_salvo):
                classe = "pool-vermelho"
                if d in resultado_alvo:
                    classe = "pool-verde"
                    acertos_pool += 1
                html_pool += f'<span class="dezena-pool {classe}">{d:02d}</span>'
            
            html_pool += f'<br><br><span style="font-size: 18px; color: #1e3799;">📊 <b>ACERTOS NO CERCO: {acertos_pool} DEZENAS</b></span>'
            html_pool += '</div>'
            st.markdown(html_pool, unsafe_allow_html=True)
        else:
            st.info("Pool não registrado nos jogos antigos.")

    # --- EXTRAÇÃO EM PDF (MANTIDO) ---
    if jogos_salvos_atual:
        btn_pdf = gerar_pdf_bonito(jogos_salvos_atual, mod_f)
        st.download_button(label="📄 EXTRAIR JOGOS SALVOS EM PDF", data=btn_pdf, file_name=f"jogos_{mod_f}.pdf", mime="application/pdf")
    else:
        st.info("Salve jogos no Gerador para habilitar a extração em PDF.")

    if st.button("🔄 ATUALIZAR E CONFERIR"): 
        st.rerun()
        
    res_db = st.session_state.ultimo_res.get(mod_f, {})
    jogos_na_espera = [j for j in st.session_state.jogos_salvos if j.get('mod') == mod_f]
    
    if jogos_na_espera:
        total_ganho = 0
        # Primeiro calculamos o total de prêmios
        for j in jogos_na_espera:
            alvo = str(j.get('concurso_alvo', ''))
            if alvo in res_db:
                sorteados = set(res_db[alvo])
                acertos = len(set(j['n']).intersection(sorteados))
                total_ganho += st.session_state.premios[mod_f].get(str(acertos), 0.0)
        
        # Painel de Resumo Luxo
        st.markdown(f'<div class="painel-luxo-black"><div class="titulo-luxo-gold">🏆 Premiação Total 🏆</div><div class="valor-luxo-white">{formata_dinheiro(total_ganho)}</div></div>', unsafe_allow_html=True)
        
        # Listagem dos Jogos com as Bolinhas das Fixas (ACRÉSCIMO SOLICITADO)
        for i, j in enumerate(jogos_na_espera):
            alvo = str(j.get('concurso_alvo', ''))
            txt_jogo = ' '.join([f'{x:02d}' for x in j['n']])
            
            if alvo in res_db:
                sorteados = set(res_db[alvo])
                acertos = len(set(j['n']).intersection(sorteados))
                val = st.session_state.premios[mod_f].get(str(acertos), 0.0)
                
                # --- NOVO: SCANNER DE FIXAS ---
                if "fixas_utilizadas" in j and j["fixas_utilizadas"]:
                    fixas_u = j["fixas_utilizadas"]
                    acertos_f = set(fixas_u).intersection(sorteados)
                    
                    bolinhas = ""
                    for f in fixas_u:
                        cor_f = "#2ecc71" if f in sorteados else "#e74c3c"
                        bolinhas += f'<span style="background:{cor_f}; color:white; padding:2px 8px; border-radius:50%; margin-right:5px; border:1px solid black; font-size:11px; font-weight:bold;">{f:02d}</span>'
                    
                    st.markdown(f"📍 **FIXAS:** {bolinhas} | **Acertos: {len(acertos_f)}/{len(fixas_u)}**", unsafe_allow_html=True)

                # Mantendo sua exibição original intacta
                st.markdown(f"<div {'class=\"jogo-premiado\"' if val>0 else ''}>**ID {i+1:02d}** | `{txt_jogo}` | **{acertos} ACERTOS** ({formata_dinheiro(val)})</div>", unsafe_allow_html=True)
            else: 
                st.markdown(f"**ID {i+1:02d}** | `{txt_jogo}` | ⏳ **AGUARDANDO CONCURSO {alvo}**")
                
    if st.button("🗑️ LIMPAR HISTÓRICO"):
        st.session_state.jogos_salvos = [j for j in st.session_state.jogos_salvos if j['mod'] != mod_f]
        st.rerun()

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



























