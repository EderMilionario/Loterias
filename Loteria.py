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
    st.markdown("<h1 style='text-align: center; color: #006644;'>🔐 Acesso Restrito - LotoMatrix</h1>", unsafe_allow_html=True)
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
if 'ultima_matriz' not in st.session_state:
    st.session_state.ultima_matriz = [] # Guarda as dezenas escolhidas pela IA
if 'alvo_atual' not in st.session_state:
    st.session_state.alvo_atual = 0

# =====================================================================
# FUNÇÕES DE CARREGAMENTO E BACKUP
# =====================================================================
def carregar_cofre_seguro(uploaded_file):
    try:
        data = json.load(uploaded_file)
        st.session_state.historico_dados = data.get("historico_dados", [])
        st.session_state.banca = data.get("banca", 0.0)
        st.session_state.jogos_salvos = data.get("jogos_salvos", [])
        st.session_state.ultima_matriz = data.get("ultima_matriz", [])
        st.session_state.alvo_atual = data.get("alvo_atual", 0)
        st.session_state.dados_carregados = True
        return True
    except Exception as e:
        st.error(f"Erro ao ler cofre: {e}")
        return False

def gerar_backup():
    return {
        "banca": st.session_state.banca,
        "historico_dados": st.session_state.historico_dados,
        "jogos_salvos": st.session_state.jogos_salvos,
        "ultima_matriz": st.session_state.ultima_matriz,
        "alvo_atual": st.session_state.alvo_atual
    }

# =====================================================================
# INTELIGÊNCIA PERICIAL
# =====================================================================
def analisar_cenario_completo(historico):
    if not historico:
        return {"total_concursos": 0, "quentes": [], "medias": [], "frias": [], "atrasos": {}, "faltam_ciclo": []}
    
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
    
    # Filtro Histórico e Repetição do Concurso Anterior (Inteligência Central)
    if set(jogo) in historico_sets: return False
    if ultimo_sorteio:
        repetidas = len(set(jogo).intersection(set(ultimo_sorteio)))
        if repetidas < 8 or repetidas > 10: return False
        
    # Curvas de Sino Baseadas em Volume
    if volume_jogos < 10:
        if not (180 <= soma <= 220): return False
        if not (7 <= impares <= 8): return False
        if not (5 <= primos <= 6): return False
    else:
        if random.random() > 0.15: # 15% fora do padrão para pegar zebras
            if not (170 <= soma <= 230): return False
            if not (6 <= impares <= 9): return False
            if not (4 <= primos <= 7): return False
            
    # Filtro de Gaps
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
# TELA DE UPLOAD DO COFRE (LOGIN DE DADOS)
# =====================================================================
if not st.session_state.dados_carregados:
    st.markdown("<h3 style='color:#006644;'>📥 Injeção do Banco de Dados (Cofre.json)</h3>", unsafe_allow_html=True)
    st.info("Para ativar a inteligência, o sistema precisa ler o seu histórico de resultados e banca.")
    uploaded_file = st.file_uploader("Arraste seu Cofre.json aqui:", type=["json"])
    if st.button("🚀 INJETAR DADOS E ATIVAR IA", type="primary", use_container_width=True):
        if uploaded_file and carregar_cofre_seguro(uploaded_file):
            st.success("🧠 Banco de Dados Injetado com Sucesso!")
            st.rerun()
        else:
            st.error("Arquivo inválido ou não selecionado.")
    st.stop()

# =====================================================================
# INTERFACE PRINCIPAL ATIVA
# =====================================================================
cenario = analisar_cenario_completo(st.session_state.historico_dados)
alvo_calculado = cenario['total_concursos'] + 1

st.markdown(f"## 🧬 LotoMatrix Premium Ativo")
st.markdown(f"**Banca:** R$ {st.session_state.banca:.2f} | **Concursos Indexados:** {cenario['total_concursos']} | **🎯 Próximo Alvo:** Concurso {alvo_calculado}")

