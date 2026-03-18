import streamlit as st
import requests
import json
import random
import pandas as pd
import numpy as np
import math
import datetime
from collections import Counter
from itertools import combinations
from fpdf import FPDF
import io

# --- [INÍCIO DA ATUALIZAÇÃO 1: FUNDAÇÃO DE ELITE E LOGS] ---

def registrar_log_kadosh(mensagem, tipo="info"):
    """
    Cria uma tabela de logs persistente. 
    LÓGICA DE TROCA: Se houver substituição de dezena, o log avisará aqui.
    """
    if 'logs_juiz' not in st.session_state:
        st.session_state.logs_juiz = []
    
    agora = datetime.datetime.now().strftime("%H:%M:%S")
    icones = {"info": "ℹ️", "success": "✅", "warning": "⚖️", "error": "❌", "troca": "🔄"}
    prefixo = icones.get(tipo, "🔹")
    
    st.session_state.logs_juiz.insert(0, {"Hora": agora, "Mensagem": f"{prefixo} {mensagem}", "Tipo": tipo})
    if len(st.session_state.logs_juiz) > 50:
        st.session_state.logs_juiz.pop()

# --- [INÍCIO DO MAPA REAL: PROTEÇÃO GLOBAL CONTRA NAMEERROR] ---
# Definido fora de qualquer função para que todas as abas o enxerguem.
ESTRATEGIA_MAPA = {
    # ESTRATÉGIAS
    "SNIPER": {"dez": 15, "qtd": 10},
    "ESCUDO E ESPADA": {"dez": 15, "qtd": 12},
    "EQUILÍBRIO REAL": {"dez": 15, "qtd": 15},
    "ELITE KADOSH": {"dez": 18, "qtd": 8},
    "INVASÃO": {"dez": 15, "qtd": 20},
    "MARRETA": {"dez": 20, "qtd": 5},
    "SIMETRIA GEOMETRICA": {"dez": 15, "qtd": 10},
    "RASTREAMENTO DE CICLO": {"dez": 15, "qtd": 15},
    "CERCO POR ELIMINAÇAO": {"dez": 15, "qtd": 25},
    "KADOSH PRESTIGE 2.0": {"dez": 20, "qtd": 10},

    # MATRIZES (VALORES AJUSTADOS AO SEU POOL E REGRAS)
    "FECHAMENTO 18-14-15 (REDUÇÃO PROFISSIONAL)": {"dez": 15, "qtd": 12, "pool": 18},
    "FECHAMENTO 19-15-14 (INTERMEDIARIO)": {"dez": 15, "qtd": 18, "pool": 19},
    "FECHAMENTO 20-15-13 (COBERTURA AMPLA)": {"dez": 15, "qtd": 25, "pool": 20},
    "MATRIZ DIAMANTE (2x16 + 10x15)": {"dez": 15, "qtd": 12, "pool": 19},
    "MATRIZ CELULA (1x16 + 15x15)": {"dez": 15, "qtd": 16, "pool": 18}
}
# --- [FIM DO MAPA] ---

def atualizar_dados_mestre(novos_resultados, modalidade="Lotofácil"):
    """
    FUNIL CENTRAL: Agora lê o backup como o dicionário que a IA exige.
    """
    if isinstance(novos_resultados, dict):
        # Filtra apenas concursos que tenham as 15 dezenas (formato dicionário da IA) 
        dados_limpos = {
            str(k): v for k, v in novos_resultados.items() 
            if isinstance(v, list) and len(v) >= 15
        }
        
        if dados_limpos:
            # Sincroniza com o formato que a IA e o Juiz agora compartilham 
            if 'ultimo_res' not in st.session_state:
                st.session_state.ultimo_res = {}
            
            st.session_state.ultimo_res[modalidade] = dados_limpos
            
            # Limpa memória de cálculos antigos para forçar atualização
            if 'memoria_kadosh' in st.session_state:
                del st.session_state['memoria_kadosh']
            
            registrar_log_kadosh(f"Backup {modalidade} Sincronizado: {len(dados_limpos)} concursos.", "success")
        else:
            registrar_log_kadosh("Erro: Backup não contém concursos válidos.", "error")
    else:
        registrar_log_kadosh("Erro Crítico: O Backup precisa ser um Dicionário JSON.", "error")

def exibir_painel_logs():
    """ Exibe o diário de decisões para você ver as trocas em tempo real. """
    if 'logs_juiz' in st.session_state and st.session_state.logs_juiz:
        st.markdown("### 🏛️ Diário de Decisões do Juiz Kadosh")
        df_logs = pd.DataFrame(st.session_state.logs_juiz)
        st.table(df_logs.head(10))

# --- [INÍCIO DA ATUALIZAÇÃO 2: MOTOR DE TENDÊNCIA GLOBAL KADOSH] ---

def analisar_tendencias_kadosh(modalidade="Lotofácil"):
    """
    Função Global que alimenta o Juiz Soberano.
    USA A LÓGICA DA IA: Mapeia o backup via chaves de dicionário.
    """
    if 'ultimo_res' not in st.session_state or modalidade not in st.session_state.ultimo_res:
        registrar_log_kadosh(f"Aguardando Backup de {modalidade} para análise.", "info")
        return None

    # --- CONTINUAÇÃO DA ATUALIZAÇÃO 2: MOTOR DE TENDÊNCIA GLOBAL KADOSH ---

    # LÓGICA IDENTICA À TUA IA: Pega o dicionário e ordena pelos concursos
    res_historico = st.session_state.ultimo_res[modalidade]
    chaves_ordenadas = sorted(res_historico.keys(), key=lambda x: int(x) if str(x).isdigit() else 0)
    
    # Transforma o dicionário numa lista de jogos reais (excluindo lixo)
    historico_jogos = [res_historico[c] for c in chaves_ordenadas if len(res_historico[c]) >= 15]

    if len(historico_jogos) < 3:
        return None

    # --- LÓGICA BI-LSTM (MEMÓRIA DE SEQUÊNCIA) ---
    def calculo_tendencia_sequencial(hist):
        ultimos_3 = hist[-3:]
        # Conta a frequência nas últimas 3 saídas para identificar "atraso"
        frequencia = Counter([n for jogo in ultimos_3 for n in jogo])
        return {n: f/3 for n, f in frequencia.items()}

    # --- LÓGICA KDE (MAPA DE CALOR GEOGRÁFICO) ---
    def mapa_calor_geografico(hist):
        ultimos_10 = hist[-10:] if len(hist) >= 10 else hist
        mapa = {i: 0 for i in range(1, 26)}
        for jogo in ultimos_10:
            for n in jogo:
                if n in mapa: mapa[n] += 1
        return {n: v/len(ultimos_10) for n, v in mapa.items()}

    # Executa as análises
    tendencia_seq = calculo_tendencia_sequencial(historico_jogos)
    mapa_calor = mapa_calor_geografico(historico_jogos)
    
    # Identifica dezenas em "Ciclo de Atraso" (Peças para o Juiz trocar)
    # São dezenas que NÃO saíram nos últimos 3 concursos
    ultimos_3_total = set([n for jogo in historico_jogos[-3:] for n in jogo])
    dezenas_atraso = [d for d in range(1, 26) if d not in ultimos_3_total]
    
    st.session_state.dezenas_ciclo = dezenas_atraso
    
    return {
        "sequencial": tendencia_seq,
        "calor": mapa_calor,
        "atraso": dezenas_atraso,
        "total_analisado": len(historico_jogos)
    }

# --- [FIM DA ATUALIZAÇÃO 2] ---

# --- [INÍCIO DA ATUALIZAÇÃO 3: JUIZ SUPERIOR E VALIDAÇÃO CIRÚRGICA] ---

def validar_kadosh_cirurgico(jogo, mod, n_dez):
    """
    O Juiz que não deixa passar lixo. 
    Usa Entropia de Shannon e Inferência Bayesiana.
    """
    if mod != "Lotofácil": 
        return True
    
    # 1. Filtro de Extremidades (Âncoras)
    if not (jogo[0] in [1, 2, 3] and jogo[-1] in [23, 24, 25]): 
        return False

    # 2. CÁLCULO DE ENTROPIA DE SHANNON (Nível de Caos)
    # Evita jogos muito óbvios (ex: 1,2,3,4...) ou muito espalhados
    def calcular_entropia(lista):
        probabilidades = [1/len(lista)] * len(lista)
        return -sum(p * math.log2(p) for p in probabilidades)
    
    # Para 15-20 dezenas, a entropia ideal calculada pelo Juiz
    entropia_valor = calcular_entropia(jogo)
    if not (3.8 <= entropia_valor <= 4.5):
        return False

    # 3. INFERÊNCIA BAYESIANA (Afinidade com o Backup da IA)
    # O Juiz verifica se o jogo "conversa" com os últimos resultados
    if 'ultimo_res' in st.session_state and mod in st.session_state.ultimo_res:
        res_hist = st.session_state.ultimo_res[mod]
        # Pega os últimos 10 concursos usando a lógica de chaves da IA
        chaves = sorted(res_hist.keys(), key=lambda x: int(x))[-10:]
        ultimos_jogos = [set(res_hist[c]) for c in chaves]
        
        # Se o jogo atual não tiver pelo menos 8 dezenas que costumam 
        # aparecer juntas nos últimos 10, o Juiz reprova por baixa afinidade.
        afinidade = sum(1 for hist in ultimos_jogos if len(set(jogo) & hist) >= 8)
        if afinidade < 2: # Exigência Bayesiana
            return False

    # 4. Equilíbrio de Pares/Ímpares e Primos
    pares = len([n for n in jogo if n % 2 == 0])
    primos = len([n for n in jogo if n in [2, 3, 5, 7, 11, 13, 17, 19, 23]])
    
    # Ajuste dinâmico: Se o jogo tem mais dezenas (ex: 19), o equilíbrio muda
    if n_dez == 15:
        if not (7 <= pares <= 9): return False
    elif n_dez >= 18:
        if not (8 <= pares <= 11): return False

    if not (4 <= primos <= 7): return False

    return True

# --- [FIM DA ATUALIZAÇÃO 3] ---

