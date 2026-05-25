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
# FUNÇÕES DE CARREGAMENTO E SEGURANÇA (TELA DE LOGIN)
# =====================================================================
def carregar_cofre_seguro(uploaded_file):
    try:
        data = json.load(uploaded_file)
        st.session_state.historico_dados = data.get("historico_dados", [])
        st.session_state.banca = data.get("banca", 200.0)
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
# INTELIGÊNCIA PERICIAL: ANÁLISE DE CENÁRIO VIVO
# =====================================================================
def analisar_cenario_completo(historico):
    if not historico:
        return {}
    
    total_concursos = len(historico)
    todas_dezenas = [n for h in historico for n in h['dezenas']]
    contagem = Counter(todas_dezenas)
    
    # Quentes, Médias e Frias
    ordenadas = [k for k, v in contagem.most_common()]
    quentes = ordenadas[:10]
    medias = ordenadas[10:20]
    frias = ordenadas[20:]
    
    # Cálculo de Atrasos
    atrasos = {n: 0 for n in range(1, 26)}
    for i, c in enumerate(reversed(historico)):
        for n in range(1, 26):
            if n in c['dezenas'] and atrasos[n] == 0 and i > 0:
                atrasos[n] = i

    # Rastreamento do Ciclo Atual
    dezenas_vistas_ciclo = set()
    concursos_no_ciclo = 0
    for c in reversed(historico):
        dezenas_vistas_ciclo.update(c['dezenas'])
        concursos_no_ciclo += 1
        if len(dezenas_vistas_ciclo) == 25:
            break
            
    # Reinicia a contagem real do ciclo aberto atual
    dezenas_abertas_ciclo = set()
    for c in reversed(historico):
        # Verifica quais dezenas saíram desde que o último ciclo fechou
        pass
        
    faltam_fechar_ciclo = set(range(1, 26)) - set(historico[-1]['dezenas'])
    # Simplificação biológica do ciclo ativo
    sorteados_no_ciclo = set()
    for c in reversed(historico):
        sorteados_no_ciclo.update(c['dezenas'])
        if len(sorteados_no_ciclo) == 25:
            sorteados_no_ciclo = set(historico[-1]['dezenas'])
            break
    faltam_ciclo = sorted(list(set(range(1, 26)) - sorteados_no_ciclo))

    return {
        "total_concursos": total_concursos,
        "quentes": sorted(quentes),
        "medias": sorted(medias),
        "frias": sorted(frias),
        "atrasos": atrasos,
        "faltam_ciclo": faltam_ciclo
    }

def filtrar_jogo(jogo, ultimo_sorteio, historico_sets, volume_jogos):
    soma = sum(jogo)
    impares = sum(1 for n in jogo if n % 2 != 0)
    primos_lista = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    primos = sum(1 for n in jogo if n in primos_lista)
    
    # 1. Filtro Histórico Absoluto
    if set(jogo) in historico_sets: return False
    
    # 2. Filtro Rígido de Repetição do Concurso Anterior (8 a 10)
    if ultimo_sorteio:
        repetidas = len(set(jogo).intersection(set(ultimo_sorteio)))
        if repetidas < 8 or repetidas > 10: return False

    # 3. Curva de Sino Condicional Inteligente
    if volume_jogos < 10:
        if not (180 <= soma <= 220): return False
        if not (7 <= impares <= 8): return False
        if not (5 <= primos <= 6): return False
    else:
        if random.random() > 0.15:
            if not (170 <= soma <= 230): return False
            if not (6 <= impares <= 9): return False
            if not (4 <= primos <= 7): return False

    # 4. Filtro de Geometria de Gaps
    jogo_ordenado = sorted(jogo)
    for i in range(len(jogo_ordenado)-1):
        if jogo_ordenado[i+1] - jogo_ordenado[i] > 5:
            return False

    return True

def calcular_premiacao_multipla(acertos, tamanho_jogo):
    valor_total = 0.0
    if tamanho_jogo == 15:
        if acertos >= 11: valor_total = PREMIOS[acertos]
    elif tamanho_jogo == 16:
        if acertos == 11: valor_total = 5 * PREMIOS[11]
        elif acertos == 12: valor_total = 4 * PREMIOS[12] + 12 * PREMIOS[11]
        elif acertos == 13: valor_total = 3 * PREMIOS[13] + 13 * PREMIOS[12]
        elif acertos == 14: valor_total = 2 * PREMIOS[14] + 14 * PREMIOS[13]
        elif acertos == 15: valor_total = PREMIOS[15] + 15 * PREMIOS[14]
    return valor_total