tabs = st.tabs(["📊 Painel do Cenário", "🎯 Gerador Autônomo", "🏆 Conferência Pericial", "💾 Central do Cofre"])

# ----------------- TAB 1: PAINEL DO CENÁRIO -----------------
with tabs[0]:
    st.markdown("### 🔍 Ecossistema Analítico")
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
            ult_jogo = st.session_state.historico_dados[-1]['dezenas'] if st.session_state.historico_dados else []
            st.write(f"🌓 **Último Sorteio:** {', '.join([f'{n:02d}' for n in ult_jogo])}")
    with c3:
        with st.container(border=True):
            st.markdown("⏱️ **Maiores Atrasos:**")
            atrasos = sorted(cenario['atrasos'].items(), key=lambda x: x[1], reverse=True)[:5]
            for dez, conc in atrasos:
                st.write(f"Dezena **{dez:02d}**: ausente há **{conc}** concursos")

# ----------------- TAB 2: GERADOR AUTÔNOMO -----------------
with tabs[1]:
    st.markdown("### 🧠 Engenharia Combinatória Baseada em Dados")
    colA, colB = st.columns(2)
    
    max_banca = max(3.5, float(st.session_state.banca))
    val_padrao = min(20.0, float(st.session_state.banca)) if st.session_state.banca >= 3.5 else 3.5
    
    orcamento = colA.number_input("Capital para a Operação (R$)", min_value=3.5, max_value=max_banca, value=val_padrao)
    modo_jogo = colB.selectbox("Formato do Jogo", ["Híbrido (15 e 16)", "15 Dezenas", "16 Dezenas"])
    
    if st.button("🚀 EXECUTAR ENGENHARIA", type="primary"):
        if st.session_state.banca < 3.5:
            st.error("Banca insuficiente. Mínimo de R$ 3.50 necessário.")
        else:
            with st.spinner("Construindo Matriz Preditiva..."):
                historico = st.session_state.historico_dados
                ultimo_sorteio = historico[-1]['dezenas'] if historico else []
                historico_sets = [set(h['dezenas']) for h in historico]
                
                # INTELIGÊNCIA: Montagem da Matriz Viva (Ciclo + Quentes/Médias)
                matriz_viva = set(cenario['faltam_ciclo'])
                for d in cenario['quentes'] + cenario['medias']:
                    if len(matriz_viva) >= 19: break
                    matriz_viva.add(d)
                matriz_viva = sorted(list(matriz_viva))
                
                # Salva a matriz escolhida na sessão para TRANSPARÊNCIA
                st.session_state.ultima_matriz = matriz_viva
                st.session_state.alvo_atual = alvo_calculado
                
                jogos_gerados = []
                tentativas, bloqueados = 0, 0
                orcamento_restante = orcamento
                
                tamanhos = [15] if modo_jogo == "15 Dezenas" else [16] if modo_jogo == "16 Dezenas" else [15, 16]
                
                while orcamento_restante >= PRECO_15 and tentativas < 60000:
                    tentativas += 1
                    tam_atual = random.choice(tamanhos)
                    if tam_atual == 16 and orcamento_restante < PRECO_16:
                        tam_atual = 15
                        
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
                        "alvo": alvo_calculado,
                        "tamanho": jg["tamanho"],
                        "dezenas": jg["dezenas"],
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                
                custo_total = orcamento - orcamento_restante
                st.session_state.banca -= custo_total
                st.rerun()

    # --- EXIBIÇÃO TRANSPARENTE E CARTÕES ---
    if st.session_state.jogos_salvos:
        st.markdown("---")
        
        # Painel de Transparência
        st.markdown(f"""
        <div style='background-color:#ffffff; padding:15px; border-radius:8px; border-left:5px solid #2b6cb0; border: 1px solid #e2e8f0; margin-bottom: 20px;'>
            <h4 style='color:#2b6cb0; margin-top:0;'>📊 Transparência da Matriz Base</h4>
            <p style='color:#4a5568; margin-bottom:5px;'>Para gerar estes jogos com a máxima eficiência matemática, a IA selecionou o seguinte grupo de <b>{len(st.session_state.ultima_matriz)} dezenas</b>:</p>
            <p style='font-family: monospace; font-size: 16px; font-weight: bold; color: #1a202c;'>{", ".join([f"{n:02d}" for n in st.session_state.ultima_matriz])}</p>
        </div>
        """, unsafe_allow_html=True)
        
        texto_extracao = f"=== JOGOS ALVO {st.session_state.alvo_atual} ===\n"
        for idx, j in enumerate(st.session_state.jogos_salvos):
            texto_extracao += f"Jogo {idx+1} [{j['tamanho']}]: {' - '.join([f'{n:02d}' for n in j['dezenas']])}\n"
            
        c_tit, c_btn1, c_btn2 = st.columns([2, 1, 1])
        c_tit.markdown("### 🎫 Lote Ativo")
        c_btn1.download_button("📥 EXTRAIR TXT", data=texto_extracao, file_name=f"Jogos_Alvo_{st.session_state.alvo_atual}.txt", use_container_width=True)
        if c_btn2.button("🗑️ Excluir Todos", use_container_width=True):
            st.session_state.jogos_salvos = []
            st.session_state.ultima_matriz = []
            st.rerun()
            
        # Cartões HTML Bonitos
        for idx, j in enumerate(st.session_state.jogos_salvos):
            cor_tag = "#e6f4ea" if j['tamanho'] == 15 else "#ebf8ff"
            cor_txt_tag = "#006644" if j['tamanho'] == 15 else "#2b6cb0"
            dezenas_str = " - ".join([f"{n:02d}" for n in j['dezenas']])
            
            st.markdown(f"""
            <div style="background: #ffffff; border-radius: 10px; padding: 15px; margin-bottom: 15px; border-left: 6px solid {cor_txt_tag}; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 1px solid #edf2f7; border-right: 1px solid #edf2f7; border-bottom: 1px solid #edf2f7;">
                <div style="margin-bottom: 8px;">
                    <span style="background: #f7fafc; color: #4a5568; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; border: 1px solid #e2e8f0;">🎯 ALVO: {j.get('alvo', 'N/A')}</span>
                    <span style="background: {cor_tag}; color: {cor_txt_tag}; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-left: 8px;">BILHETE {idx+1} • {j['tamanho']} DEZENAS</span>
                </div>
                <p style="margin: 0; color: #1a202c; font-family: monospace; font-size: 18px; letter-spacing: 2px; font-weight: bold;">{dezenas_str}</p>
            </div>
            """, unsafe_allow_html=True)