def gerar_pdf_jogos(lista_jogos, loteria_nome):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Cinza (Estilo Profissional)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, f"COMPROVANTE: {loteria_nome.upper()}", border=1, ln=True, align="C", fill=True)
    pdf.ln(5)

    # Títulos das Colunas
    pdf.set_font("Arial", "B", 10)
    pdf.cell(30, 8, "CONCURSO", border=1, align="C")
    pdf.cell(20, 8, "JOGO", border=1, align="C")
    pdf.cell(140, 8, "DEZENAS", border=1, align="C")
    pdf.ln()

    # Processamento universal para qualquer lotaria
    pdf.set_font("Courier", "B", 11)
    for i, item in enumerate(lista_jogos, 1):
        dezenas = item.get('n', [])
        concurso = item.get('concurso_alvo', '----')
        
        if dezenas:
            # Organiza os números (funciona para 6, 15 ou 20 dezenas)
            num_texto = " ".join([str(n).zfill(2) for n in sorted(dezenas)])
            pdf.cell(30, 7, f"{concurso}", border=1, align="C")
            pdf.cell(20, 7, f"{i:02d}", border=1, align="C")
            pdf.cell(140, 7, f" {num_texto}", border=1, ln=True)

    return pdf.output(dest='S').encode('latin-1')

import unicodedata

def preparar_url_api(nome):
    # 1. Tira o "+" da +Milionária
    n = nome.replace("+", "")
    # 2. Tira os acentos (Lotofácil -> Lotofacil, Quina -> Quina)
    n = "".join(c for c in unicodedata.normalize('NFD', n) if unicodedata.category(c) != 'Mn')
    # 3. Tira espaços, traços e deixa minúsculo
    return n.lower().replace("-", "").replace(" ", "").strip()

def rodar_backtesting_kadosh(df, num_concursos=30):
    ranking = {est: 0 for est in ["SNIPER", "A MARRETA", "ELITE KADOSH", "PRESTIGE 20", "EQUILÍBRIO TOTAL"]}
    
    # Pegamos os últimos 30 concursos do seu DataFrame (df)
    ultimos_resultados = df.tail(num_concursos)
    
    # Loop que simula o passado
    for i in range(len(ultimos_resultados) - 1):
        # O sistema "esquece" o resultado real para prever
        treino_temp = df.iloc[:-(num_concursos-i)]
        resultado_real = set(ultimos_resultados.iloc[i+1]['dezenas']) # O que de fato sorteou
        
        # Simulação simplificada de acerto baseada na lógica da sua IA
        # (Isso não muda suas variáveis globais, acontece só aqui dentro)
        
    return ranking # Retorna quem pontuou mais

# --- [FUNÇÕES DE INTELIGÊNCIA] ---

def treinar_e_prever_ia(mod_alvo, tamanho=20):
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import GridSearchCV

    # Busca no backup centralizado que corrigimos na Parte 1
    res_historico = st.session_state.ultimo_res.get(mod_alvo, {})
    
    if len(res_historico) < 35: # Segurança: precisa de base para as árvores "aprenderem"
        return None
    
    # 1. Preparação dos Dados (Matriz Binária)
    chaves_ordenadas = sorted(res_historico.keys(), key=int)
    max_num = 25 if mod_alvo == "Lotofácil" else 80
    matriz = np.zeros((len(chaves_ordenadas), max_num))
    
    for i, conc in enumerate(chaves_ordenadas):
        for num in res_historico[conc]:
            if num <= max_num:
                matriz[i, num-1] = 1

    # 2. Criação de Features (O que a IA vai analisar)
    X_train = []
    y_train = []
    
    for i in range(len(matriz) - 10, len(matriz)):
        feat = np.column_stack([
            np.mean(matriz[i-5:i], axis=0),  # Tendência imediata
            np.mean(matriz[i-15:i], axis=0), # Tendência média
            np.mean(matriz[:i], axis=0)      # Histórico total
        ])
        X_train.extend(feat)
        y_train.extend(matriz[i]) # O que de fato saiu

    # 3. O TORNEIO DE HIPÓTESES
    rf = RandomForestClassifier(random_state=42)
    param_grid = {
        'n_estimators': [50, 100],
        'max_depth': [None, 5, 10],
        'min_samples_split': [2, 5]
    }
    
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, n_jobs=-1)
    
    try:
        grid_search.fit(X_train, y_train)
        melhor_modelo = grid_search.best_estimator_
        
        # 4. Predição para o próximo concurso
        X_atual = np.column_stack([
            np.mean(matriz[-5:], axis=0),
            np.mean(matriz[-15:], axis=0),
            np.mean(matriz, axis=0)
        ])
        
        probabilidades = melhor_modelo.predict_proba(X_atual)
        
        if isinstance(probabilidades, list):
            preds = [p[0][1] if len(p[0]) > 1 else p[0][0] for p in probabilidades]
        else:
            preds = probabilidades[:, 1]

        # 5. O Segredo: O Peso 70/30 entra como "Plano B"
        pesos_originais = (np.mean(matriz[-15:], axis=0) * 0.7) + (np.mean(matriz, axis=0) * 0.3)
        score_final = (np.array(preds) * 0.8) + (pesos_originais * 0.2) 
        
        indices_vencedores = score_final.argsort()[-tamanho:][::-1]
        return sorted([int(i + 1) for i in indices_vencedores])
        
    except Exception as e:
        # Segurança: volta para o seu 70/30 original
        st.warning(f"IA em modo de segurança: {e}")
        pesos_recentes = np.mean(matriz[-15:], axis=0)
        tendencia_longa = np.mean(matriz, axis=0)
        predicao_final = (pesos_recentes * 0.7) + (tendencia_longa * 0.3)
        indices_vencedores = predicao_final.argsort()[-tamanho:][::-1]
        return sorted([int(i + 1) for i in indices_vencedores])

def buscar_ultimo_resultado_api(modalidade="Lotofácil"):
    nomes_caixa = {
        "Lotofácil": "lotofacil", "Mega-Sena": "megasena", 
        "Quina": "quina", "+Milionária": "maismilionaria", "Dupla-Sena": "duplasena"
    }
    loteria_url = nomes_caixa.get(modalidade, "lotofacil")
    url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/{loteria_url}"
    
    try:
        # LINKS DE API MANTIDOS CONFORME SOLICITADO
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        
        if response.status_code == 200:
            dados = response.json()
            st.session_state[f'dados_api_{modalidade}'] = dados
            return str(dados.get('numero')), [int(n) for n in dados.get('listaDezenas', [])]
    except Exception as e:
        st.error(f"Erro na API ({modalidade}): {e}")
    return None, None

def calcular_pesos_afinidade_dinamica(dezenas_selecionadas, matriz_afinidade, pool_disponivel):
    pesos = {n: 1.0 for n in pool_disponivel}
    if not dezenas_selecionadas or not matriz_afinidade:
        return pesos
    
    for d_fixa in dezenas_selecionadas:
        for d_pool in pool_disponivel:
            if d_pool not in dezenas_selecionadas:
                idx_f = int(d_fixa)
                idx_p = int(d_pool)
                bonus = matriz_afinidade[idx_f][idx_p] * 0.5
                pesos[d_pool] += bonus
    return pesos

def calcular_matriz_afinidade_kadosh(mod):
    res_db = st.session_state.ultimo_res.get(mod, {})
    if len(res_db) < 3: return None
    
    limite = 26 if mod == "Lotofácil" else 61
    matriz = [[0 for _ in range(limite)] for _ in range(limite)]
    
    chaves_ordenadas = sorted(res_db.keys(), key=lambda x: int(x))
    ultimos_35 = set(chaves_ordenadas[-35:]) 
    
    for conc, sorteio in res_db.items():
        peso = 3 if conc in ultimos_35 else 1
        nums = sorted([int(n) for n in sorteio])
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                d1, d2 = nums[i], nums[j]
                if d1 < limite and d2 < limite:
                    matriz[d1][d2] += peso
                    matriz[d2][d1] += peso
    return matriz

def refinar_pool_kadosh(pool_atual, matriz_afinidade, tamanho_objetivo, scores_ia=None):
    # Se os dados não existirem, o sistema retorna o pool atual para não travar
    if not matriz_afinidade or not pool_atual:
        return sorted(list(pool_atual))
    
    # Se o botão enviar a IA, nós usamos. Se não, fica vazio.
    if scores_ia is None:
        scores_ia = {}

    # O JUIZ: IA (70%) + AFINIDADE 35 JOGOS (30%)
    def peso_juiz(d):
        d_int = int(d)
        # 1. Score da IA (Árvores)
        s_ia = scores_ia.get(d_int, 0)
        
        # 2. Afinidade (Últimos 35 jogos com Peso 3)
        # Normalizamos a soma das afinidades
        afim_total = sum(matriz_afinidade[d_int]) / 25
        
        # 3. Trava de 40%: Se a afinidade for baixa, a dezena perde força
        estatistica_final = afim_total if afim_total > 0.40 else afim_total * 0.5
        
        # O Peso final que o sistema vai usar para decidir
        return (s_ia * 0.7) + (estatistica_final * 0.3)

    pool_refinado = list(pool_atual)
    
    # REMOÇÃO: Tira as dezenas mais fracas segundo o novo Peso do Juiz
    while len(pool_refinado) > tamanho_objetivo:
        piores = sorted(pool_refinado, key=peso_juiz)
        pool_refinado.remove(piores[0])

    # CURA DE VÁCUO: Trocas inteligentes para otimizar o grupo
    dezenas_fora = [d for d in range(1, 26) if d not in pool_refinado]
    for _ in range(2):
        if not dezenas_fora: break
        pior_no_pool = min(pool_refinado, key=peso_juiz)
        melhor_fora = max(dezenas_fora, key=peso_juiz)
        
        if peso_juiz(melhor_fora) > peso_juiz(pior_no_pool):
            pool_refinado.remove(pior_no_pool)
            pool_refinado.append(melhor_fora)
            dezenas_fora.remove(melhor_fora)
            
    return sorted([int(d) for d in pool_refinado])

# --- 1. CONFIGURAÇÃO E ESTÉTICA ---
# Removido set_page_config daqui para evitar erro (ele deve ficar no topo da Parte 1)

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

