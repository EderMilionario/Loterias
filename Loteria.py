import streamlit as st
import pandas as pd
import requests
import json
import random
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
            senha = st.text_input("Digite a Senha (admin123):", type="password")
            if st.button("ENTRAR NO SISTEMA", type="primary", use_container_width=True):
                if senha == "admin123":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Acesso Negado.")
    st.stop()

# =====================================================================
# BLINDAGEM E MIGRAÇÃO DE DADOS (Resolve o KeyError)
# =====================================================================
def sanitizar_dados(d):
    """Garante que o backup antigo ganhe as novas funções de IA sem travar."""
    if "banca" not in d: d["banca"] = 0.0
    if "historico_dados" not in d: d["historico_dados"] = []
    if "jogos_salvos" not in d: d["jogos_salvos"] = []
    if "ia_memoria" not in d: # Aqui a IA guarda os acertos para aprender
        d["ia_memoria"] = {"Tendencia": {"usos": 0, "pontos": 0}, "Reversao": {"usos": 0, "pontos": 0}}
    
    for j in d["jogos_salvos"]:
        if "justificativa" not in j: j["justificativa"] = "Jogo legado (Cofre antigo)."
        if "estrategia" not in j: j["estrategia"] = "Padrão"
        if "acertos" not in j: j["acertos"] = 0
        if "tamanho" not in j: j["tamanho"] = len(j.get("dezenas", []))
        if "status" not in j: j["status"] = "Aguardando Sorteio"
    return d

if 'data' not in st.session_state:
    st.session_state.data = sanitizar_dados({})

# =====================================================================
# CÉREBRO DA IA (Análise e Aprendizado)
# =====================================================================
def raciocinio_ia(historico, memoria):
    if not historico: return None
    todas = [n for h in historico for n in h['dezenas']]
    freq = Counter(todas)
    
    atrasos = {n: 0 for n in range(1, 26)}
    for h in reversed(historico):
        for n in range(1, 26):
            if n not in h['dezenas'] and atrasos[n] == 0: atrasos[n] += 1
            elif n in h['dezenas'] and atrasos[n] == 0: pass
            
    # IA Aprendendo: Qual estratégia deu mais pontos no passado?
    media_tendencia = memoria["Tendencia"]["pontos"] / max(1, memoria["Tendencia"]["usos"])
    media_reversao = memoria["Reversao"]["pontos"] / max(1, memoria["Reversao"]["usos"])
    
    # Decisão
    if media_tendencia >= media_reversao:
        estrategia = "Tendencia"
        pesos = {i: freq.get(i, 1) for i in range(1, 26)}
        motivo = "A IA escolheu TENDÊNCIA porque, no histórico do seu Cofre, focar nas quentes gerou mais acertos."
    else:
        estrategia = "Reversao"
        pesos = {i: atrasos[i] + 1 for i in range(1, 26)}
        motivo = "A IA escolheu REVERSÃO. O histórico mostra que quebrar padrões atrasados está rendendo mais."

    # Ciclo
    ciclo = set()
    concursos_ciclo = 0
    for h in reversed(historico):
        ciclo.update(h['dezenas'])
        concursos_ciclo += 1
        if len(ciclo) == 25: break
    faltam_ciclo = sorted(list(set(range(1, 26)) - ciclo))

    return {"estrategia": estrategia, "motivo": motivo, "pesos": pesos, "freq": freq, "atrasos": atrasos, "ciclo_tamanho": concursos_ciclo, "faltam_ciclo": faltam_ciclo}

# =====================================================================
# INTERFACE (5 ABAS PROFISSIONAIS)
# =====================================================================
st.markdown("<h2 style='text-align: center; color: #1f77b4;'>🧬 LotoMatrix PRO - Agente Autônomo</h2>", unsafe_allow_html=True)

tabs = st.tabs(["📂 1. Gestão e Cofre", "📊 2. Painel da IA", "🤖 3. Gerador", "📜 4. Jogos em Espera", "🏆 5. Auditoria & Caixa"])

