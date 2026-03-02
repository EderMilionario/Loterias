import streamlit as st
import json
import random
import re
import pandas as pd
from collections import Counter
from itertools import combinations
from fpdf import FPDF
import io

# --- 1. CONFIGURAÇÃO E ESTÉTICA (ILUMINAÇÃO LUXO DARK INTEGRADA) ---
st.set_page_config(page_title="LOTERIAS - KADOSH ESTRATÉGICO", layout="wide")
st.markdown("""
    <style>
    /* Fundo Dark Profundo e Textos */
    .stApp {background-color: #050505 !important;}
    p, label, span, div {color: #ffffff !important; font-weight: bold !important;}
    .stCodeBlock {border: 2px solid #d4af37 !important; background-color: #111 !important;}
    code {font-size: 18px !important; color: #d4af37 !important; font-weight: bold !important;}
    
    /* Botões com Gradiente Ouro */
    div.stButton > button {
        background: linear-gradient(135deg, #d4af37 0%, #8a6d3b 100%) !important;
        color: #000 !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        border: 1px solid #fff !important;
        width: 100% !important;
        height: 50px !important;
        transition: 0.4s !important;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.4) !important;
        text-transform: uppercase !important;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 30px rgba(212, 175, 55, 0.8) !important;
        transform: translateY(-2px) !important;
    }

    /* Painel de Luxo Black/Gold */
    .painel-luxo-black {
        background: linear-gradient(145deg, #1a1a1a, #0a0a0a);
        border: 2px solid #d4af37;
        padding: 40px;
        border-radius: 30px;
        text-align: center;
        box-shadow: 0 20px 50px rgba(0,0,0,0.9), inset 0 0 20px rgba(212,175,55,0.1);
        margin-bottom: 30px;
    }
    .titulo-luxo-gold {
        color: #d4af37 !important;
        font-size: 24px !important;
        letter-spacing: 5px !important;
        text-shadow: 0 0 15px rgba(212,175,55,0.6);
        text-transform: uppercase;
    }
    .valor-luxo-white {
        color: #ffffff !important;
        font-size: 65px !important;
        font-weight: 900 !important;
        text-shadow: 0 0 20px rgba(255,255,255,0.4);
    }
    
    .jogo-premiado {
        background-color: #1a2e1a !important;
        border: 3px solid #d4af37 !important;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 8px;
        box-shadow: 0 4px 15px rgba(212,175,55,0.3);
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
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 12px;
        float: right;
        background: #111;
        border: 1px solid #d4af37;
        color: #d4af37 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. FUNÇÃO DE PDF ESTILO VOLANTE ---
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

# --- 3. MAPA DE ESTRATÉGIAS E MATRIZES (INTEGRAL) ---
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

# --- 4. MOTOR TÉCNICO E AUDITORIA CIRÚRGICA (SEM ALTERAÇÕES) ---
def formata_dinheiro(valor):
    try: return f"R$ {float(valor):,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    except: return f"R$ {valor}"

def definir_label_chance(jogo, mod):
    if mod != "Lotofácil": return "PADRÃO"
    soma = sum(jogo)
    n = len(jogo)
    media_esperada = 180 + ((n - 15) * 13)
    if (media_esperada - 10) <= soma <= (media_esperada + 10): return "ALTA"
    return "PADRÃO"

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
    is_atypical = random.random() < 0.12 
    if not is_atypical:
        vizinhos, sequencia_max, atual = 0, 1, 1
        for i in range(len(jogo)-1):
            if jogo[i+1] - jogo[i] == 1:
                vizinhos += 1
                atual += 1
                sequencia_max = max(sequencia_max, atual)
            else: atual = 1
        if not (3 <= vizinhos <= 8): return False
        if sequencia_max < 3 or sequencia_max > 5: return False
    linhas, colunas = [0]*5, [0]*5
    for n in jogo:
        linhas[(n-1)//5] += 1
        colunas[(n-1)%5] += 1
    if any(l == 0 for l in linhas) or any(c == 0 for c in colunas): return False
    if any(l > 5 for l in linhas) or any(c > 5 for c in colunas): return False
    soma = sum(jogo)
    primos_list = [2,3,5,7,11,13,17,19,23]
    moldura_list = [1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25]
    primos = len([n for n in jogo if n in primos_list])
    moldura = len([n for n in jogo if n in moldura_list])
    cfg = {'s': (165 + (diff_n * 12), 215 + (diff_n * 14)), 'p': (4 + int(diff_n * 0.5), 7 + int(diff_n * 0.8)), 'm': (8 + int(diff_n * 0.7), 11 + int(diff_n * 0.9))}
    if not (cfg['s'][0] <= soma <= cfg['s'][1]): return False
    if not (cfg['p'][0] <= primos <= cfg['p'][1]): return False
    if not (cfg['m'][0] <= moldura <= cfg['m'][1]): return False
    if jogo_ja_saiu(jogo, mod): return False
    return True

def renderizar_heatmap(mod, res_loto):
    if not res_loto or mod != "Lotofácil": return
    st.markdown("### 🗺️ MAPA DE CALOR E ANÁLISE DE CICLO (Últimos 20)")
    conc_ordenados = sorted(res_loto.keys(), key=lambda x: int(x), reverse=True)[:20]
    frequencia = Counter()
    atraso = {n: 0 for n in range(1, 26)}
    ja_apareceu = set()
    for i, c in enumerate(conc_ordenados):
        sorteados = res_loto[c]
        for n in range(1, 26):
            if n in sorteados: frequencia[n] += 1; ja_apareceu.add(n)
            elif n not in ja_apareceu: atraso[n] += 1
    cols = st.columns(5)
    for n in range(1, 26):
        freq, atr = frequencia[n], atraso[n]
        bg_color, texto = "#222", "#d4af37"
        if freq >= 12: bg_color, texto = "#d4af37", "#000"
        elif atr >= 3: bg_color, texto = "#0984e3", "#fff"
        with cols[(n-1)%5]:
            st.markdown(f'<div style="background-color:{bg_color}; color:{texto}; border-radius:10px; padding:10px; text-align:center; border:1px solid #d4af37; margin-bottom:5px;"><span style="font-size:20px;">{n:02d}</span><br><span style="font-size:10px;">F:{freq} | A:{atr}</span></div>', unsafe_allow_html=True)
    st.markdown("---")

# --- 5. ESTADOS E ACESSO ---
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

if not st.session_state.auth:
    st.markdown('<div class="painel-luxo-black"><div class="titulo-luxo-gold">TERMINAL CRIPTOGRAFADO KADOSH</div></div>', unsafe_allow_html=True)
    with st.form("login_form"):
        senha = st.text_input("CHAVE DE ACESSO", type="password")
        if st.form_submit_button("DESBLOQUEAR"):
            if senha == "kadosh": st.session_state.auth = True; st.rerun()
            else: st.error("Chave Inválida")
    st.stop()

def mostrar_status_backup():
    total_jogos = len(st.session_state.jogos_salvos)
    total_res = sum(len(v) for v in st.session_state.ultimo_res.values())
    st.markdown(f'<div class="status-backup">📁 Backup: {total_jogos} jogos | {total_res} resultados</div>', unsafe_allow_html=True)

# --- 6. INTERFACE EM ABAS (7 ABAS COMPLETAS) ---
st.title("📊 GESTÃO ESTRATÉGICA KADOSH")
abas = st.tabs(["🎯 GERADOR PRO", "🔍 CONFERIR", "⚙️ VALORES", "📥 DATABASE", "💾 BACKUP", "🧠 INTELIGÊNCIA", "🔗 AFINIDADE"])

with abas[0]:
    mostrar_status_backup()
    mod = st.selectbox("Modalidade", list(st.session_state.custos.keys()))
    if 'ultima_mod_selecionada' not in st.session_state: st.session_state.ultima_mod_selecionada = mod
    if st.session_state.ultima_mod_selecionada != mod:
        st.session_state.jogos_gerados = []
        st.session_state.ultima_mod_selecionada = mod
        st.rerun()
    
    col_est1, col_est2 = st.columns(2)
    with col_est1:
        est_escolhida = st.selectbox("💎 ESTRATÉGIA KADOSH", list(ESTRATEGIA_MAPA.keys())) if mod == "Lotofácil" else "Personalizado"
        info_est = ESTRATEGIA_MAPA[est_escolhida]
        st.progress(info_est["peso"])
    with col_est2:
        fe_escolhido = st.selectbox("📐 MATRIZ", list(MATRIZES_FECHAMENTO.keys())) if mod == "Lotofácil" else "Nenhum"
        info_fech = MATRIZES_FECHAMENTO.get(fe_escolhido)
        if info_fech: st.progress(info_fech["peso"])

    c1, c2 = st.columns(2)
    with c1:
        if info_fech:
            def_dez, def_qtd = (16, 2) if "DIAMANTE" in fe_escolhido else (16, 1) if "CÉLULA" in fe_escolhido else (15, 24 if "18-15" in fe_escolhido else 45)
        else: def_dez, def_qtd = info_est["dez"], info_est.get("qtd", 10)
        n_dez = st.selectbox("Dezenas por Bilhete", list(st.session_state.custos[mod].keys()), index=list(st.session_state.custos[mod].keys()).index(def_dez) if def_dez in st.session_state.custos[mod] else 0)
        qtd = st.number_input("Quantidade", 1, 500, def_qtd)
    with c2:
        max_v = 25 if mod=="Lotofácil" else 60 if mod=="Mega-Sena" else 80
        if st.button("🧠 POOL INTELIGENTE KADOSH"):
            res_loto = st.session_state.ultimo_res.get(mod, {})
            if len(res_loto) >= 5:
                n_p = info_fech['n_pool'] if info_fech else 20
                scores = {n: (Counter(sum(res_loto.values(), []))[n] + (random.randint(1,5)*0.5)) for n in range(1, max_v+1)}
                st.session_state.favoritas[mod] = sorted([n for n, s in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n_p]])
                st.rerun()
        pool = st.multiselect("POOL SELECIONADO", range(1, max_v + 1), default=st.session_state.favoritas.get(mod, []))
        st.session_state.favoritas[mod] = pool

    if st.button("🚀 GERAR JOGOS (SINCRO-MATRIZ)"):
        novos = []
        def gerar(t, q):
            s, tent = 0, 0
            while s < q and tent < 20000:
                comb = sorted(random.sample(pool, t))
                if not any(set(comb) == set(x['n']) for x in novos) and validar_kadosh_cirurgico(comb, mod, t):
                    novos.append({"mod": mod, "n": comb, "tam": t, "chance": definir_label_chance(comb, mod), "est": fe_escolhido if info_fech else est_escolhida})
                    s += 1
                tent += 1
        if info_fech:
            if "DIAMANTE" in fe_escolhido: gerar(16, 2); gerar(15, 10)
            elif "CÉLULA" in fe_escolhido: gerar(16, 1); gerar(15, 15)
            else: gerar(15, qtd)
        elif est_escolhida == "6. A MARRETA": gerar(18, 1); gerar(16, 5)
        else: gerar(n_dez, qtd)
        st.session_state.jogos_gerados = novos
        st.rerun()

    for i, j in enumerate(st.session_state.jogos_gerados):
        st.code(f"JOGO {i+1:02d} | {j['est']} | {' '.join([f'{x:02d}' for x in j['n']])} | {j['chance']}")
    
    if st.session_state.jogos_gerados and st.button("💾 SALVAR JOGOS"):
        res_e = st.session_state.ultimo_res.get(mod, {})
        u_c = int(max(res_e.keys(), key=int)) if res_e else 0
        for jj in st.session_state.jogos_gerados: jj['concurso_alvo'] = u_c + 1; st.session_state.jogos_salvos.append(jj)
        st.session_state.jogos_gerados = []; st.rerun()

with abas[1]:
    mostrar_status_backup()
    mod_f = st.selectbox("Loteria", list(st.session_state.custos.keys()), key="f_c")
    js_atual = [j for j in st.session_state.jogos_salvos if j['mod'] == mod_f]
    if js_atual: st.download_button("📄 PDF VOLANTES", gerar_pdf_bonito(js_atual, mod_f), f"Kadosh_{mod_f}.pdf")
    
    res_db = st.session_state.ultimo_res.get(mod_f, {})
    total_g = 0
    for j in js_atual:
        alvo = str(j.get('concurso_alvo', ''))
        if alvo in res_db:
            acc = len(set(j['n']).intersection(set(res_db[alvo])))
            v = st.session_state.premios[mod_f].get(str(acc), 0.0)
            total_g += v
            st.markdown(f"<div {'class=\"jogo-premiado\"' if v>0 else ''}>ID {js_atual.index(j)+1} | {' '.join([f'{x:02d}' for x in j['n']])} | {acc} ACERTOS ({formata_dinheiro(v)})</div>", unsafe_allow_html=True)
    st.markdown(f'<div class="painel-luxo-black"><div class="valor-luxo-white">{formata_dinheiro(total_g)}</div></div>', unsafe_allow_html=True)

with abas[2]:
    mod_v = st.selectbox("Loteria", list(st.session_state.premios.keys()), key="v_s")
    for fx, vl in st.session_state.premios[mod_v].items():
        st.session_state.premios[mod_v][fx] = st.number_input(f"Prêmio {fx} pts", value=float(vl))

with abas[3]:
    m_db = st.selectbox("Loteria", list(st.session_state.custos.keys()), key="m_d")
    id_c = st.number_input("Concurso", 1, 9999)
    txt = st.text_area("Números Sorteados")
    if txt and st.button("GRAVAR"):
        nums = sorted(list(set([int(n) for n in re.findall(r'\d+', txt) if 1 <= int(n) <= 80])))
        st.session_state.ultimo_res[m_db][str(int(id_c))] = nums; st.success("OK")

with abas[4]:
    st.download_button("📤 EXPORTAR", json.dumps({"salvos": st.session_state.jogos_salvos, "premios": st.session_state.premios, "res": st.session_state.ultimo_res}), "backup.json")
    f = st.file_uploader("IMPORTAR")
    if f and st.button("CONFIRMAR"):
        d = json.load(f); st.session_state.jogos_salvos = d['salvos']; st.session_state.ultimo_res = d['res']; st.rerun()

with abas[5]:
    st.header("🧠 CENTRAL KADOSH")
    st.table(pd.DataFrame([{"Estratégia": k, "Foco": v["desc"], "Chance": v["prob"]} for k,v in ESTRATEGIA_MAPA.items() if k != "Personalizado"]))
    st.table(pd.DataFrame([{"Matriz": k, "Pool": v["n_pool"], "Garantia": v["desc"]} for k,v in MATRIZES_FECHAMENTO.items() if v]))

with abas[6]:
    st.markdown('<div class="painel-luxo-black"><div class="titulo-luxo-gold">🔗 AFINIDADE E VÍNCULOS</div></div>', unsafe_allow_html=True)
    m_af = st.selectbox("Loteria", list(st.session_state.custos.keys()), key="af_s")
    res_af = st.session_state.ultimo_res.get(m_af, {})
    if len(res_af) > 3:
        lim = 26 if m_af == "Lotofácil" else 61
        mat = [[0]*lim for _ in range(lim)]
        for s in res_af.values():
            n_s = sorted([int(x) for x in s])
            for i, j in combinations(n_s, 2): 
                if i < lim and j < lim: mat[i][j] += 1
        
        l_pares = []
        for i in range(1, lim):
            for j in range(i+1, lim):
                if mat[i][j] > 0: l_pares.append({"Par": f"{i:02d}+{j:02d}", "Vezes": mat[i][j], "Afinidade": f"{(mat[i][j]/len(res_af))*100:.1f}%"})
        st.table(pd.DataFrame(sorted(l_pares, key=lambda x: x['Vezes'], reverse=True)[:15]))
    else: st.warning("Dados insuficientes.")