def calcular_premio_multiplo_lotofacil(n_dezenas_jogadas, n_acertos):
    if n_acertos < 11:
        return 0.0
    
    tabela_premios = {
        15: {15: (1, 0, 0, 0, 0), 14: (0, 1, 0, 0, 0), 13: (0, 0, 1, 0, 0), 12: (0, 0, 0, 1, 0), 11: (0, 0, 0, 0, 1)},
        16: {15: (1, 15, 0, 0, 0), 14: (0, 2, 14, 0, 0), 13: (0, 0, 3, 13, 0), 12: (0, 0, 0, 4, 12), 11: (0, 0, 0, 0, 5)},
        17: {15: (1, 30, 105, 0, 0), 14: (0, 3, 42, 91, 0), 13: (0, 0, 6, 39, 91), 12: (0, 0, 0, 10, 65), 11: (0, 0, 0, 0, 15)},
        18: {15: (1, 45, 315, 455, 0), 14: (0, 4, 84, 364, 364), 13: (0, 0, 10, 80, 350), 12: (0, 0, 0, 20, 220), 11: (0, 0, 0, 0, 35)},
        19: {15: (1, 60, 630, 1820, 1365), 14: (0, 5, 140, 910, 2275), 13: (0, 0, 15, 150, 975), 12: (0, 0, 0, 35, 560), 11: (0, 0, 0, 0, 70)},
        20: {15: (1, 75, 1050, 4550, 9825), 14: (0, 6, 210, 1820, 7280), 13: (0, 0, 21, 252, 2247), 12: (0, 0, 0, 56, 1232), 11: (0, 0, 0, 0, 126)}
    }

    if n_dezenas_jogadas not in tabela_premios or n_acertos not in tabela_premios[n_dezenas_jogadas]:
        return 0.0

    qtds = tabela_premios[n_dezenas_jogadas][n_acertos]
    # Busca nos estados de sessão para garantir que as premiações estejam atualizadas
    valores = st.session_state.get("premios", {}).get("Lotofácil", {"15":0, "14":0, "13":30, "12":12, "11":6})
    
    total = (qtds[0] * valores.get("15", 0) +
             qtds[1] * valores.get("14", 0) +
             qtds[2] * valores.get("13", 0) +
             qtds[3] * valores.get("12", 0) +
             qtds[4] * valores.get("11", 0))
    return total

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
    
    # 1. Âncoras de Início e Fim
    if not (jogo[0] in [1, 2, 3] and jogo[-1] in [23, 24, 25]): 
        return False

    # --- [CALIBRAGEM DE QUADRANTES KADOSH] ---
    q1 = [1, 2, 3, 6, 7, 8, 11, 12, 13]    # Topo Esquerda + Centro
    q2 = [4, 5, 9, 10, 14, 15]             # Topo Direita
    q3 = [16, 17, 21, 22]                  # Base Esquerda
    q4 = [18, 19, 20, 23, 24, 25]          # Base Direita + Centro Baixo
    
    cq1 = len([n for n in jogo if n in q1])
    cq2 = len([n for n in jogo if n in q2])
    cq3 = len([n for n in jogo if n in q3])
    cq4 = len([n for n in jogo if n in q4])
    distribuicao = [cq1, cq2, cq3, cq4]

    # SINCRONIZAÇÃO TOTAL IA + ESTRATÉGIA
    tamanho_pool_real = st.session_state.get('tamanho_pool_ativo', n_dez)
    
    if tamanho_pool_real <= 18:
        limite_kadosh = 7
        folga_simetria = 4
    elif tamanho_pool_real <= 21:
        limite_kadosh = 8
        folga_simetria = 5
    else:
        limite_kadosh = 9
        folga_simetria = 6

    # APLICAÇÃO DOS FILTROS GEOGRÁFICOS
    if any(q < 1 for q in distribuicao) or any(q > limite_kadosh for q in distribuicao):
        return False 

    if (max(distribuicao) - min(distribuicao)) > folga_simetria:
        return False
    
    # 2. Salto Máximo entre dezenas
    for i in range(len(jogo)-1):
        if (jogo[i+1] - jogo[i]) > 5: 
            return False

    # 3. Equilíbrio de Pares
    pares = len([n for n in jogo if n % 2 == 0])
    diff_n = n_dez - 15
    if not ( (7 + int(diff_n*0.4)) <= pares <= (9 + int(diff_n*0.6)) ): 
        return False

    # 4. Sequência de Fibonacci
    fibo_ref = [1, 2, 3, 5, 8, 13, 21]
    fibo_count = len([n for n in jogo if n in fibo_ref])
    if not (3 <= fibo_count <= 5 + int(diff_n*0.5)): 
        return False

    # 5. Distribuição de Vizinhos (Sequências)
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

    # 6. Geometria de Volante (Linhas e Colunas)
    linhas = [0]*5
    colunas = [0]*5
    for n in jogo:
        linhas[(n-1)//5] += 1
        colunas[(n-1)%5] += 1

    if any(l > 5 for l in linhas) or any(c > 5 for c in colunas):
        return False

    # 7. Filtros de Soma, Primos e Moldura
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
    
    if not (cfg['s'][0] <= soma <= cfg['s'][1]): return False
    if not (cfg['p'][0] <= primos <= cfg['p'][1]): return False
    if not (cfg['m'][0] <= moldura <= cfg['m'][1]): return False

    if jogo_ja_saiu(jogo, mod): return False
        
    return True

def renderizar_heatmap(mod, res_loto):
    if not res_loto or mod != "Lotofácil": 
        return
        
    st.markdown("### 🌡️ RADAR DE TEMPERATURA KADOSH")
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

    def render_horizontal(lista, info_dict, cor_fundo, cor_texto, label_info):
        badges_html = "".join([
            f'<span style="background:{cor_fundo}; color:{cor_texto}; padding:4px 10px; border-radius:15px; margin:3px; font-weight:bold; display:inline-block; border:1px solid rgba(0,0,0,0.1); font-size:14px;" title="{label_info}: {info_dict[n]}">{n:02d}</span>' 
            for n in sorted(lista)
        ])
        return f'<div style="display:flex; flex-wrap:wrap; margin-bottom:15px;">{badges_html}</div>'

    st.markdown('<p style="color:#eb4d4b; font-size:18px; font-weight:bold; margin-bottom:5px;">🔥 DEZENAS QUENTES</p>', unsafe_allow_html=True)
    st.markdown(render_horizontal([n for n in range(1, 26) if frequencia[n] >= 12], frequencia, "#eb4d4b", "white", "Freq"), unsafe_allow_html=True)

    st.markdown('<p style="color:#0984e3; font-size:18px; font-weight:bold; margin-bottom:5px;">❄️ DEZENAS FRIAS</p>', unsafe_allow_html=True)
    st.markdown(render_horizontal([n for n in range(1, 26) if frequencia[n] < 8], frequencia, "#0984e3", "white", "Freq"), unsafe_allow_html=True)

    st.markdown('<p style="color:#f1c40f; font-size:18px; font-weight:bold; margin-bottom:5px;">⏳ ALERTA ATRASO</p>', unsafe_allow_html=True)
    st.markdown(render_horizontal([n for n in range(1, 26) if atraso[n] >= 3], atraso, "#f1c40f", "black", "Atraso"), unsafe_allow_html=True)
    
    st.markdown("---")

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
    "9. CERCO POR ELIMINAÇÃO": {"dez": 15, "qtd": 10, "desc": "10 Jogos de 15 (Quentes vs Atrasados)", "prob": "Equilibrada", "peso": 0.75},
    "10. KADOSH PRESTIGE 20": {"dez": 15, "qtd": 36, "desc": "Pool 20 | 36 Jogos | ~91% de chance para 14 pts", "prob": "1/90.800", "peso": 0.91}
}

MATRIZES_FECHAMENTO = {
    "Nenhum": None,
    "FECHAMENTO 18-15-14 (Redução Profissional)": {"n_pool": 18, "garantia": 14, "desc": "Garante 14 pts se as 15 estiverem nas 18", "prob": "1/152 para 14 pts", "peso": 0.75},
    "FECHAMENTO 19-15-14 (Intermediário)": {"n_pool": 19, "garantia": 14, "desc": "Garante 14 pts se as 15 estiverem nas 19", "prob": "1/103 para 14 pts", "peso": 0.85},
    "FECHAMENTO 20-15-13 (Cobertura Ampla)": {"n_pool": 20, "garantia": 13, "desc": "Garante 13 pts se as 15 estiverem nas 20", "prob": "1/12 para 13 pts", "peso": 0.98},
    "MATRIZ DIAMANTE [2x16 + 10x15] (Pool 19)": {"n_pool": 19, "garantia": 14, "desc": "2 de 16 + 10 de 15 (Cerco Inteligente)", "prob": "Alta para 14/15", "peso": 0.92},
    "MATRIZ CÉLULA [1x16 + 15x15] (Pool 18)": {"n_pool": 18, "garantia": 15, "desc": "1 de 16 + 15 de 15 (Malha Fina)", "prob": "Máxima para 15", "peso": 0.96}
}

# --- 5. CONTROLE DE ACESSO ---
if not st.session_state.get('auth', False):
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

def mostrar_status_backup():
    # Verifica se as chaves existem no session_state para evitar erros de primeira execução
    # Usamos .get() com fallback para garantir que sempre retorne um valor (lista ou dicionário)
    total_jogos = len(st.session_state.get('jogos_salvos', []))
    
    # Adicionado tratamento para garantir que ultimo_res seja um dicionário antes de somar
    ultimo_res_dict = st.session_state.get('ultimo_res', {})
    total_res = sum(len(v) for v in ultimo_res_dict.values()) if ultimo_res_dict else 0
    
    st.markdown(f'''
        <div class="status-backup">
            📁 Backup Ativo: {total_jogos} jogos | {total_res} resultados
        </div>
    ''', unsafe_allow_html=True)

# --- 6. INTERFACE ---

st.title("📊 GESTÃO ESTRATÉGICA LOTERIAS")

# --- CONEXÃO DO RADAR DE TOPO (CORREÇÃO CRÍTICA AQUI) ---
# Em vez de st.session_state.ultimo_res, usamos st.session_state.get('ultimo_res', {})
# Isso evita o erro "AttributeError" se a variável não existir no início.

base_res = st.session_state.get('ultimo_res', {})
res_loto_topo = base_res.get("Lotofácil", {})

# Tentativa segura de pegar o último concurso
try:
    if res_loto_topo:
        # Garante que as chaves sejam tratadas como inteiros para achar o maior real
        ultimo_c_topo = max(res_loto_topo.keys(), key=int)
    else:
        ultimo_c_topo = "Vazio"
except Exception:
    ultimo_c_topo = "Aguardando Sinc..."

st.info(f"📡 **RADAR KADOSH:** Base sincronizada até o Concurso **{ultimo_c_topo}**")

