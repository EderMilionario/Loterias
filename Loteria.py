import streamlit as st
import itertools
import random
import json
import requests
from collections import Counter
from datetime import datetime
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# --- BLOCO DE SEGURANÇA E CARREGAMENTO ---
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False

def carregar_cofre_seguro(uploaded_file):
    import json
    try:
        data = json.load(uploaded_file)
        st.session_state.historico_dados = data.get("historico_dados", [])
        st.session_state.banca = data.get("banca", 200.0)
        st.session_state.dados_carregados = True
        return True
    except Exception as e:
        st.error(f"Erro ao ler cofre: {e}")
        return False
# ------------------------------------------

# =====================================================================
# CONFIGURAÇÕES E PREÇOS - LOTOMATRIX PREMIUM 2026
# =====================================================================
st.set_page_config(page_title="LotoMatrix Premium", page_icon="🧬", layout="wide")

PRECO_15, PRECO_16 = 3.50, 56.00
PREMIO_11, PREMIO_12, PREMIO_13 = 7.00, 14.00, 35.00

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =====================================================================
# AUTENTICAÇÃO E MEMÓRIA DE SESSÃO (BLINDADA)
# =====================================================================
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center; color: #1a237e;'>🧬 LotoMatrix Premium</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #546e7a;'>IA Autônoma de Engenharia Preditiva (Versão 2026)</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container(border=True):
            senha = st.text_input("Credencial de Acesso:", type="password")
            if st.button("Iniciar Sistema", use_container_width=True, type="primary"):
                if senha == "7777":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("❌ Credencial Inválida.")
    st.stop()

if 'banca' not in st.session_state: st.session_state.banca = 000.0
if 'lote_ativo' not in st.session_state: st.session_state.lote_ativo = None
if 'matriz_gerada' not in st.session_state: st.session_state.matriz_gerada = None
if 'historico_dados' not in st.session_state: st.session_state.historico_dados = []
if 'ultimo_concurso_sincronizado' not in st.session_state: st.session_state.ultimo_concurso_sincronizado = 3693
if 'tela_conferencia' not in st.session_state: st.session_state.tela_conferencia = None 

# =====================================================================
# API DA CAIXA E MOTOR AUTÔNOMO DE IA
# =====================================================================
def buscar_sorteio_caixa(concurso=""):
    url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{concurso}"
    try:
        req = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10, verify=False)
        if req.status_code == 200:
            d = req.json()
            dezs = sorted([int(x) for x in d['listaDezenas']])
            v14, v15 = 1500.00, 1500000.00
            for r in d.get('listaRateioPremio', []):
                if r['faixa'] == 1: v15 = r['valorPremio']
                elif r['faixa'] == 2: v14 = r['valorPremio']
            return {"sucesso": True, "concurso": d['numero'], "dezenas": dezs, "v14": v14, "v15": v15}
        return {"sucesso": False, "erro": "Sorteio não encontrado ou sistema da Caixa fora do ar."}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

def motor_inteligencia_autonoma(orcamento):
    """IA 100% Autônoma: Lê o histórico completo e o saldo para decidir a melhor estratégia sozinha."""
    if not st.session_state.historico_dados: return []
    
    todas = [n for s in st.session_state.historico_dados for n in s["dezenas"]]
    freq = Counter(todas)
    ordenadas = [n for n, c in freq.most_common()]
    faltantes = [n for n in range(1, 26) if n not in ordenadas]
    ordenadas.extend(faltantes)
    
    # A IA decide a matriz baseada no poder de fogo (orçamento)
    if orcamento >= 500: tamanho_matriz = 20
    elif orcamento >= 200: tamanho_matriz = 19
    elif orcamento >= 60: tamanho_matriz = 18
    else: tamanho_matriz = 17

    # A IA calcula a mescla perfeita sem perguntar ao utilizador
    qtd_quentes = tamanho_matriz // 2
    qtd_frias = 4
    qtd_medias = tamanho_matriz - qtd_quentes - qtd_frias
    
    matriz = sorted(ordenadas[:qtd_quentes] + ordenadas[10:10+qtd_medias] + ordenadas[-qtd_frias:])
        
    st.session_state.matriz_gerada = {"completa": matriz, "modo": f"Autônoma Inteligente ({tamanho_matriz} Dezenas)"}
    return matriz