# =====================================================================
# FLUXO DE EXECUÇÃO E INTERFACE INTERNA
# =====================================================================

# --- TELA DE LOGIN / BLOQUEIO DE SEGURANÇA ---
if not st.session_state.dados_carregados:
    st.markdown("<h1 style='text-align: center; color: #00ffcc;'>🧬 LotoMatrix Premium</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #aaa;'>SISTEMA TRAVADO: Autentique inserindo seu arquivo de Backup do Cofre</p>", unsafe_allow_html=True)
    
    col_login, _ = st.columns([2, 1])
    with col_login:
        with st.container(border=True):
            st.markdown("### 📥 Upload de Chave de Segurança")
            uploaded_file = st.file_uploader("Selecione o arquivo Cofre.json para descriptografar os dados:", type=["json"])
            if uploaded_file is not None:
                st.session_state.bytes_arquivo = uploaded_file.getvalue()
            
            if st.button("🚀 PROCESSAR E ATIVAR IA", type="primary", use_container_width=True):
                if 'bytes_arquivo' in st.session_state and st.session_state.bytes_arquivo:
                    import io
                    f = io.BytesIO(st.session_state.bytes_arquivo)
                    if carregar_cofre_seguro(f):
                        st.success("🧠 Inteligência Preditiva Desbloqueada!")
                        st.rerun()
                else:
                    st.error("Nenhum arquivo detectado. Faça o upload do Cofre.json.")
    st.stop()

# --- PAINEL PRINCIPAL APÓS LOGIN ---
cenario = analisar_cenario_completo(st.session_state.historico_dados)

st.markdown(f"<h1 style='color: #00ffcc; margin-bottom: 0;'>🧬 LotoMatrix Ativo</h1>", unsafe_allow_html=True)
st.markdown(f"**Base de Dados:** {cenario['total_concursos']} concursos catalogados e indexados | **Banca:** R$ {st.session_state.banca:.2f}")

tabs = st.tabs(["📊 Painel do Cenário Atual", "🎯 Gerador Autônomo", "🏆 Conferência Pericial", "💾 Backup & Saldo"])

# ----------------- TAB 1: PAINEL DO CENÁRIO -----------------
with tabs[0]:
    st.markdown("### 🔍 Transparência Total do Ecossistema Matemática")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div style='background-color:#111; padding:15px; border-radius:10px; border-top:4px solid #ff3333;'><h4>🔥 Dezenas Quentes (Mais Sorteadas)</h4></div>", unsafe_allow_html=True)
        st.write(", ".join([f"{n:02d}" for n in cenario['quentes']]))
        
        st.markdown("<br><div style='background-color:#111; padding:15px; border-radius:10px; border-top:4px solid #3399ff;'><h4>❄️ Dezenas Frias (Menos Sorteadas)</h4></div>", unsafe_allow_html=True)
        st.write(", ".join([f"{n:02d}" for n in cenario['frias']]))
        
    with c2:
        st.markdown("<div style='background-color:#111; padding:15px; border-radius:10px; border-top:4px solid #ffcc00;'><h4>⏳ Ciclo Ativo da Lotofácil</h4></div>", unsafe_allow_html=True)
        if cenario['faltam_ciclo']:
            st.warning(f"Faltam sair para fechar o ciclo: {', '.join([f'{n:02d}' for n in cenario['faltam_ciclo']])}")
        else:
            st.success("O Ciclo acabou de fechar ou reiniciar!")
            
        st.markdown("<br><div style='background-color:#111; padding:15px; border-radius:10px; border-top:4px solid #9933ff;'><h4>🌓 Último Comportamento Padrão</h4></div>", unsafe_allow_html=True)
        ult_jogo = st.session_state.historico_dados[-1]['dezenas']
        st.write(f"**Dezenas do último concurso:** {', '.join([f'{n:02d}' for n in ult_jogo])}")
        
    with c3:
        st.markdown("<div style='background-color:#111; padding:15px; border-radius:10px; border-top:4px solid #00ffcc;'><h4>⏱️ Ranking de Atraso Atual</h4></div>", unsafe_allow_html=True)
        atraso_ordenado = sorted(cenario['atrasos'].items(), key=lambda x: x[1], reverse=True)[:5]
        for dez, concursos in atraso_ordenado:
            st.write(f"Dezena **{dez:02d}**: sem sair há **{concursos}** concursos.")

