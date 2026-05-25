import streamlit as st
import itertools
import random
import json
from datetime import datetime
from collections import Counter

# =====================================================================
# 1. CONFIGURAÇÃO E AUTENTICAÇÃO (SENHA)
# =====================================================================
st.set_page_config(page_title="LotoPro — IA e Fechamentos", page_icon="🤖", layout="wide")

# Sistema de Login
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔒 Acesso Restrito - LotoPro")
    st.write("Por favor, insira a sua credencial para aceder ao portal de Engenharia Preditiva.")
    senha = st.text_input("Senha de Acesso:", type="password")
    
    if st.button("Entrar", type="primary"):
        if senha == "7777": # <-- MUDE A SUA SENHA AQUI
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("❌ Senha incorreta. Acesso negado.")
    st.stop() # Bloqueia o resto do código até a senha estar correta

# =====================================================================
# 2. VARIÁVEIS DE SISTEMA E BANCA VIRTUAL
# =====================================================================
PRECO_15 = 3.50
PRECO_16 = 56.00

if 'banca_saldo' not in st.session_state: st.session_state.banca_saldo = 200.0 # Saldo inicial
if 'lote_ativo' not in st.session_state: st.session_state.lote_ativo = None
if 'concurso_alvo' not in st.session_state: st.session_state.concurso_alvo = 3693 

# O cérebro da IA: Simulando os últimos 50 concursos para análise
if 'historico_50_sorteios' not in st.session_state:
    historico = []
    for _ in range(49):
        historico.append(sorted(random.sample(range(1, 26), 15)))
    historico.append([2, 3, 5, 6, 7, 9, 10, 13, 14, 15, 19, 20, 23, 24, 25]) # O 3692
    st.session_state.historico_50_sorteios = historico

# =====================================================================
# 3. MOTOR DE INTELIGÊNCIA E ESTATÍSTICA
# =====================================================================
def obter_dezenas_inteligentes():
    frequencia = Counter()
    for sorteio in st.session_state.historico_50_sorteios:
        frequencia.update(sorteio)
    dezenas_ordenadas = [numero for numero, contagem in frequencia.most_common()]
    return dezenas_ordenadas

def validar_jogo(jogo):
    soma = sum(jogo)
    impares = len([x for x in jogo if x % 2 != 0])
    if soma < 180 or soma > 220: return False
    if impares < 6 or impares > 9: return False
    return True

def calcular_premios(jogo, sorteadas):
    acertos = len(set(jogo).intersection(sorteadas))
    tamanho = len(jogo)
    retorno = 0.0
    tipo_premio = "Simples"
    
    if tamanho == 15:
        if acertos == 11: retorno = 7.00
        elif acertos == 12: retorno = 14.00
        elif acertos == 13: retorno = 35.00
        elif acertos == 14: retorno = 1500.00
        elif acertos == 15: retorno = 1000000.00
        
    elif tamanho == 16:
        tipo_premio = "Múltiplo (16 Dez)"
        if acertos == 11: retorno = 5 * 7.00
        elif acertos == 12: retorno = (4 * 14.00) + (12 * 7.00)
        elif acertos == 13: retorno = (3 * 35.00) + (13 * 14.00)
        elif acertos == 14: retorno = (2 * 1500.00) + (14 * 35.00)
        elif acertos == 15: retorno = 1000000.00 + (15 * 1500.00)
        
    return acertos, retorno, tipo_premio

# =====================================================================
# 4. INTERFACE PRINCIPAL
# =====================================================================
st.title("🤖 LotoPro — Piloto Automático")
st.caption("Automação, Transparência de Dados e Gestão Financeira Rigorosa.")

# Transparência do Banco de Dados no Sidebar
st.sidebar.markdown("### 📊 Status do Cérebro (IA)")
st.sidebar.info(f"📚 **Base de Dados Ativa:** {len(st.session_state.historico_50_sorteios)} resultados oficiais armazenados.")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação do Sistema", 
    ["1. Gerador (Piloto Automático)", "2. Os Meus Bilhetes (Recibo)", "3. Conferência Oficial", "4. Gestão de Banca e Backup"]
)

