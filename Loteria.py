import streamlit as st
import itertools
import random
import json
import requests
from collections import Counter
from datetime import datetime

# =====================================================================
# CONFIGURAÇÕES E PREÇOS ATUAIS
# =====================================================================
st.set_page_config(page_title="LotoPro — API Caixa", page_icon="🤖", layout="wide")

PRECO_15 = 3.50
PRECO_16 = 56.00

# Prémios Fixos Oficiais
PREMIO_11 = 7.00
PREMIO_12 = 14.00
PREMIO_13 = 35.00

# =====================================================================
# INICIALIZAÇÃO E AUTENTICAÇÃO
# =====================================================================
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔒 LotoPro - Terminal Profissional")
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
if 'historico_dados' not in st.session_state: st.session_state.historico_dados = []

# =====================================================================
# COMUNICAÇÃO COM A API OFICIAL DA CAIXA
# =====================================================================
def buscar_sorteio_caixa(concurso=""):
    """
    Liga-se à API da Caixa Econômica Federal.
    Se concurso for vazio, traz o último sorteio realizado.
    """
    url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{concurso}"
    # O Header (User-Agent) é obrigatório para a Caixa não bloquear a nossa ligação
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            dados = response.json()
            
            # Formatar os dados recebidos da Caixa
            dezenas = [int(dezena) for dezena in dados['listaDezenas']]
            
            # Buscar os valores dos prémios de 14 e 15 acertos
            valor_14 = 1500.00 # Valor base caso falhe a leitura
            valor_15 = 1500000.00
            
            for rateio in dados.get('listaRateioPremio', []):
                if rateio['faixa'] == 1: # 15 acertos
                    valor_15 = rateio['valorPremio']
                elif rateio['faixa'] == 2: # 14 acertos
                    valor_14 = rateio['valorPremio']

            return {
                "sucesso": True,
                "concurso": dados['numero'],
                "dezenas": sorted(dezenas),
                "data": dados['dataApuracao'],
                "valor_14": valor_14,
                "valor_15": valor_15
            }
        else:
            return {"sucesso": False, "erro": f"Sorteio não encontrado ou API indisponível (Erro {response.status_code})"}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

# =====================================================================
# MOTOR DE INTELIGÊNCIA (IA) E REGRAS MATEMÁTICAS
# =====================================================================
def analisar_frequencias():
    if not st.session_state.historico_dados:
        return Counter()
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
        if acertos == 11: 
            valor = 5 * PREMIO_11; detalhe = "5x Prémio 11"
        elif acertos == 12: 
            valor = (4 * PREMIO_12) + (12 * PREMIO_11); detalhe = "Múltiplo 12"
        elif acertos == 13: 
            valor = (3 * PREMIO_13) + (13 * PREMIO_12); detalhe = "Múltiplo 13"
        elif acertos == 14: 
            valor = (2 * valor_14) + (14 * PREMIO_13); detalhe = "Múltiplo 14"
        elif acertos == 15: 
            valor = valor_15 + (15 * valor_14); detalhe = "Múltiplo 15"

    return acertos, valor, detalhe

# =====================================================================
# INTERFACE DO SISTEMA
# =====================================================================
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Evita avisos de SSL da Caixa

st.sidebar.markdown("## 📡 LotoPro - Ligado à Caixa")
st.sidebar.metric("Saldo em Caixa", f"R$ {st.session_state.banca:.2f}")
st.sidebar.info(f"📚 Banco de Dados: {len(st.session_state.historico_dados)} Sorteios")

menu = st.sidebar.radio("Painel de Controlo", [
    "1. IA Geradora de Jogos", 
    "2. Sincronização & Conferência", 
    "3. Cofre e Gestão"
])

# ---------------------------------------------------------------------
# ABA 1: GERADOR INTELIGENTE
# ---------------------------------------------------------------------
if menu == "1. IA Geradora de Jogos":
    st.header("🧠 Cérebro Analítico e Gerador")
    
    if not st.session_state.historico_dados:
        st.warning("O seu Banco de Dados está vazio. Vá à Aba 2 e sincronize os últimos sorteios da Caixa para a IA funcionar.")
    else:
        freq = analisar_frequencias()
        top_18 = [n for n, c in freq.most_common(18)]
        
        with st.expander("📊 Raio-X da IA (Transparência Total)", expanded=True):
            st.write(f"A analisar as tendências dos **{len(st.session_state.historico_dados)}** concursos registados no sistema.")
            st.write("**Dezenas Mais Frequentes (Top 18):**")
            st.code(sorted(top_18))
            st.markdown("Filtros Aplicados: Soma `180-220` | Ímpares `6-9` | Primos `4-7`")

        st.markdown("---")
        orcamento = st.number_input("Orçamento para esta operação (R$):", min_value=3.50, value=59.50, step=3.50)
        
        if st.button("Acionar Fechamento Híbrido", type="primary"):
            if orcamento > st.session_state.banca:
                st.error("Saldo insuficiente.")
            else:
                with st.spinner("A cruzar matrizes e calcular fechamentos..."):
                    jogos = []
                    caixa_temp = orcamento
                    
                    # 16 Dezenas
                    qtd_16 = int(caixa_temp // PRECO_16)
                    if qtd_16 > 0:
                        cand_16 = [j for j in itertools.combinations(top_18, 16) if filtro_matematico(j)]
                        escolhidos_16 = random.sample(cand_16, min(qtd_16, len(cand_16))) if cand_16 else []
                        for j in escolhidos_16:
                            jogos.append({"tipo": 16, "dezenas": list(j)})
                            caixa_temp -= PRECO_16
                    
                    # 15 Dezenas
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
                        "status": "Aguardando Sorteio"
                    }
                    
                    st.success("✅ Fechamento Gerado com Sucesso!")
                    for i, b in enumerate(jogos):
                        st.markdown(f"**Bilhete {i+1}** (Format: {b['tipo']} dezenas): `{sorted(b['dezenas'])}`")