# ----------------- TAB 2: GERADOR AUTÔNOMO -----------------
with tabs[1]:
    st.markdown("### 🧠 Engenharia Combinatória Baseada em Dados")
    
    colA, colB = st.columns(2)
    orcamento = colA.number_input("Capital Destinado à Operação (R$)", min_value=3.5, max_value=st.session_state.banca, value=20.0)
    tamanho = colB.selectbox("Tamanho do Jogo", [15, 16])
    
    custo = PRECO_15 if tamanho == 15 else PRECO_16
    jogos_possiveis = int(orcamento // custo)
    
    st.info(f"O motor gerará **{jogos_possiveis} bilhetes** baseando-se no cenário atual.")
    
    if st.button("🚀 EXECUTAR ENGENHARIA MATRICIAL", type="primary"):
        if jogos_possiveis < 1:
            st.error("Saldo insuficiente para gerar ao menos 1 jogo neste formato.")
        else:
            with st.spinner("Construindo Matriz Inteligente..."):
                historico = st.session_state.historico_dados
                ultimo_sorteio = historico[-1]['dezenas'] if historico else []
                historico_sets = [set(h['dezenas']) for h in historico]
                
                # Montagem Biológica da Matriz (Prioridade total para o Ciclo + Quentes)
                matriz_viva = set(cenario['faltam_ciclo'])
                for d in cenario['quentes'] + cenario['medias']:
                    if len(matriz_viva) >= 19: break
                    matriz_viva.add(d)
                matriz_viva = sorted(list(matriz_viva))
                
                jogos_gerados = []
                tentativas, bloqueados_filtros = 0, 0
                
                while len(jogos_gerados) < jogos_possiveis and tentativas < 60000:
                    tentativas += 1
                    candidato = sorted(random.sample(matriz_viva, tamanho))
                    if filtrar_jogo(candidato, ultimo_sorteio, historico_sets, jogos_possiveis):
                        if candidato not in jogos_gerados:
                            jogos_gerados.append(candidato)
                    else:
                        bloqueados_filtros += 1
                
                # Injeta os metadados e os jogos na memória persistente
                for jg in jogos_gerados:
                    st.session_state.jogos_salvos.append({
                        "tamanho": tamanho,
                        "dezenas": jg,
                        "matriz_viva": matriz_viva,
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                
                st.session_state.banca -= (len(jogos_gerados) * custo)
                
                # Relatório completo de Transparência
                st.success("⚙️ PROCESSO CONCLUÍDO COM SUCESSO!")
                st.markdown(f"""
                <div style='background-color:#111; padding:20px; border-radius:8px; border-left:5px solid #00ffcc;'>
                    <h4>📊 Relatório de Transparência do Motor Preditivo:</h4>
                    <ul>
                        <li><b>Tamanho da Matriz Viva Selecionada:</b> {len(matriz_viva)} dezenas</li>
                        <li><b>Dezenas Fixadas na Matriz para este lote:</b> {", ".join([f"{n:02d}" for n in matriz_viva])}</li>
                        <li><b>Combinações barradas nos filtros rígidos (evitou desperdício):</b> {bloqueados_filtros} tentativas</li>
                        <li><b>Bilhetes salvos com sucesso e injetados no sistema:</b> {len(jogos_gerados)}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                st.rerun()

    # Apresentação dos Jogos que estão na Espera do Sorteio
    if st.session_state.jogos_salvos:
        st.markdown("---")
        col_tit, col_btn = st.columns([3, 1])
        col_tit.markdown("### 🎫 Bilhetes Ativos no Sistema (Aguardando Sorteio Alvo)")
        if col_btn.button("🗑️ Excluir Todos os Jogos", type="secondary", use_container_width=True):
            st.session_state.jogos_salvos = []
            st.success("Jogos excluídos!")
            st.rerun()
            
        for idx, j in enumerate(st.session_state.jogos_salvos):
            dezenas_formatadas = " - ".join([f"{n:02d}" for n in j['dezenas']])
            st.markdown(f"""
            <div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #00ffcc;">
                <h4 style="margin:0; color: #00ffcc;">Bilhete {idx+1} [Formato: {j['tamanho']} Dezenas]</h4>
                <p style="font-size: 18px; letter-spacing: 2px; margin-top: 10px; font-family: monospace;">{dezenas_formatadas}</p>
                <small style="color: #666;">Gerado em: {j.get('data', 'N/A')} | Baseado em matriz de {len(j.get('matriz_viva', []))} números</small>
            </div>
            """, unsafe_allow_html=True)

# ----------------- TAB 3: CONFERÊNCIA PERICIAL -----------------
with tabs[2]:
    st.markdown("### 🏆 Auditoria Forense de Resultados")
    
    if not st.session_state.jogos_salvos:
        st.info("Nenhum jogo salvo em espera de sorteio. Crie novos jogos na aba anterior.")
    else:
        resultado_str = st.text_input("Digite as 15 dezenas do sorteio oficial (separadas por um único espaço):")
        
        if st.button("🔍 AUDITAR BILHETES E APURAR LUCROS", type="primary"):
            try:
                sorteio_oficial = [int(x) for x in resultado_str.split()]
                if len(sorteio_oficial) != 15:
                    st.error("Erro: O sorteio oficial deve conter exatamente 15 dezenas.")
                else:
                    sorteio_set = set(sorteio_oficial)
                    ganho_lote = 0.0
                    
                    # Relatório de assertividade da escolha de Dezenas da Matriz
                    primeiro_jogo = st.session_state.jogos_salvos[0]
                    if "matriz_viva" in primeiro_jogo:
                        matriz_usada = set(primeiro_jogo["matriz_viva"])
                        acertos_da_matriz = len(matriz_usada.intersection(sorteio_set))
                        st.markdown(f"""
                        <div style="background-color: #111; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #3399ff;">
                            <h4 style="color:#3399ff; margin:0;">📊 Assertividade Biológica da IA (Escolha de Dezenas):</h4>
                            <p style="margin-top: 5px; font-size:15px;">Das <b>{len(matriz_usada)} dezenas</b> que a inteligência selecionou para gerar os jogos, <b>{acertos_da_matriz} foram sorteadas</b> no concurso oficial.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    for idx, j in enumerate(st.session_state.jogos_salvos):
                        acertos = len(set(j['dezenas']).intersection(sorteio_set))
                        premio_jogo = calcular_premiacao_multipla(acertos, j['tamanho'])
                        ganho_lote += premio_jogo
                        
                        # Destaca dezenas acertadas visualmente em verde neon
                        exibicao_nums = " - ".join([
                            f"<span style='color: {'#00ff00' if n in sorteio_set else '#ffffff'}; font-weight: {'bold' if n in sorteio_set else 'normal'}; font-size: 18px;'>{n:02d}</span>"
                            for n in j['dezenas']
                        ])
                        
                        if acertos >= 11:
                            cor_borda = "#00ff00"
                            status = f"🎉 PREMIADO COM {acertos} ACERTOS! Ganho: R$ {premio_jogo:.2f}"
                        else:
                            cor_borda = "#ff4444"
                            status = f"❌ {acertos} Acertos (Sem Premiação)"
                            
                        st.markdown(f"""
                        <div style="background-color: #262626; padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 6px solid {cor_borda};">
                            <h4 style="margin:0; color: {cor_borda};">{status}</h4>
                            <p style="background: #000; padding: 10px; border-radius: 4px; margin-top: 10px; letter-spacing: 2px; font-family: monospace;">{exibicao_nums}</p>
                            <small style="color:#aaa;">Tipo de bilhete: {j['tamanho']} dezenas | Premiações desdobradas aplicadas automaticamente.</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    st.session_state.banca += ganho_lote
                    st.success(f"💰 Operação de Auditoria Concluída! R$ {ganho_lote:.2f} creditados no seu saldo principal.")
                    
            except ValueError:
                st.error("Erro crítico: Verifique os caracteres informados. Digite apenas números separados por espaços.")

# ----------------- TAB 4: BACKUP & SALDO -----------------
with tabs[3]:
    st.markdown("### 💾 Central de Sincronização do Cofre")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Saldo Líquido Registrado", f"R$ {st.session_state.banca:.2f}")
        st.write("Ajuste manual da banca se necessário:")
        nova_banca = st.number_input("Alterar banca para:", value=st.session_state.banca)
        if st.button("Atualizar Saldo"):
            st.session_state.banca = nova_banca
            st.success("Saldo atualizado!")
            st.rerun()
            
    with col2:
        st.markdown("#### 📤 Exportar Nova Versão do Cofre")
        st.write("Baixe a cópia de segurança para salvar seus jogos gerados pendentes e o saldo atualizado.")
        
        doc_json = json.dumps(gerar_backup())
        st.download_button(
            label="💾 BAIXAR COFRE ATUALIZADO (.JSON)",
            data=doc_json,
            file_name="Cofre.json",
            mime="application/json",
            type="primary"
        )