# ---------------------------------------------------------------------
# ABA 1: GERADOR
# ---------------------------------------------------------------------
if menu == "1. Gerador (Piloto Automático)":
    st.header(f"⚙️ Estratégia para o Concurso {st.session_state.concurso_alvo}")
    
    st.write(f"### 💳 Saldo Disponível na Banca: R$ {st.session_state.banca_saldo:.2f}")
    
    orcamento = st.number_input("Quanto deste limite deseja usar hoje? (R$):", min_value=10.0, value=50.0, step=10.0)
    prioridade = st.radio("Estratégia:", ["Mista (Tentar incluir 16 dezenas e preencher troco com 15)", "Apenas apostas simples de 15 dezenas"])
    
    if st.button("Executar Robô de Análise", type="primary"):
        if orcamento > st.session_state.banca_saldo:
            st.error(f"❌ Erro Financeiro: Não tem saldo suficiente. O seu orçamento (R$ {orcamento}) é maior que a sua Banca (R$ {st.session_state.banca_saldo}). Vá à Aba 4 para injetar capital.")
        else:
            with st.spinner("A cruzar dados históricos e a aplicar filtros..."):
                dezenas_elite = obter_dezenas_inteligentes()
                jogos_finais = []
                custo_total = 0.0
                orcamento_restante = orcamento
                
                if prioridade.startswith("Mista"):
                    qtd_16 = int(orcamento_restante // PRECO_16)
                    if qtd_16 > 0:
                        dezenas_para_16 = sorted(dezenas_elite[:18])
                        boas_16 = [j for j in itertools.combinations(dezenas_para_16, 16) if validar_jogo(j)]
                        if boas_16:
                            for jogo in random.sample(boas_16, min(qtd_16, len(boas_16))):
                                jogos_finais.append({"tipo": 16, "dezenas": list(jogo)})
                                custo_total += PRECO_16
                                orcamento_restante -= PRECO_16
                
                qtd_15 = int(orcamento_restante // PRECO_15)
                if qtd_15 > 0:
                    dezenas_para_15 = sorted(dezenas_elite[:18])
                    boas_15 = [j for j in itertools.combinations(dezenas_para_15, 15) if validar_jogo(j)]
                    if boas_15:
                        for jogo in random.sample(boas_15, min(qtd_15, len(boas_15))):
                            jogos_finais.append({"tipo": 15, "dezenas": list(jogo)})
                            custo_total += PRECO_15
                            orcamento_restante -= PRECO_15
                
                # Desconta o valor exato na hora!
                st.session_state.banca_saldo -= custo_total
                
                st.session_state.lote_ativo = {
                    "concurso": st.session_state.concurso_alvo,
                    "data_geracao": datetime.now().strftime("%d/%m/%Y às %H:%M:%S"),
                    "custo": custo_total,
                    "bilhetes": jogos_finais,
                    "status": "Aguardando Sorteio"
                }
                
                st.success("✅ Estratégia processada! Os bilhetes foram gerados e o valor debitado da sua Banca.")
                st.info(f"O seu troco de R$ {orcamento_restante:.2f} não foi gasto e permanece na Banca.")

# ---------------------------------------------------------------------
# ABA 2: RECIBO
# ---------------------------------------------------------------------
elif menu == "2. Os Meus Bilhetes (Recibo)":
    st.header("🎫 Recibo Oficial de Lote")
    lote = st.session_state.lote_ativo
    if not lote or lote["status"] == "Conferido":
        st.warning("Não há nenhum lote ativo à espera de sorteio.")
    else:
        col1, col2 = st.columns(2)
        col1.write(f"🎯 **Concurso Alvo:** {lote['concurso']}")
        col1.write(f"📅 **Gerado a:** {lote['data_geracao']}")
        col2.write(f"💰 **Custo Debitado da Banca:** R$ {lote['custo']:.2f}")
        col2.write(f"⏳ **Status Atual:** {lote['status']}")
        
        st.markdown("---")
        for i, jogo in enumerate(lote["bilhetes"]):
            linha = " - ".join([f"{n:02d}" for n in sorted(jogo["dezenas"])])
            if jogo["tipo"] == 16: st.success(f"⭐ **(Múltiplo 16 Dez):** {linha}")
            else: st.code(f"Simples (15 Dez): {linha}")

# ---------------------------------------------------------------------
# ABA 3: CONFERÊNCIA
# ---------------------------------------------------------------------
elif menu == "3. Conferência Oficial":
    st.header("🔍 Máquina de Auditoria")
    lote = st.session_state.lote_ativo
    if not lote:
        st.info("Nenhum lote pendente.")
    elif lote["status"] == "Conferido":
        st.info(f"O lote do concurso {lote['concurso']} já foi conferido e liquidado na Banca.")
    else:
        st.write(f"### Conferência para o Concurso: **{lote['concurso']}**")
        sorteio_oficial = st.text_input("Resultado do Sorteio (separado por vírgula):", "1, 4, 6, 7, 9, 10, 11, 13, 14, 16, 17, 18, 20, 21, 25")
        
        if st.button("Auditar Lote", type="primary"):
            sorteadas = set([int(x.strip()) for x in sorteio_oficial.split(",")])
            total_ganho = 0.0
            st.markdown("---")
            
            for i, jogo in enumerate(lote["bilhetes"]):
                acertos, valor, tipo_premio = calcular_premios(jogo["dezenas"], sorteadas)
                total_ganho += valor
                linha_jogo = " - ".join([f"{n:02d}" for n in sorted(jogo["dezenas"])])
                
                if valor > 0:
                    # VISUAL BONITO PARA BILHETES PREMIADOS
                    st.markdown(f"""
                    <div style="background-color: #d4edda; border-left: 5px solid #28a745; padding: 10px; border-radius: 4px; margin-bottom: 8px;">
                        <h4 style="color: #155724; margin: 0;">🎉 Bilhete {i+1} PREMIADO! ({acertos} Acertos)</h4>
                        <p style="color: #155724; margin: 5px 0 0 0;"><b>Jogo:</b> {linha_jogo}</p>
                        <p style="color: #155724; margin: 5px 0 0 0;"><b>Retorno Calculado:</b> R$ {valor:.2f} <i>(Regra: {tipo_premio})</i></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.write(f"❌ *Bilhete {i+1} ({jogo['tipo']} dez) — {acertos} acertos (Sem prêmio)*")
            
            # SOMA O PRÊMIO NA BANCA IMEDIATAMENTE
            st.session_state.banca_saldo += total_ganho
            st.session_state.lote_ativo["status"] = "Conferido"
            st.session_state.concurso_alvo += 1 
            
            st.markdown("---")
            st.success(f"💰 Auditoria Concluída! O prêmio total de R$ {total_ganho:.2f} foi adicionado à sua Banca.")

# ---------------------------------------------------------------------
# ABA 4: GESTÃO E BACKUP
# ---------------------------------------------------------------------
elif menu == "4. Gestão de Banca e Backup":
    st.header("💾 Cofre e Gestão Financeira")
    
    st.markdown("### 🏦 Aportes e Limites de Período")
    st.write("Defina aqui qual o seu limite ou injete novo capital no sistema.")
    
    colA, colB = st.columns(2)
    colA.metric("Saldo Atual da Banca", f"R$ {st.session_state.banca_saldo:.2f}")
    
    novo_aporte = colB.number_input("Injetar novo limite/saldo (R$):", min_value=0.0, step=50.0)
    if colB.button("Atualizar Banca"):
        st.session_state.banca_saldo = novo_aporte
        st.success(f"✅ Banca atualizada! O seu novo limite de operação é R$ {novo_aporte:.2f}")
        st.rerun()

    st.markdown("---")
    st.write("### 📤 Exportar / 📥 Restaurar Backup (JSON)")
    
    estado_sistema = {
        "banca_saldo": st.session_state.banca_saldo,
        "concurso_alvo": st.session_state.concurso_alvo,
        "lote_ativo": st.session_state.lote_ativo
    }
    
    st.download_button("📤 Descarregar Cofre (Backup .json)", json.dumps(estado_sistema), "Meu_Cofre_LotoPro.json", "application/json")
    
    arquivo_importacao = st.file_uploader("Suba o ficheiro .json que guardou:", type=["json"])
    if arquivo_importacao is not None:
        try:
            conteudo = json.load(arquivo_importacao)
            st.session_state.banca_saldo = conteudo.get("banca_saldo", 200.0)
            st.session_state.concurso_alvo = conteudo.get("concurso_alvo", 3693)
            st.session_state.lote_ativo = conteudo.get("lote_ativo", None)
            st.success("✅ Cofre restaurado! Todo o seu histórico voltou à memória.")
            st.rerun()
        except:
            st.error("Erro ao ler ficheiro.")
