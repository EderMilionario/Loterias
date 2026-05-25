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
PREMIOS = {11: 6.00, 12: 12.00, 13: 30.00, 14: 2000.00, 15: 1500000.00}

# =====================================================================
# SEGURANÇA E AUTENTICAÇÃO
# =====================================================================
SENHA_ACESSO = "admin123"  # <-- MUDE A SUA SENHA AQUI

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- TELA DE LOGIN COM SENHA ---
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔐 Acesso Restrito - LotoMatrix</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            senha_digitada = st.text_input("Digite a Senha de Acesso:", type="password")
            if st.button("ENTRAR NO SISTEMA", type="primary", use_container_width=True):
                if senha_digitada == SENHA_ACESSO:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Senha Incorreta. Acesso Negado.")
    st.stop()

# --- INICIALIZAÇÃO DO ESTADO GLOBAL ---
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False
if 'historico_dados' not in st.session_state:
    st.session_state.historico_dados = []
if 'banca' not in st.session_state:
    st.session_state.banca = 0.0
if 'jogos_salvos' not in st.session_state:
    st.session_state.jogos_salvos = []

# =====================================================================
# FUNÇÕES DE CARREGAMENTO
# =====================================================================
def carregar_cofre_seguro(uploaded_file):
    try:
        data = json.load(uploaded_file)
        st.session_state.historico_dados = data.get("historico_dados", [])
        st.session_state.banca = data.get("banca", 0.0)
        st.session_state.jogos_salvos = data.get("jogos_salvos", [])
        st.session_state.dados_carregados = True
        return True
    except Exception as e:
        st.error(f"Erro ao ler cofre: {e}")
        return False

def gerar_backup():
    return {
        "banca": st.session_state.banca,
        "historico_dados": st.session_state.historico_dados,
        "jogos_salvos": st.session_state.jogos_salvos
    }

# =====================================================================
# INTELIGÊNCIA PERICIAL
# =====================================================================
def analisar_cenario_completo(historico):
    if not historico:
        return {}
    total_concursos = len(historico)
    todas_dezenas = [n for h in historico for n in h['dezenas']]
    contagem = Counter(todas_dezenas)
    ordenadas = [k for k, v in contagem.most_common()]
    
    atrasos = {n: 0 for n in range(1, 26)}
    for i, c in enumerate(reversed(historico)):
        for n in range(1, 26):
            if n in c['dezenas'] and atrasos[n] == 0 and i > 0:
                atrasos[n] = i

    sorteados_no_ciclo = set()
    for c in reversed(historico):
        sorteados_no_ciclo.update(c['dezenas'])
        if len(sorteados_no_ciclo) == 25:
            sorteados_no_ciclo = set(historico[-1]['dezenas'])
            break
    faltam_ciclo = sorted(list(set(range(1, 26)) - sorteados_no_ciclo))

    return {
        "total_concursos": total_concursos,
        "quentes": sorted(ordenadas[:10]),
        "medias": sorted(ordenadas[10:20]),
        "frias": sorted(ordenadas[20:]),
        "atrasos": atrasos,
        "faltam_ciclo": faltam_ciclo
    }

def filtrar_jogo(jogo, ultimo_sorteio, historico_sets, volume_jogos):
    soma = sum(jogo)
    impares = sum(1 for n in jogo if n % 2 != 0)
    primos_lista = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    primos = sum(1 for n in jogo if n in primos_lista)
    if set(jogo) in historico_sets: return False
    if ultimo_sorteio:
        repetidas = len(set(jogo).intersection(set(ultimo_sorteio)))
        if repetidas < 8 or repetidas > 10: return False
    if volume_jogos < 10:
        if not (180 <= soma <= 220): return False
        if not (7 <= impares <= 8): return False
        if not (5 <= primos <= 6): return False
    else:
        if random.random() > 0.15:
            if not (170 <= soma <= 230): return False
            if not (6 <= impares <= 9): return False
            if not (4 <= primos <= 7): return False
    jogo_ordenado = sorted(jogo)
    for i in range(len(jogo_ordenado)-1):
        if jogo_ordenado[i+1] - jogo_ordenado[i] > 5:
            return False
    return True

def calcular_premiacao_multipla(acertos, tamanho_jogo):
    valor = 0.0
    if tamanho_jogo == 15 and acertos >= 11: valor = PREMIOS[acertos]
    elif tamanho_jogo == 16:
        if acertos == 11: valor = 5 * PREMIOS[11]
        elif acertos == 12: valor = 4 * PREMIOS[12] + 12 * PREMIOS[11]
        elif acertos == 13: valor = 3 * PREMIOS[13] + 13 * PREMIOS[12]
        elif acertos == 14: valor = 2 * PREMIOS[14] + 14 * PREMIOS[13]
        elif acertos == 15: valor = PREMIOS[15] + 15 * PREMIOS[14]
    return valor