# ----------------- TAB 3: CONFERÊNCIA PERICIAL -----------------
with tabs[2]:
    st.markdown("### 🏆 Auditoria Forense")
    
    if not st.session_state.jogos_salvos:
        st.info("Você ainda não gerou nenhum lote para auditar.")
    else:
        # Exibição da Matriz Antes de Auditar
        if st.session_state.ultima_matriz:
            st.markdown(f"""
            <div style='background-color:#f7fafc; padding:15px; border-radius:8px; border: 1px solid #e2e8f0; margin-bottom: 20px;'>
                <p style='margin:0; color:#4a5568;'><b>Matriz em Análise:</b> {len(st.session_state.ultima_matriz)} dezenas preparadas para o Concurso {st.session_state.alvo_atual}.</p>
            </div>
            """, unsafe_allow_html=True)

        # Mostra os cartões antes da auditoria para visibilidade
        with st.expander("👀 Ver Bilhetes Aguardando Conferência", expanded=False):
            for idx, j in enumerate(st.session_state.jogos_salvos):
                st.markdown(f"**Bilhete {idx+1} [{j['tamanho']}]**: {' - '.join([f'{n:02d}' for n in j['dezenas']])}")

        resultado_str = st.text_input("Digite as 15 dezenas do sorteio oficial (separadas por espaço):")
        
        if st.button("🔍 AUDITAR RESULTADOS", type="primary"):
            try:
                sorteio_set = set([int(x) for x in resultado_str.split()])
                if len(sorteio_set) != 15:
                    st.error("Insira exatamente 15 números.")
                else:
                    ganho_lote = 0.0
                    
                    # Desempenho da Matriz
                    if st.session_state.ultima_matriz:
                        matriz_set = set(st.session_state.ultima_matriz)
                        acertos_matriz = len(matriz_set.intersection(sorteio_set))
                        st.markdown(f"""
                        <div style="background-color: #ebf8ff; color: #2b6cb0; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #bee3f8;">
                            <h4 style="margin:0;">🎯 Desempenho da Inteligência (Matriz)</h4>
                            <p style="margin-top: 5px; font-size:15px;">A IA escolheu <b>{len(matriz_set)} dezenas</b>. Destas, <b>{acertos_matriz} caíram no sorteio oficial</b>.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Cartões de Auditoria
                    for idx, j in enumerate(st.session_state.jogos_salvos):
                        acertos = len(set(j['dezenas']).intersection(sorteio_set))
                        premio = calcular_premiacao_multipla(acertos, j['tamanho'])
                        ganho_lote += premio
                        
                        exibicao_nums = " - ".join([
                            f"<span style='color: {'#2f855a' if n in sorteio_set else '#a0aec0'}; font-weight: {'bold' if n in sorteio_set else 'normal'};'>{n:02d}</span>"
                            for n in j['dezenas']
                        ])
                        
                        if acertos >= 11:
                            cor_borda, icone, txt_cor = "#48bb78", "🎉", "#2f855a"
                            status = f"PREMIADO! {acertos} Acertos | Retorno: R$ {premio:.2f}"
                        else:
                            cor_borda, icone, txt_cor = "#f56565", "❌", "#c53030"
                            status = f"Não Premiado ({acertos} Acertos)"
                            
                        st.markdown(f"""
                        <div style="background: #ffffff; padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 6px solid {cor_borda}; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                            <h4 style="margin:0; color: {txt_cor};">{icone} Bilhete {idx+1} - {status}</h4>
                            <p style="margin-top: 10px; font-family: monospace; font-size: 18px; background: #f7fafc; padding: 10px; border-radius: 4px; border: 1px solid #edf2f7;">{exibicao_nums}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.session_state.banca += ganho_lote
                    st.success(f"💰 Lucro de R$ {ganho_lote:.2f} adicionado à banca.")
            except:
                st.error("Erro de digitação. Digite apenas números separados por espaço.")

# ----------------- TAB 4: COFRE -----------------
with tabs[3]:
    st.markdown("### 💾 Central de Segurança e Backup")
    
    st.markdown("""
    <div style='background-color:#fff3cd; padding:15px; border-radius:8px; border-left:5px solid #ffc107; margin-bottom: 20px; color:#856404;'>
        <b>Atenção:</b> Sempre que gerar novos jogos ou auditar resultados, baixe o seu Cofre atualizado no botão abaixo para não perder sua banca e os jogos salvos!
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.metric("Saldo do Cofre", f"R$ {st.session_state.banca:.2f}")
            nova_banca = st.number_input("Ajustar saldo manualmente (R$):", value=float(st.session_state.banca))
            if st.button("Atualizar Valor"):
                st.session_state.banca = nova_banca
                st.rerun()
                
    with c2:
        with st.container(border=True):
            st.markdown("#### 📥 Sobrescrever Banco de Dados")
            novo_upload = st.file_uploader("Subir Backup Cofre.json:", type=["json"])
            if st.button("🔄 CARREGAR NOVO BACKUP"):
                if novo_upload and carregar_cofre_seguro(novo_upload):
                    st.success("Dados substituídos com sucesso!")
                    st.rerun()

    st.markdown("---")
    st.markdown("### 📤 Exportação de Segurança")
    doc_json = json.dumps(gerar_backup())
    st.download_button(
        label="💾 BAIXAR SEU COFRE ATUALIZADO (.JSON)",
        data=doc_json,
        file_name="Cofre.json",
        mime="application/json",
        type="primary",
        use_container_width=True
    )
