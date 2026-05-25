import streamlit as st
import itertools
import random
import json
import requests
from collections import Counter
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =====================================================================
# CONFIGURAÇÕES E PREÇOS - LOTOMATRIX PREMIUM
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
    st.markdown("<p style='text-align: center; color: #546e7a;'>Terminal de Engenharia Preditiva Avançada</p>", unsafe_allow_html=True)
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

# Memória persistente (Não apaga ao mudar de aba)
if 'banca' not in st.session_state: st.session_state.banca = 200.0
if 'lote_ativo' not in st.session_state: st.session_state.lote_ativo = None
if 'matriz_gerada' not in st.session_state: st.session_state.matriz_gerada = None
if 'historico_dados' not in st.session_state: st.session_state.historico_dados = []
if 'ultimo_concurso_sincronizado' not in st.session_state: st.session_state.ultimo_concurso_sincronizado = 3693

# =====================================================================
# API DA CAIXA E MOTORES DO SISTEMA
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

def motor_inteligencia_equilibrada():
    """Gera a Matriz cobrindo Quentes (Tendência), Médias (Equilíbrio) e Frias (Atrasadas)"""
    if not st.session_state.historico_dados: return [], [], [], []
    todas = [n for s in st.session_state.historico_dados for n in s["dezenas"]]
    freq = Counter(todas)
    ordenadas = [n for n, c in freq.most_common()]
    
    faltantes = [n for n in range(1, 26) if n not in ordenadas]
    ordenadas.extend(faltantes)
    
    quentes = ordenadas[:9]
    intermediarias = ordenadas[9:14]
    frias = ordenadas[-4:]
    
    matriz_final = sorted(quentes + intermediarias + frias)
    
    # Salva na memória global para não sumir e para podermos auditar depois
    st.session_state.matriz_gerada = {
        "completa": matriz_final, "quentes": quentes, "medias": intermediarias, "frias": frias
    }
    return matriz_final, quentes, intermediarias, frias

def validar_matematica(jogo):
    soma = sum(jogo)
    impares = len([x for x in jogo if x % 2 != 0])
    return (180 <= soma <= 220) and (6 <= impares <= 9)

# =====================================================================
# INTERFACE E NAVEGAÇÃO
# =====================================================================
st.sidebar.markdown("<h2 style='color: #1a237e;'>🧬 LotoMatrix Premium</h2>", unsafe_allow_html=True)
st.sidebar.metric("🏦 Capital da Banca", formatar_moeda(st.session_state.banca))
st.sidebar.metric("🎯 Alvo (Próximo Sorteio)", st.session_state.ultimo_concurso_sincronizado + 1)

# PAINEL DE DADOS FIXO E SEMPRE VISÍVEL
st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Status do Cérebro")
if len(st.session_state.historico_dados) > 0:
    st.sidebar.success(f"**{len(st.session_state.historico_dados)} Sorteios Salvos** na base.")
else:
    st.sidebar.error("Base de Dados Vazia!")

st.sidebar.markdown("---")
menu = st.sidebar.radio("Módulos de Operação", [
    "1. Gerador Matrix", 
    "2. Os Meus Bilhetes", 
    "3. Conferência e Resultados", 
    "4. Sistema Financeiro e Cofre"
])

