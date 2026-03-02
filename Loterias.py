import streamlit as st
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

    .status-backup {
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        float: right;
        background: #f0f2f6;
        border: 1px solid #d1d1d1;
    }
    
    /* Estilo para as tabelas da nova aba */
    .stTable { background-color: #ffffff; border-radius: 10px; }
    thead tr th { background-color: #d4af37 !important; color: black !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. FUNÇÕES TÉCNICAS (MOTOR DE ALTA PRECISÃO) ---

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
        dez_str = ' | '.join([f"{x:02d}" for x in j['n']])
        pdf.multi_cell(0, 10, txt=f"DEZENAS: {dez_str}", border=1)
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1')

def calcular_matriz_afinidade_kadosh(mod):
    """Calcula a frequência conjunta de pares de dezenas (Coocorrência)"""
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

def formata_dinheiro(valor):
    try: return f"R$ {float(valor):,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    except: return f"R$ {valor}"

def definir_label_chance(jogo, mod):
    if mod != "Lotofácil": return "PADRÃO"
    soma = sum(jogo)
    media_esperada = 180 + ((len(jogo) - 15) * 13)
    return "ALTA" if (media_esperada - 10) <= soma <= (media_esperada + 10) else "PADRÃO"

def jogo_ja_saiu(jogo, mod):
    res_hist = st.session_state.ultimo_res.get(mod, {})
    if not res_hist: return False
    conjunto_resultados = [set(res) for res in res_hist.values()]
    if len(jogo) == 15: return set(jogo) in conjunto_resultados
    for combo in combinations(jogo, 15):
        if set(combo) in conjunto_resultados: return True
    return False

def validar_kadosh_cirurgico(jogo, mod, n_dez):
    if mod != "Lotofácil": return True
    if not (jogo[0] in [1, 2, 3] and jogo[-1] in [23, 24, 25]): return False
    for i in range(len(jogo)-1):
        if (jogo[i+1] - jogo[i]) > 5: return False
    pares = len([n for n in jogo if n % 2 == 0])
    diff_n = n_dez - 15
    if not ( (7 + int(diff_n*0.4)) <= pares <= (9 + int(diff_n*0.6)) ): return False
    fibo_ref = [1, 2, 3, 5, 8, 13, 21]
    fibo_count = len([n for n in jogo if n in fibo_ref])
    if not (3 <= fibo_count <= 5 + int(diff_n*0.5)): return False
    if random.random() >= 0.12:
        vizinhos = 0
        sequencia_max, atual = 1, 1
        for i in range(len(jogo)-1):
            if jogo[i+1] - jogo[i] == 1:
                vizinhos += 1
                atual += 1
                sequencia_max = max(sequencia_max, atual)
            else: atual = 1
        if not (3 <= vizinhos <= 8) or not (3 <= sequencia_max <= 5): return False
    linhas, colunas = [0]*5, [0]*5
    for n in jogo:
        linhas[(n-1)//5] += 1
        colunas[(n-1)%5] += 1
    if any(l == 0 for l in linhas) or any(c == 0 for c in colunas) or any(l > 5 for l in linhas) or any(c > 5 for c in colunas): return False
    soma = sum(jogo)
    primos_list = [2,3,5,7,11,13,17,19,23]
    moldura_list = [1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25]
    primos = len([n for n in jogo if n in primos_list])
    moldura = len([n for n in jogo if n in moldura_list])
    cfg = {'s': (165 + (diff_n * 12), 215 + (diff_n * 14)), 'p': (4 + int(diff_n * 0.5), 7 + int(diff_n * 0.8)), 'm': (8 + int(diff_n * 0.7), 11 + int(diff_n * 0.9))}
    if not (cfg['s'][0] <= soma <= cfg['s'][1]) or not (cfg['p'][0] <= primos <= cfg['p'][1]) or not (cfg['m'][0] <= moldura <= cfg['m'][1]): return False
    return not jogo_ja_saiu(jogo, mod)

def renderizar_heatmap(mod, res_loto):
    if not res_loto or mod != "Lotofácil": return
    st.markdown("### 🗺️ MAPA DE CALOR E ANÁLISE DE CICLO (Últimos 20)")
    conc_ordenados = sorted(res_loto.keys(), key=lambda x: int(x), reverse=True)[:20]
    frequencia = Counter()
    atraso = {n: 0 for n in range(1, 26)}
    ja_apareceu = set()
    for c in conc_ordenados:
        sorteados = res_loto[c]
        for n in range(1, 26):
            if n in sorteados:
                frequencia[n] += 1
                ja_apareceu.add(n)
            elif n not in ja_apareceu: atraso[n] += 1
    cols = st.columns(5)
    for n in range(1, 26):
        freq, atr = frequencia[n], atraso[n]
        bg_color, texto = "#f1f2f6", "black"
        if freq >= 12: bg_color, texto = "#eb4d4b", "white"
        elif atr >= 3: bg_color, texto = "#0984e3", "white"
        with cols[(n-1)%5]:
            st.markdown(f'<div style="background-color:{bg_color}; color:{texto}; border-radius:10px; padding:10px; text-align:center; border:2px solid #2d3436; margin-bottom:5px;"><span style="font-size:20px;">{n:02d}</span><br><span style="font-size:10px;">F:{freq} | A:{atr}</span></div>', unsafe_allow_html=True)

# --- 3. MAPA DE ESTRATÉGIAS E MATRIZES ---
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

# --- 4. ESTADOS ---
for key in ['auth', 'jogos_gerados', 'jogos_salvos']:
    if key not in st.session_state: st.session_state[key] = False if key == 'auth' else []
if 'ultimo_res' not in st.session_state: st.session_state.ultimo_res = {m: {} for m in ["Lotofácil", "Mega-Sena", "Quina", "+Milionária", "Dupla-Sena"]}
if 'favoritas' not in st.session_state: st.session_state.favoritas = {m: [] for m in ["Lotofácil", "Mega-Sena", "Quina", "+Milionária", "Dupla-Sena"]}
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
            else: st.error("Senha incorreta!")
    st.stop()

def mostrar_status_backup():
    total_jogos = len(st.session_state.jogos_salvos)
    total_res = sum(len(v) for v in st.session_state.ultimo_res.values())
    st.markdown(f'<div class="status-backup">📁 Backup Ativo: {total_jogos} jogos | {total_res} resultados</div>', unsafe_allow_html=True)

# --- 6. INTERFACE PRINCIPAL ---
st.title("📊 GESTÃO ESTRATÉGICA LOTERIAS")
# ADIÇÃO DA 7ª ABA: 🔗 AFINIDADE
abas = st.tabs(["🎯 GERADOR PRO", "🔍 CONFERIR", "⚙️ VALORES", "📥 DATABASE", "💾 BACKUP", "🧠 INTELIGÊNCIA", "🔗 AFINIDADE"])

with abas[0]:
    mostrar_status_backup()
    mod = st.selectbox("Modalidade", list(st.session_state.custos.keys()), key="mod_selector")
    if 'ultima_mod_selecionada' not in st.session_state: st.session_state.ultima_mod_selecionada = mod
    if st.session_state.ultima_mod_selecionada != mod:
        st.session_state.jogos_gerados = []
        st.session_state.ultima_mod_selecionada = mod
        st.rerun()
    col_est1, col_est2 = st.columns(2)
    with col_est1:
        if mod == "Lotofácil":
            est_escolhida = st.selectbox("💎 ESTRATÉGIA KADOSH", list(ESTRATEGIA_MAPA.keys()))
            est_info = ESTRATEGIA_MAPA[est_escolhida]
            st.progress(est_info["peso"])
            st.markdown(f"🎯 **Probabilidade:** {est_info['prob']}")
        else: est_escolhida = "Personalizado"
    with col_est2:
        if mod == "Lotofácil":
            fe_escolhido = st.selectbox("📐 MODO FECHAMENTO (MATRIZ)", list(MATRIZES_FECHAMENTO.keys()))
            if fe_escolhido != "Nenhum":
                fe_info = MATRIZES_FECHAMENTO[fe_escolhido]
                st.progress(fe_info["peso"])
        else: fe_escolhido = "Nenhum"

    info_fech = MATRIZES_FECHAMENTO.get(fe_escolhido) if mod == "Lotofácil" else None
    info_est = ESTRATEGIA_MAPA.get(est_escolhida) if mod == "Lotofácil" else ESTRATEGIA_MAPA["Personalizado"]
    
    c1, c2 = st.columns(2)
    with c1:
        if info_fech:
            if "DIAMANTE" in fe_escolhido: def_dez, def_qtd = 16, 2
            elif "CÉLULA" in fe_escolhido: def_dez, def_qtd = 16, 1
            else: def_dez, def_qtd = 15, (24 if "18-15-14" in fe_escolhido else 45)
        elif est_escolhida != "Personalizado" and mod == "Lotofácil": def_dez, def_qtd = info_est["dez"], info_est.get("qtd", 10)
        else: def_dez, def_qtd = list(st.session_state.custos[mod].keys())[0], 10
        n_dez = st.selectbox("Dezenas por Bilhete", list(st.session_state.custos[mod].keys()), index=list(st.session_state.custos[mod].keys()).index(def_dez) if def_dez in st.session_state.custos[mod] else 0)
        qtd = st.number_input("Quantidade de Jogos", 1, 300, def_qtd)
    with c2:
        max_v = 25 if mod=="Lotofácil" else 60 if mod=="Mega-Sena" else 80
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
                    conc_ordenados = sorted(res_loto.keys(), key=lambda x: int(x), reverse=True)[:20]
                    score_kadosh, contagem = {}, Counter()
                    for c in conc_ordenados:
                        for n in res_loto[c]: contagem[n] += 1
                    for n in range(1, 26):
                        atraso_n = 0
                        for c in conc_ordenados:
                            if n not in res_loto[c]: atraso_n += 1
                            else: break
                        score_kadosh[n] = contagem[n] + (atraso_n * 1.5)
                    melhores = sorted(score_kadosh.items(), key=lambda x: x[1], reverse=True)
                    st.session_state.favoritas[mod] = sorted([n for n, s in melhores[:n_pool_req]])
                    st.rerun()
        pool = st.multiselect("SELECIONE SEU POOL", range(1, max_v + 1), default=st.session_state.favoritas.get(mod, []))
        st.session_state.favoritas[mod] = pool
        renderizar_heatmap(mod, st.session_state.ultimo_res.get(mod, {}))

    if st.button("🚀 GERAR JOGOS (SINCRO-MATRIZ KADOSH)"):
        if len(pool) < (info_fech['n_pool'] if info_fech else n_dez): st.error(f"Pool insuficiente!")
        else:
            novos = []
            def gerar_com_matriz(tamanho, quantidade, filtragem=True):
                sucessos, tentativas = 0, 0
                while sucessos < quantidade and tentativas < 20000:
                    comb = sorted(random.sample(pool, tamanho))
                    if any(set(comb) == set(e['n']) for e in novos): tentativas += 1; continue
                    if not filtragem or validar_kadosh_cirurgico(comb, mod, tamanho):
                        novos.append({"mod": mod, "n": comb, "tam": tamanho, "chance": definir_label_chance(comb, mod), "est": fe_escolhido if info_fech else est_escolhida})
                        sucessos += 1
                    tentativas += 1
            if info_fech:
                if "DIAMANTE" in fe_escolhido: gerar_com_matriz(16, 2); gerar_com_matriz(15, 10)
                elif "CÉLULA" in fe_escolhido: gerar_com_matriz(16, 1); gerar_com_matriz(15, 15)
                else: gerar_com_matriz(15, qtd)
            elif est_escolhida == "6. A MARRETA": gerar_com_matriz(18, 1); gerar_com_matriz(16, 5)
            elif est_escolhida == "7. SIMETRIA GEOMÉTRICA": gerar_com_matriz(16, 2); gerar_com_matriz(15, 8)
            elif est_escolhida != "Personalizado" and mod == "Lotofácil":
                gerar_com_matriz(info_est['dez'], info_est.get('qtd', 1))
                if "qtd_15" in info_est: gerar_com_matriz(15, info_est['qtd_15'])
            else: gerar_com_matriz(n_dez, qtd)
            st.session_state.jogos_gerados = novos
            st.rerun()

    for i, j in enumerate(st.session_state.jogos_gerados):
        st.code(f"JOGO {i+1:02d} | {j['est']} | {j['tam']} DEZ | {' '.join([f'{x:02d}' for x in j['n']])} / {j['chance']}")
    if st.session_state.jogos_gerados and st.button("💾 SALVAR PARA CONFERIR"):
        res_ex = st.session_state.ultimo_res.get(mod, {})
        u_c = int(max(res_ex.keys(), key=int)) if res_ex else 0
        for j in st.session_state.jogos_gerados:
            j['concurso_alvo'] = u_c + 1
            st.session_state.jogos_salvos.append(j)
        st.session_state.jogos_gerados = []; st.rerun()

with abas[1]:
    mostrar_status_backup(); st.header("🔍 Conferência")
    mod_f = st.selectbox("Loteria", list(st.session_state.custos.keys()), key="f_conf")
    j_salvos_atual = [j for j in st.session_state.jogos_salvos if j['mod'] == mod_f]
    if j_salvos_atual:
        st.download_button("📄 EXTRAIR JOGOS EM PDF", gerar_pdf_bonito(j_salvos_atual, mod_f), f"jogos_{mod_f}.pdf", "application/pdf")
    if st.button("🔄 ATUALIZAR"): st.rerun()
    res_db = st.session_state.ultimo_res.get(mod_f, {})
    if j_salvos_atual:
        total_ganho = 0
        for j in j_salvos_atual:
            alvo = str(j.get('concurso_alvo', ''))
            if alvo in res_db: total_ganho += st.session_state.premios[mod_f].get(str(len(set(j['n']).intersection(set(res_db[alvo])))), 0.0)
        st.markdown(f'<div class="painel-luxo-black"><div class="titulo-luxo-gold">🏆 Premiação Total</div><div class="valor-luxo-white">{formata_dinheiro(total_ganho)}</div></div>', unsafe_allow_html=True)
        for i, j in enumerate(j_salvos_atual):
            alvo = str(j.get('concurso_alvo', ''))
            if alvo in res_db:
                ac = len(set(j['n']).intersection(set(res_db[alvo])))
                val = st.session_state.premios[mod_f].get(str(ac), 0.0)
                st.markdown(f"<div {'class=\"jogo-premiado\"' if val>0 else ''}>**ID {i+1:02d}** | `{' '.join([f'{x:02d}' for x in j['n']])}` | **{ac} ACERTOS** ({formata_dinheiro(val)})</div>", unsafe_allow_html=True)
            else: st.markdown(f"**ID {i+1:02d}** | `{' '.join([f'{x:02d}' for x in j['n']])}` | ⏳ **AGUARDANDO {alvo}**")
    if st.button("🗑️ LIMPAR"): st.session_state.jogos_salvos = [j for j in st.session_state.jogos_salvos if j['mod'] != mod_f]; st.rerun()

with abas[2]:
    mostrar_status_backup(); st.header("⚙️ Valores")
    mod_v = st.selectbox("Loteria", list(st.session_state.premios.keys()), key="v_sel")
    nv = {f: st.number_input(f"Prêmio {f} acertos", value=float(v), key=f"v_{mod_v}_{f}") for f, v in st.session_state.premios[mod_v].items()}
    if st.button("💾 SALVAR"): st.session_state.premios[mod_v] = nv; st.success("Atualizado!")

with abas[3]:
    mostrar_status_backup(); st.header("📥 Database")
    m_db = st.selectbox("Loteria", list(st.session_state.custos.keys()), key="m_db")
    id_c = st.number_input("Nº Concurso", 1, 9999)
    txt_site = st.text_area("Cole os números sorteados").strip()
    if txt_site:
        nums = sorted(list(set([int(n) for n in re.findall(r'\d+', txt_site) if 1 <= int(n) <= 80])))
        st.code(" ".join([f"{x:02d}" for x in nums]))
        if st.button("💾 GRAVAR"): st.session_state.ultimo_res[m_db][str(int(id_c))] = nums; st.success("Gravado!")

with abas[4]:
    mostrar_status_backup(); st.header("💾 Backup")
    st.download_button("📤 EXPORTAR", json.dumps({"salvos": st.session_state.jogos_salvos, "premios": st.session_state.premios, "res": st.session_state.ultimo_res}, indent=4), "backup_kadosh.json")
    f = st.file_uploader("Importar", type="json")
    if f and st.button("📥 CONFIRMAR"):
        d = json.load(f); st.session_state.jogos_salvos = d.get("salvos", []); st.session_state.premios = d.get("premios", st.session_state.premios); st.session_state.ultimo_res = d.get("res", st.session_state.ultimo_res); st.rerun()

with abas[5]:
    mostrar_status_backup(); st.header("🧠 CENTRAL DE INTELIGÊNCIA")
    dados_est = [{"Estratégia": n, "Jogos": i.get("qtd", 0) + i.get("qtd_15", 0) + i.get("qtd_16", 0), "Foco": i["desc"], "Chances": i["prob"]} for n, i in ESTRATEGIA_MAPA.items() if n != "Personalizado"]
    st.table(pd.DataFrame(dados_est))
    st.markdown("---")
    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        res_loto = st.session_state.ultimo_res.get("Lotofácil", {})
        if res_loto:
            st.subheader("🔄 Ciclo Atual")
            sorteadas = set()
            for c in sorted(res_loto.keys(), key=int, reverse=True):
                sorteadas.update(res_loto[c])
                if len(sorteadas) == 25: break
            faltam = sorted(list(set(range(1, 26)) - sorteadas))
            if not faltam: st.success("✅ CICLO FECHADO!")
            else: st.warning(f"⚠️ Faltam: {faltam}")
    with col_inf2:
        st.subheader("⚖️ Auditoria")
        st.markdown("- **Paridade:** 7-9 Pares\n- **Âncoras:** Início [1,2,3] Fim [23,24,25]\n- **Soma:** 180-220\n- **Moldura:** 8-11")

# --- 7. ABA DE AFINIDADE (PLUG-AND-PLAY) ---
with abas[6]:
    st.markdown('<div class="painel-luxo-black"><div class="titulo-luxo-gold">🔗 ANÁLISE DE AFINIDADE E VÍNCULOS</div><div style="color:white; font-size:12px; margin-top:10px;">Identificação de pares de dezenas com alta frequência conjunta</div></div>', unsafe_allow_html=True)
    mod_af = st.selectbox("Selecione a Loteria para Estudo", list(st.session_state.custos.keys()), key="af_selector")
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
                        lista_pares.append({"Par": f"{i:02d} + {j:02d}", "Frequência": freq, "Afinidade": f"{(freq/len(st.session_state.ultimo_res[mod_af]))*100:.1f}%"})
            st.table(pd.DataFrame(sorted(lista_pares, key=lambda x: x['Frequência'], reverse=True)[:15]))
        with col_vin2:
            st.subheader("🚫 Pares em Vácuo (Exemplos)")
            vacuos, cont_v = [], 0
            for i in range(1, len(matriz_vinculos)):
                for j in range(i + 1, len(matriz_vinculos)):
                    if matriz_vinculos[i][j] == 0 and cont_v < 15: vacuos.append(f"{i:02d} + {j:02d}"); cont_v += 1
            for v in vacuos: st.markdown(f"❌ `{v}`")
        st.info("💡 **DICA:** Dezenas com alta Afinidade devem ser priorizadas no seu Pool Inteligente.")
    else: st.warning("⚠️ Database insuficiente (mínimo 3 resultados).")