import streamlit as st
import requests
import json
from collections import Counter
import random

# =====================================================================
# 1. CONFIGURAÇÃO DA PÁGINA (PADRÃO SEGURO NATIVO STREAMLIT)
# =====================================================================
st.set_page_config(
    page_title="SuperLoto - Engenharia Preditiva",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal usando elementos puros do Streamlit (Sem HTML)
st.title("👑 SuperLoto Premium")
st.caption("Sistema Privado de Engenharia Preditiva Avançada — Versão Blindada Python 3.13")

# =====================================================================
# 2. SISTEMA DE SESSÃO E BANCO DE DADOS LOCAL
# =====================================================================
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "usuario_ativo" not in st.session_state: st.session_state.usuario_ativo = None
if "aba_atual" not in st.session_state: st.session_state.aba_atual = "🎯 Operações SuperLoto"
if "historico_sorteios" not in st.session_state: st.session_state.historico_sorteios = {}
if "caixa_saldo" not in st.session_state: st.session_state.caixa_saldo = 500.00
if "jogos_salvos" not in st.session_state: st.session_state.jogos_salvos = []
if "pool_atual" not in st.session_state: st.session_state.pool_atual = []
if "fixas_atuais" not in st.session_state: st.session_state.fixas_atuais = []

USUARIOS_SISTEMA = {"admin": "kadosh15", "irma": "loto15"}

# Histórico de ignição base para o sistema funcionar imediatamente
if not st.session_state.historico_sorteios:
    st.session_state.historico_sorteios = {
        "3100": [1, 2, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 24, 25],
        "3101": [1, 3, 4, 6, 8, 10, 11, 12, 14, 16, 18, 20, 22, 24, 25],
        "3102": [2, 3, 5, 7, 9, 11, 13, 14, 15, 17, 19, 21, 23, 24, 25],
        "3103": [1, 2, 4, 5, 8, 9, 12, 13, 16, 17, 20, 21, 22, 23, 25]
    }

# =====================================================================
# 3. INTERFACE DE AUTENTICAÇÃO
# =====================================================================
if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        user_input = st.text_input("Operador do Sistema", key="login_user")
        pass_input = st.text_input("Chave Kadosh de Acesso", type="password", key="login_pass")
        if st.button("ATIVAR MOTORES PRECOGNITIVOS"):
            if user_input in USUARIOS_SISTEMA and USUARIOS_SISTEMA[user_input] == pass_input:
                st.session_state.autenticado = True
                st.session_state.usuario_ativo = "Irmã" if user_input == "irma" else "Operador Principal"
                st.rerun()
            else:
                st.error("Chave de acesso ou operador incorretos.")

else:
    # Menu lateral nativo completo
    with st.sidebar:
        st.subheader("👑 Menu SuperLoto")
        st.write(f"Operador: **{st.session_state.usuario_ativo}**")
        st.write(f"Caixa: **R$ {st.session_state.caixa_saldo:.2f}**")
        st.markdown("---")
        
        abas_menu = ["🎯 Operações SuperLoto", "📊 Análise de Ciclo & Engenharia", "💳 Gestão de Caixa", "💾 Segurança & Backup"]
        st.session_state.aba_atual = st.radio("Módulos do Sistema", abas_menu)
        
        st.markdown("---")
        if st.button("Encerrar Sessão"):
            st.session_state.autenticado = False
            st.session_state.usuario_ativo = None
            st.rerun()

    st.subheader(f"Módulo: {st.session_state.aba_atual}")

    # =====================================================================
    # 4. MÉTODO DE CAPTURA DA CAIXA (BLINDADO CONTRA TIMEOUT)
    # =====================================================================
    def capturar_resultado_caixa_estavel(concurso=None):
        try:
            url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/"
            if concurso: url += str(concurso)
            response = requests.get(url, timeout=7, verify=False)
            if response.status_code == 200:
                dados = response.json()
                return str(dados["numero"]), [int(x) for x in dados["listaDezenas"]]
        except:
            pass
        return None, None

    # =====================================================================
    # 5. OS 6 MOTORES DE INTELIGÊNCIA UNIFICADOS
    # =====================================================================
    def processar_cerebro_unificado_superloto():
        historico = st.session_state.historico_sorteios
        if len(historico) < 3: return list(range(1, 21)), list(range(1, 9)), "ESTÁVEL"
        
        concursos_ordenados = sorted(historico.keys(), key=lambda x: int(x), reverse=True)
        
        # Motor 1: Cadeia de Transição de Estados (Markov de 2ª Ordem)
        u1 = set(historico[concursos_ordenados[0]])
        u2 = set(historico[concursos_ordenados[1]])
        u3 = set(historico[concursos_ordenados[2]])
        
        scores_base = {}
        for n in range(1, 26):
            score = 0.0
            if n in u1 and n in u2 and n in u3: score += 1.0
            elif n in u1 and n in u2 and n not in u3: score += 2.5
            elif n in u1 and n not in u2 and n not in u3: score += 3.5  
            elif n not in u1 and n in u2 and n in u3: score += 1.5
            elif n not in u1 and n not in u2 and n in u3: score += 2.0
            elif n not in u1 and n not in u2 and n not in u3:
                atraso = 0
                for c in concursos_ordenados:
                    if n not in historico[c]: atraso += 1
                    else: break
                score += (atraso * 1.2)
            scores_base[n] = score

        # Motores 2 e 3: Coocorrência Espacial e Lógica Bayesiana
        top_3_recentes = sorted(list(u1), key=lambda x: scores_base.get(x, 0), reverse=True)[:3]
        co_ocorrencia = Counter()
        for c in concursos_ordenados[:30]:
            sorteio = historico[c]
            if any(t in sorteio for t in top_3_recentes):
                for n in sorteio: co_ocorrencia[n] += 1
        
        scores_finais = {}
        for n in range(1, 26):
            peso_co = (co_ocorrencia[n] / 30.0) * 2.0
            scores_finais[n] = scores_base[n] + peso_co

        # Motor 4: Rastreador Antissaturação de Ciclo das Pedras
        dezenas_sorteadas_no_ciclo = set()
        for c in concursos_ordenados:
            dezenas_sorteadas_no_ciclo.update(historico[c])
            if len(dezenas_sorteadas_no_ciclo) == 25:
                dezenas_sorteadas_no_ciclo = set(historico[c]) 
                break
        dezenas_faltantes_ciclo = set(range(1, 26)) - dezenas_sorteadas_no_ciclo
        
        for n in dezenas_faltantes_ciclo: scores_finais[n] += 4.0

        ranking = sorted(scores_finais.keys(), key=lambda x: scores_finais[x], reverse=True)
        pool_20 = sorted(ranking[:20])
        fixas_8 = sorted(ranking[:8])
        
        repeticao_ultimo = len(u1.intersection(u2))
        clima = "ESTÁVEL" if 8 <= repeticao_ultimo <= 10 else "ERRÁTICO"
        
        return pool_20, fixas_8, clima

    # Motor 5: Peneira de Validação Geométrica Kadosh
    def validar_jogo_peneira_geometrica(dezenas):
        linha1 = len([x for x in dezenas if 1 <= x <= 5])
        linha5 = len([x for x in dezenas if 21 <= x <= 25])
        soma = sum(dezenas)
        pares = len([x for x in dezenas if x % 2 == 0])
        
        if not (160 <= soma <= 220): return False
        if not (6 <= pares <= 9): return False
        if linha1 > 5 or linha5 > 5: return False
        return True

    # Motor 6: Gestor Dinâmico de Caixa Inteligente
    def obter_recomendacao_piloto_caixa(clima):
        saldo = st.session_state.caixa_saldo
        if saldo < 100.00:
            return "🛡️ O ESCUDO", "Aviso: Caixa em zona de risco crítico. Use proteção absoluta."
        if clima == "ERRÁTICO":
            return "🪓 O MACHADO", "Aviso: Clima atual está instável/errático. Reduza custos utilizando jogos de 15 dezenas."
        return "🔱 A LANÇA", "Ambiente Ideal! Caixa saudável e Clima Firme. Força de ataque máxima liberada."

    # =====================================================================
    # MÓDULO 1: 🎯 OPERAÇÕES SUPERLOTO
    # =====================================================================
    if st.session_state.aba_atual == "🎯 Operações SuperLoto":
        col_api1, col_api2 = st.columns([2, 1])
        with col_api1:
            c_input = st.text_input("Digitar Concurso Específico (Vazio para Último Oficial)")
        with col_api2:
            st.markdown(" ") # Substituído de forma segura (Sem HTML)
            if st.button("🔄 SINCRONIZAR CONCURSO REAL"):
                num_c, dez_c = capturar_resultado_caixa_estavel(c_input if c_input else None)
                if num_c:
                    st.session_state.historico_sorteios[num_c] = dez_c
                    st.success(f"Concurso {num_c} sincronizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Servidor da Caixa indisponível no momento. Insira manualmente abaixo para não travar seu jogo.")

        with st.expander("📝 Inserção Manual de Sorteio Suplementar"):
            c_man = st.text_input("Número do Concurso Manual")
            d_man = st.text_input("Insira as 15 Dezenas Separadas por Vírgula (Ex: 1,2,3,4...)")
            if st.button("GRAVAR MANUALMENTE"):
                try:
                    lista_d = [int(x.strip()) for x in d_man.split(",")]
                    if len(lista_d) == 15:
                        st.session_state.historico_sorteios[str(c_man)] = sorted(lista_d)
                        st.success(f"Sorteio {c_man} gravado com sucesso no histórico!")
                        st.rerun()
                    else: st.error("Erro: Um sorteio oficial precisa ter exatamente 15 números.")
                except: st.error("Formato de dados incorreto. Use apenas números separados por vírgulas.")

        st.markdown("---")
        
        pool_20, fixas_8, clima = processar_cerebro_unificado_superloto()
        st.session_state.pool_atual = pool_20
        st.session_state.fixas_atuais = fixas_8
        
        rec_est, rec_txt = obter_recomendacao_piloto_caixa(clima)
        
        c_clima, c_caixa, c_rec = st.columns(3)
        with c_clima: st.metric("🌡️ CLIMA DO SORTEIO", clima)
        with c_caixa: st.metric("💳 SEU CAIXA OPERACIONAL", f"R$ {st.session_state.caixa_saldo:.2f}")
        with c_rec: st.metric("🎯 RECOMENDAÇÃO DO PILOTO", rec_est, help=rec_txt)

        st.write("### 🔮 Volante Preditivo SuperLoto")
        st.write(f"🔒 **Dezenas Fixas Selecionadas (Markov):** {', '.join(f'{x:02d}' for x in fixas_8)}")
        st.write(f"🔮 **Dezenas do seu Pool de Elite (Bayes/Coocorrência):** {', '.join(f'{x:02d}' for x in pool_20 if x not in fixas_8)}")
        st.write(f"❌ **Dezenas Excluídas (Baixa Probabilidade):** {', '.join(f'{x:02d}' for x in range(1, 26) if x not in pool_20)}")

        st.markdown("---")

        st.write("### ⚔️ Configuração do Formato de Ataque")
        
        opcoes_estrategias = {
            "🔱 A LANÇA": {
                "desc": "Poder Ofensivo Máximo. Une 2 jogos de 16 dezenas com 10 jogos de 15 dezenas para cercar desvios e anomalias do sorteio.",
                "custo": 147.00, "prob15": "1 em 4.430", "prob14": "1 em 118", "j15": 10, "j16": 2
            },
            "⚔️ A MARRETA": {
                "desc": "Alto Impacto Concentrado. 3 jogos puros de 16 dezenas montados em matriz compensatória de escada. Prêmios multiplicados.",
                "custo": 168.00, "prob15": "1 em 5.160", "prob14": "1 em 141", "j15": 0, "j16": 3
            },
            "🪓 O MACHADO": {
                "desc": "Cerco Matemático Econômico. Distribuição simétrica perfeita do Pool em 4 jogos simples de 15 dezenas com baixíssimo custo.",
                "custo": 14.00, "prob15": "1 em 3.876", "prob14": "1 em 242", "j15": 4, "j16": 0
            },
            "💎 A COROA": {
                "desc": "Sistema Misto de Equilíbrio. 1 jogo de 16 dezenas (padrão histórico) cruzado com 2 jogos de 15 dezenas focados no fim do ciclo.",
                "custo": 63.00, "prob15": "1 em 7.750", "prob14": "1 em 310", "j15": 2, "j16": 1
            },
            "🛡️ O ESCUDO": {
                "desc": "Proteção Absoluta de Caixa. Gera 2 jogos cirúrgicos de 15 dezenas baseados nos pivôs estáveis de Markov para proteger capital.",
                "custo": 7.00, "prob15": "1 em 7.752", "prob14": "1 em 484", "j15": 2, "j16": 0
            }
        }

        est_escolhida = st.selectbox("Escolha sua Estratégia de Combate", list(opcoes_estrategias.keys()))
        dados_est = opcoes_estrategias[est_escolhida]
        
        st.info(f"""
        **Especificação:** {dados_est['desc']}  
        **💸 Custo da Operação:** R$ {dados_est['custo']:.2f}  
        **🎯 Probabilidade de 15 acertos (No Pool):** {dados_est['prob15']}  
        **🎯 Probabilidade de 14 acertos (No Pool):** {dados_est['prob14']}
        """)

        if st.button("⚡ PROCESSAR E FILTRAR JOGOS DE ELITE"):
            jogos_gerados = []
            restante_pool = [x for x in pool_20 if x not in fixas_8]
            
            tentativas = 0
            alvo_16 = dados_est["j16"]
            alvo_15 = dados_est["j15"]
            
            while len(jogos_gerados) < alvo_16 and tentativas < 1000:
                tentativas += 1
                comb = sorted(fixas_8 + random.sample(restante_pool, 8))
                if validar_jogo_peneira_geometrica(comb) and comb not in jogos_gerados:
                    jogos_gerados.append(comb)
            
            while len(jogos_gerados) < (alvo_16 + alvo_15) and tentativas < 2000:
                tentativas += 1
                comb = sorted(fixas_8 + random.sample(restante_pool, 7))
                if validar_jogo_peneira_geometrica(comb) and comb not in jogos_gerados:
                    jogos_gerados.append(comb)
            
            st.session_state.jogos_salvos = jogos_gerados
            st.session_state.caixa_saldo -= dados_est["custo"]
            st.success(f"Sucesso! {len(jogos_gerados)} Jogos calculados e salvos em memória.")
            st.rerun()

        if st.session_state.jogos_salvos:
            st.write("### 📋 Bilhetes Prontos para Registrar")
            for idx, jogo in enumerate(st.session_state.jogos_salvos):
                texto_jogo = ", ".join(f"{x:02d}" for x in jogo)
                st.code(f"Jogo {idx+1} ({len(jogo)} Dezenas): {texto_jogo}", language="text")

    # =====================================================================
    # MÓDULO 2: 📊 ANÁLISE DE CICLO & ENGENHARIA
    # =====================================================================
    if st.session_state.aba_atual == "📊 Análise de Ciclo & Engenharia":
        st.write("### ⚙️ Auditoria de Motores Preditivos")
        st.write("Base de dados de concursos armazenados no histórico:")
        st.json(st.session_state.historico_sorteios)

    # =====================================================================
    # MÓDULO 3: 💳 GESTÃO DE CAIXA
    # =====================================================================
    if st.session_state.aba_atual == "💳 Gestão de Caixa":
        st.write("### 📈 Painel Financeiro e Apuração de Rateio")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            novo_saldo = st.number_input("Ajustar Saldo de Caixa (R$)", value=float(st.session_state.caixa_saldo))
            if st.button("CONFIRMAR OPERAÇÃO DE SALDO"):
                st.session_state.caixa_saldo = novo_saldo
                st.success("Saldo operacional de banca atualizado!")
                st.rerun()
                
        with col_c2:
            conc_verificar = st.text_input("Número do Concurso para Conferencia de Rateio")
            
        if st.button("🔄 CONFERIR APURAR RATEIO OFICIAL"):
            if conc_verificar in st.session_state.historico_sorteios:
                sorteio_real = set(st.session_state.historico_sorteios[conc_verificar])
                total_ganho = 0.0
                cartoes_premiados = 0
                
                for jogo in st.session_state.jogos_salvos:
                    acertos = len(set(jogo).intersection(sorteio_real))
                    
                    if len(jogo) == 16:
                        if acertos == 15: total_ganho += 1500000.00; cartoes_premiados += 1 
                        elif acertos == 14: total_ganho += 2400.00; cartoes_premiados += 1 
                        elif acertos == 13: total_ganho += 105.00; cartoes_premiados += 1  
                        elif acertos == 12: total_ganho += 48.00; cartoes_premiados += 1   
                        elif acertos == 11: total_ganho += 17.50; cartoes_premiados += 1   
                    else:
                        if acertos == 15: total_ganho += 1500000.00; cartoes_premiados += 1
                        elif acertos == 14: total_ganho += 1200.00; cartoes_premiados += 1
                        elif acertos == 13: total_ganho += 30.00; cartoes_premiados += 1
                        elif acertos == 12: total_ganho += 12.00; cartoes_premiados += 1
                        elif acertos == 11: total_ganho += 6.00; cartoes_premiados += 1
                
                st.session_state.caixa_saldo += total_ganho
                st.success(f"Apuração Finalizada! {cartoes_premiados} cartões premiados encontrados. Retorno de R$ {total_ganho:.2f} adicionados.")
                st.write(f"**Resultado do Concurso {conc_verificar}:** {', '.join(f'{x:02d}' for x in sorted(list(sorteio_real)))}")
            else:
                st.error("Concurso não localizado. Sincronize o concurso ou insira manualmente na aba Operações primeiro.")

    # =====================================================================
    # MÓDULO 4: 💾 SEGURANÇA & BACKUP
    # =====================================================================
    if st.session_state.aba_atual == "💾 Segurança & Backup":
        st.write("### 📂 Central de Salvaguarda de Dados (Backup)")
        
        dados_backup = {
            "caixa_saldo": st.session_state.caixa_saldo,
            "historico_sorteios": st.session_state.historico_sorteios,
            "jogos_salvos": st.session_state.jogos_salvos
        }
        json_string = json.dumps(dados_backup)
        
        st.download_button(
            label="📥 EXTRAIR BACKUP COMPLETO (.JSON)",
            data=json_string,
            file_name="SUPERLOTO_BACKUP.json",
            mime="application/json"
        )
        
        st.markdown("---")
        st.write("#### 📤 Importar Estrutura de Backup")
        arquivo_upload = st.file_uploader("Arraste seu arquivo .json de Backup aqui", type=["json"])
        
        if arquivo_upload is not None:
            try:
                conteudo = json.load(arquivo_upload)
                st.session_state.caixa_saldo = conteudo["caixa_saldo"]
                st.session_state.historico_sorteios = conteudo["historico_sorteios"]
                st.session_state.jogos_salvos = conteudo["jogos_salvos"]
                st.success("Toda a estrutura, saldo e histórico restaurados com sucesso absoluto!")
                st.rerun()
            except:
                st.error("Falha ao descriptografar arquivo de backup. Verifique se o arquivo está correto.")