# --- ABA 1: COFRE ---
with tabs[0]:
    st.markdown("### 💾 Segurança de Dados")
    c1, c2 = st.columns([2, 1])
    with c1:
        with st.container(border=True):
            st.info("Suba seu backup para a IA começar a trabalhar.")
            file = st.file_uploader("Upload do Cofre.json", type="json")
            if file:
                try:
                    raw_data = json.load(file)
                    st.session_state.data = sanitizar_dados(raw_data)
                    st.success("✅ Banco de Dados Injetado e Limpo de Erros!")
                except Exception as e: st.error(f"Arquivo corrompido: {e}")
    with c2:
        with st.container(border=True):
            st.metric("Banca Atual", f"R$ {st.session_state.data['banca']:.2f}")
            st.download_button("📥 Baixar Novo Cofre (Backup)", json.dumps(st.session_state.data), "Cofre_Atualizado.json", type="primary", use_container_width=True)

# --- ABA 2: PAINEL DA IA ---
with tabs[1]:
    if st.session_state.data["historico_dados"]:
        ia = raciocinio_ia(st.session_state.data["historico_dados"], st.session_state.data["ia_memoria"])
        st.markdown("### 🧠 Central de Raciocínio (XAI)")
        st.info(f"**Estratégia Dominante:** {ia['estrategia']}\n\n**O que a IA está pensando:** {ia['motivo']}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Status do Ciclo", f"{ia['ciclo_tamanho']} Concursos")
        if ia['faltam_ciclo']: c1.warning(f"Faltam sair: {ia['faltam_ciclo']}")
        else: c1.success("Ciclo Fechado.")
        
        c2.markdown("#### 🔥 Dezenas Quentes")
        df_freq = pd.DataFrame.from_dict(ia['freq'], orient='index', columns=['Vezes Sorteada']).sort_values('Vezes Sorteada', ascending=False)
        c2.bar_chart(df_freq.head(10))
        
        c3.markdown("#### ❄️ Maiores Atrasos")
        df_atr = pd.DataFrame.from_dict(ia['atrasos'], orient='index', columns=['Concursos Atrasada']).sort_values('Concursos Atrasada', ascending=False)
        c3.bar_chart(df_atr.head(10))
    else: st.warning("Suba o Cofre na Aba 1.")

# --- ABA 3: GERADOR ---
with tabs[2]:
    st.markdown("### 🚀 Laboratório de Geração Automática")
    if st.session_state.data["historico_dados"]:
        ia = raciocinio_ia(st.session_state.data["historico_dados"], st.session_state.data["ia_memoria"])
        col1, col2 = st.columns(2)
        budget = col1.number_input("Quanto deseja investir neste lote? (R$)", min_value=3.5, step=3.5, value=10.5)
        
        if st.button("🧬 GERAR LOTE INTELIGENTE", type="primary", use_container_width=True):
            st.session_state.data["banca"] -= budget
            jogos_gerados = []
            
            while budget >= 3.5:
                tam = 16 if budget >= 56.0 and random.random() > 0.8 else 15
                custo = 56.0 if tam == 16 else 3.5
                if budget < custo: break
                
                # Sorteio ponderado pela IA
                numeros = list(range(1, 26))
                pesos_lista = [ia['pesos'][i] for i in numeros]
                jogo = sorted(list(set(random.choices(numeros, weights=pesos_lista, k=tam))))
                
                # Garante que gerou o tamanho certo
                while len(jogo) < tam:
                    faltantes = list(set(numeros) - set(jogo))
                    jogo.append(random.choice(faltantes))
                    jogo = sorted(jogo)

                novo = {
                    "dezenas": jogo, "tamanho": tam, "estrategia": ia['estrategia'],
                    "justificativa": ia['motivo'], "status": "Aguardando Sorteio", "acertos": 0
                }
                st.session_state.data["jogos_salvos"].append(novo)
                jogos_gerados.append(novo)
                budget -= custo
                
            st.success("Jogos gerados e guardados! A banca foi atualizada.")
            st.rerun()
            
        if st.session_state.data["jogos_salvos"]:
            texto_txt = "=== JOGOS LOTO MATRIX ===\n"
            for j in st.session_state.data["jogos_salvos"]: texto_txt += str(j['dezenas']) + "\n"
            st.download_button("📥 Extrair Todos os Jogos para TXT", texto_txt, "Meus_Jogos.txt", use_container_width=True)
    else: st.warning("Suba o Cofre na Aba 1.")