# ---------------------------------------------------------------------
# ABA 2: SINCRONIZAÇÃO E CONFERÊNCIA COM A CAIXA
# ---------------------------------------------------------------------
elif menu == "2. Sincronização & Conferência":
    st.header("📡 Sincronização Oficial (Caixa Econômica)")
    st.write("Conecte-se aos servidores oficiais para puxar resultados reais, auditar bilhetes ativos e atualizar a inteligência do sistema.")
    
    # 1. SINCRONIZAR AUTOMATICAMENTE
    st.markdown("### 📥 Puxar Dados Direto da Internet")
    concurso_busca = st.text_input("Qual concurso deseja baixar? (Deixe em branco para puxar o ÚLTIMO SORTEIO VIGENTE):")
    
    if st.button("Buscar na Caixa", type="primary"):
        with st.spinner("A conectar aos servidores da Caixa..."):
            resultado_api = buscar_sorteio_caixa(concurso_busca)
            
            if resultado_api["sucesso"]:
                conc = resultado_api["concurso"]
                dezs = resultado_api["dezenas"]
                
                st.success(f"✅ Concurso {conc} ({resultado_api['data']}) importado com sucesso!")
                st.code(f"Dezenas: {dezs}")
                st.info(f"Prémios Oficiais lidos -> 14 Acertos: R$ {resultado_api['valor_14']:.2f} | 15 Acertos: R$ {resultado_api['valor_15']:.2f}")
                
                # Guarda no Banco de Dados da IA se não existir
                if not any(d["concurso"] == conc for d in st.session_state.historico_dados):
                    st.session_state.historico_dados.append({"concurso": conc, "dezenas": dezs})
                    st.write("💾 Sorteio adicionado ao Cérebro da IA.")
                
                # Se houver apostas ativas, faz a auditoria financeira
                if st.session_state.lote_ativo and st.session_state.lote_ativo["status"] != "Auditado":
                    st.markdown("---")
                    st.markdown("### 🔍 Auditoria dos Seus Bilhetes")
                    total_ganho = 0.0
                    for i, b in enumerate(st.session_state.lote_ativo["bilhetes"]):
                        acertos, valor, detalhe = calcular_premio_real(b["dezenas"], dezs, resultado_api['valor_14'], resultado_api['valor_15'])
                        total_ganho += valor
                        if valor > 0:
                            st.write(f"🎉 **Bilhete {i+1} ({b['tipo']} dez) premiado!** Acertos: {acertos} | Prémio: R$ {valor:.2f} ({detalhe})")
                        else:
                            st.write(f"❌ Bilhete {i+1} - {acertos} acertos.")
                    
                    st.session_state.banca += total_ganho
                    st.session_state.lote_ativo["status"] = "Auditado"
                    st.success(f"💰 Auditoria finalizada. R$ {total_ganho:.2f} adicionados à banca!")
            else:
                st.error(f"Falha na comunicação: {resultado_api['erro']}")
                st.warning("A API da Caixa pode estar em manutenção. Tente novamente mais tarde ou insira manualmente no Cofre.")

# ---------------------------------------------------------------------
# ABA 3: GESTÃO E BACKUP
# ---------------------------------------------------------------------
elif menu == "3. Cofre e Gestão":
    st.header("💾 Cofre do Sistema")
    st.write("Guarde o seu progresso. O ficheiro JSON contém a sua banca, apostas e **todo o histórico da Caixa que descarregou**.")
    
    st.metric("Saldo Atual", f"R$ {st.session_state.banca:.2f}")
    
    estado_total = {
        "banca": st.session_state.banca,
        "historico_dados": st.session_state.historico_dados,
        "lote_ativo": st.session_state.lote_ativo
    }
    
    st.download_button("📤 Salvar Cofre Atualizado (.json)", json.dumps(estado_total), "LotoPro_Backup.json", "application/json", type="primary")
    
    st.markdown("---")
    st.subheader("📥 Restaurar Cofre")
    arquivo = st.file_uploader("Suba um LotoPro_Backup.json para restaurar:", type=["json"])
    if arquivo is not None:
        try:
            dados = json.load(arquivo)
            st.session_state.banca = dados.get("banca", 200.0)
            st.session_state.historico_dados = dados.get("historico_dados", [])
            st.session_state.lote_ativo = dados.get("lote_ativo", None)
            st.success("✅ Cofre restaurado! Inteligência e Saldo atualizados.")
            st.rerun()
        except:
            st.error("Erro ao ler o ficheiro.")
