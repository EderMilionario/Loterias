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
# CONFIGURAÇÕES PREMIUM
# =====================================================================
st.set_page_config(page_title="LotoPro Ultimate", page_icon="📈", layout="wide")

PRECO_15, PRECO_16 = 3.50, 56.00
PREMIO_11, PREMIO_12, PREMIO_13 = 7.00, 14.00, 35.00

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =====================================================================
# AUTENTICAÇÃO E INICIALIZAÇÃO
# =====================================================================
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🔒 LotoPro Ultimate</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Terminal Profissional de Engenharia Preditiva</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container(border=True):
            senha = st.text_input("Credencial de Operador:", type="password")
            if st.button("Autenticar Sistema", use_container_width=True, type="primary"):
                if senha == "7777":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("❌ Acesso Negado.")
    st.stop()

if 'banca' not in st.session_state: st.session_state.banca = 200.0
if 'lote_ativo' not in st.session_state: st.session_state.lote_ativo = None
if 'historico_dados' not in st.session_state: st.session_state.historico_dados = []
if 'ultimo_concurso_sincronizado' not in st.session_state: st.session_state.ultimo_concurso_sincronizado = 3693

# =====================================================================
# MOTORES DO SISTEMA (API E IA)
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
        return {"sucesso": False, "erro": "Sorteio não encontrado."}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

def motor_inteligencia_equilibrada():
    """IA Profissional: Mescla Quentes, Médias e Frias para cobrir a variância."""
    if not st.session_state.historico_dados: return [], [], [], []
    todas = [n for s in st.session_state.historico_dados for n in s["dezenas"]]
    freq = Counter(todas)
    ordenadas = [n for n, c in freq.most_common()]
    
    # Se não houver 25 dezenas no histórico, preenche com as faltantes
    faltantes = [n for n in range(1, 26) if n not in ordenadas]
    ordenadas.extend(faltantes)
    
    quentes = ordenadas[:9]         # Top 9 que mais saem
    intermediarias = ordenadas[9:14] # 5 do meio da tabela
    frias = ordenadas[-4:]          # 4 mais atrasadas (frias)
    
    matriz_final = sorted(quentes + intermediarias + frias)
    return matriz_final, quentes, intermediarias, frias

def validar_matematica(jogo):
    soma = sum(jogo)
    impares = len([x for x in jogo if x % 2 != 0])
    return (180 <= soma <= 220) and (6 <= impares <= 9)

def exportar_bilhetes_txt(lote):
    texto = f"=== LOTOPRO ULTIMATE ===\n"
    texto += f"Concurso Alvo: {lote['concurso_alvo']}\n"
    texto += f"Data de Geração: {lote['data']}\n"
    texto += f"Investimento: {formatar_moeda(lote['custo'])}\n"
    texto += "------------------------\n"
    for i, b in enumerate(lote["bilhetes"]):
        dezs_str = " - ".join([f"{n:02d}" for n in sorted(b["dezenas"])])
        texto += f"Jogo {i+1:02d} [{b['tipo']} Dez]: {dezs_str}\n"
    return texto

# =====================================================================
# INTERFACE E MÓDULOS
# =====================================================================
st.sidebar.markdown("<h2 style='color: #1E3A8A;'>📈 LotoPro Ultimate</h2>", unsafe_allow_html=True)
st.sidebar.metric("🏦 Saldo Disponível", formatar_moeda(st.session_state.banca))
st.sidebar.metric("🎯 Próximo Concurso (Alvo)", st.session_state.ultimo_concurso_sincronizado + 1)
st.sidebar.markdown("---")

menu = st.sidebar.radio("Módulos do Sistema", [
    "1. Cérebro & Gerador", 
    "2. Os Meus Bilhetes (Exportar)", 
    "3. Sincronização Caixa (API)", 
    "4. Banco de Dados & Cofre"
])

