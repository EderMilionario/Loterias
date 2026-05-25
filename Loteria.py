import streamlit as st
import itertools
import random
import json
from collections import Counter
from datetime import datetime

# =====================================================================
# CONFIGURAÇÕES E PREÇOS ATUAIS (ATUALIZADOS)
# =====================================================================
st.set_page_config(page_title="LotoPro Ultimate", page_icon="💎", layout="wide")

PRECO_15 = 3.50
PRECO_16 = 56.00

# Prémios Fixos Oficiais
PREMIO_11 = 7.00
PREMIO_12 = 14.00
PREMIO_13 = 35.00

# =====================================================================
# INICIALIZAÇÃO DE ESTADO E BANCO DE DADOS
# =====================================================================
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔒 LotoPro Ultimate - Acesso")
    senha = st.text_input("Senha de Operador:", type="password")
    if st.button("Entrar", type="primary"):
        if senha == "7777":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Acesso Negado.")
    st.stop()

# Variáveis do Sistema
if 'banca' not in st.session_state: st.session_state.banca = 200.0
if 'lote_ativo' not in st.session_state: st.session_state.lote_ativo = None
if 'historico_dados' not in st.session_state:
    # Estrutura base de dados: armazena como dicionários para saber exatamente o concurso
    st.session_state.historico_dados = [
        {"concurso": 3643, "dezenas": [1, 2, 3, 5, 6, 8, 10, 11, 14, 15, 17, 20, 21, 23, 24]},
        {"concurso": 3644, "dezenas": [2, 4, 5, 7, 9, 10, 12, 13, 16, 17, 18, 20, 22, 24, 25]}
        # O sistema irá adicionar novos sorteios aqui!
    ]

# =====================================================================
# MOTOR DE INTELIGÊNCIA (IA) E REGRAS MATEMÁTICAS
# =====================================================================
def analisar_frequencias():
    # Extrai apenas as dezenas de todo o histórico para análise
    todas = [n for sorteio in st.session_state.historico_dados for n in sorteio["dezenas"]]
    return Counter(todas)

def filtro_matematico(jogo):
    soma = sum(jogo)
    impares = len([x for x in jogo if x % 2 != 0])
    primos = len([x for x in jogo if x in [2, 3, 5, 7, 11, 13, 17, 19, 23]])
    return (180 <= soma <= 220) and (6 <= impares <= 9) and (4 <= primos <= 7)

def calcular_premio_real(jogo, sorteadas, valor_14, valor_15):
    acertos = len(set(jogo).intersection(sorteadas))
    tamanho = len(jogo)
    valor = 0.0
    detalhe = "Sem prémio"

    if tamanho == 15:
        if acertos == 11: valor = PREMIO_11; detalhe = "1x Prémio 11"
        elif acertos == 12: valor = PREMIO_12; detalhe = "1x Prémio 12"
        elif acertos == 13: valor = PREMIO_13; detalhe = "1x Prémio 13"
        elif acertos == 14: valor = valor_14; detalhe = "1x Prémio 14"
        elif acertos == 15: valor = valor_15; detalhe = "Prémio Máximo!"
    
    elif tamanho == 16:
        # Matemática de apostas múltiplas exata da Lotofácil (16 dezenas)
        if acertos == 11: 
            valor = 5 * PREMIO_11
            detalhe = "5x Prémio 11"
        elif acertos == 12: 
            valor = (4 * PREMIO_12) + (12 * PREMIO_11)
            detalhe = "4x Prémio 12 + 12x Prémio 11"
        elif acertos == 13: 
            valor = (3 * PREMIO_13) + (13 * PREMIO_12)
            detalhe = "3x Prémio 13 + 13x Prémio 12"
        elif acertos == 14: 
            valor = (2 * valor_14) + (14 * PREMIO_13)
            detalhe = "2x Prémio 14 + 14x Prémio 13"
        elif acertos == 15: 
            valor = valor_15 + (15 * valor_14)
            detalhe = "1x Prémio 15 + 15x Prémio 14"

    return acertos, valor, detalhe

# =====================================================================
# INTERFACE DO SISTEMA
# =====================================================================
st.sidebar.markdown("## 💎 LotoPro Ultimate")
st.sidebar.metric("Saldo em Caixa", f"R$ {st.session_state.banca:.2f}")
st.sidebar.info(f"📚 Histórico: {len(st.session_state.historico_dados)} sorteios na base.")