def validar_matematica(jogo):
    soma = sum(jogo)
    impares = len([x for x in jogo if x % 2 != 0])
    primos = len([x for x in jogo if x in [2, 3, 5, 7, 11, 13, 17, 19, 23]])
    
    # EXCLUSÃO HISTÓRICA: Se o jogo gerado já foi prémio máximo no passado, elimina!
    if len(jogo) == 15:
        historico_sets = [set(d['dezenas']) for d in st.session_state.historico_dados]
        if set(jogo) in historico_sets:
            return False

    return (180 <= soma <= 220) and (6 <= impares <= 9) and (4 <= primos <= 7)

# =====================================================================
# INTERFACE PRINCIPAL
# =====================================================================
st.sidebar.markdown("<h2 style='color: #1a237e;'>🧬 LotoMatrix Premium</h2>", unsafe_allow_html=True)
st.sidebar.metric("🏦 Capital da Banca", formatar_moeda(st.session_state.banca))
st.sidebar.metric("🎯 Alvo (Próximo Sorteio)", st.session_state.ultimo_concurso_sincronizado + 1)
st.sidebar.markdown("---")
st.sidebar.success(f"**{len(st.session_state.historico_dados)} Sorteios Salvos** no Cérebro da IA.")
st.sidebar.markdown("---")

menu = st.sidebar.radio("Módulos de Operação", ["1. Gerador Autônomo", "2. Os Meus Bilhetes", "3. Conferência e Resultados", "4. Cofre (Backup)"])