# ---------------------------------------------------------------------
# MÓDULO 1: GERADOR
# ---------------------------------------------------------------------
if menu == "1. Cérebro & Gerador":
    st.header("🧠 Matriz de Inteligência Artificial")
    
    concurso_alvo = st.session_state.ultimo_concurso_sincronizado + 1
    st.markdown(f"**Operando Fechamentos para o Concurso Alvo:** `< {concurso_alvo} >`")
    
    if not st.session_state.historico_dados:
        st.warning("⚠️ Banco de Dados Vazio! Vá ao Módulo 3 e sincronize com a Caixa para a IA obter dados.")
    else:
        matriz, quentes, medias, frias = motor_inteligencia_equilibrada()
        
        with st.container(border=True):
            st.markdown("### 📊 Raio-X da Matriz Equilibrada (18 Dezenas)")
            st.write("A IA abandonou o método amador de 'apenas as mais quentes' e construiu uma matriz matemática cobrindo as tendências de variância do globo da Caixa:")
            col1, col2, col3 = st.columns(3)
            col1.error(f"🔥 **9 Quentes:**\n\n`{sorted(quentes)}`")
            col2.warning(f"⚖️ **5 Intermediárias:**\n\n`{sorted(medias)}`")
            col3.info(f"❄️ **4 Frias (Atrasadas):**\n\n`{sorted(frias)}`")
            st.success(f"🧬 **Matriz Base de Geração:** `{matriz}`")

        st.markdown("---")
        with st.container(border=True):
            st.markdown("### ⚙️ Configuração Financeira do Lote")
            colA, colB = st.columns(2)
            orcamento = colA.number_input("Orçamento Máximo (R$):", min_value=3.50, value=59.50, step=3.50)
            estrategia = colB.selectbox("Estratégia do Fechamento:", ["Híbrida (16 e 15 Dezenas)", "Somente 15 Dezenas", "Somente 16 Dezenas"])
            
            if st.button("🚀 Gerar Fechamento Algorítmico", use_container_width=True, type="primary"):
                if orcamento > st.session_state.banca:
                    st.error(f"❌ Orçamento ({formatar_moeda(orcamento)}) excede o Caixa ({formatar_moeda(st.session_state.banca)}).")
                else:
                    with st.spinner("Compilando jogos matematicamente validados..."):
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

                        custo_final = orcamento - caixa_temp
                        st.session_state.banca -= custo_final
                        st.session_state.lote_ativo = {
                            "concurso_alvo": concurso_alvo,
                            "data": datetime.now().strftime("%d/%m/%Y às %H:%M"),
                            "custo": custo_final,
                            "bilhetes": jogos,
                            "status": "Aguardando Sorteio"
                        }
                    st.success(f"✅ Jogos processados com sucesso! O valor de {formatar_moeda(custo_final)} foi descontado da Banca. Verifique o 'Módulo 2'.")

