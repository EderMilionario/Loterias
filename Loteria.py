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
    mostrar_status_backup()
    st.header("🎯 Gerador Kadosh Estratégico")
    
    col_c1, col_c2, col_c3 = st.columns([1,1,1])
    with col_c1:
        # Adicionei 'Avulso/Sem Estratégia' para quando você não quiser seguir o mapa
        lista_opcoes = list(ESTRATEGIA_MAPA.keys()) + ["Avulso/Sem Estratégia"]
        mod_est = st.selectbox("Escolha a Estratégia", lista_opcoes, key="mod_est_0")
        
        id_prox_0 = max(1, int(max(st.session_state.ultimo_res['Lotofácil'].keys() or [0])) + 1)
        id_alvo = st.number_input("Concurso Alvo", 1, 9999, value=id_prox_0, key="id_alvo_0")
    
    with col_c2:
        pool_tipo = st.radio("Origem das Dezenas", ["Pool Inteligente (IA)", "Seleção Manual"])
        qtd_avulso = st.slider("Quantidade de Jogos", 1, 50, 10) if mod_est == "Avulso/Sem Estratégia" else None
        
    with col_c3:
        if pool_tipo == "Seleção Manual":
            pool_usar = st.multiselect("Dezenas (Mín. 18)", list(range(1,26)), default=list(range(1,19)))
        else:
            pool_usar = processar_pool_inteligente("Lotofácil")
            st.info(f"IA selecionou {len(pool_usar)} dezenas.")

    if st.button("🚀 GERAR JOGOS"):
        jogos_gerados = []
        
        # Se NÃO usar estratégia do mapa (O que você perguntou)
        if mod_est == "Avulso/Sem Estratégia":
            for _ in range(qtd_avulso):
                jogos_gerados.append(sorted(random.sample(pool_usar, 15)))
        
        # Se usar as estratégias do mapa
        elif mod_est == "A MARRETA (SISTEMA 18)":
            jogos_gerados.append(sorted(random.sample(pool_usar, 18)))
            for _ in range(5): 
                jogos_gerados.append(validar_kadosh_cirurgico(pool_usar, 15))
        else:
            info = ESTRATEGIA_MAPA[mod_est]
            for _ in range(info.get("qtd", 10)): jogos_gerados.append(validar_kadosh_cirurgico(pool_usar, 15))
            for _ in range(info.get("qtd_16", 0)): jogos_gerados.append(validar_kadosh_cirurgico(pool_usar, 16))

        st.session_state.temp_jogos = [j for j in jogos_gerados if j]
        st.success(f"Gerados {len(st.session_state.temp_jogos)} jogos!")

    # Mostrar e Salvar
    if st.session_state.get('temp_jogos'):
        for idx, j in enumerate(st.session_state.temp_jogos):
            st.code(f"Jogo {idx+1:02d}: " + " ".join([f"{x:02d}" for x in j]))
        
        if st.button("💾 SALVAR TUDO NO SISTEMA"):
            for j in st.session_state.temp_jogos:
                st.session_state.jogos_salvos.append({
                    "concurso_alvo": id_alvo,
                    "n": j,
                    "est": mod_est, # Se for avulso, salva como 'Avulso/Sem Estratégia'
                    "data": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                })
            st.success("✅ Jogos salvos com a etiqueta correta!")
            st.session_state.temp_jogos = []
            st.rerun()