# --- ABA 4: JOGOS EM ESPERA ---
with tabs[3]:
    st.markdown("### 🎫 Lote de Jogos Ativos")
    c_btn = st.columns([3, 1])[1]
    if c_btn.button("🗑️ Excluir Todos os Jogos", use_container_width=True):
        st.session_state.data["jogos_salvos"] = []
        st.rerun()

    if not st.session_state.data["jogos_salvos"]: st.info("Nenhum jogo na fila.")
    for idx, j in enumerate(st.session_state.data["jogos_salvos"]):
        cor = "green" if j.get('status') == "Premiado" else "blue" if j.get('status') == "Aguardando Sorteio" else "gray"
        with st.container(border=True):
            st.markdown(f"**BILHETE {idx+1}** | Tamanho: {j.get('tamanho')} | Status: :{cor}[{j.get('status')}]")
            st.code(" - ".join([f"{n:02d}" for n in j.get('dezenas', [])]))
            st.caption(f"**🧠 Veredito da IA na hora da geração:** {j.get('justificativa', 'Sem info')}")

# --- ABA 5: AUDITORIA CAIXA ---
with tabs[4]:
    st.markdown("### 🏆 Conferência Real e Inteligência de Aprendizado")
    
    if st.button("🔄 Sincronizar Resultado Oficial", type="primary", use_container_width=True):
        with st.spinner("Puxando dados da Caixa..."):
            try:
                res = requests.get("https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest", verify=False, timeout=10).json()
                sorteio = set(map(int, res['dezenas']))
                st.session_state.ultimo_sorteio_caixa = res
                
                # Confere os jogos e Ensina a IA
                ganho_total = 0.0
                for j in st.session_state.data["jogos_salvos"]:
                    if j['status'] == "Aguardando Sorteio":
                        acertos = len(set(j['dezenas']).intersection(sorteio))
                        j['acertos'] = acertos
                        
                        # IA Aprendendo!
                        est_usada = j.get('estrategia', 'Tendencia')
                        if est_usada in st.session_state.data["ia_memoria"]:
                            st.session_state.data["ia_memoria"][est_usada]["usos"] += 1
                            st.session_state.data["ia_memoria"][est_usada]["pontos"] += acertos
                        
                        premio = 0.0
                        if acertos == 11: premio = 6.0
                        elif acertos == 12: premio = 12.0
                        elif acertos == 13: premio = 30.0
                        elif acertos == 14: premio = 2000.0
                        elif acertos == 15: premio = 1000000.0
                        
                        if acertos >= 11:
                            j['status'] = "Premiado"
                            ganho_total += premio
                        else: j['status'] = "Não Premiado"
                
                st.session_state.data["banca"] += ganho_total
                st.success(f"Auditoria concluída! Lucro do lote: R$ {ganho_total:.2f}. A IA registrou os acertos para a próxima geração.")
            except: st.error("Erro na API da Caixa. Tente novamente em instantes.")

    if 'ultimo_sorteio_caixa' in st.session_state:
        res = st.session_state.ultimo_sorteio_caixa
        st.markdown(f"#### Concurso {res['concurso']} | Data: {res['data']}")
        st.code(" - ".join(res['dezenas']))
        st.markdown("#### 🏛️ Rateio Oficial")
        st.table(pd.DataFrame(res['premiacoes']))