# =====================================================================
# TELA DE UPLOAD DO COFRE (APÓS LOGIN)
# =====================================================================
if not st.session_state.dados_carregados:
    st.markdown("### 📥 Insira o arquivo Cofre.json para descriptografar os dados:")
    uploaded_file = st.file_uploader("", type=["json"])
    if st.button("🚀 CARREGAR SISTEMA", type="primary"):
        if uploaded_file and carregar_cofre_seguro(uploaded_file):
            st.success("🧠 Inteligência Desbloqueada com Sucesso!")
            st.rerun()
        else:
            st.error("Arquivo inválido ou não selecionado.")
    st.stop()

# =====================================================================
# INTERFACE PRINCIPAL
# =====================================================================
cenario = analisar_cenario_completo(st.session_state.historico_dados)
st.markdown(f"## 🧬 LotoMatrix Premium Ativo")
st.markdown(f"**Banca Disponível:** R$ {st.session_state.banca:.2f} | **Concursos Indexados:** {cenario['total_concursos']}")

tabs = st.tabs(["📊 Painel do Cenário Atual", "🎯 Gerador Autônomo", "🏆 Conferência Pericial", "💾 Central do Cofre"])

# ----------------- TAB 1: PAINEL -----------------
with tabs[0]:
    st.markdown("### 🔍 Transparência Total do Ecossistema")
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.error(f"🔥 **Dezenas Quentes:** {', '.join([f'{n:02d}' for n in cenario['quentes']])}")
            st.info(f"❄️ **Dezenas Frias:** {', '.join([f'{n:02d}' for n in cenario['frias']])}")
    with c2:
        with st.container(border=True):
            if cenario['faltam_ciclo']:
                st.warning(f"⏳ **Faltam no Ciclo:** {', '.join([f'{n:02d}' for n in cenario['faltam_ciclo']])}")
            else:
                st.success("✅ **Ciclo Fechado no último concurso!**")
            ult_jogo = st.session_state.historico_dados[-1]['dezenas']
            st.write(f"🌓 **Último Sorteio:** {', '.join([f'{n:02d}' for n in ult_jogo])}")
    with c3:
        with st.container(border=True):
            st.markdown("⏱️ **Maiores Atrasos:**")
            atrasos = sorted(cenario['atrasos'].items(), key=lambda x: x[1], reverse=True)[:5]
            for dez, conc in atrasos:
                st.write(f"Dezena **{dez:02d}**: ausente há **{conc}** concursos")

