import streamlit as st
import pandas as pd
import requests
import json
import random
import uuid
from collections import Counter
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =====================================================================
# CONFIGURAÇÃO E LOGIN
# =====================================================================
st.set_page_config(page_title="LotoMatrix PRO - Agente Autônomo", page_icon="🧬", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #006644;'>🔐 Acesso Restrito - LotoMatrix PRO</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            senha = st.text_input("Digite a Senha de Acesso:", type="password")
            if st.button("ENTRAR NO SISTEMA", type="primary", use_container_width=True):
                if senha == "777":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Acesso Negado.")
    st.stop()

# =====================================================================
# BLINDAGEM DE MEMÓRIA E SANITIZAÇÃO ABSOLUTA
# =====================================================================
def sanitizar_dados(d):
    """Higieniza o backup antigo para os padrões da nova IA e evita KeyError"""
    if "banca" not in d: d["banca"] = 0.0
    if "historico_dados" not in d: d["historico_dados"] = []
    if "jogos_salvos" not in d: d["jogos_salvos"] = []
    if "matriz_viva_atual" not in d: d["matriz_viva_atual"] = []
    if "ia_memoria" not in d: 
        d["ia_memoria"] = {"Tendencia": {"usos": 0, "pontos": 0}, "Reversao": {"usos": 0, "pontos": 0}}
    
    # Arruma jogos antigos que não tinham todos os dados
    for j in d["jogos_salvos"]:
        if "id" not in j: j["id"] = str(uuid.uuid4())
        if "concurso_alvo" not in j: j["concurso_alvo"] = "Legado (S/ Info)"
        if "tamanho" not in j: j["tamanho"] = len(j.get("dezenas", []))
        if "status" not in j: j["status"] = "Aguardando Sorteio"
        if "acertos" not in j: j["acertos"] = 0
        if "estrategia" not in j: j["estrategia"] = "Estratégia Antiga"
        if "justificativa" not in j: j["justificativa"] = "Jogo recuperado de backup antigo."
    return d

if 'data' not in st.session_state:
    st.session_state.data = sanitizar_dados({})

# =====================================================================
# FUNÇÕES DE CALLBACK (Ações dos Botões)
# =====================================================================
def cb_depositar():
    valor = st.session_state.get("input_aporte", 0.0)
    if valor > 0:
        st.session_state.data['banca'] += valor
        st.toast(f"R$ {valor:.2f} creditados na banca!", icon="💰")

def cb_excluir_jogo(jogo_id):
    st.session_state.data['jogos_salvos'] = [j for j in st.session_state.data['jogos_salvos'] if j.get('id') != jogo_id]
    st.toast("Bilhete excluído permanentemente.", icon="🗑️")

def cb_excluir_todos():
    st.session_state.data['jogos_salvos'] = []
    st.toast("Todos os jogos foram apagados da fila.", icon="🧹")

def cb_carregar_cofre():
    file = st.session_state.uploader_cofre
    if file:
        try:
            raw = json.load(file)
            st.session_state.data = sanitizar_dados(raw)
            st.toast("Cofre sincronizado e dados limpos!", icon="✅")
        except Exception as e: st.error(f"Erro ao ler JSON: {e}")

# =====================================================================
# CÉREBRO DA IA (Análise Completa e Transparente)
# =====================================================================
def raciocinio_total_ia(historico, memoria):
    if not historico: return None
    
    todas_dezenas = [n for h in historico for n in h['dezenas']]
    freq = Counter(todas_dezenas)
    freq_max = max(freq.values()) if freq else 1
    
    primos_lista = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    moldura_lista = [1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25]
    
    ultimos_10 = historico[-10:] if len(historico) >= 10 else historico
    media_soma = sum([sum(h['dezenas']) for h in ultimos_10]) / len(ultimos_10)
    media_impares = sum([sum(1 for n in h['dezenas'] if n % 2 != 0) for h in ultimos_10]) / len(ultimos_10)
    media_primos = sum([sum(1 for n in h['dezenas'] if n in primos_lista) for h in ultimos_10]) / len(ultimos_10)
    media_moldura = sum([sum(1 for n in h['dezenas'] if n in moldura_lista) for h in ultimos_10]) / len(ultimos_10)

    atrasos = {n: 0 for n in range(1, 26)}
    for h in reversed(historico):
        for n in range(1, 26):
            if n not in h['dezenas'] and atrasos[n] == 0: atrasos[n] += 1

    ciclo = set()
    jogos_ciclo = 0
    for h in reversed(historico):
        ciclo.update(h['dezenas'])
        jogos_ciclo += 1
        if len(ciclo) == 25: break
    faltam_ciclo = sorted(list(set(range(1, 26)) - ciclo))

    # --- LIBERDADE DA IA: TAMANHO DA MATRIZ ---
    if len(faltam_ciclo) >= 9: qtd_matriz = 23
    elif len(faltam_ciclo) >= 6: qtd_matriz = 21
    elif len(faltam_ciclo) >= 3: qtd_matriz = 19
    else: qtd_matriz = 18

    # --- APRENDIZADO (MEMÓRIA) E PESOS MATEMÁTICOS ---
    pts_tend = memoria["Tendencia"]["pontos"] / max(1, memoria["Tendencia"]["usos"])
    pts_rev = memoria["Reversao"]["pontos"] / max(1, memoria["Reversao"]["usos"])
    
    if media_soma > 198 or pts_rev > pts_tend:
        estrategia = "Reversão Estatística"
        pesos = {i: max(1, (freq_max - freq.get(i, 0)) + (atrasos.get(i, 0) * 5)) for i in range(1, 26)}
        motivo_est = f"A IA escolheu REVERSÃO. A soma está alta ({media_soma:.1f}) ou a memória provou que atrasadas dão mais lucro. Foco em quebra de padrão."
    else:
        estrategia = "Tendência de Frequência"
        pesos = {i: max(1, freq.get(i, 0) + 10) for i in range(1, 26)}
        motivo_est = f"A IA escolheu TENDÊNCIA. A soma está no padrão ({media_soma:.1f}). Aproveitaremos o ciclo das dezenas quentes."

    dezenas_ordenadas = sorted(range(1, 26), key=lambda x: pesos[x], reverse=True)
    matriz_base = sorted(dezenas_ordenadas[:qtd_matriz])
    
    motivo_qtd = f"Matriz fixada em {qtd_matriz} dezenas porque o ciclo ainda busca {len(faltam_ciclo)} números."
    alvo = (historico[-1]['concurso'] + 1) if historico else 1

    return {
        "estrategia": estrategia, "motivo_est": motivo_est, "pesos": pesos, "freq": freq, 
        "atrasos": atrasos, "ciclo_tam": jogos_ciclo, "faltam_ciclo": faltam_ciclo,
        "soma": media_soma, "impares": media_impares, "primos": media_primos, 
        "moldura": media_moldura, "alvo": alvo, "qtd_matriz": qtd_matriz, 
        "motivo_qtd": motivo_qtd, "matriz_base": matriz_base, "pts_tend": pts_tend, "pts_rev": pts_rev
    }

# =====================================================================
# INTERFACE (5 ABAS INTERLIGADAS)
# =====================================================================
st.markdown("<h2 style='text-align: center; color: #1f77b4;'>🧬 LotoMatrix PRO - Agente Autônomo</h2>", unsafe_allow_html=True)
tabs = st.tabs(["📂 1. Banco de Dados", "🧠 2. Cérebro Analítico (IA)", "🤖 3. Geração Autônoma", "📜 4. Fila de Espera", "🏆 5. Sincronização & Rateio"])

# --- TAB 1: GESTÃO CENTRAL E BANCA ---
with tabs[0]:
    st.markdown("### 💾 Gestão Central e Banca")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.file_uploader("📥 Carregar Cofre.json (Ativar Inteligência)", type="json", key="uploader_cofre", on_change=cb_carregar_cofre)
            st.info(f"📊 **Dados Oficiais na Memória:** {len(st.session_state.data['historico_dados'])} concursos.")
            st.download_button("📤 Fazer Backup do Cofre Seguro", json.dumps(st.session_state.data), "Cofre_Atualizado.json", type="primary", use_container_width=True)
    with c2:
        with st.container(border=True):
            st.metric("💰 Saldo em Banca (R$)", f"{st.session_state.data['banca']:.2f}")
            st.number_input("Adicionar Saldo (R$):", min_value=0.0, step=10.0, key="input_aporte")
            st.button("CONFIRMAR DEPÓSITO", on_click=cb_depositar, use_container_width=True)

# --- TAB 2: CÉREBRO ANALÍTICO COMPLETO ---
with tabs[1]:
    if st.session_state.data["historico_dados"]:
        ia = raciocinio_total_ia(st.session_state.data["historico_dados"], st.session_state.data["ia_memoria"])
        st.session_state.data["matriz_viva_atual"] = ia["matriz_base"]
        
        st.markdown(f"### 🧠 O Raio-X da Inteligência — Preparação para o Concurso `{ia['alvo']}`")
        
        # 1. Estratégia e Decisão
        st.success(f"**💡 ESTRATÉGIA ATIVA:** {ia['estrategia']} \n\n**O PORQUÊ:** {ia['motivo_est']}")
        st.info(f"**🎯 MATRIZ VIVA ({ia['qtd_matriz']} Dezenas):** {', '.join([f'{n:02d}' for n in ia['matriz_base']])} \n\n*{ia['motivo_qtd']}*")
        
        # 2. Resumo de Comportamento e Ciclo
        st.markdown("#### ⚙️ Parâmetros Oficiais do Cenário Atual")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Soma Global (Ideal~195)", f"{ia['soma']:.1f}")
        c2.metric("Ímpares (Ideal~7.5)", f"{ia['impares']:.1f}")
        c3.metric("Primos (Ideal~5.5)", f"{ia['primos']:.1f}")
        c4.metric("Moldura (Ideal~10)", f"{ia['moldura']:.1f}")

        st.warning(f"⏳ **O Ciclo:** Aberto há {ia['ciclo_tam']} sorteios. **Faltam:** {ia['faltam_ciclo']}")
        
        # 3. Gráficos de Frequência vs Atraso
        col_f, col_a = st.columns(2)
        with col_f:
            st.markdown("🔥 **Ranking das Quentes**")
            df_freq = pd.DataFrame.from_dict(ia['freq'], orient='index', columns=['Sorteios']).sort_values('Sorteios', ascending=False)
            st.dataframe(df_freq.head(7), use_container_width=True)
        with col_a:
            st.markdown("❄️ **Ranking de Atrasos**")
            df_atr = pd.DataFrame.from_dict(ia['atrasos'], orient='index', columns=['Sem Sair']).sort_values('Sem Sair', ascending=False)
            st.dataframe(df_atr.head(7), use_container_width=True)
            
        st.markdown("#### 🧠 O que a IA aprendeu até agora (Memória Automática)")
        st.write(f"Estratégia **Tendência**: {ia['pts_tend']:.1f} pts de média | Estratégia **Reversão**: {ia['pts_rev']:.1f} pts de média")

    else: st.warning("Suba o Cofre na Aba 1 para despertar a inteligência.")

# --- TAB 3: GERAÇÃO AUTÔNOMA ---
with tabs[2]:
    st.markdown("### 🚀 Algoritmo de Criação Anti-Repetição")
    if st.session_state.data["historico_dados"]:
        ia = raciocinio_total_ia(st.session_state.data["historico_dados"], st.session_state.data["ia_memoria"])
        
        orcamento = st.number_input("Autorizar orçamento para apostar (R$):", min_value=3.5, max_value=max(3.5, st.session_state.data['banca']), step=3.5)
        
        if st.button("🧬 GERAR JOGOS EXCLUSIVOS", type="primary", use_container_width=True):
            if st.session_state.data['banca'] < orcamento:
                st.error("Banca insuficiente. Por favor, deposite na Aba 1.")
            else:
                st.session_state.data['banca'] -= orcamento
                historico_sets = [set(h['dezenas']) for h in st.session_state.data["historico_dados"]]
                gasto = 0.0
                
                while (orcamento - gasto) >= 3.5:
                    tam = 16 if (orcamento - gasto) >= 56.0 and random.random() > 0.85 else 15
                    custo = 56.0 if tam == 16 else 3.5
                    
                    dezenas_disponiveis = ia['matriz_base']
                    pesos_sublista = [ia['pesos'][i] for i in dezenas_disponiveis]
                    
                    tentativas = 0
                    jogo_inedito = []
                    while tentativas < 1000: # Proteção extra no loop
                        candidato = sorted(list(set(random.choices(dezenas_disponiveis, weights=pesos_sublista, k=tam))))
                        while len(candidato) < tam:
                            sobra = list(set(dezenas_disponiveis) - set(candidato))
                            if not sobra: break
                            candidato.append(random.choice(sobra))
                            candidato = sorted(list(set(candidato)))
                        
                        if set(candidato) not in historico_sets:
                            jogo_inedito = candidato
                            break
                        tentativas += 1
                    
                    if not jogo_inedito: 
                        jogo_inedito = sorted(random.sample(dezenas_disponiveis, tam))
                        
                    st.session_state.data["jogos_salvos"].append({
                        "id": str(uuid.uuid4()), 
                        "concurso_alvo": ia['alvo'], 
                        "dezenas": jogo_inedito,
                        "tamanho": tam, 
                        "estrategia": ia['estrategia'], 
                        "justificativa": f"Matriz {ia['qtd_matriz']} Dz. Motivo: {ia['estrategia']}",
                        "status": "Aguardando Sorteio", 
                        "acertos": 0
                    })
                    gasto += custo
                st.success(f"Geração concluída! R$ {gasto:.2f} investidos da banca. Veja os cards na Aba 4.")
                st.rerun()
    else: st.warning("Suba o Cofre na Aba 1.")

# --- TAB 4: FILA DE ESPERA (O CARD À PROVA DE BALAS) ---
with tabs[3]:
    st.markdown("### 🎫 Cartões Prontos na Fila de Sorteio")
    if st.session_state.data["jogos_salvos"]:
        st.button("🚨 APAGAR TODOS OS JOGOS DA TELA", on_click=cb_excluir_todos, type="secondary")
        st.divider()
        
        for j in st.session_state.data["jogos_salvos"]:
            with st.container(border=True):
                c_card, c_del = st.columns([5, 1])
                with c_card:
                    # O uso do .get() abaixo BLINDA a tela contra KeyErrors de arquivos antigos
                    alvo = j.get('concurso_alvo', 'N/A')
                    tam = j.get('tamanho', len(j.get('dezenas', [])))
                    status = j.get('status', 'Aguardando Sorteio')
                    dezenas = j.get('dezenas', [])
                    justif = j.get('justificativa', 'Sem info.')
                    
                    cor = "green" if status == "Premiado" else "blue" if status == "Aguardando Sorteio" else "gray"
                    
                    st.markdown(f"🎯 **Alvo:** `{alvo}` | **{tam} Dezenas** | Status: :{cor}[{status}]")
                    st.code(" - ".join([f"{n:02d}" for n in dezenas]))
                    st.caption(f"💡 *Raciocínio:* {justif}")
                with c_del:
                    jogo_id = j.get('id')
                    if jogo_id:
                        st.button("🗑️ Apagar", key=f"del_{jogo_id}", on_click=cb_excluir_jogo, args=(jogo_id,), use_container_width=True)
    else: st.info("Não existem bilhetes na fila. Gere novos jogos na Aba 3.")

# --- TAB 5: AUDITORIA E SINCRONIZAÇÃO CAIXA ---
with tabs[4]:
    st.markdown("### 🏆 Sincronização, Avaliação e Ensino da IA")
    
    if st.button("🔄 CONFERIR RESULTADO E ENSINAR A IA", type="primary", use_container_width=True):
        with st.spinner("Puxando concurso oficial direto da Caixa..."):
            try:
                res = requests.get("https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest", verify=False, timeout=10).json()
                st.session_state.caixa_latest = res
                sorteio_oficial = set(map(int, res['dezenas']))
                
                lucro = 0.0
                for j in st.session_state.data.get("jogos_salvos", []):
                    if j.get('status') == "Aguardando Sorteio":
                        pontos = len(set(j.get('dezenas', [])).intersection(sorteio_oficial))
                        j['acertos'] = pontos
                        
                        # --- IA APRENDENDO O RESULTADO! ---
                        estr_nome = "Tendencia" if "Tendência" in j.get('estrategia', '') else "Reversao"
                        st.session_state.data["ia_memoria"][estr_nome]["usos"] += 1
                        st.session_state.data["ia_memoria"][estr_nome]["pontos"] += pontos
                        
                        premio = {11: 6.0, 12: 12.0, 13: 30.0, 14: 2000.0, 15: 1500000.0}.get(pontos, 0.0)
                        if pontos >= 11:
                            j['status'] = "Premiado"
                            lucro += premio
                        else: j['status'] = "Não Premiado"
                
                st.session_state.data["banca"] += lucro
                st.success(f"Conferência concluída! Lucro processado: R$ {lucro:.2f}. A IA foi atualizada e aprendeu com a nota!")
            except: st.error("Erro ao conectar nos servidores oficiais da Caixa Econômica.")

    if 'caixa_latest' in st.session_state:
        r = st.session_state.caixa_latest
        if st.session_state.data.get("matriz_viva_atual"):
            mv = set(st.session_state.data["matriz_viva_atual"])
            sorteio_set = set(map(int, r['dezenas']))
            acertos_mv = len(mv.intersection(sorteio_set))
            
            st.markdown(f"""
            <div style="background: #ebf8ff; padding: 15px; border-left: 5px solid #2b6cb0; margin-bottom: 15px; border-radius: 4px;">
                <h4 style="margin:0; color:#2b6cb0;">📊 Análise Forense da Matriz IA</h4>
                A Matriz construída continha <b>{len(mv)} dezenas</b>. No concurso oficial da Caixa, <b>{acertos_mv} dezenas</b> saíram de dentro da Matriz escolhida.
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"#### 🏛️ Concurso Oficial: {r['concurso']} ({r['data']})")
        st.code(" - ".join(r['dezenas']))
        st.markdown("#### 💰 Tabela Oficial de Rateio")
        st.table(pd.DataFrame(r['premiacoes']))