# ---------------------------------------------------------------------
# MÓDULO 1: GERADOR
# ---------------------------------------------------------------------
if menu == "1. Gerador Autônomo":
    st.header("🧠 Cérebro Analítico Autônomo (IA 2026)")
    concurso_alvo = st.session_state.ultimo_concurso_sincronizado + 1
    
    if not st.session_state.historico_dados:
        st.warning("Vá ao Módulo 3 e sincronize todo o histórico da Caixa para a IA trabalhar.")
    else:
        with st.container(border=True):
            st.markdown("### ⚙️ Configuração do Lote")
            colA, colB = st.columns(2)
            orcamento = colA.number_input("Limite de Capital para Investir (R$):", min_value=3.50, value=59.50, step=3.50)
            estrategia = colB.selectbox("Formato dos Bilhetes:", ["Híbrida (16 e 15 Dezenas)", "Apenas 15 Dezenas", "Apenas 16 Dezenas"])
            
            if st.button("🚀 Iniciar Análise e Processar Fechamento", use_container_width=True, type="primary"):
                if orcamento > st.session_state.banca:
                    st.error("❌ Capital insuficiente no Cofre.")
                else:
                    with st.spinner("IA assumindo o controle: Analisando Big Data, rejeitando históricos passados e calculando matriz..."):
                        
                        # A IA decide a matriz baseada no capital
                        matriz = motor_inteligencia_autonoma(orcamento)
                        st.info(f"🧬 A IA processou o seu capital e montou uma matriz de risco de {len(matriz)} dezenas: `{matriz}`")
                        
                        jogos, caixa_temp = [], orcamento
                        
                        if "Híbrida" in estrategia or "16" in estrategia:
                            qtd_16 = int(caixa_temp // PRECO_16)
                            if qtd_16 > 0:
                                cand_16 = [j for j in itertools.combinations(matriz, 16) if validar_matematica(j)]
                                for j in (random.sample(cand_16, min(qtd_16, len(cand_16))) if cand_16 else []):
                                    jogos.append({"tipo": 16, "dezenas": list(j)})
                                    caixa_temp -= PRECO_16

                        if "Híbrida" in estrategia or "15" in estrategia:
                            qtd_15 = int(caixa_temp // PRECO_15)
                            if qtd_15 > 0:
                                cand_15 = [j for j in itertools.combinations(matriz, 15) if validar_matematica(j)]
                                for j in (random.sample(cand_15, min(qtd_15, len(cand_15))) if cand_15 else []):
                                    jogos.append({"tipo": 15, "dezenas": list(j)})
                                    caixa_temp -= PRECO_15

                        custo = orcamento - caixa_temp
                        st.session_state.banca -= custo
                        st.session_state.lote_ativo = {
                            "concurso_alvo": concurso_alvo,
                            "data": datetime.now().strftime("%d/%m/%Y às %H:%M"),
                            "custo": custo, "bilhetes": jogos, "status": "Aguardando Sorteio"
                        }
                    st.success("✅ O Sistema concluiu o fechamento e blindou os jogos. Vá para a Aba 2.")

# ---------------------------------------------------------------------
# MÓDULO 2: BILHETES
# ---------------------------------------------------------------------
elif menu == "2. Os Meus Bilhetes":
    st.header("🎫 Gestão de Lote")
    lote = st.session_state.lote_ativo
    if not lote:
        st.info("Nenhum lote ativo. Utilize o Cérebro Autônomo no Módulo 1.")
    else:
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            col1.metric("Alvo", lote['concurso_alvo'])
            col2.metric("Status", lote['status'])
            col3.metric("Custo", formatar_moeda(lote['custo']))
            
            if st.button("🗑️ Excluir Lote e Estornar Capital", type="primary"):
                if lote['status'] != "Conferido e Liquidado":
                    st.session_state.banca += lote['custo']
                st.session_state.lote_ativo = None
                st.rerun()

        txt = f"ALVO: {lote['concurso_alvo']}\n"
        for i, b in enumerate(lote["bilhetes"]):
            txt += f"Jogo {i+1} [{b['tipo']}]: " + " - ".join([f"{n:02d}" for n in sorted(b["dezenas"])]) + "\n"
        st.download_button("📥 Exportar Jogos (.txt)", txt, "Jogos_LotoMatrix.txt", use_container_width=True)
        
        st.markdown("---")
        for i, b in enumerate(lote["bilhetes"]):
            st.markdown(f"**Jogo {i+1:02d} ({b['tipo']} dez):** `{sorted(b['dezenas'])}`")

# ---------------------------------------------------------------------
# MÓDULO 3: CONFERÊNCIA E BIG DATA
# ---------------------------------------------------------------------
elif menu == "3. Conferência e Resultados":
    st.header("🎯 Auditoria Oficial e Sincronização Absoluta")
    
    with st.expander("📥 SINCRONIZAÇÃO TOTAL DE HISTÓRICO (Base Completa)", expanded=False):
        st.write("Atenção: O sistema irá varrer desde o Concurso 1 até o último concurso oficial. Isto garantirá 100% de precisão para a IA.")
        if st.button("🔄 INICIAR DOWNLOAD DE TODO O HISTÓRICO (Pode demorar minutos)"):
            with st.status("Comandos enviados à Caixa... Iniciando download em massa.", expanded=True) as status:
                res_ultimo = buscar_sorteio_caixa("")
                if res_ultimo["sucesso"]:
                    ultimo = res_ultimo["concurso"]
                    concursos_ja_salvos = [d["concurso"] for d in st.session_state.historico_dados]
                    salvos_agora = 0
                    
                    for c in range(1, ultimo + 1):
                        if c not in concursos_ja_salvos:
                            dados_c = buscar_sorteio_caixa(c)
                            if dados_c["sucesso"]:
                                st.session_state.historico_dados.append({"concurso": dados_c["concurso"], "dezenas": dados_c["dezenas"]})
                                salvos_agora += 1
                                if salvos_agora % 50 == 0:
                                    st.write(f"📥 Progresso: {salvos_agora} sorteios baixados...")
                    
                    st.session_state.ultimo_concurso_sincronizado = ultimo
                    status.update(label=f"Sincronização Absoluta Concluída! {salvos_agora} novos concursos armazenados.", state="complete", expanded=False)
                else:
                    status.update(label="Falha de conexão com os servidores oficiais.", state="error", expanded=False)

    st.markdown("---")
    
    if st.session_state.tela_conferencia:
        st.markdown(st.session_state.tela_conferencia, unsafe_allow_html=True)
        if st.button("🗑️ Limpar Tela de Auditoria", type="primary"):
            st.session_state.tela_conferencia = None
            st.rerun()
        st.markdown("---")

    with st.container(border=True):
        st.markdown("### 🔍 Conferência Unitária do Lote")
        concurso = st.text_input("Nº do Concurso para Auditar (Deixe vazio para o Último):")
        if st.button("Sincronizar Sorteio e Auditar Lote", use_container_width=True):
            with st.spinner("Conectando..."):
                res = buscar_sorteio_caixa(concurso)
                if res["sucesso"]:
                    conc, sorteadas = res["concurso"], res["dezenas"]
                    st.session_state.ultimo_concurso_sincronizado = conc
                    
                    if not any(d["concurso"] == conc for d in st.session_state.historico_dados):
                        st.session_state.historico_dados.append({"concurso": conc, "dezenas": sorteadas})
                    
                    tela = f"<h3>Sorteio Oficial {conc}: <code style='color:black;'>{sorteadas}</code></h3>"
                    
                    if st.session_state.matriz_gerada:
                        acertos_matriz = len(set(st.session_state.matriz_gerada['completa']).intersection(sorteadas))
                        tela += f"<div style='background:#1a237e; color:#fff; padding:10px; border-radius:5px;'>O Algoritmo Autônomo ({st.session_state.matriz_gerada['modo']}) acertou <b>{acertos_matriz} dezenas</b> da sua Matriz de Risco neste sorteio.</div><br>"
                    
                    lote = st.session_state.lote_ativo
                    if lote and lote["concurso_alvo"] == conc and lote["status"] != "Conferido e Liquidado":
                        total_ganho = 0.0
                        for i, b in enumerate(lote["bilhetes"]):
                            acertos = len(set(b["dezenas"]).intersection(sorteadas))
                            valor = 0.0
                            if b["tipo"] == 15:
                                if acertos == 11: valor = PREMIO_11
                                elif acertos == 12: valor = PREMIO_12
                                elif acertos == 13: valor = PREMIO_13
                                elif acertos == 14: valor = res['v14']
                                elif acertos == 15: valor = res['v15']
                            elif b["tipo"] == 16:
                                if acertos == 11: valor = 5 * PREMIO_11
                                elif acertos == 12: valor = (4 * PREMIO_12) + (12 * PREMIO_11)
                                elif acertos == 13: valor = (3 * PREMIO_13) + (13 * PREMIO_12)
                                elif acertos == 14: valor = (2 * res['v14']) + (14 * PREMIO_13)
                                elif acertos == 15: valor = res['v15'] + (15 * res['v14'])
                            
                            total_ganho += valor
                            if valor > 0:
                                tela += f"<p style='color:green; font-weight:bold;'>🎉 Jogo {i+1} ({b['tipo']} dez): {acertos} Acertos -> {formatar_moeda(valor)}</p>"
                            else:
                                tela += f"<p style='color:red;'>❌ Jogo {i+1}: {acertos} acertos.</p>"
                        
                        st.session_state.banca += total_ganho
                        st.session_state.lote_ativo["status"] = "Conferido e Liquidado"
                        tela += f"<h4>💰 Resultado Financeiro: {formatar_moeda(total_ganho)} creditados no Caixa.</h4>"
                    else:
                        tela += "<p>Nenhum bilhete correspondente aguardando conferência.</p>"
                    
                    st.session_state.tela_conferencia = tela
                    st.rerun()
                else:
                    st.error(res["erro"])

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# MÓDULO 4: COFRE (BACKUP) - VERSÃO DE PERSISTÊNCIA TOTAL
# ---------------------------------------------------------------------
elif menu == "4. Cofre (Backup)":
    st.header("🏦 Administração e Backup Total")
    
    with st.container(border=True):
        st.metric("Saldo Líquido", formatar_moeda(st.session_state.banca))
        aporte = st.number_input("Realizar Aporte (R$):", min_value=0.0, step=50.0)
        if st.button("Confirmar Depósito"):
            st.session_state.banca += aporte
            st.rerun()
    
    st.markdown("### 💾 Salvar Progresso")
    estado = {
        "banca": st.session_state.banca, 
        "historico_dados": st.session_state.historico_dados,
        "lote_ativo": st.session_state.lote_ativo, 
        "matriz_gerada": st.session_state.matriz_gerada,
        "ultimo_concurso_sincronizado": st.session_state.ultimo_concurso_sincronizado
    }
    st.download_button("📤 Baixar Cofre de Segurança (.json)", json.dumps(estado), "Cofre.json", "application/json", type="primary")
    
    st.markdown("### 📥 Restaurar Sistema")
    
    # Este file_uploader guarda o conteúdo na sessão para não sumir
    uploaded_file = st.file_uploader("Selecione o arquivo Cofre.json:", type=["json"])
    
    if uploaded_file is not None:
        # Armazena o conteúdo em bytes na sessão para não perder no clique do botão
        st.session_state.bytes_arquivo = uploaded_file.getvalue()
        
    if st.button("🚀 PROCESSAR E CARREGAR DADOS"):
        if 'bytes_arquivo' in st.session_state and st.session_state.bytes_arquivo:
            with st.spinner("Lendo histórico do cofre..."):
                try:
                    import io
                    # Criamos um arquivo virtual a partir dos bytes salvos
                    f = io.BytesIO(st.session_state.bytes_arquivo)
                    if carregar_cofre_seguro(f):
                        st.success("✅ Sistema Restaurado e Inteligência Carregada!")
                        st.session_state.bytes_arquivo = None # Limpa memória
                        st.rerun()
                    else:
                        st.error("Erro ao processar arquivo.")
                except Exception as e:
                    st.error(f"Erro crítico: {e}")
        else:
            st.warning("⚠️ Selecione o arquivo antes de clicar em processar.")
