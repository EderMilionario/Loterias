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
# CONFIGURAÇÕES E PREÇOS 
# =====================================================================
st.set_page_config(page_title="LotoPro — Terminal Profissional", page_icon="📈", layout="wide")

PRECO_15 = 3.50
PRECO_16 = 56.00
PREMIO_11 = 7.00
PREMIO_12 = 14.00
PREMIO_13 = 35.00

def formatar_moeda(valor):
    """Formata para o padrão brasileiro: R$ 1.500,00"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =====================================================================
# AUTENTICAÇÃO E INICIALIZAÇÃO DE ESTADO
# =====================================================================
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔒 LotoPro - Terminal Profissional")
    senha = st.text_input("Credencial de Operador:", type="password")
    if st.button("Autenticar", type="primary"):
        if senha == "7777":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Acesso Negado.")
    st.stop()

if 'banca' not in st.session_state: st.session_state.banca = 200.0
if 'lote_ativo' not in st.session_state: st.session_state.lote_ativo = None
if 'historico_dados' not in st.session_state: st.session_state.historico_dados = []

# =====================================================================
# MOTOR DE IA E API CAIXA
# =====================================================================
def buscar_sorteio_caixa(concurso=""):
    url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{concurso}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        req = requests.get(url, headers=headers, timeout=10, verify=False)
        if req.status_code == 200:
            dados = req.json()
            dezenas = sorted([int(d) for d in dados['listaDezenas']])
            v14, v15 = 1500.00, 1500000.00
            for r in dados.get('listaRateioPremio', []):
                if r['faixa'] == 1: v15 = r['valorPremio']
                elif r['faixa'] == 2: v14 = r['valorPremio']
            return {"sucesso": True, "concurso": dados['numero'], "dezenas": dezenas, "data": dados['dataApuracao'], "v14": v14, "v15": v15}
        return {"sucesso": False, "erro": "Sorteio não encontrado."}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

def motor_inteligencia():
    if not st.session_state.historico_dados: return []
    todas = [n for s in st.session_state.historico_dados for n in s["dezenas"]]
    return [n for n, c in Counter(todas).most_common(18)]

def validar_matematica(jogo):
    soma = sum(jogo)
    impares = len([x for x in jogo if x % 2 != 0])
    primos = len([x for x in jogo if x in [2, 3, 5, 7, 11, 13, 17, 19, 23]])
    return (180 <= soma <= 220) and (6 <= impares <= 9) and (4 <= primos <= 7)

def calcular_auditoria(jogo, sorteadas, v14, v15):
    acertos = len(set(jogo).intersection(sorteadas))
    tamanho = len(jogo)
    valor = 0.0
    detalhe = "Sem prémio"
    
    if tamanho == 15:
        if acertos == 11: valor, detalhe = PREMIO_11, "1x Prémio 11"
        elif acertos == 12: valor, detalhe = PREMIO_12, "1x Prémio 12"
        elif acertos == 13: valor, detalhe = PREMIO_13, "1x Prémio 13"
        elif acertos == 14: valor, detalhe = v14, "1x Prémio 14"
        elif acertos == 15: valor, detalhe = v15, "Prémio Máximo (15)!"
    elif tamanho == 16:
        if acertos == 11: valor, detalhe = 5 * PREMIO_11, "5x Prémio 11"
        elif acertos == 12: valor, detalhe = (4 * PREMIO_12) + (12 * PREMIO_11), "Múltiplo 12 Acertos"
        elif acertos == 13: valor, detalhe = (3 * PREMIO_13) + (13 * PREMIO_12), "Múltiplo 13 Acertos"
        elif acertos == 14: valor, detalhe = (2 * v14) + (14 * PREMIO_13), "Múltiplo 14 Acertos"
        elif acertos == 15: valor, detalhe = v15 + (15 * v14), "Prémio Máximo (Múltiplo)!"
    return acertos, valor, detalhe

# =====================================================================
# INTERFACE E NAVEGAÇÃO
# =====================================================================
st.sidebar.markdown("### 📊 LotoPro Terminal")
st.sidebar.metric("Saldo em Caixa", formatar_moeda(st.session_state.banca))
st.sidebar.info(f"📚 Base de Dados: {len(st.session_state.historico_dados)} Sorteios")

menu = st.sidebar.radio("Módulos do Sistema", [
    "1. Gerador Analítico", 
    "2. Os Meus Bilhetes", 
    "3. Conferência & API", 
    "4. Caixa & Backup"
])

# ---------------------------------------------------------------------
# MÓDULO 1: GERADOR
# ---------------------------------------------------------------------
if menu == "1. Gerador Analítico":
    st.header("🧠 Inteligência e Geração de Fechamentos")
    
    if not st.session_state.historico_dados:
        st.warning("Base de dados vazia. Vá ao módulo 3 e sincronize a API da Caixa.")
    else:
        top_18 = motor_inteligencia()
        with st.expander("🔍 Transparência do Algoritmo (Como o sistema pensa)", expanded=True):
            st.write(f"O sistema analisou o histórico de **{len(st.session_state.historico_dados)}** sorteios oficiais.")
            st.markdown(f"**Matriz Base (As 18 dezenas mais quentes):** `{sorted(top_18)}`")
            st.write("**Lógica de Filtragem Aplicada:**")
            st.write("O sistema usa a matemática combinatória para gerar todas as combinações possíveis destas 18 dezenas, e depois elimina os jogos 'lixo' usando filtros de probabilidade (Soma de 180 a 220, 6 a 9 Ímpares, e 4 a 7 Primos). O que sobra é o FECHAMENTO DE ELITE.")

        st.markdown("---")
        orcamento = st.number_input("Orçamento para esta operação (R$):", min_value=3.50, value=59.50, step=3.50)
        
        estrategia = st.radio("Selecione o tipo de Fechamento:", [
            "Híbrido (Priorizar 16 dezenas, preencher troco com 15)",
            "Apenas 15 Dezenas",
            "Apenas 16 Dezenas"
        ])
        
        if st.button("Processar Fechamento Algorítmico", type="primary"):
            if orcamento > st.session_state.banca:
                st.error(f"Erro: Orçamento ({formatar_moeda(orcamento)}) excede o Saldo em Caixa ({formatar_moeda(st.session_state.banca)}).")
            else:
                with st.status("A processar algoritmo...", expanded=True) as status:
                    st.write("Gerando combinações matemáticas...")
                    jogos = []
                    caixa_temp = orcamento
                    
                    if "Híbrido" in estrategia or "16" in estrategia:
                        qtd_16 = int(caixa_temp // PRECO_16)
                        if qtd_16 > 0:
                            st.write(f"Filtrando matrizes para jogos de 16 dezenas...")
                            cand_16 = [j for j in itertools.combinations(top_18, 16) if validar_matematica(j)]
                            escolhas = random.sample(cand_16, min(qtd_16, len(cand_16))) if cand_16 else []
                            for j in escolhas:
                                jogos.append({"tipo": 16, "dezenas": list(j)})
                                caixa_temp -= PRECO_16

                    if "Híbrido" in estrategia or "15" in estrategia:
                        qtd_15 = int(caixa_temp // PRECO_15)
                        if qtd_15 > 0:
                            st.write(f"Filtrando matrizes para jogos de 15 dezenas...")
                            cand_15 = [j for j in itertools.combinations(top_18, 15) if validar_matematica(j)]
                            escolhas = random.sample(cand_15, min(qtd_15, len(cand_15))) if cand_15 else []
                            for j in escolhas:
                                jogos.append({"tipo": 15, "dezenas": list(j)})
                                caixa_temp -= PRECO_15

                    custo_final = orcamento - caixa_temp
                    st.session_state.banca -= custo_final
                    
                    st.session_state.lote_ativo = {
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "custo": custo_final,
                        "bilhetes": jogos,
                        "status": "Aguardando Auditoria"
                    }
                    status.update(label="Fechamento Concluído e Salvo!", state="complete", expanded=False)
                
                st.success(f"✅ Sucesso! O valor de {formatar_moeda(custo_final)} foi debitado da banca. Vá ao 'Módulo 2' para ver os bilhetes gerados.")

# ---------------------------------------------------------------------
# MÓDULO 2: OS MEUS BILHETES
# ---------------------------------------------------------------------
elif menu == "2. Os Meus Bilhetes":
    st.header("🎫 Lote Ativo")
    if not st.session_state.lote_ativo:
        st.warning("Não há nenhum bilhete gerado aguardando sorteio.")
    else:
        lote = st.session_state.lote_ativo
        st.info(f"**Status:** {lote['status']} | **Gerado em:** {lote['data']} | **Custo Total:** {formatar_moeda(lote['custo'])}")
        st.markdown("---")
        for i, b in enumerate(lote["bilhetes"]):
            cor = "#cce5ff" if b["tipo"] == 16 else "#e2e3e5"
            st.markdown(f"""
            <div style="background-color: {cor}; padding: 10px; border-radius: 5px; margin-bottom: 8px;">
                <b>Bilhete {i+1} ({b['tipo']} dezenas):</b> <span style="font-family: monospace; font-size: 16px;">{str(sorted(b['dezenas'])).replace('[','').replace(']','')}</span>
            </div>
            """, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# MÓDULO 3: CONFERÊNCIA E API DA CAIXA
# ---------------------------------------------------------------------
elif menu == "3. Conferência & API":
    st.header("📡 Conexão Caixa e Auditoria")
    
    st.markdown("### Puxar Resultado Oficial")
    concurso = st.text_input("Nº do Concurso (Deixe em branco para o último):")
    if st.button("Sincronizar com Servidor Caixa", type="primary"):
        with st.spinner("Conectando à API da Caixa..."):
            res = buscar_sorteio_caixa(concurso)
            if res["sucesso"]:
                conc = res["concurso"]
                st.success(f"✅ Sorteio {conc} sincronizado com sucesso!")
                st.write(f"**Dezenas:** `{res['dezenas']}`")
                st.write(f"**Prémios Oficiais:** 14 Acertos = {formatar_moeda(res['v14'])} | 15 Acertos = {formatar_moeda(res['v15'])}")
                
                # Guarda no histórico
                if not any(d["concurso"] == conc for d in st.session_state.historico_dados):
                    st.session_state.historico_dados.append({"concurso": conc, "dezenas": res['dezenas']})
                
                # Auditar bilhetes
                if st.session_state.lote_ativo and st.session_state.lote_ativo["status"] != "Auditado":
                    st.markdown("---")
                    st.subheader("🔍 Auditoria do Seu Lote")
                    total_ganho = 0.0
                    for i, b in enumerate(st.session_state.lote_ativo["bilhetes"]):
                        ac, val, det = calcular_auditoria(b["dezenas"], res['dezenas'], res['v14'], res['v15'])
                        total_ganho += val
                        if val > 0:
                            st.markdown(f"<div style='color: green; font-weight: bold;'>🎉 Bilhete {i+1} ({b['tipo']} dez) PREMIADO! {ac} Acertos -> {formatar_moeda(val)} ({det})</div>", unsafe_allow_html=True)
                        else:
                            st.write(f"❌ Bilhete {i+1} ({b['tipo']} dez) - {ac} acertos.")
                    
                    st.session_state.banca += total_ganho
                    st.session_state.lote_ativo["status"] = "Auditado"
                    st.info(f"O saldo da sua banca foi atualizado com o prémio total de {formatar_moeda(total_ganho)}.")
            else:
                st.error(res["erro"])

# ---------------------------------------------------------------------
# MÓDULO 4: CAIXA E BACKUP
# ---------------------------------------------------------------------
elif menu == "4. Caixa & Backup":
    st.header("🏦 Gestão Financeira e Cofre JSON")
    
    col1, col2 = st.columns(2)
    col1.metric("Saldo Atual da Banca", formatar_moeda(st.session_state.banca))
    
    st.markdown("### 💸 Injetar Saldo")
    novo_aporte = st.number_input("Adicionar dinheiro à Banca (R$):", min_value=0.0, step=50.0)
    if st.button("Depositar na Banca"):
        st.session_state.banca += novo_aporte
        st.success(f"✅ Depósito de {formatar_moeda(novo_aporte)} efetuado! Novo saldo: {formatar_moeda(st.session_state.banca)}")
        st.rerun()

    st.markdown("---")
    st.markdown("### 📥 Backup do Sistema (Salvar Progresso)")
    estado = {
        "banca": st.session_state.banca,
        "historico_dados": st.session_state.historico_dados,
        "lote_ativo": st.session_state.lote_ativo
    }
    st.download_button("📤 Descarregar Cofre (.json)", json.dumps(estado), "Meu_Cofre_LotoPro.json", "application/json", type="primary")
    
    st.markdown("### 📤 Restaurar Sistema")
    arquivo = st.file_uploader("Suba o ficheiro Meu_Cofre_LotoPro.json:", type=["json"])
    if arquivo is not None:
        try:
            dados = json.load(arquivo)
            st.session_state.banca = dados.get("banca", 0.0)
            st.session_state.historico_dados = dados.get("historico_dados", [])
            st.session_state.lote_ativo = dados.get("lote_ativo", None)
            st.success("✅ Cofre restaurado com sucesso!")
            st.rerun()
        except:
            st.error("Erro ao ler ficheiro.")