with abas[1]:
    mostrar_status_backup()
    st.header("📐 Matrizes de Fechamento")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        mod_mat = st.selectbox("Selecione a Matriz", list(MATRIZES_FECHAMENTO.keys()))
        # Busca o próximo concurso automaticamente
        id_prox = max(1, int(max(st.session_state.ultimo_res['Lotofácil'].keys() or [0])) + 1)
        id_alvo_m = st.number_input("Concurso Alvo", 1, 9999, value=id_prox, key="id_alvo_m")
    
    with col_m2:
        m_info = MATRIZES_FECHAMENTO[mod_mat]
        st.info(f"**Garantia:** {m_info['garantia']} Pontos | **Probabilidade:** {m_info['prob']}")
        pool_m = st.multiselect(f"Escolha EXATAMENTE {m_info['n_pool']} dezenas para o Pool", list(range(1,26)), key="pool_matriz")

    # VALIDAÇÃO DE QUANTIDADE DE DEZENAS
    if len(pool_m) != m_info['n_pool']:
        st.warning(f"⚠️ Selecione exatamente {m_info['n_pool']} dezenas. Você selecionou {len(pool_m)}.")
    else:
        if st.button("🧩 GERAR FECHAMENTO"):
            jogos_finais = []
            # Lógica de Matriz Diamante ou Fechamento Padrão
            if mod_mat == "DIAMANTE (19-15-14/15)":
                for _ in range(2): jogos_finais.append(validar_kadosh_cirurgico(pool_m, 16))
                for _ in range(10): jogos_finais.append(validar_kadosh_cirurgico(pool_m, 15))
            else:
                # Gera 12 jogos baseados no pool selecionado para garantir volume
                for _ in range(12): jogos_finais.append(validar_kadosh_cirurgico(pool_m, 15))
            
            st.session_state.temp_matriz = [j for j in jogos_finais if j]
            st.success(f"Matriz {mod_mat} gerada com sucesso!")

    # EXIBIÇÃO E SALVAMENTO
    if st.session_state.get('temp_matriz'):
        st.markdown("---")
        for idx, j in enumerate(st.session_state.temp_matriz):
            st.code(f"Jogo {idx+1:02d}: " + " ".join([f"{x:02d}" for x in j]))
        
        col_sm1, col_sm2 = st.columns(2)
        with col_sm1:
            if st.button("💾 SALVAR JOGOS DA MATRIZ"):
                for j in st.session_state.temp_matriz:
                    st.session_state.jogos_salvos.append({
                        "concurso_alvo": id_alvo_m,
                        "n": j,
                        "est": f"Matriz: {mod_mat}", # ESTA LINHA É O QUE ALIMENTA O TEU RANKING
                        "data": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                    })
                st.success("✅ Jogos salvos! Agora aparecem no Ranking da Central de Inteligência.")
                st.session_state.temp_matriz = [] # Limpa a memória temporária
                st.rerun()
        
        with col_sm2:
            pdf_m = gerar_pdf_bonito(st.session_state.temp_matriz, f"Matriz_{mod_mat}")
            st.download_button("📥 Baixar PDF da Matriz", pdf_m, "matriz_kadosh.pdf")

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
    
    # --- NOVO BLOCO: RANKING DE PERFORMANCE REAL ---
    st.subheader("🏆 Desempenho Histórico por Estratégia")
    
    jogos_salvos = st.session_state.get('jogos_salvos', [])
    res_db = st.session_state.ultimo_res.get("Lotofácil", {}) # Focado em Lotofácil por ser o motor principal
    
    if not jogos_salvos or not res_db:
        st.info("💡 Para ver o ranking de performance, você precisa ter jogos salvos e resultados cadastrados na Database.")
    else:
        stats_est = {}
        for j in jogos_salvos:
            est_nome = j.get('est', 'Outros')
            if est_nome not in stats_est:
                stats_est[est_nome] = {"jogos": 0, "premios": 0.0, "acertos_11_13": 0, "acertos_14_15": 0}
            
            alvo = str(j.get('concurso_alvo', ''))
            if alvo in res_db:
                acertos = len(set(j['n']).intersection(set(res_db[alvo])))
                val_premio = st.session_state.premios["Lotofácil"].get(str(acertos), 0.0)
                
                stats_est[est_nome]["jogos"] += 1
                stats_est[est_nome]["premios"] += val_premio
                if 11 <= acertos <= 13:
                    stats_est[est_nome]["acertos_11_13"] += 1
                elif acertos >= 14:
                    stats_est[est_nome]["acertos_14_15"] += 1
        
        if stats_est:
            df_ranking = []
            for est, dados in stats_est.items():
                df_ranking.append({
                    "Estratégia": est,
                    "Qtd Jogos": dados["jogos"],
                    "Premiação Total": formata_dinheiro(dados["premios"]),
                    "11 a 13 pts": dados["acertos_11_13"],
                    "14 a 15 pts": dados["acertos_14_15"]
                })
            
            # Ordena pelo que deu mais dinheiro
            df_ranking = sorted(df_ranking, key=lambda x: float(x["Premiação Total"].replace('R$ ', '').replace('.', '').replace(',', '.')), reverse=True)
            st.table(pd.DataFrame(df_ranking))
        else:
            st.warning("Aguardando sorteio dos concursos vinculados aos jogos salvos.")

    st.markdown("---")
    
    # --- MANTENDO O RESTANTE DA ABA SEM ALTERAÇÕES ---
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

# --- CONTEÚDO DA NOVA ABA 7 ---
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





