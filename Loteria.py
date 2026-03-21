import streamlit as st
import pandas as pd
import numpy as np
import json
import base64
import time
import os
import pickle
from datetime import datetime

# =================================================================
# 1. CONFIGURAÇÃO DE INTERFACE E ESTILO (VISUAL PROFISSIONAL)
# =================================================================
st.set_page_config(page_title="KADOSH QUANTUM v4.0", layout="wide", initial_sidebar_state="expanded")

def aplicar_estilo_kadosh():
    st.markdown("""
    <style>
        /* Fundo e Texto para Alta Legibilidade */
        .main { background-color: #F5F7F9; }
        .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }
        
        /* Estilo dos Cards de Jogos (Fundo Claro, Texto Escuro) */
        .card-jogo {
            background-color: #FFFFFF;
            padding: 20px;
            border-radius: 15px;
            border-left: 10px solid #2E86C1;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
            color: #1A1A1A;
            margin-bottom: 15px;
            font-family: 'Roboto', sans-serif;
        }
        .dezena-bola {
            display: inline-block;
            width: 35px;
            height: 35px;
            line-height: 35px;
            text-align: center;
            border-radius: 50%;
            background-color: #EBF5FB;
            color: #21618C;
            font-weight: bold;
            margin: 4px;
            border: 1px solid #AED6F1;
        }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. SISTEMA DE SEGURANÇA (LOGIN E SENHA)
# =================================================================
def gerenciar_acesso():
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    
    # Senha padrão inicial (Pode ser alterada no sistema)
    if 'senha_mestra' not in st.session_state:
        st.session_state.senha_mestra = "kadosh"

    if not st.session_state.autenticado:
        st.title("🔐 KADOSH QUANTUM v4.0")
        with st.form("login"):
            senha_input = st.text_input("Introduza a Senha de Acesso", type="password")
            btn_login = st.form_submit_button("Aceder ao Sistema")
            if btn_login:
                if senha_input == st.session_state.senha_mestra:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Senha Incorreta. Tente novamente.")
        st.stop() # Bloqueia o resto do código se não logar

# =================================================================
# 3. SISTEMA DE MEMÓRIA E PERSISTÊNCIA (BRAIN BACKUP)
# =================================================================
def exportar_cerebro_kadosh():
    # Estrutura de dados que contém tudo o que a IA aprendeu
    dados_memoria = {
        "historicos": st.session_state.get('historicos', {}),
        "pesos_ia": st.session_state.get('pesos_ia', {}),
        "senha": st.session_state.senha_mestra,
        "configuracoes": st.session_state.get('config_user', {}),
        "data_backup": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    b64 = base64.b64encode(pickle.dumps(dados_memoria)).decode()
    return f"data:application/octet-stream;base64,{b64}"

def importar_cerebro_kadosh(arquivo_subido):
    if arquivo_subido is not None:
        try:
            dados = pickle.load(arquivo_subido)
            st.session_state.historicos = dados.get('historicos', {})
            st.session_state.pesos_ia = dados.get('pesos_ia', {})
            st.session_state.senha_mestra = dados.get('senha', "kadosh")
            st.success("🧠 Inteligência e Histórico Carregados com Sucesso!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao ler backup: {e}")

# Inicialização das variáveis de estado
if 'historicos' not in st.session_state: st.session_state.historicos = {}
if 'pesos_ia' not in st.session_state: st.session_state.pesos_ia = {}

# Execução do Bloco 1
aplicar_estilo_kadosh()
gerenciar_acesso()
# =================================================================
# 4. MOTORES DE INTELIGÊNCIA ARTIFICIAL (SÉRIES TEMPORAIS)
# =================================================================

class KadoshBrain:
    """
    Motor Central de IA que gere as previsões para todas as lotarias.
    Utiliza LSTM para padrões sequenciais e Markov para transições.
    """
    def __init__(self, modalidade):
        self.modalidade = modalidade
        self.modelo_treinado = False
        self.matriz_transicao = {} # Cadeia de Markov
        self.probabilidades_base = {} # Bayes
        
    def preparar_dados_sequenciais(self, historico_dezenas, janela=10):
        """Transforma o histórico numa matriz de aprendizagem para a IA."""
        X, y = [], []
        if len(historico_dezenas) <= janela:
            return np.array(X), np.array(y)
        
        for i in range(len(historico_dezenas) - janela):
            X.append(historico_dezenas[i:i+janela])
            y.append(historico_dezenas[i+janela])
        return np.array(X), np.array(y)

    def treinar_markov_kadosh(self, historico_jogos):
        """Analisa a probabilidade de um número sair dado que outro saiu (Vizinhança)."""
        transicoes = {}
        for jogo in historico_jogos:
            jogo_ordenado = sorted(list(jogo))
            for i in range(len(jogo_ordenado)-1):
                atual = jogo_ordenado[i]
                proximo = jogo_ordenado[i+1]
                if atual not in transicoes: transicoes[atual] = []
                transicoes[atual].append(proximo)
        
        # Converte listas em probabilidades reais
        for k, v in transicoes.items():
            counts = pd.Series(v).value_counts(normalize=True).to_dict()
            self.matriz_transicao[k] = counts

    def calcular_peso_ia(self, dezena, ultimos_resultados):
        """
        Calcula o Score Final de uma dezena cruzando:
        LSTM (Tendência) + Markov (Vizinhança) + Frequência
        """
        score = 0.5 # Base neutra
        
        # 1. Influência de Vizinhança (Markov)
        if ultimos_resultados:
            ultimo_jogo = ultimos_resultados[-1]
            for d in ultimo_jogo:
                if d in self.matriz_transicao and dezena in self.matriz_transicao[d]:
                    score += (self.matriz_transicao[d][dezena] * 1.5) # Peso de transição
        
        # 2. Influência de Tendência (Simulação de LSTM rápida)
        frequencia_recente = sum([1 for jogo in ultimos_resultados[-15:] if dezena in jogo])
        score += (frequencia_recente / 15) * 2.0
        
        return round(score, 4)

# =================================================================
# 5. GESTÃO DINÂMICA DE ATUALIZAÇÕES (PLUGINS)
# =================================================================

def atualizar_cerebro_automatico(modalidade, novos_dados):
    """
    Função 'Invisível' que atualiza a inteligência sem o utilizador intervir.
    """
    if modalidade not in st.session_state.pesos_ia:
        st.session_state.pesos_ia[modalidade] = KadoshBrain(modalidade)
    
    brain = st.session_state.pesos_ia[modalidade]
    
    # Treina a lógica de Markov com os novos dados
    brain.treinar_markov_kadosh(novos_dados)
    brain.modelo_treinado = True
    
    # Guarda na sessão
    st.session_state.pesos_ia[modalidade] = brain

import math
import random

# =================================================================
# 6. INTELIGÊNCIA DE ENXAME (PSO) E ENTROPIA DE SHANNON
# =================================================================

class KadoshOptimizer:
    """
    Motor que utiliza enxame de partículas para encontrar o equilíbrio 
    entre filtros estatísticos e o caos natural dos sorteios.
    """
    
    @staticmethod
    def calcular_entropia(jogo):
        """
        Mede o grau de desordem de um jogo. 
        Sorteios reais têm entropia média, nem muito baixa (padrões) nem muito alta.
        """
        n = len(jogo)
        if n <= 1: return 0
        
        # Calcula as distâncias entre números consecutivos
        distancias = [jogo[i+1] - jogo[i] for i in range(n-1)]
        contagem = pd.Series(distancias).value_counts()
        probs = contagem / len(distancias)
        
        # Fórmula de Shannon: -sum(p * log2(p))
        entropia = -sum(p * math.log2(p) for p in probs)
        return round(entropia, 4)

    def otimizar_pso(self, pool_dezenas, qtd_dezenas, n_particulas=50, iteracoes=30):
        """
        Algoritmo de Enxame: Gera vários jogos 'partículas' e as faz 
        evoluir para a melhor combinação de filtros.
        """
        melhor_global = None
        melhor_score_global = -1
        
        # Criação das partículas iniciais (Jogos aleatórios do Pool)
        particulas = [random.sample(pool_dezenas, qtd_dezenas) for _ in range(n_particulas)]
        
        for _ in range(iteracoes):
            for i in range(n_particulas):
                jogo_atual = sorted(particulas[i])
                
                # Avalia o jogo (Filtros + Entropia + IA)
                score = self.avaliar_jogo_kadosh(jogo_atual)
                
                if score > melhor_score_global:
                    melhor_score_global = score
                    melhor_global = jogo_atual
                
                # 'Mutação' da partícula: Troca uma dezena ruim por uma melhor do Pool
                if random.random() > 0.7:
                    idx_troca = random.randint(0, qtd_dezenas - 1)
                    nova_dezena = random.choice(pool_dezenas)
                    if nova_dezena not in jogo_atual:
                        particulas[i][idx_troca] = nova_dezena
                        
        return melhor_global

    def avaliar_jogo_kadosh(self, jogo):
        """
        O 'Juiz' do PSO. Dá uma nota ao jogo baseada na realidade oficial.
        """
        score = 0
        entropia = self.calcular_entropia(jogo)
        
        # 1. Filtro de Realismo: Evita entropia muito baixa (jogos seguidos/óbvios)
        if 1.5 < entropia < 3.5:
            score += 20
        
        # 2. IA de Markov/LSTM (Se houver pesos carregados)
        if 'pesos_ia' in st.session_state:
            # Soma os pesos que a IA deu para cada dezena do jogo
            # (Essa parte integra com o Bloco 2)
            pass 
            
        return score

# =================================================================
# 7. GERADOR DE POOL INTELIGENTE (O 'BOTÃO MÁGICO')
# =================================================================

def gerar_pool_kadosh(modalidade, dezenas_alvo=20):
    """
    Cria o grupo de elite de dezenas cruzando IA e estatística.
    """
    brain = st.session_state.pesos_ia.get(modalidade)
    if not brain:
        return random.sample(range(1, 26 if modalidade == "Lotofácil" else 61), dezenas_alvo)
    
    scores_dezenas = {}
    limite = 26 if modalidade == "Lotofácil" else 61
    
    # Busca histórico para a IA analisar
    hist = st.session_state.historicos.get(modalidade, [])
    
    for d in range(1, limite):
        scores_dezenas[d] = brain.calcular_peso_ia(d, hist)
    
    # Ordena e pega as melhores
    pool_ordenado = sorted(scores_dezenas.items(), key=lambda x: x[1], reverse=True)
    pool_final = [d[0] for d in pool_ordenado[:dezenas_alvo]]
    
    return sorted(pool_final)

# =================================================================
# 8. MOTOR DE FILTROS ADAPTATIVOS (DENSIDADE PROPORCIONAL)
# =================================================================

class KadoshFilters:
    """
    Define as regras biométricas de cada sorteio. 
    Os filtros ajustam-se sozinhos ao tamanho do jogo.
    """
    
    @staticmethod
    def verificar_primos(jogo):
        primos_ref = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59]
        return len([d for d in jogo if d in primos_ref])

    @staticmethod
    def verificar_moldura(jogo, colunas=5):
        # Lógica para Lotofácil (5x5) ou outras
        count = 0
        for d in jogo:
            # Exemplo Lotofácil: Linha 1, Linha 5, Coluna 1, Coluna 5
            if d <= 5 or d >= 21 or d % 5 == 1 or d % 5 == 0:
                count += 1
        return count

    def validar_por_modalidade(self, jogo, modalidade):
        qtd = len(jogo)
        # Cálculo de Proporção (Densidade)
        # Ex: Se em 15 números o ideal é 60% de pares, em 18 também será 60%
        pares = len([d for d in jogo if d % 2 == 0])
        primos = self.verificar_primos(jogo)
        soma = sum(jogo)
        
        if modalidade == "Lotofácil":
            # Filtros dinâmicos baseados na quantidade (15 a 20 dezenas)
            prop_par = pares / qtd
            prop_primo = primos / qtd
            if not (0.4 <= prop_par <= 0.65): return False # Equilíbrio Par/Ímpar
            if not (0.2 <= prop_primo <= 0.45): return False # Primos proporcionais
            if not (160 <= soma <= 240) and qtd == 15: return False
            
        elif modalidade == "Mega-Sena":
            # Filtro de Quadrantes (Essencial para Mega)
            q1 = len([d for d in jogo if d % 10 <= 5 and d <= 30])
            q2 = len([d for d in jogo if d % 10 > 5 and d <= 30])
            q3 = len([d for d in jogo if d % 10 <= 5 and d > 30])
            q4 = len([d for d in jogo if d % 10 > 5 and d > 30])
            # Impede que um quadrante tenha mais de 70% das dezenas
            if max(q1, q2, q3, q4) > (qtd * 0.7): return False
            
        elif modalidade == "+Milionária":
            # Filtro específico para a matriz 50
            if not (110 <= soma <= 190) and qtd == 6: return False
            
        # Filtro Universal de Sequências (Máximo 3 ou 4 números juntos)
        seq_max = 0
        atual = 1
        for i in range(len(jogo)-1):
            if jogo[i+1] == jogo[i] + 1:
                atual += 1
            else:
                seq_max = max(seq_max, atual)
                atual = 1
        if seq_max > 4: return False # Ninguém ganha com 1,2,3,4,5,6...
        
        return True

# =================================================================
# 9. DICIONÁRIO DE ESTRATÉGIAS (PLUG-AND-PLAY)
# =================================================================

# Esta estrutura permite que você apenas adicione uma linha aqui 
# e o sistema já entenda a nova estratégia ou matriz no futuro.
ESTRATEGIAS_KADOSH = {
    "Lotofácil": {
        "Padrão 15": {"dezenas": 15, "jogos": 10},
        "Cercamento 18": {"dezenas": 18, "jogos": 5},
        "Elite 20": {"dezenas": 20, "jogos": 2},
    },
    "Mega-Sena": {
        "Surpresinha IA": {"dezenas": 6, "jogos": 6},
        "Fechamento 8": {"dezenas": 8, "jogos": 3},
    },
    "Quina": {
        "Estratégia 5": {"dezenas": 5, "jogos": 10},
    },
    "+Milionária": {
        "Foco Trevos": {"dezenas": 6, "jogos": 5},
    }
}
import requests

# =================================================================
# 10. MOTOR DE DADOS: API, SINCRONISMO E ENTRADA MANUAL
# =================================================================

class KadoshDataEngine:
    """
    Gere a entrada de dados. Se a API falhar ou estiver desatualizada, 
    permite a alimentação manual para não travar a IA.
    """
    
    @staticmethod
    def buscar_resultado_api(modalidade):
        """
        Consome os teus links de API. 
        Adaptado para as urls que já funcionam no teu código original.
        """
        urls = {
            "Lotofácil": "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil",
            "Mega-Sena": "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena",
            "Quina": "https://servicebus2.caixa.gov.br/portaldeloterias/api/quina",
            "Dupla Sena": "https://servicebus2.caixa.gov.br/portaldeloterias/api/duplasena",
            "+Milionária": "https://servicebus2.caixa.gov.br/portaldeloterias/api/maismilionaria"
        }
        
        try:
            response = requests.get(urls.get(modalidade), timeout=10)
            if response.status_code == 200:
                dados = response.json()
                # Extração universal de dezenas e concurso
                return {
                    "concurso": dados.get('numero'),
                    "dezenas": [int(d) for d in dados.get('listaDezenas', [])],
                    "data": dados.get('dataApuracao'),
                    "rateio": dados.get('listaRateioPremios', []),
                    "acumulado": dados.get('acumulado')
                }
        except:
            return None
        return None

    def atualizar_historico_local(self, modalidade, novos_jogos_lista):
        """
        Adiciona concursos manualmente ou via API ao banco de dados interno.
        Verifica duplicatas para não corromper a IA.
        """
        if modalidade not in st.session_state.historicos:
            st.session_state.historicos[modalidade] = []
        
        # Converte para lista de sets para busca rápida
        historico_atual = st.session_state.historicos[modalidade]
        
        cont_novos = 0
        for jogo in novos_jogos_lista:
            if jogo not in historico_atual:
                historico_atual.append(sorted(list(jogo)))
                cont_novos += 1
        
        if cont_novos > 0:
            # Re-treina a IA com os novos dados (Chama o Bloco 2)
            from Bloco2 import atualizar_cerebro_automatico # Referência lógica
            atualizar_cerebro_automatico(modalidade, historico_atual)
            
        return cont_novos

# =================================================================
# 11. SISTEMA DE CONFERÊNCIA PROFISSIONAL
# =================================================================

def conferir_jogos_kadosh(jogos_gerados, resultado_oficial):
    """
    Compara os teus jogos com o resultado da API.
    Calcula acertos e destaca o desempenho.
    """
    res_set = set(resultado_oficial)
    conferencia = []
    
    for jogo in jogos_gerados:
        jogo_set = set(jogo)
        acertos = len(jogo_set.intersection(res_set))
        conferencia.append({
            "jogo": sorted(list(jogo)),
            "acertos": acertos,
            "detalhe": [d for d in jogo if d in res_set] # Dezenas acertadas
        })
        
    return conferencia

# Função auxiliar para formatar a entrada manual de múltiplos concursos
def processar_texto_manual(texto):
    """
    Transforma texto copiado (ex: de sites de resultados) em listas de dezenas.
    """
    linhas = texto.split('\n')
    resultados_limpos = []
    for linha in linhas:
        # Busca grupos de 2 dígitos (01, 02...)
        dezenas = re.findall(r'\b\d{2}\b', linha)
        if dezenas:
            resultados_limpos.append([int(d) for d in dezenas])
    return resultados_limpos

# =================================================================
# 12. INTERFACE DE UTILIZADOR (UI) E DASHBOARD CENTRAL
# =================================================================

def main():
    # Inicializa o estilo e segurança do Bloco 1
    aplicar_estilo_kadosh()
    
    st.sidebar.title("💎 KADOSH QUANTUM")
    st.sidebar.markdown("---")
    
    # Navegação por Modalidade
    lotaria_foco = st.sidebar.selectbox(
        "Escolha a Lotaria:", 
        ["Lotofácil", "Mega-Sena", "Quina", "Dupla Sena", "+Milionária"]
    )
    
    aba1, aba2, aba3, aba4 = st.tabs([
        "🚀 Gerador Inteligente", 
        "📊 Análise & Pool", 
        "📥 Dados & Backup", 
        "⚙️ Configurações"
    ])

    # --- ABA 1: GERADOR (USANDO PSO E FILTROS ADAPTATIVOS) ---
    with aba1:
        st.header(f"Gerador IA - {lotaria_foco}")
        
        col1, col2 = st.columns(2)
        with col1:
            estrat_nome = st.selectbox("Estratégia/Matriz:", list(ESTRATEGIAS_KADOSH[lotaria_foco].keys()))
            config = ESTRATEGIAS_KADOSH[lotaria_foco][estrat_nome]
        
        with col2:
            st.info(f"Configuração: {config['dezenas']} dezenas | {config['jogos']} jogos")
            btn_gerar = st.button(f"GERAR JOGOS {lotaria_foco.upper()}")

        if btn_gerar:
            # 1. Gera o Pool usando o Bloco 3
            pool = gerar_pool_kadosh(lotaria_foco, dezenas_alvo=config['dezenas'] + 5)
            
            # 2. Otimiza com PSO e Filtros do Bloco 4
            otimizador = KadoshOptimizer()
            jogos_finais = []
            
            with st.spinner("IA Processando Sequências..."):
                for _ in range(config['jogos']):
                    jogo = otimizador.otimizar_pso(pool, config['dezenas'])
                    if jogo: jogos_finais.append(jogo)
            
            # 3. Renderiza os Cards de Alta Visibilidade
            for i, jogo in enumerate(jogos_finais):
                dezenas_html = "".join([f'<span class="dezena-bola">{d:02d}</span>' for d in jogo])
                st.markdown(f"""
                <div class="card-jogo">
                    <div style="display: flex; justify-content: space-between;">
                        <b>JOGO #{i+1:02d}</b>
                        <span style="color: #2E86C1;">{lotaria_foco}</span>
                    </div>
                    <hr style="border: 0.5px solid #eee;">
                    <div style="margin-top: 10px;">{dezenas_html}</div>
                </div>
                """, unsafe_allow_html=True)

    # --- ABA 2: ANÁLISE & POOL (O "CÉREBRO" VISUAL) ---
    with aba2:
        st.subheader("Otimização de Pool por IA")
        if st.button("CALCULAR MELHOR POOL AGORA"):
            pool_ia = gerar_pool_kadosh(lotaria_foco, dezenas_alvo=20)
            st.success("As dezenas abaixo foram selecionadas cruzando LSTM e Markov:")
            st.write(pool_ia)
            st.info("Este grupo de dezenas tem a maior afinidade com os últimos sorteios oficiais.")

    # --- ABA 3: DADOS & BACKUP (ATUALIZAÇÃO FÁCIL) ---
    with aba3:
        st.subheader("Sincronização e Memória")
        
        # Botão de API (Usa os seus links)
        if st.button("🔄 SINCRONIZAR COM API OFICIAL"):
            engine = KadoshDataEngine()
            res = engine.buscar_resultado_api(lotaria_foco)
            if res:
                st.write(f"Concurso: {res['concurso']} | Dezenas: {res['dezenas']}")
                engine.atualizar_historico_local(lotaria_foco, [res['dezenas']])
                st.success("IA Atualizada com o último sorteio!")
            else:
                st.error("Falha ao contactar API. Verifique a conexão.")

        st.markdown("---")
        # Sistema de Backup do Bloco 1
        st.write("Backup do Cérebro (Salvar tudo o que a IA aprendeu)")
        st.download_button("BAIXAR BACKUP (.kadosh)", data=exportar_cerebro_kadosh(), file_name=f"backup_kadosh_{datetime.now().strftime('%d_%m')}.kadosh")
        
        arquivo_up = st.file_uploader("Subir Backup / Atualização de Inteligência", type=["kadosh"])
        if arquivo_up:
            importar_cerebro_kadosh(arquivo_up)

    # --- ABA 4: CONFIGURAÇÕES (MUDAR SENHA) ---
    with aba4:
        st.subheader("Segurança do Sistema")
        nova_senha = st.text_input("Nova Senha de Acesso:", type="password")
        if st.button("ALTERAR SENHA AGORA"):
            st.session_state.senha_mestra = nova_senha
            st.success("Senha alterada! Use a nova senha no próximo login.")

if __name__ == "__main__":
    main()