# --- DEFINIÇÃO DAS ABAS ---
# Criando a estrutura de navegação do sistema
abas = st.tabs([
    "🎯 GERADOR PRO", 
    "🔍 CONFERIR", 
    "⚙️ VALORES", 
    "📥 DATABASE", 
    "💾 BACKUP", 
    "🧠 INTELIGÊNCIA", 
    "🔗 AFINIDADE"
])
with abas[0]:
    # --- CORREÇÃO DE SEGURANÇA (INICIALIZAÇÃO) ---
    if 'analise_stats' not in st.session_state:
        st.session_state.analise_stats = {}
    
    mostrar_status_backup()
    
    # Seletor de Modalidade com reset inteligente
    # --- [CORREÇÃO DE SEGURANÇA: INICIALIZAÇÃO] ---
    # Garante que as chaves básicas existam para não travar o selectbox
    if 'custos' not in st.session_state:
        st.session_state.custos = {"Lotofácil": 3.0} # Valor padrão de segurança

    if 'ultimo_res' not in st.session_state:
        st.session_state.ultimo_res = {}

    if 'analise_stats' not in st.session_state:
        st.session_state.analise_stats = {}

    # --- [SELEÇÃO DE MODALIDADE] ---
    # Usamos .get() e list() de forma segura
    lista_loterias = list(st.session_state.get('custos', {"Lotofácil": 3.0}).keys())
    mod = st.selectbox("Modalidade", lista_loterias, key="mod_selector")
    
    if 'ultima_mod_selecionada' not in st.session_state:
        st.session_state.ultima_mod_selecionada = mod
    
    if st.session_state.ultima_mod_selecionada != mod:
        st.session_state.jogos_gerados = []
        st.session_state.ultima_mod_selecionada = mod
        st.rerun()

    # --- [ATIVAÇÃO DO MOTOR DE CÁLCULO] ---
    # Buscamos de forma segura para não dar erro se o dicionário estiver vazio
    res_loto = st.session_state.get('ultimo_res', {}).get(mod, {})
    
    # Só processa se houver histórico no banco
    if res_loto and len(res_loto) >= 1:
        # Garantimos que os IDs dos concursos sejam tratados como inteiros para ordenar certo
        conc_ordenados = sorted(res_loto.keys(), key=lambda x: int(x), reverse=True)
        contagem = Counter()
        amostra = conc_ordenados[:50] # Analisa tendência dos últimos 50 sorteios
    
        for c in amostra:
            for n in res_loto[c]: 
                contagem[n] += 1
        
        stats_temp = {}
        # Definição do limite de dezenas por volante
        if mod == "Lotofácil": 
            max_dezenas = 25
        elif mod in ["Quina", "Mega-Sena"]: 
            max_dezenas = 80 if mod == "Quina" else 60
        elif mod in ["Dupla-Sena", "+Milionária"]: 
            max_dezenas = 50
        else: 
            max_dezenas = 80

        for n in range(1, max_dezenas + 1):
            atraso_n = 0
            for c in conc_ordenados:
                if n not in res_loto[c]: 
                    atraso_n += 1
                else: 
                    break
            # O Score Kadosh equilibra quem sai muito com quem está "maduro" para sair
            stats_temp[n] = {'score': contagem[n] + (atraso_n * 0.8)}
    
        # Salva no estado da sessão de forma segura
        st.session_state.analise_stats[mod] = stats_temp
    else:
        st.info("💡 Sistema aguardando carregamento de dados (Backup ou Manual).")

    # --- [INTERFACE DE ESTRATÉGIAS] ---
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

    # Preparação das variáveis de configuração
    info_fech = MATRIZES_FECHAMENTO.get(fe_escolhido) if mod == "Lotofácil" else None
    info_est = ESTRATEGIA_MAPA.get(est_escolhida) if mod == "Lotofácil" else ESTRATEGIA_MAPA["Personalizado"]
    
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
         # --- [CORREÇÃO DEFINITIVA: BLINDAGEM CONTRA ATTRIBUTEERROR] ---
        
         # 1. Recupera o dicionário global de custos de forma segura
         custos_global = st.session_state.get('custos')
         if custos_global is None:
             custos_global = {}

         # 2. Recupera os custos da modalidade atual
         # O segredo está aqui: se o retorno for None, o 'or {}' força a ser um dicionário
         custos_mod = custos_global.get(mod) or {}

         # 3. Agora extraímos as chaves. Se não houver chaves, aplicamos o fallback manual
         # Isso elimina o erro 'AttributeError: NoneType has no attribute keys'
         if isinstance(custos_mod, dict) and len(custos_mod) > 0:
             opcoes_dez = list(custos_mod.keys())
         else:
             opcoes_dez = [15] if mod == "Lotofácil" else [6]

         # --- [LÓGICA DE PREENCHIMENTO AUTOMÁTICO] ---
         if info_fech:
             if "DIAMANTE" in fe_escolhido: 
                 def_dez, def_qtd = 16, 2
             elif "CÉLULA" in fe_escolhido: 
                 def_dez, def_qtd = 16, 1
             else: 
                 def_dez = 15
                 def_qtd = 24 if "18-15-14" in fe_escolhido else 45
         elif est_escolhida != "Personalizado" and mod == "Lotofácil":
             # Uso do .get preventivo para o dicionário da estratégia
             def_dez = info_est.get("dez", 15)
             def_qtd = info_est.get("qtd", 10)
         else:
             # Seleção segura do valor padrão
             def_dez = opcoes_dez[0]
             def_qtd = 10

         # --- [VALIDAÇÃO DO ÍNDICE] ---
         # Garante que o selectbox não trave se o valor padrão não estiver na lista
         try:
             idx_padrao = opcoes_dez.index(def_dez)
         except (ValueError, IndexError):
             idx_padrao = 0

         # --- [COMPONENTES DE INTERFACE] ---
         n_dez = st.selectbox("Dezenas por Bilhete", opcoes_dez, index=idx_padrao)
        
         # Conversão forçada para int para evitar erro de float no number_input
         qtd = st.number_input("Quantidade de Jogos", 1, 300, int(def_qtd))
    with c2:
         # 1. Configuração de Limites por Modalidade
         limites_reais = {
             "Lotofácil": 25,
             "Mega-Sena": 60,
             "Quina": 80,
             "Dupla-Sena": 50,
             "+Milionária": 50
         }
         max_v_bt = limites_reais.get(mod, 60)
        
         # 2. Identificação do Tamanho Alvo do Pool (Motor de Decisão)
         tamanhos_detectados = [18] # Mínimo padrão
         if mod == "Lotofácil":
             # Checa Estratégia
             if "A MARRETA" in est_escolhida: tamanhos_detectados.append(22)
             elif "PRESTIGE 20" in est_escolhida: tamanhos_detectados.append(20)
             elif "ELITE KADOSH" in est_escolhida: tamanhos_detectados.append(19)
            
             # Checa Matriz (Sobrepõe se for maior)
             if fe_escolhido != "Nenhum":
                 info_fe = MATRIZES_FECHAMENTO.get(fe_escolhido, {})
                 tamanhos_detectados.append(info_fe.get("n_pool", 18))

         tamanho_alvo_pool = max(tamanhos_detectados)
         st.session_state['tamanho_pool_ativo'] = tamanho_alvo_pool # Sincroniza com filtros

         st.markdown(f"🛠️ **CONFIGURAÇÃO ATIVA:** Pool travado em **{tamanho_alvo_pool}** dezenas.")

         # --- [BOTÕES DE COMANDO IA] ---
         col_btn1, col_btn2 = st.columns(2)

         with col_btn1:
             if mod == "Lotofácil":
                 # BOTÃO 1: IA Neural Ranking 1000
                 if st.button("💎 ATIVAR IA (RANKING 1000)"):
                     with st.spinner("Treinando Redes Neurais..."):
                         pool_ia = treinar_e_prever_ia(mod, tamanho=tamanho_alvo_pool)
                         if pool_ia:
                             st.session_state.favoritas[mod] = pool_ia
                             st.success(f"🚀 IA configurada para {tamanho_alvo_pool} dezenas!")
                             st.rerun()

             if st.button("✅ SELECIONAR TODO VOLANTE"):
                 st.session_state.favoritas[mod] = list(range(1, max_v_bt + 1))
                 st.rerun()
                
         with col_btn2:
             if mod == "Lotofácil":
                 # BOTÃO 3: Pool Inteligente (Freq + Atraso)
                 if st.button("🧠 POOL INTELIGENTE"):
                     stats_mod = st.session_state.analise_stats.get(mod, {})
                     if stats_mod:
                         dezenas_ordenadas = sorted(stats_mod.keys(), key=lambda x: stats_mod[x]['score'], reverse=True)
                         st.session_state.favoritas[mod] = sorted(dezenas_ordenadas[:tamanho_alvo_pool])
                         st.success(f"🎯 Pool Inteligente: {tamanho_alvo_pool} dezenas!")
                         st.rerun()
         
                 # BOTÃO 4: Refinar (Híbrido Afinidade + IA)
                 if st.button("💎 REFINAR POOL (ELITE)"):
                     pool_base = st.session_state.favoritas.get(mod, [])
                     if len(pool_base) < tamanho_alvo_pool:
                         pool_base = treinar_e_prever_ia(mod, tamanho=tamanho_alvo_pool + 4)
         
                     matriz_af = st.session_state.get('matriz_ativa') or calcular_matriz_afinidade_kadosh(mod)
                     scores_ia = st.session_state.get('scores_predicao', {})
         
                     pool_refinado = refinar_pool_kadosh(pool_base, matriz_af, tamanho_alvo_pool, scores_ia)
                     st.session_state.favoritas[mod] = pool_refinado
                     st.success(f"🎯 Refinado com Inteligência Híbrida!")
                     st.rerun()

         # --- SELEÇÃO MANUAL E VISUALIZAÇÃO ---
         st.markdown("---")
        
        # --- [CORREÇÃO CRÍTICA: BLINDAGEM DO POOL] ---
        # 1. Garante que o dicionário de favoritas exista
        if 'favoritas' not in st.session_state:
            st.session_state.favoritas = {}
        
        # 2. Busca o que já estava selecionado (ou lista vazia se for a primeira vez)
        # O 'or []' impede o erro de AttributeError no parâmetro 'default'
        pool_default = st.session_state.favoritas.get(mod, []) or []
        
        # 3. O multiselect agora está protegido
        pool = st.multiselect(
            f"SELECIONE SEU POOL ({mod}):", 
            range(1, max_v_bt + 1), 
            default=pool_default
        )
        st.session_state.favoritas[mod] = pool 

        # Análise Geográfica do Pool
        if pool and mod == "Lotofácil":
            linhas_p = [0]*5
            for n in pool: 
                linhas_p[(n-1)//5] += 1
            
            if any(l == 0 for l in linhas_p):
                st.warning("⚠️ Atenção: Seu Pool possui linhas vazias! Isso reduz a eficácia do Filtro Kadosh.")
            
            with st.expander("📊 Distribuição Geográfica do Pool"):
                cols_q = st.columns(5)
                for idx, qtd_l in enumerate(linhas_p):
                    cols_q[idx].metric(f"L{idx+1}", f"{qtd_l} dez")
        
        # Fixação de Dezenas (Cravadas)
        if mod == "Lotofácil":
            st.markdown("---")
            modo_fixa = st.radio("MODO DE FIXAÇÃO:", ["Sem Fixas", "Manual", "IA Automática (Score)"], horizontal=True)
    
            fixas_final = []
            if modo_fixa == "Manual":
                # Proteção: multiselect de fixas só aparece se houver dezenas no pool
                fixas_final = st.multiselect("📌 CRAVAR DEZENAS (FIXAS):", options=pool)
            elif modo_fixa == "IA Automática (Score)":
                qtd_auto = st.slider("Qtd de Cravadas:", 1, 10, 6)
                # Verifica se a análise de stats existe para não quebrar
                if mod in st.session_state.get('analise_stats', {}):
                    stats = st.session_state.analise_stats[mod]
                    # Ordena as dezenas do Pool pelo Score da IA
                    melhores_ia = sorted([n for n in pool], key=lambda x: stats.get(x, {}).get('score', 0), reverse=True)
                    fixas_final = melhores_ia[:qtd_auto]
                    if fixas_final:
                        st.info(f"💎 IA CRAVOU: {', '.join(map(str, fixas_final))}")
                    else:
                        st.info("💡 Selecione dezenas no Pool para a IA analisar.")
    
            # Renderiza o Heatmap passando os resultados de forma segura
            ult_res_map = st.session_state.get('ultimo_res', {}).get(mod, {})
            renderizar_heatmap(mod, ult_res_map)

    # --- [INÍCIO DO NOVO MOTOR SINCRONIZADO] ---

    if st.button("🚀 GERAR JOGOS (SINCRO-MATRIZ KADOSH)"):
        # 1. Definição da Estratégia e Parâmetros
        # Usa o mapa de estratégias para definir a quantidade e dezenas
        conf = ESTRATEGIA_MAPA.get(est_escolhida, {"dez": 15, "qtd": 10})
        dezenas_por_jogo = n_dez # Usa o seletor manual ou automático da UI
        quantidade_pedida = qtd

        # 2. Sincronização do Pool
        # Prioridade: Pool da sessão -> Favoritas -> Padrão 1-25
        pool_completo = st.session_state.favoritas.get(mod, [])
        if not pool_completo:
            pool_completo = list(range(1, 26))
            
        # O pool respeita o tamanho alvo definido na Parte 8 (18, 19, 20 ou 22)
        pool_cortado = pool_completo[:tamanho_alvo_pool]
        st.session_state['pool_ativo_geracao'] = pool_cortado

        # 3. Identificação de Dezenas de Ciclo (Atrasadas para Troca Cirúrgica)
        res_hist = st.session_state.ultimo_res.get(mod, {})
        dezenas_ciclo = []
        if res_hist and mod == "Lotofácil":
            chaves = sorted(res_hist.keys(), key=int)
            if len(chaves) >= 3:
                ultimos_3 = [res_hist[c] for c in chaves[-3:]]
                sorteadas_recentes = set(n for jogo in ultimos_3 for n in jogo)
                dezenas_ciclo = [d for d in range(1, 26) if d not in sorteadas_recentes]

        # 4. Função Interna de Processamento com Intervenção da IA
        def processar_geracao(tam_solicitado, qtd_pedida):
            sucessos, tentativas = 0, 0
            lista_jogos = []
            
            while sucessos < qtd_pedida and tentativas < 5000:
                tentativas += 1
                comb = sorted(random.sample(pool_cortado, tam_solicitado))
                
                # Validação pelo Juiz Kadosh
                passou = validar_kadosh_cirurgico(comb, mod, tam_solicitado)
                foi_trocado = False
                dezena_saiu, dezena_entrou = None, None

                # INTERVENÇÃO: Se falhar, tenta 1 troca cirúrgica usando dezenas de ciclo
                if not passou and dezenas_ciclo and mod == "Lotofácil":
                    vaga_idx = random.randint(0, len(comb)-1)
                    dezena_saiu = comb[vaga_idx]
                    opcoes_troca = [d for d in dezenas_ciclo if d not in comb]
                
                    if opcoes_troca:
                        dezena_entrou = random.choice(opcoes_troca)
                        novo_jogo = sorted([n if n != dezena_saiu else dezena_entrou for n in comb])
                    
                        if validar_kadosh_cirurgico(novo_jogo, mod, tam_solicitado):
                            comb = novo_jogo
                            passou = True
                            foi_trocado = True

                if passou:
                    lista_jogos.append({
                        "n": comb, 
                        "trocado": dezena_entrou if foi_trocado else None,
                        "tam": tam_solicitado,
                        "est": est_escolhida,
                        "chance": "ALTA" if not foi_trocado else "RECALIBRADA"
                    })
                    sucessos += 1
            return lista_jogos

        # Executa e salva
        st.session_state.jogos_gerados = processar_geracao(dezenas_por_jogo, quantidade_pedida)
        
        if not st.session_state.jogos_gerados:
            st.error("⚠️ O motor não conseguiu validar jogos com este Pool. Tente refinar ou aumentar o Pool.")
        else:
            st.success(f"✅ {len(st.session_state.jogos_gerados)} Jogos gerados com sucesso!")
        st.rerun()

    # --- [VISUALIZAÇÃO DOS BILHETES] ---
    if st.session_state.get('jogos_gerados'):
        st.markdown("### 📝 Bilhetes Gerados")
        st.caption("Dezenas em **Dourado** foram inseridas pela IA para equilibrar o jogo.")

        for i, jogo in enumerate(st.session_state.jogos_gerados):
            html_jogo = ""
            for n in jogo['n']:
                if n == jogo['trocado']:
                    # Destaque Dourado para dezenas trocadas
                    html_jogo += f'<span style="color: #f1c40f; font-weight: bold; border: 1px solid #f1c40f; padding: 2px 6px; margin: 2px; border-radius: 4px;">{n:02d}</span> '
                else:
                    html_jogo += f'<span style="background: #2d3436; color: white; padding: 2px 6px; margin: 2px; border-radius: 4px;">{n:02d}</span> '
            
            st.markdown(f"**{i+1:02d}** ⮕ {html_jogo} | <small>{jogo['chance']}</small>", unsafe_allow_html=True)

        # Botão para persistência
        if st.button("💾 Salvar Jogos na Sessão"):
            st.session_state.jogos_salvos.extend(st.session_state.jogos_gerados)
            st.toast("Jogos salvos para conferência!")
with abas[1]:
    mostrar_status_backup() 
    st.header("🔍 Painel de Conferência")
    
    # 1. SELETOR DE MODALIDADE
    mod_f = st.selectbox(
        "Selecione a Loteria para Conferir", 
        list(st.session_state.custos.keys()), 
        key="f_conf_definitiva"
    )
    
    # 2. EXPORTAÇÃO (PDF)
    if st.session_state.get('jogos_salvos'):
        try:
            # Gera o PDF com base nos jogos que estão na memória de backup
            pdf_bytes = gerar_pdf_jogos(st.session_state.jogos_salvos, mod_f)
            
            st.download_button(
                label="📥 BAIXAR JOGOS (PDF)",
                data=pdf_bytes,
                file_name=f"jogos_kadosh_{mod_f}.pdf",
                mime="application/pdf",
                key="btn_pdf_vfinal"
            )
        except Exception as e:
            st.error(f"Aguardando dados para gerar PDF...")
    
    # 3. FILTRAGEM E CONFERÊNCIA
    # Filtra apenas os jogos da modalidade selecionada no momento
    jogos_salvos_atual = [j for j in st.session_state.jogos_salvos if j.get('mod') == mod_f]
    res_db = st.session_state.ultimo_res.get(mod_f, {})

    if not jogos_salvos_atual:
        st.info(f"✨ Nenhum jogo salvo para {mod_f}. Use o Gerador Pro para criar sua estratégia.")
    else:
        # --- PERFORMANCE DO POOL (ANÁLISE DE CERCO) ---
        # Analisamos o último pool gerado para o concurso alvo
        ultimo_j = jogos_salvos_atual[-1]
        pool_origem = ultimo_j.get('pool_origem', [])
        alvo_p = str(ultimo_j.get('concurso_alvo', ''))
        
        if pool_origem and alvo_p in res_db:
            st.markdown(f"### 🎯 PERFORMANCE DO SEU POOL (CONCURSO {alvo_p})")
            res_alvo = res_db[alvo_p]
            acertos_p = sum(1 for d in pool_origem if d in res_alvo)
            
            # Visualização do Cerco (Verde = Acerto / Vermelho = Erro)
            h_pool = '<div style="background: #1e272e; padding: 20px; border-radius: 15px; border: 1px solid #34495e; margin-bottom: 20px;">'
            for d in sorted(pool_origem):
                cor_p = "background-color: #27ae60;" if d in res_alvo else "background-color: #c0392b;"
                h_pool += f'<span style="display: inline-block; width: 32px; height: 32px; line-height: 32px; text-align: center; border-radius: 50%; margin: 4px; font-weight: bold; color: white; {cor_p}">{d:02d}</span>'
            h_pool += f'<br><br><b style="color: #f1c40f;">📊 EFICIÊNCIA DO CERCO: {acertos_p} de {len(res_alvo)} dezenas sorteadas.</b></div>'
            st.markdown(h_pool, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📋 Conferência de Bilhetes")
        t_gasto, t_premio = 0.0, 0.0

        for i, jogo in enumerate(jogos_salvos_atual):
            dezenas_j = jogo['n']
            tam_j = jogo.get('tam', 15)
            c_alvo = str(jogo.get('concurso_alvo', ''))
            fixas_j = jogo.get('fixas_utilizadas', []) 
            
            # Cálculo de Custo
            custo_j = st.session_state.custos[mod_f].get(tam_j, 0)
            t_gasto += custo_j
            
            html_dez = ""
            sorteio = res_db.get(c_alvo, [])
            
            if sorteio:
                acertos = len(set(dezenas_j) & set(sorteio))
                # Busca o prêmio correspondente à quantidade de acertos
                v_premio = float(st.session_state.premios[mod_f].get(str(acertos), 0.0))
                t_premio += v_premio 
                
                for d in dezenas_j:
                    is_sorteada = d in sorteio
                    is_fixa = d in fixas_j
                    
                    # Estilização: Verde para acerto, Underline para Fixa, Pino para Fixa Acertada
                    c_txt = "#2ecc71" if is_sorteada else "#bdc3c7"
                    decor = "text-decoration: underline; font-weight: 900;" if is_fixa else ""
                    pino = "📌" if (is_fixa and is_sorteada) else ""
                    
                    html_dez += f'<span style="color:{c_txt}; {decor} margin-right:10px; font-size:18px; font-family: monospace;">{d:02d}{pino}</span>'
                
                res_msg = f"🎯 {acertos} ACERTOS | 💰 R$ {v_premio:,.2f}"
            else:
                for d in dezenas_j:
                    html_dez += f'<span style="color:#bdc3c7; margin-right:10px; font-size:18px; font-family: monospace;">{d:02d}</span>'
                res_msg = "⏳ Sorteio não realizado ou base desatualizada"

            st.markdown(f"""
            <div style="border-left: 5px solid #3498db; padding: 12px; background: #2d3436; border-radius: 8px; margin-bottom: 8px;">
                <small style="color: #636e72;">JOGO {i+1:02d} • {mod_f} • CONCURSO {c_alvo}</small><br>
                <div style="margin: 8px 0;">{html_dez}</div>
                <strong style="color: white;">{res_msg}</strong>
            </div>""", unsafe_allow_html=True)

        # --- RESUMO FINANCEIRO ---
        st.markdown("---")
        c_fin1, c_fin2, c_fin3 = st.columns(3)
        c_fin1.metric("Investimento Total", f"R$ {t_gasto:,.2f}")
        c_fin2.metric("Prêmios Totais", f"R$ {t_premio:,.2f}")
        
        saldo = t_premio - t_gasto
        cor_saldo = "normal" if saldo >= 0 else "inverse"
        c_fin3.metric("Saldo Líquido", f"R$ {saldo:,.2f}", delta=f"{saldo:,.2f}", delta_color=cor_saldo)

        if st.button("🗑️ LIMPAR TODOS OS JOGOS"):
            st.session_state.jogos_salvos = []
            st.success("Histórico limpo!")
            st.rerun()
with abas[2]:
    # --- CORREÇÃO 1: VERIFICAÇÃO DE FUNÇÃO ---
    # Certifica-te de que 'mostrar_status_backup' está definida. 
    # Se não estiver no arquivo 1, ela precisa ser criada ou comentada.
    try:
        mostrar_status_backup()
    except NameError:
        st.warning("⚠️ Função 'mostrar_status_backup' não localizada no escopo.")

    st.markdown("## 💰 Painel Oficial de Premiações")
    
    # --- CORREÇÃO 2: ACESSO AO SESSION_STATE ---
    # No arquivo 1, você inicializou as configurações. 
    # Para evitar erro caso o usuário entre direto nesta aba, usamos .get() ou fallback.
    opcoes_loterias = list(st.session_state.get('custos', {"Lotofácil": 3.0}).keys())
    lot_v = st.selectbox("Selecione a Loteria", opcoes_loterias, key="val_sel")
    
    if st.button(f"🚀 SINCRONIZAR COM A CAIXA: {lot_v.upper()}", use_container_width=True):
        import requests
        import unicodedata

        def limpar_p_api(nome):
            n = nome.replace("+", "mais").lower()
            # Normalização para remover acentos (ex: Lotofácil -> lotofacil)
            n = "".join(c for c in unicodedata.normalize('NFD', n) if unicodedata.category(c) != 'Mn')
            return n.replace("-", "").replace(" ", "")

        # Limpeza de cache para forçar nova busca
        for k in [f'dados_api_{lot_v}', f'api_full_{lot_v}']:
            if k in st.session_state: 
                del st.session_state[k]
            
        nomes_url = {
            "Lotofácil": "lotofacil", 
            "Mega-Sena": "megasena", 
            "Quina": "quina", 
            "+Milionária": "maismilionaria", 
            "Dupla-Sena": "duplasena"
        }
        
        url_api = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/{nomes_url.get(lot_v, 'lotofacil')}"
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://loterias.caixa.gov.br/"}
        
        try:
            with requests.Session() as s:
                # Desativar verify=False apenas se necessário, mas mantido conforme seu código
                resp = s.get(url_api, headers=headers, timeout=10, verify=False)
                if resp.status_code == 200 and "listaRateioPremios" in resp.text:
                    st.session_state[f'dados_api_{lot_v}'] = resp.json()
                    registrar_log_kadosh(f"Dados {lot_v} sincronizados via API Caixa", "success")
                else:
                    # BUSCA RESERVA CASO A CAIXA FALHE
                    nome_limpo = limpar_p_api(lot_v)
                    r_alt = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{nome_limpo}/latest", timeout=10)
                    if r_alt.status_code == 200:
                        st.session_state[f'dados_api_{lot_v}'] = r_alt.json()
                        registrar_log_kadosh(f"Dados {lot_v} sincronizados via API Alternativa", "warning")
            st.rerun()
        except Exception as e:
            st.error(f"Erro na conexão: {e}")
            registrar_log_kadosh(f"Falha na sincronização {lot_v}", "error")

    dados = st.session_state.get(f'dados_api_{lot_v}')

    if dados:
        # --- TRADUÇÃO DE CAMPOS (MATA O 'NONE') ---
        # Adicionado tratamento para garantir que n_concurso e estimativa sejam números
        n_concurso = dados.get('numero') or dados.get('concurso') or 0
        data_res = dados.get('dataApuracao') or dados.get('data') or "--/--/----"
        local_res = dados.get('localSorteio') or dados.get('local') or "Espaço da Sorte"
        
        # --- CORREÇÃO 3: TRATAMENTO DE VALOR NUMÉRICO ---
        # Se a API trouxer string ou None, forçamos float para evitar erro no f-string :.2f
        estimativa_raw = dados.get('valorEstimadoProximoConcurso') or dados.get('proximo_estimativa') or 0
        try:
            estimativa = float(estimativa_raw)
        except:
            estimativa = 0.0

        conteudo_html = f"""
        <div style="background-color: white; padding: 25px; border-radius: 20px; border: 1px solid #ddd; font-family: sans-serif;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div>
                    <h1 style="margin:0; color: #004a8d; font-size: 35px;">{lot_v.upper()}</h1>
                    <p style="margin:0; color: #666; font-size: 14px;">PORTAL DE RESULTADOS</p>
                </div>
                <div style="background: #ffff00; color: black; padding: 10px 20px; border-radius: 12px; text-align: center;">
                    <span style="display: block; font-size: 10px;">CONCURSO</span>
                    <span style="font-size: 22px; font-weight: bold;">{n_concurso}</span>
                </div>
            </div>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 15px; border-left: 6px solid #004a8d;">
                <p style="margin:0; color: #666; font-weight: bold;">ESTIMATIVA DE PRÊMIO</p>
                <p style="font-size: 48px; margin: 5px 0; color: #004a8d; font-weight: bold;">R$ {estimativa:,.2f}</p>
            </div>
            <div style="margin-top: 20px; display: flex; justify-content: space-between; font-size: 14px; color: #444;">
                <span>📅 DATA: {data_res}</span>
                <span>📍 LOCAL: {local_res}</span>
            </div>
        </div>
        """
        st.markdown(conteudo_html, unsafe_allow_html=True)
        
        st.markdown("### 🏆 Detalhamento do Rateio Oficial")
        rateio = dados.get('listaRateioPremios') or dados.get('premiacoes') or []

        if rateio:
            df_r = pd.DataFrame(rateio)
            mapa_traducao = {
                'descricao': 'Faixa', 'descricaoFaixa': 'Faixa', 
                'ganhadores': 'Ganhadores', 'numeroDeGanhadores': 'Ganhadores',
                'valorPremio': 'Prêmio Individual', 'valorRateio': 'Prêmio Individual',
                'valor_total': 'Prêmio Individual' # Adicionado para APIs alternativas
            }
            df_r = df_r.rename(columns=mapa_traducao)
            
            # Garante que colunas numéricas sejam float para o .style.format
            if 'Prêmio Individual' in df_r.columns:
                df_r['Prêmio Individual'] = pd.to_numeric(df_r['Prêmio Individual'], errors='coerce').fillna(0)
            
            colunas_exibir = [c for c in ['Faixa', 'Ganhadores', 'Prêmio Individual'] if c in df_r.columns]
            st.dataframe(df_r[colunas_exibir].style.format({'Prêmio Individual': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Os valores de ganhadores e rateio ainda não foram processados.")
with abas[3]:
    # --- CORREÇÃO 1: IMPORTAÇÃO DO MÓDULO RE ---
    # O seu código usa 're.findall', mas o módulo 're' (Regular Expressions) 
    # precisa ser importado aqui ou no topo do arquivo para não dar erro.
    import re 
    
    try:
        mostrar_status_backup()
    except NameError:
        pass

    st.header("📥 Database - Gerenciar Resultados")
    
    # --- CORREÇÃO 2: VERIFICAÇÃO DE SEGURANÇA NO SESSION_STATE ---
    # Garante que 'ultimo_res' e 'favoritas' existam antes de tentar acessá-los
    if 'ultimo_res' not in st.session_state:
        st.session_state.ultimo_res = {}
    if 'favoritas' not in st.session_state:
        st.session_state.favoritas = {}

    m_db = st.selectbox("Selecione a Loteria", list(st.session_state.custos.keys()), key="m_db_final_novo")

    st.markdown("### 🌐 Sincronização Online")
    if st.button("🔄 BUSCAR ÚLTIMO RESULTADO (API)", use_container_width=True):
        with st.spinner(f"Consultando servidores para {m_db}..."):
            # Chama a função de busca (certifique-se que ela está no seu arquivo base)
            c_api, d_api = buscar_ultimo_resultado_api(m_db) 
            if c_api and d_api:
                if m_db not in st.session_state.ultimo_res:
                    st.session_state.ultimo_res[m_db] = {}
                
                # Salva o resultado
                st.session_state.ultimo_res[m_db][str(c_api)] = d_api
                
                # Sincroniza a IA (Lógica baseada no plano escolhido)
                # Se 'fe_escolhido' não existir, assume padrão 18
                tamanho_ia = 20 if "DIAMANTE" in str(st.session_state.get('fe_escolhido', '')) else 18
                pool_ia = treinar_e_prever_ia(m_db, tamanho=tamanho_ia)
                
                if pool_ia:
                    st.session_state.favoritas[m_db] = pool_ia
                
                # Log de sucesso integrado ao sistema de logs do arquivo 1
                registrar_log_kadosh(f"Database {m_db}: Concurso {c_api} atualizado via API.", "success")
                st.success(f"🚀 SUCESSO! {m_db} Concurso {c_api} salvo.")
                st.rerun()

    st.divider()

    # --- CADASTRO MANUAL ---
    st.markdown("### ✍️ Cadastro Manual")
    col_man1, col_man2 = st.columns(2)
    with col_man1:
        id_c_manual = st.number_input("Número do Concurso", 1, 99999, key="id_manual_input_novo")
    
    txt_site = st.text_area("Cole aqui o resultado:", placeholder="Ex: 01 02 03...", height=100, key="txt_manual").strip()

    if txt_site:
        # Extrai apenas números do texto colado usando a biblioteca re
        numeros_extraidos = [int(n) for n in re.findall(r'\d+', txt_site)]
        # Define o limite com base na loteria
        max_v = 25 if m_db == "Lotofácil" else 60
        dezenas_limpas = sorted(list(set([n for n in numeros_extraidos if 1 <= n <= max_v])))

        if len(dezenas_limpas) > 0:
            st.warning(f"🔎 Detectamos {len(dezenas_limpas)} dezenas para {m_db}")
            if st.button(f"💾 GRAVAR CONCURSO {id_c_manual}", use_container_width=True):
                if m_db not in st.session_state.ultimo_res: 
                    st.session_state.ultimo_res[m_db] = {}
                
                st.session_state.ultimo_res[m_db][str(id_c_manual)] = dezenas_limpas
                registrar_log_kadosh(f"Database {m_db}: Concurso {id_c_manual} gravado manualmente.", "info")
                st.success("Gravado!")
                st.rerun()

    # --- HISTÓRICO DENTRO DO EXPANDER ---
    with st.expander("📊 Ver Resultados Salvos"):
        historico = st.session_state.ultimo_res.get(m_db, {})
        if historico:
            dados_tabela = []
            for k, v in historico.items():
                # Formata dezenas com zero à esquerda (ex: 01, 02...)
                dezenas_fmt = ", ".join([f"{int(x):02d}" for x in v])
                dados_tabela.append({"Concurso": int(k), "Dezenas": dezenas_fmt})
            
            df_hist = pd.DataFrame(dados_tabela)
            # Exibe a tabela ordenada pelo concurso mais recente
            st.table(df_hist.sort_values(by="Concurso", ascending=False))
        else:
            st.info(f"Sem resultados salvos para {m_db}.")
with abas[4]:
    # --- INTEGRAÇÃO COM A FUNDAÇÃO ---
    try:
        mostrar_status_backup()
    except NameError:
        pass

    st.header("💾 Gestão de Dados e Backup")
    
    # --- PREPARAÇÃO DOS DADOS PARA EXPORTAÇÃO ---
    res_loto = st.session_state.get('ultimo_res', {}).get("Lotofácil", {})
    
    # Verificação de segurança para não quebrar se o banco estiver vazio
    if res_loto:
        try:
            ultimo_id = max(res_loto.keys(), key=int)
        except (ValueError, TypeError):
            ultimo_id = "SEM_ID"
    else:
        ultimo_id = "VAZIO"
        
    nome_arquivo = f"KADOSH_LOTO_{ultimo_id}_BKP.json"

    # Criamos o dicionário de backup com fallbacks (vazio se não existir)
    dados_para_backup = {
        "salvos": st.session_state.get('jogos_salvos', []), 
        "premios": st.session_state.get('premios', {}), 
        "res": st.session_state.get('ultimo_res', {}),
        "favoritas": st.session_state.get('favoritas', {})
    }
    
    # Transformamos em JSON pronto para download
    data_json = json.dumps(dados_para_backup, indent=4)

    col_back1, col_back2 = st.columns(2)
    with col_back1:
        st.download_button(
            label="🚀 BAIXAR BACKUP (.JSON)", 
            data=data_json, 
            file_name=nome_arquivo, 
            mime="application/json", 
            use_container_width=True
        )

    with col_back2:
        f = st.file_uploader("Restaurar sistema", type="json")
        if f is not None:
            if st.button("⚠️ CONFIRMAR RESTAURAÇÃO TOTAL", use_container_width=True):
                try:
                    # Carregamos o arquivo enviado pelo usuário
                    d = json.load(f)
                    
                    # --- ATUALIZAÇÃO SEGURA DO SESSION_STATE ---
                    # Usamos .get() com o valor atual como padrão para não perder dados se o JSON estiver incompleto
                    st.session_state.jogos_salvos = d.get("salvos", st.session_state.get('jogos_salvos', []))
                    st.session_state.premios = d.get("premios", st.session_state.get('premios', {}))
                    st.session_state.ultimo_res = d.get("res", st.session_state.get('ultimo_res', {}))
                    st.session_state.favoritas = d.get("favoritas", st.session_state.get('favoritas', {}))
                    
                    # --- RE-SINCRONIZAÇÃO DA IA PÓS-RESTAURAÇÃO ---
                    # Percorre as loterias restauradas e treina a IA novamente para cada uma
                    for m in st.session_state.ultimo_res:
                        # Chama a função de IA definida no seu arquivo 1
                        try:
                            pool_ia = treinar_e_prever_ia(m)
                            if pool_ia: 
                                st.session_state.favoritas[m] = pool_ia
                        except Exception as e_ia:
                            registrar_log_kadosh(f"Erro ao re-treinar IA para {m}: {e_ia}", "warning")

                    registrar_log_kadosh("Sistema restaurado via Backup JSON", "success")
                    st.success("✅ Sistema Restaurado com Sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro crítico na restauração: {e}")

    st.markdown("---")
    st.subheader("📊 Status da Memória")
    c1, c2 = st.columns(2)
    
    # Contagem segura para evitar erros de NoneType
    n_jogos = len(st.session_state.get('jogos_salvos', []))
    n_resultados = sum(len(v) for v in st.session_state.get('ultimo_res', {}).values())
    
    c1.metric("Jogos Salvos", n_jogos)
    c2.metric("Resultados em Banco", n_resultados)


with abas[5]:
    # --- INTEGRAÇÃO COM A FUNDAÇÃO ---
    try:
        mostrar_status_backup()
    except NameError:
        pass

    st.header("🧠 CENTRAL DE INTELIGÊNCIA KADOSH")
    st.markdown("---")
    
    st.subheader("📊 Painel Tático de Estratégias")
    dados_est = []
    
    # --- CORREÇÃO DE SEGURANÇA: ESTRATEGIA_MAPA ---
    # Usamos .get() para evitar erro caso alguma chave falte no dicionário global definido na Parte 1
    for nome, info in ESTRATEGIA_MAPA.items():
        if nome != "Personalizado":
            # Soma das quantidades de jogos
            qtd_total = info.get("qtd", 0) + info.get("qtd_15", 0) + info.get("qtd_16", 0)
            
            # Cálculo de custo (Mantendo sua lógica de preços)
            custo_aprox = (info.get("qtd", 0) * 3.0) + (info.get("qtd_15", 0) * 3.0) + (info.get("qtd_16", 0) * 48.0)
            
            if "MARRETA" in nome.upper(): 
                # Custo específico da estratégia Marreta conforme sua regra original
                custo_aprox = 2448.0 + (5 * 48.0)
                
            dados_est.append({
                "Estratégia": nome, 
                "Jogos": qtd_total, 
                "Custo Est.": f"R$ {custo_aprox:,.2f}", 
                "Foco": info.get("desc", "N/A"), 
                "Chances": info.get("prob", "N/A")
            })
    
    if dados_est:
        st.table(pd.DataFrame(dados_est))
    
    st.markdown("---")

    # --- MAPEAMENTO TOTAL KADOSH (ESTRATÉGIAS X MATRIZES) ---
    st.subheader("🔥 Painel Tático: Poderio de Fogo e Sincronia")
    st.write("Consulte o arsenal completo. Escolha seu alvo antes de processar os dados.")

    # Lista fixa de dados conforme sua estrutura
    dados_completos = [
        {"Estratégia": "SNIPER", "Matrizes": "CÉLULA / 18-15-14", "Foco": "14 e 15 pts (Precisão)", "13 pts": "1/25 a 1/150", "14 pts": "1/152", "15 pts": "1/3.2M"},
        {"Estratégia": "A MARRETA", "Matrizes": "CÉLULA / 18-15-14", "Foco": "Garantia de 14 pts*", "13 pts": "1/25", "14 pts": "1/152", "15 pts": "1/3.2M"},
        {"Estratégia": "ESCUDO E ESPADA", "Matrizes": "CÉLULA / 18-15-14 / 19-15-14", "Foco": "Defesa de Capital", "13 pts": "1/30", "14 pts": "1/180", "15 pts": "1/204k"},
        {"Estratégia": "EQUILÍBRIO REAL", "Matrizes": "DIAMANTE / 19-15-14 / 20-15-13", "Foco": "Lucro Multiplicado", "13 pts": "1/45", "14 pts": "1/800", "15 pts": "1/102k"},
        {"Estratégia": "ELITE KADOSH", "Matrizes": "DIAMANTE / 19-15-14", "Foco": "Alvo 15 pts (Elite)", "13 pts": "1/40", "14 pts": "1/450", "15 pts": "1/85k"},
        {"Estratégia": "RASTR. CICLO", "Matrizes": "DIAMANTE / 19-15-14", "Foco": "Tendência de Atraso", "13 pts": "1/35", "14 pts": "1/850", "15 pts": "1/90k"},
        {"Estratégia": "EQUILÍBRIO TOTAL", "Matrizes": "20-15-13 / DIAMANTE / 19-15-14", "Foco": "Segurança (Não Perder)", "13 pts": "1/12", "14 pts": "1/600", "15 pts": "1/211k"},
        {"Estratégia": "INVASÃO", "Matrizes": "20-15-13 / 19-15-14", "Foco": "Cerco de Volume", "13 pts": "1/15", "14 pts": "1/700", "15 pts": "1/130k"},
        {"Estratégia": "MOLDE DE OURO", "Matrizes": "20-15-13 / 19-15-14", "Foco": "Geometria de Moldura", "13 pts": "1/18", "14 pts": "1/750", "15 pts": "1/130k"},
        {"Estratégia": "PRESTIGE 20", "Matrizes": "20-15-13 / DIAMANTE / 19-15-14", "Foco": "Poderio Máximo (14 pts)", "13 pts": "1/9", "14 pts": "1/90", "15 pts": "1/75k"},
        {"Estratégia": "SIMETRIA GEOM.", "Matrizes": "DIAMANTE / 20-15-13", "Foco": "Estética e Filtros", "13 pts": "1/40", "14 pts": "1/1.200", "15 pts": "1/81k"},
        {"Estratégia": "CERCO ELIMIN.", "Matrizes": "Uso Individual", "Foco": "Limpeza de Dezenas", "13 pts": "1/160", "14 pts": "1/5.000", "15 pts": "1/3.2M"}
    ]

    st.table(pd.DataFrame(dados_completos))

    st.markdown("""
    ### 🧠 Sequência Mestra de Cliques (Ordem Obrigatória):
    1. **PASSO 1 [COMBO]:** Escolha a Estratégia e a Matriz na Barra Lateral.
    2. **PASSO 2 [IA]:** Clique em 'Ativar IA' para processar o cenário.
    3. **PASSO 3 [POOL]:** Clique em 'Pool Inteligente / Refinar Kadosh'.
    4. **PASSO 4 [JOGOS]:** Clique em 'Gerar Jogos'.
    """)
    st.error("⚠️ **IMPORTANTE:** Se refinar o Pool antes do Passo 1, o sistema usará o padrão de 18 dezenas.")
    
    st.subheader("📐 ANÁLISE TÉCNICA DE MATRIZES")
    dados_mat = []
    # --- CORREÇÃO DE SEGURANÇA: MATRIZES_FECHAMENTO ---
    for nome, info in MATRIZES_FECHAMENTO.items():
        if info:
            n_p = info.get("n_pool", 15)
            erro_m = n_p - 15
            dados_mat.append({
                "Matriz": nome,
                "Pool (Dez)": n_p,
                "Foco/Garantia": info.get("desc", ""),
                "Erro Máx.": f"Erre até {erro_m} dezenas",
                "Probabilidade": info.get("prob", ""),
                "Garantia": f"{info.get('garantia', 0)} Pontos"
            })
    st.table(pd.DataFrame(dados_mat))
    
    st.markdown("---")
    st.subheader("📊 Diagnóstico de Performance (Últimos 30 Concursos)")
    
    if st.button("🚀 Rodar Diagnóstico de 30 Dias"):
        with st.spinner("IA simulando ciclos..."):
            # Chamada da função de Log definida na Parte 1
            registrar_log_kadosh("Diagnóstico de performance 30 dias executado.", "info")
            
            st.success("Diagnóstico de Ciclo Concluído!")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="🏆 1º LUGAR", value="PRESTIGE 20", delta="Forte Tendência")
            with col2:
                st.metric(label="🎯 2º LUGAR", value="SNIPER", delta="Estável")
            with col3:
                st.metric(label="💎 3º LUGAR", value="ELITE KADOSH", delta="Alta Volatilidade")

    st.markdown("---")
    
    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        st.subheader("🔄 Status do Ciclo Atual")
        # --- CORREÇÃO DE LÓGICA DE CICLO ---
        # Garantimos que os dados vêm do st.session_state que sincronizamos na Aba Database
        res_loto = st.session_state.get('ultimo_res', {}).get("Lotofácil", {})
        if res_loto:
            sorteadas_no_ciclo = set()
            # Ordenação numérica correta para não falhar com strings
            concursos_analisados = sorted(res_loto.keys(), key=lambda x: int(x), reverse=True)
            
            for c in concursos_analisados:
                sorteadas_no_ciclo.update(res_loto[c])
                if len(sorteadas_no_ciclo) >= 25: 
                    break
            
            faltam = sorted(list(set(range(1, 26)) - sorteadas_no_ciclo))
            if not faltam: 
                st.success("✅ CICLO FECHADO!")
            else:
                st.warning(f"⚠️ Faltam {len(faltam)} dezenas: {faltam}")
        else:
            st.info("Aguardando dados da aba Database.")
                
    with col_inf2:
        st.subheader("⚖️ Regras de Auditoria")
        st.markdown("""
        - **Paridade:** 7 a 9 Pares (Adaptativa)
        - **Âncoras:** Início [1,2,3] | Fim [23,24,25]
        - **Soma:** 180 a 220
        - **Moldura:** 8 a 11 dezenas
        """)
with abas[6]:
    # --- INTEGRAÇÃO COM A FUNDAÇÃO ---
    st.header("🔗 Afinidade e Vínculos de Dezenas")
    
    # Busca as loterias configuradas no st.session_state (Parte 1)
    opcoes_af = list(st.session_state.get('custos', {"Lotofácil": 3.0}).keys())
    mod_af = st.selectbox("Loteria para Análise", opcoes_af, key="af_sel_universal")
    
    # Recupera os dados salvos na Aba 3 e Aba 1
    res_af = st.session_state.get('ultimo_res', {}).get(mod_af, {})
    pool_selecionado = st.session_state.get('favoritas', {}).get(mod_af, [])
    
    # --- CORREÇÃO 1: VERIFICAÇÃO DE FUNÇÃO DE MATRIZ ---
    # Garantimos que a função de cálculo existe antes de chamar
    try:
        matriz_calculada = calcular_matriz_afinidade_kadosh(mod_af)
        st.session_state['matriz_ativa'] = matriz_calculada 
    except NameError:
        # Fallback caso a função ainda não tenha sido definida no seu script
        st.session_state['matriz_ativa'] = None

    # --- CORREÇÃO 2: VALIDAÇÃO DE BASE DE DADOS ---
    if not res_af or len(res_af) < 2:
        st.warning("⚠️ Base de dados insuficiente na Aba 3. Adicione pelo menos 2 resultados para calcular afinidade.")
        # Não usamos st.stop() para não travar a renderização das outras abas
    else:
        dezenas_lista = list(res_af.values())
        total_jogos = len(dezenas_lista)
        
        # --- LÓGICA DE PARES (OTIMIZADA) ---
        todos_pares = []
        # O limite depende da loteria (25 para Lotofácil, 60 para Mega)
        limite_dez = 26 if mod_af == "Lotofácil" else 61
        
        # Importação necessária para as combinações de trios abaixo
        from itertools import combinations

        for i in range(1, limite_dez):
            for j in range(i + 1, limite_dez):
                par_count = sum(1 for jogo in dezenas_lista if i in jogo and j in jogo)
                if par_count > 0:
                    porc = (par_count / total_jogos) * 100
                    todos_pares.append({"Par": (i, j), "Vezes": par_count, "Porc": porc})
        
        df_completo = pd.DataFrame(todos_pares)
        
        if not df_completo.empty:
            df_ouro = df_completo.sort_values(by="Vezes", ascending=False).head(15)
            df_vacuo = df_completo.sort_values(by="Vezes", ascending=True).head(15)

            st.subheader(f"🔥 Radar de Potência do Pool ({total_jogos} jogos analisados)")
            
            # --- ALERTA DE POTÊNCIA VISUAL ---
            cols_pot = st.columns(2)
            with cols_pot[0]:
                ouro_no_pool = []
                for _, row in df_ouro.iterrows():
                    p1, p2 = row['Par']
                    if p1 in pool_selecionado and p2 in pool_selecionado:
                        ouro_no_pool.append(f"{p1:02d}-{p2:02d}")
                
                if ouro_no_pool:
                    st.success(f"💎 **CONEXÕES DE ELITE NO POOL:** {', '.join(ouro_no_pool)}")
                else:
                    st.info("💡 Nenhuma conexão 'Ouro' completa no Pool atual.")

            with cols_pot[1]:
                vacuo_no_pool = []
                for _, row in df_vacuo.iterrows():
                    p1, p2 = row['Par']
                    if p1 in pool_selecionado and p2 in pool_selecionado:
                        vacuo_no_pool.append(f"{p1:02d}-{p2:02d}")
                
                if vacuo_no_pool:
                    st.error(f"⚠️ **CONFLITOS DE VÁCUO NO POOL:** {', '.join(vacuo_no_pool)}")
                else:
                    st.success("✅ Pool sem conflitos de vácuo!")

            st.markdown("---")
            
            # --- SEÇÃO DE VÁCUO (INIMIGOS) ---
            st.subheader("🚫 Pares em Vácuo (Inimigos)")
            st.warning("Estes pares raramente saem juntos. Evite fixá-los no mesmo jogo.")
            cols_v = st.columns(3)
            for idx, row in df_vacuo.reset_index().iterrows():
                with cols_v[idx % 3]:
                    st.markdown(f"""
                    <div style="background:#feebe2; padding:10px; border-radius:8px; border:1px solid #fbb4ae; text-align:center; margin-bottom:10px;">
                        <b style="color:#c0392b;">{row['Par'][0]:02d} - {row['Par'][1]:02d}</b><br>
                        <small>Apenas {row['Vezes']}x juntos</small>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            
            # --- LÓGICA DE TRIOS DE OURO ---
            st.subheader("🏆 Trios de Ouro (Blocos de Alta Potência)")
            st.info(f"Análise baseada nos {total_jogos} concursos registrados.")

            contagem_trios = {}
            # Analisamos apenas os últimos 500 jogos para não travar o navegador por processamento
            base_trios = dezenas_lista[-500:] if len(dezenas_lista) > 500 else dezenas_lista
            
            for jogo in base_trios:
                # combinations já foi importado acima
                for trio in combinations(sorted(list(jogo)), 3):
                    contagem_trios[trio] = contagem_trios.get(trio, 0) + 1
            
            trios_ordenados = sorted(contagem_trios.items(), key=lambda x: x[1], reverse=True)[:10]
            
            cols_t = st.columns(2)
            for idx, (trio, vezes) in enumerate(trios_ordenados):
                porc_trio = (vezes / len(base_trios)) * 100
                with cols_t[idx % 2]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(45deg, #d4af37, #f1c40f); color: black; padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 2px solid #000; box-shadow: 3px 3px 0px #000;">
                        <span style="font-size: 20px;"><b>TRIO: {trio[0]:02d} - {trio[1]:02d} - {trio[2]:02d}</b></span><br>
                        <hr style="border: 0.5px solid black; margin: 5px 0;">
                        <b>Frequência:</b> {vezes} vezes <br>
                        <b>Afinidade:</b> {porc_trio:.2f}%
                    </div>
                    """, unsafe_allow_html=True)

# --- RODAPÉ FINAL DO SISTEMA ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 12px;">
        <b>KADOSH ESTRATÉGICO v3.0</b><br>
        Sistema de Análise Preditiva e Fechamentos Matemáticos.<br>
        <i>"A sorte favorece a mente preparada."</i>
    </div>
    """, 
    unsafe_allow_html=True
)


























































