# ---------------------------------------------------------------------
# MÓDULO 2: OS MEUS BILHETES & EXPORTAÇÃO
# ---------------------------------------------------------------------
elif menu == "2. Os Meus Bilhetes (Exportar)":
    st.header("🎫 Gestão de Bilhetes Gerados")
    lote = st.session_state.lote_ativo
    
    if not lote:
        st.info("Nenhum lote de apostas pendente. Gere jogos no Módulo 1.")
    else:
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            col1.metric("🎯 Concurso Alvo", lote['concurso_alvo'])
            col2.metric("💳 Investimento do Lote", formatar_moeda(lote['custo']))
            col3.metric("📊 Status", lote['status'])
            
            # BOTÃO DE EXPORTAÇÃO (.TXT)
            texto_exportacao = exportar_bilhetes_txt(lote)
            st.download_button(
                label="📥 Exportar Jogos para Bloco de Notas (.txt)",
                data=texto_exportacao,
                file_name=f"LotoPro_Concurso_{lote['concurso_alvo']}.txt",
                mime="text/plain",
                type="primary",
                use_container_width=True
            )
        
        st.markdown("### Detalhamento Visual dos Jogos")
        for i, b in enumerate(lote["bilhetes"]):
            cor_fundo = "#e8f5e9" if b["tipo"] == 15 else "#e3f2fd"
            borda = "#2e7d32" if b["tipo"] == 15 else "#1565c0"
            dezenas_formatadas = " - ".join([f"{n:02d}" for n in sorted(b["dezenas"])])
            st.markdown(f"""
            <div style="background-color: {cor_fundo}; border-left: 5px solid {borda}; padding: 10px; margin-bottom: 10px; border-radius: 4px;">
                <b style="color: {borda};">Jogo {i+1:02d} | Categoria: {b['tipo']} Dezenas</b><br>
                <span style="font-family: monospace; font-size: 18px; color: #333;">{dezenas_formatadas}</span>
            </div>
            """, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# MÓDULO 3: SINCRONIZAÇÃO API CAIXA
# ---------------------------------------------------------------------
elif menu == "3. Sincronização Caixa (API)":
    st.header("📡 Ligação Direta Caixa Econômica")
    st.write("Baixe o resultado oficial, audite os seus jogos automaticamente e engorde a base de dados da IA.")
    
    with st.container(border=True):
        concurso = st.text_input("Nº do Concurso para baixar (Deixe vazio para puxar o último sorteado):")
        if st.button("Sincronizar Oficial", type="primary", use_container_width=True):
            with st.spinner("Consultando servidores da Caixa..."):
                res = buscar_sorteio_caixa(concurso)
                if res["sucesso"]:
                    conc = res["concurso"]
                    st.session_state.ultimo_concurso_sincronizado = conc
                    
                    st.success(f"✅ Concurso {conc} verificado com sucesso!")
                    st.info(f"**Dezenas Sorteadas:** `{res['dezenas']}`")
                    
                    if not any(d["concurso"] == conc for d in st.session_state.historico_dados):
                        st.session_state.historico_dados.append({"concurso": conc, "dezenas": res['dezenas']})
                        st.write("💾 O sorteio foi arquivado na base de dados da Inteligência.")
                    
                    # AUDITORIA DOS JOGOS
                    lote = st.session_state.lote_ativo
                    if lote and lote["concurso_alvo"] == conc and lote["status"] != "Conferido e Liquidado":
                        st.markdown("### 🏆 Auditoria Oficial do Lote")
                        total_ganho = 0.0
                        for i, b in enumerate(lote["bilhetes"]):
                            acertos = len(set(b["dezenas"]).intersection(res['dezenas']))
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
                                st.success(f"🎉 **Jogo {i+1} PREMIADO!** {acertos} Acertos -> **{formatar_moeda(valor)}**")
                            else:
                                st.error(f"❌ Jogo {i+1} - Sem prêmio ({acertos} acertos).")
                        
                        st.session_state.banca += total_ganho
                        st.session_state.lote_ativo["status"] = "Conferido e Liquidado"
                        st.markdown(f"### 💰 Resultado Financeiro: {formatar_moeda(total_ganho)} creditados na Banca.")
                else:
                    st.error(res["erro"])

# ---------------------------------------------------------------------
# MÓDULO 4: CAIXA E BACKUP
# ---------------------------------------------------------------------
elif menu == "4. Banco de Dados & Cofre":
    st.header("🏦 Administração Financeira e Cofre JSON")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.metric("Saldo em Caixa (Real)", formatar_moeda(st.session_state.banca))
            aporte = st.number_input("Adicionar Capital (R$):", min_value=0.0, step=50.0)
            if st.button("Injetar na Banca", use_container_width=True):
                st.session_state.banca += aporte
                st.success(f"Novo saldo: {formatar_moeda(st.session_state.banca)}")
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### 💾 Exportar Cofre (Save Game)")
            estado = {
                "banca": st.session_state.banca,
                "historico_dados": st.session_state.historico_dados,
                "lote_ativo": st.session_state.lote_ativo,
                "ultimo_concurso_sincronizado": st.session_state.ultimo_concurso_sincronizado
            }
            st.download_button("📤 Descarregar Cofre de Segurança (.json)", json.dumps(estado), "LotoPro_Backup.json", "application/json", type="primary", use_container_width=True)
            
            st.markdown("### 📥 Restaurar Cofre")
            arquivo = st.file_uploader("Envie seu LotoPro_Backup.json:", type=["json"])
            if arquivo is not None:
                try:
                    d = json.load(arquivo)
                    st.session_state.banca = d.get("banca", 0.0)
                    st.session_state.historico_dados = d.get("historico_dados", [])
                    st.session_state.lote_ativo = d.get("lote_ativo", None)
                    st.session_state.ultimo_concurso_sincronizado = d.get("ultimo_concurso_sincronizado", 3693)
                    st.success("✅ Sistema restaurado perfeitamente!")
                    st.rerun()
                except:
                    st.error("Erro na leitura do cofre.")