# ----------------- TAB 2: GERADOR -----------------
with tabs[1]:
    st.markdown("### 🧠 Engenharia Combinatória Baseada em Dados")
    colA, colB = st.columns(2)
    
    # Tratamento para evitar o erro StreamlitValueAboveMaxError
    max_banca = max(3.5, float(st.session_state.banca))
    val_padrao = min(20.0, float(st.session_state.banca)) if st.session_state.banca >= 3.5 else 3.5
    
    orcamento = colA.number_input("Capital para a Operação Atual (R$)", min_value=3.5, max_value=max_banca, value=val_padrao)
    modo_jogo = colB.selectbox("Formato do Jogo", ["15 Dezenas", "16 Dezenas", "Híbrido (15 e 16)"])
    
    if st.button("🚀 EXECUTAR ENGENHARIA", type="primary"):
        if st.session_state.banca < 3.5:
            st.error("Banca insuficiente. Mínimo de R$ 3.50 necessário.")
        else:
            with st.spinner("Construindo Matriz Preditiva..."):
                historico = st.session_state.historico_dados
                ultimo_sorteio = historico[-1]['dezenas'] if historico else []
                historico_sets = [set(h['dezenas']) for h in historico]
                
                matriz_viva = set(cenario['faltam_ciclo'])
                for d in cenario['quentes'] + cenario['medias']:
                    if len(matriz_viva) >= 19: break
                    matriz_viva.add(d)
                matriz_viva = sorted(list(matriz_viva))
                
                jogos_gerados = []
                tentativas, bloqueados = 0, 0
                orcamento_restante = orcamento
                
                # Define os tamanhos permitidos com base na escolha
                tamanhos = [15] if modo_jogo == "15 Dezenas" else [16] if modo_jogo == "16 Dezenas" else [15, 16]
                
                while orcamento_restante >= PRECO_15 and tentativas < 60000:
                    tentativas += 1
                    tam_atual = random.choice(tamanhos)
                    if tam_atual == 16 and orcamento_restante < PRECO_16:
                        tam_atual = 15 # Reduz para 15 se não tiver saldo para 16
                        
                    custo_atual = PRECO_15 if tam_atual == 15 else PRECO_16
                    
                    if orcamento_restante >= custo_atual:
                        candidato = sorted(random.sample(matriz_viva, tam_atual))
                        if filtrar_jogo(candidato, ultimo_sorteio, historico_sets, 10):
                            if candidato not in [j['dezenas'] for j in jogos_gerados]:
                                jogos_gerados.append({"tamanho": tam_atual, "dezenas": candidato})
                                orcamento_restante -= custo_atual
                        else:
                            bloqueados += 1

                for jg in jogos_gerados:
                    st.session_state.jogos_salvos.append({
                        "tamanho": jg["tamanho"],
                        "dezenas": jg["dezenas"],
                        "matriz_viva": matriz_viva,
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                
                custo_total = orcamento - orcamento_restante
                st.session_state.banca -= custo_total
                
                with st.container(border=True):
                    st.success("⚙️ PROCESSO MÁXIMO CONCLUÍDO!")
                    st.write(f"- **Matriz Viva:** {len(matriz_viva)} dezenas ({', '.join([f'{n:02d}' for n in matriz_viva])})")
                    st.write(f"- **Bloqueados por Filtros:** {bloqueados} tentativas")
                    st.write(f"- **Bilhetes Gerados:** {len(jogos_gerados)}")
                st.rerun()

    if st.session_state.jogos_salvos:
        st.markdown("---")
        texto_extracao = "=== JOGOS GERADOS ===\n"
        for idx, j in enumerate(st.session_state.jogos_salvos):
            texto_extracao += f"Jogo {idx+1} [{j['tamanho']}]: {' - '.join([f'{n:02d}' for n in j['dezenas']])}\n"
            
        c_tit, c_btn1, c_btn2 = st.columns([2, 1, 1])
        c_tit.markdown("### 🎫 Bilhetes Ativos")
        c_btn1.download_button("📥 EXTRAIR TXT", data=texto_extracao, file_name="Jogos.txt", use_container_width=True)
        if c_btn2.button("🗑️ Excluir Todos", use_container_width=True):
            st.session_state.jogos_salvos = []
            st.rerun()
            
        for idx, j in enumerate(st.session_state.jogos_salvos):
            with st.container(border=True):
                st.markdown(f"**Bilhete {idx+1} [{j['tamanho']} Dezenas]**: {' - '.join([f'{n:02d}' for n in j['dezenas']])}")

# ----------------- TAB 3: CONFERÊNCIA -----------------
with tabs[2]:
    st.markdown("### 🏆 Auditoria Forense")
    if not st.session_state.jogos_salvos:
        st.info("Nenhum jogo em espera.")
    else:
        resultado_str = st.text_input("Digite as 15 dezenas sorteadas (espaçadas):")
        if st.button("🔍 AUDITAR BILHETES", type="primary"):
            try:
                sorteio_set = set([int(x) for x in resultado_str.split()])
                if len(sorteio_set) != 15:
                    st.error("Insira exatamente 15 números únicos.")
                else:
                    ganho_lote = 0.0
                    matriz_usada = set(st.session_state.jogos_salvos[0].get("matriz_viva", []))
                    acertos_matriz = len(matriz_usada.intersection(sorteio_set))
                    
                    if matriz_usada:
                        st.info(f"📊 **Assertividade da Matriz:** Das {len(matriz_usada)} dezenas base selecionadas pela IA, **{acertos_matriz} foram sorteadas**.")
                    
                    for idx, j in enumerate(st.session_state.jogos_salvos):
                        acertos = len(set(j['dezenas']).intersection(sorteio_set))
                        premio = calcular_premiacao_multipla(acertos, j['tamanho'])
                        ganho_lote += premio
                        
                        status = f"🎉 PREMIADO! R$ {premio:.2f}" if acertos >= 11 else f"❌ {acertos} Acertos"
                        with st.container(border=True):
                            st.markdown(f"**Bilhete {idx+1}**: {status}")
                            st.write(f"Dezenas: {' - '.join([f'{n:02d}' for n in j['dezenas']])}")
                    
                    st.session_state.banca += ganho_lote
                    st.success(f"💰 Lucro de R$ {ganho_lote:.2f} adicionado à banca.")
            except:
                st.error("Erro de digitação. Digite apenas números.")

# ----------------- TAB 4: COFRE -----------------
with tabs[3]:
    st.markdown("### 💾 Gestão do Cofre")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Saldo Atual", f"R$ {st.session_state.banca:.2f}")
        nova_banca = st.number_input("Ajustar saldo:", value=float(st.session_state.banca))
        if st.button("Atualizar Saldo"):
            st.session_state.banca = nova_banca
            st.rerun()
    with c2:
        st.download_button(
            label="💾 BAIXAR COFRE ATUAL (.JSON)",
            data=json.dumps(gerar_backup()),
            file_name="Cofre.json",
            mime="application/json",
            type="primary"
        )