menu = st.sidebar.radio("Navegação", [
    "1. Cérebro & Gerador", 
    "2. Conferência de Sorteio", 
    "3. Cofre e Banco de Dados"
])

# ---------------------------------------------------------------------
# ABA 1: GERADOR INTELIGENTE
# ---------------------------------------------------------------------
if menu == "1. Cérebro & Gerador":
    st.header("🧠 Inteligência e Geração de Bilhetes")
    
    freq = analisar_frequencias()
    top_18 = [n for n, c in freq.most_common(18)]
    
    with st.expander("📊 Transparência: Ver Análise do Motor (Cérebro)", expanded=True):
        st.write("**As 18 dezenas mais quentes da sua Base de Dados:**")
        st.code(sorted(top_18))
        st.write("*(O sistema cruza estas tendências com a probabilidade matemática usando filtros para criar o fechamento perfeito).*")

    st.markdown("---")
    orcamento = st.number_input("Orçamento para esta rodada (R$):", min_value=3.50, value=59.50, step=3.50)
    
    if st.button("Executar IA (Estratégia Híbrida)", type="primary"):
        if orcamento > st.session_state.banca:
            st.error("Orçamento superior ao saldo em caixa! Vá à Aba 3 para adicionar fundos.")
        else:
            with st.spinner("A calcular probabilidades e cruzar dados..."):
                jogos = []
                caixa_temp = orcamento
                
                # Tenta gerar de 16 primeiro
                qtd_16 = int(caixa_temp // PRECO_16)
                if qtd_16 > 0:
                    cand_16 = [j for j in itertools.combinations(top_18, 16) if filtro_matematico(j)]
                    escolhidos_16 = random.sample(cand_16, min(qtd_16, len(cand_16))) if cand_16 else []
                    for j in escolhidos_16:
                        jogos.append({"tipo": 16, "dezenas": list(j)})
                        caixa_temp -= PRECO_16
                
                # Preenche com de 15
                qtd_15 = int(caixa_temp // PRECO_15)
                if qtd_15 > 0:
                    cand_15 = [j for j in itertools.combinations(top_18, 15) if filtro_matematico(j)]
                    escolhidos_15 = random.sample(cand_15, min(qtd_15, len(cand_15))) if cand_15 else []
                    for j in escolhidos_15:
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
                
                st.success("✅ Fechamento Gerado!")
                st.info(f"Foram gastos R$ {custo_final:.2f}. O troco de R$ {caixa_temp:.2f} foi mantido na banca.")
                
                for i, b in enumerate(jogos):
                    cor = "blue" if b["tipo"] == 16 else "green"
                    st.markdown(f"**Bilhete {i+1}** (:{cor}[{b['tipo']} dezenas]): `{sorted(b['dezenas'])}`")

# ---------------------------------------------------------------------
# ABA 2: CONFERÊNCIA E SINCRONIZAÇÃO DADOS OFICIAIS
# ---------------------------------------------------------------------
elif menu == "2. Conferência de Sorteio":
    st.header("🎯 Auditoria e Sincronização Dinâmica")
    st.write("Indique o sorteio, o resultado e os prémios variáveis do dia. O sistema irá auditar os bilhetes, pagar os prémios à sua banca e **guardar o sorteio no seu Histórico**.")
    
    colA, colB = st.columns(2)
    numero_concurso = colA.number_input("Número do Concurso (Sorteio):", min_value=1, step=1, value=3693)
    entrada_sorteio = colB.text_input("15 Números (separados por vírgula):")
    
    st.write("💰 **Valores Oficiais da Caixa para este sorteio:**")
    colC, colD = st.columns(2)
    valor_14_hoje = colC.number_input("Valor Prémio 14 (R$):", value=1500.00, step=100.0)
    valor_15_hoje = colD.number_input("Valor Prémio 15 (R$):", value=1500000.00, step=10000.0)
    
    if st.button("Auditar Jogos e Salvar Sorteio", type="primary"):
        if not entrada_sorteio:
            st.error("Insira o resultado oficial.")
        else:
            try:
                sorteio = sorted([int(x.strip()) for x in entrada_sorteio.split(",")])
                if len(sorteio) != 15:
                    st.error("Tem que inserir exatamente 15 dezenas.")
                else:
                    # Sincroniza Banco de Dados
                    concurso_existe = any(d["concurso"] == numero_concurso for d in st.session_state.historico_dados)
                    if not concurso_existe:
                        st.session_state.historico_dados.append({"concurso": numero_concurso, "dezenas": sorteio})
                        st.success(f"💾 O concurso {numero_concurso} foi adicionado à inteligência do robô!")
                    else:
                        st.warning(f"O concurso {numero_concurso} já existia na base e não foi duplicado.")

                    # Auditoria (se houver lote)
                    if not st.session_state.lote_ativo or st.session_state.lote_ativo["status"] == "Auditado":
                        st.info("O sorteio foi salvo, mas não havia bilhetes pendentes para este concurso.")
                    else:
                        total_premios = 0.0
                        st.markdown("### Resultados do Seu Lote")
                        for i, b in enumerate(st.session_state.lote_ativo["bilhetes"]):
                            acertos, valor, detalhe = calcular_premio_real(b["dezenas"], sorteio, valor_14_hoje, valor_15_hoje)
                            total_premios += valor
                            
                            if valor > 0:
                                st.markdown(f"""
                                <div style="background-color: #d4edda; padding: 10px; border-left: 5px solid #28a745; margin-bottom: 5px;">
                                    <b style="color: #155724;">✅ Bilhete {i+1} PREMIADO! ({b['tipo']} dezenas)</b><br>
                                    <span style="color: #155724;">Acertos: <b>{acertos}</b> | Retorno: <b>R$ {valor:.2f}</b> <i>({detalhe})</i></span><br>
                                    <code style="color: black; background: transparent;">{sorted(b['dezenas'])}</code>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.write(f"❌ Bilhete {i+1} ({b['tipo']} dez) — {acertos} acertos.")
                        
                        st.session_state.banca += total_premios
                        st.session_state.lote_ativo["status"] = "Auditado"
                        st.success(f"🎉 R$ {total_premios:.2f} ganhos! Saldo atualizado para R$ {st.session_state.banca:.2f}.")

                    st.info("👉 Vá à Aba 3 e faça o download do Cofre para garantir que este sorteio não se perca!")
            except:
                st.error("Formato inválido. Use vírgulas para separar as dezenas.")

# ---------------------------------------------------------------------
# ABA 3: GESTÃO E BACKUP (COFRE E BANCO DE DADOS)
# ---------------------------------------------------------------------
elif menu == "3. Cofre e Banco de Dados":
    st.header("💾 Cofre de Segurança do Sistema")
    st.write("Ao fazer o download do cofre, estás a salvar todo o teu histórico oficial de sorteios, as tuas apostas e a tua banca financeira.")
    
    col1, col2 = st.columns(2)
    col1.metric("Saldo Atual da Banca", f"R$ {st.session_state.banca:.2f}")
    col2.metric("Tamanho do Banco de Dados", f"{len(st.session_state.historico_dados)} Sorteios Registados")
    
    st.markdown("---")
    st.subheader("📥 Exportar Sistema Completo (.json)")
    
    estado_total = {
        "banca": st.session_state.banca,
        "historico_dados": st.session_state.historico_dados,
        "lote_ativo": st.session_state.lote_ativo
    }
    json_export = json.dumps(estado_total)
    
    st.download_button(
        label="Download Cofre Atualizado (LotoPro_Backup.json)",
        data=json_export,
        file_name="LotoPro_Backup.json",
        mime="application/json",
        type="primary"
    )
    
    st.markdown("---")
    st.subheader("📤 Importar Cofre Anterior")
    arquivo = st.file_uploader("Carregue o seu LotoPro_Backup.json para restaurar o banco de dados:", type=["json"])
    if arquivo is not None:
        try:
            dados = json.load(arquivo)
            st.session_state.banca = dados.get("banca", 200.0)
            st.session_state.historico_dados = dados.get("historico_dados", [])
            st.session_state.lote_ativo = dados.get("lote_ativo", None)
            st.success("✅ Sistema e Inteligência restaurados com sucesso!")
            st.rerun()
        except:
            st.error("Ficheiro inválido ou corrompido.")