# ---------------------------------------------------------------------
# MÓDULO 1: GERADOR
# ---------------------------------------------------------------------
if menu == "1. Gerador Matrix":
    st.header("🧠 Cérebro Analítico: LotoMatrix")
    
    concurso_alvo = st.session_state.ultimo_concurso_sincronizado + 1
    
    if not st.session_state.historico_dados:
        st.warning("⚠️ Precisa de sincronizar dados da Caixa no Módulo 3 antes de gerar jogos.")
    else:
        # Gera e salva a matriz na memória
        motor_inteligencia_equilibrada()
        mg = st.session_state.matriz_gerada
        
        with st.container(border=True):
            st.markdown("### 🧬 Arquitetura da Matriz Base (18 Dezenas)")
            st.write("A distribuição estatística protege os seus jogos. Matematicamente, a Lotofácil nunca sorteia apenas as dezenas mais quentes. A matriz mescla tendências para cercar os prêmios altos.")
            col1, col2, col3 = st.columns(3)
            col1.error(f"🔥 **9 Quentes:**\n\n`{sorted(mg['quentes'])}`")
            col2.warning(f"⚖️ **5 Médias:**\n\n`{sorted(mg['medias'])}`")
            col3.info(f"❄️ **4 Frias:**\n\n`{sorted(mg['frias'])}`")
            st.success(f"🎯 **Matriz Selecionada para os Jogos:** `{mg['completa']}`")

        st.markdown("---")
        with st.container(border=True):
            st.markdown("### ⚙️ Engenharia do Fechamento")
            colA, colB = st.columns(2)
            orcamento = colA.number_input("Limite de Capital (R$):", min_value=3.50, value=59.50, step=3.50)
            estrategia = colB.selectbox("Estratégia:", ["Híbrida (16 e 15 Dezenas)", "Apenas 15 Dezenas", "Apenas 16 Dezenas"])
            
            if st.button("🚀 Processar Algoritmo", use_container_width=True, type="primary"):
                if orcamento > st.session_state.banca:
                    st.error("❌ Capital insuficiente na Banca.")
                else:
                    with st.spinner("Processando combinações matemáticas..."):
                        jogos, caixa_temp = [], orcamento
                        
                        if "Híbrida" in estrategia or "16" in estrategia:
                            qtd_16 = int(caixa_temp // PRECO_16)
                            if qtd_16 > 0:
                                cand_16 = [j for j in itertools.combinations(mg['completa'], 16) if validar_matematica(j)]
                                for j in (random.sample(cand_16, min(qtd_16, len(cand_16))) if cand_16 else []):
                                    jogos.append({"tipo": 16, "dezenas": list(j)})
                                    caixa_temp -= PRECO_16

                        if "Híbrida" in estrategia or "15" in estrategia:
                            qtd_15 = int(caixa_temp // PRECO_15)
                            if qtd_15 > 0:
                                cand_15 = [j for j in itertools.combinations(mg['completa'], 15) if validar_matematica(j)]
                                for j in (random.sample(cand_15, min(qtd_15, len(cand_15))) if cand_15 else []):
                                    jogos.append({"tipo": 15, "dezenas": list(j)})
                                    caixa_temp -= PRECO_15

                        custo_final = orcamento - caixa_temp
                        st.session_state.banca -= custo_final
                        st.session_state.lote_ativo = {
                            "concurso_alvo": concurso_alvo,
                            "data": datetime.now().strftime("%d/%m/%Y às %H:%M"),
                            "custo": custo_final,
                            "bilhetes": jogos,
                            "status": "Aguardando Sorteio"
                        }
                    st.success(f"✅ Fechamento Gerado! {formatar_moeda(custo_final)} processados. Pode mudar de abas que nada irá sumir.")

# ---------------------------------------------------------------------
# MÓDULO 2: OS MEUS BILHETES & EXCLUSÃO
# ---------------------------------------------------------------------
elif menu == "2. Os Meus Bilhetes":
    st.header("🎫 Lote de Apostas Gerado")
    lote = st.session_state.lote_ativo
    
    if not lote:
        st.info("Não tem jogos pendentes. Vá ao Módulo 1 para gerar.")
    else:
        # PAINEL DE CONTROLO DO LOTE
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Alvo", lote['concurso_alvo'])
            col2.metric("Status", lote['status'])
            col3.metric("Custo", formatar_moeda(lote['custo']))
            
            # BOTÃO DE EXCLUIR QUE DEVOLVE O DINHEIRO À BANCA SE NÃO TIVER SIDO CONFERIDO
            with col4:
                st.write("") # Espaço
                if st.button("🗑️ Excluir Lote", type="primary", help="Apaga os jogos e devolve o dinheiro ao caixa (se não estiver conferido)."):
                    if lote['status'] != "Conferido e Liquidado":
                        st.session_state.banca += lote['custo'] # Estorna o valor
                    st.session_state.lote_ativo = None
                    st.rerun()

        # EXPORTAÇÃO
        texto_exportacao = f"ALVO: {lote['concurso_alvo']}\n"
        for i, b in enumerate(lote["bilhetes"]):
            texto_exportacao += f"Jogo {i+1} [{b['tipo']}]: " + " - ".join([f"{n:02d}" for n in sorted(b["dezenas"])]) + "\n"
        
        st.download_button("📥 Exportar Jogos (.txt)", texto_exportacao, f"Bilhetes_{lote['concurso_alvo']}.txt", use_container_width=True)
        
        # EXIBIÇÃO VISUAL
        st.markdown("---")
        for i, b in enumerate(lote["bilhetes"]):
            cor = "#f1f8e9" if b["tipo"] == 15 else "#e3f2fd"
            st.markdown(f"""
            <div style="background-color: {cor}; padding: 10px; margin-bottom: 5px; border-radius: 4px; border-left: 5px solid {'#43a047' if b['tipo'] == 15 else '#1e88e5'};">
                <b>Jogo {i+1:02d} ({b['tipo']} dezenas):</b> <span style="font-size: 16px;">{str(sorted(b["dezenas"])).replace('[','').replace(']','')}</span>
            </div>
            """, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# MÓDULO 3: CONFERÊNCIA E AUDITORIA DA MATRIZ
# ---------------------------------------------------------------------
elif menu == "3. Conferência e Resultados":
    st.header("🎯 Auditoria Oficial")
    
    with st.container(border=True):
        concurso = st.text_input("Nº do Concurso (Deixe vazio para o último):")
        if st.button("Sincronizar e Auditar", type="primary", use_container_width=True):
            with st.spinner("Buscando resultados..."):
                res = buscar_sorteio_caixa(concurso)
                if res["sucesso"]:
                    conc, sorteadas = res["concurso"], res["dezenas"]
                    st.session_state.ultimo_concurso_sincronizado = conc
                    
                    st.success(f"✅ Sorteio {conc} sincronizado.")
                    st.info(f"**Resultado:** `{sorteadas}`")
                    
                    if not any(d["concurso"] == conc for d in st.session_state.historico_dados):
                        st.session_state.historico_dados.append({"concurso": conc, "dezenas": sorteadas})
                    
                    # 1. AUDITORIA DA MATRIZ BASE (Nova Funcionalidade Genial)
                    if st.session_state.matriz_gerada:
                        acertos_matriz = len(set(st.session_state.matriz_gerada['completa']).intersection(sorteadas))
                        st.markdown(f"""
                        <div style="background-color: #333; color: #fff; padding: 15px; border-radius: 5px; text-align: center; margin-top: 15px;">
                            <h3 style="margin: 0;">🧬 Auditoria da Matriz Base</h3>
                            <p style="font-size: 18px; margin-top: 5px;">A matriz de 18 dezenas do robô acertou <b>{acertos_matriz} dezenas</b> neste sorteio oficial!</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 2. AUDITORIA DOS BILHETES
                    lote = st.session_state.lote_ativo
                    if lote and lote["concurso_alvo"] == conc and lote["status"] != "Conferido e Liquidado":
                        st.markdown("### 💰 Prêmios dos seus Bilhetes")
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
                                st.success(f"🎉 **Jogo {i+1} PREMIADO!** {acertos} Acertos -> {formatar_moeda(valor)}")
                            else:
                                st.error(f"❌ Jogo {i+1} - {acertos} acertos.")
                        
                        st.session_state.banca += total_ganho
                        st.session_state.lote_ativo["status"] = "Conferido e Liquidado"
                        st.info(f"O valor de {formatar_moeda(total_ganho)} foi depositado no Caixa.")
                else:
                    st.error(res["erro"])

# ---------------------------------------------------------------------
# MÓDULO 4: COFRE FINANCEIRO E BACKUP
# ---------------------------------------------------------------------
elif menu == "4. Sistema Financeiro e Cofre":
    st.header("🏦 Administração e Backup")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.metric("Saldo do Caixa", formatar_moeda(st.session_state.banca))
            aporte = st.number_input("Adicionar Dinheiro (R$):", min_value=0.0, step=50.0)
            if st.button("Depositar", use_container_width=True):
                st.session_state.banca += aporte
                st.success("Depósito concluído.")
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### 💾 Backup de Segurança")
            estado = {
                "banca": st.session_state.banca,
                "historico_dados": st.session_state.historico_dados,
                "lote_ativo": st.session_state.lote_ativo,
                "matriz_gerada": st.session_state.matriz_gerada,
                "ultimo_concurso_sincronizado": st.session_state.ultimo_concurso_sincronizado
            }
            st.download_button("📤 Baixar Cofre.json", json.dumps(estado), "LotoMatrix_Cofre.json", "application/json", type="primary", use_container_width=True)
            
            st.markdown("### 📥 Restaurar Cofre")
            arquivo = st.file_uploader("Envie seu Cofre.json:", type=["json"])
            if arquivo is not None:
                try:
                    d = json.load(arquivo)
                    st.session_state.banca = d.get("banca", 0.0)
                    st.session_state.historico_dados = d.get("historico_dados", [])
                    st.session_state.lote_ativo = d.get("lote_ativo", None)
                    st.session_state.matriz_gerada = d.get("matriz_gerada", None)
                    st.session_state.ultimo_concurso_sincronizado = d.get("ultimo_concurso_sincronizado", 3693)
                    st.success("Sistema restaurado!")
                    st.rerun()
                except:
                    st.error("Ficheiro inválido.")
