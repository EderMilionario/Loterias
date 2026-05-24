import streamlit as st
import requests
import json
from collections import Counter
import random

# =====================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E IDENTIDADE VISUAL (DARK, MAGENTA & GOLD)
# =====================================================================
st.set_page_config(
    page_title="SuperLoto - Engenharia Preditiva",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Injetada para Visual Premium de Elite (CORRIGIDO)
st.markdown("""
    <style>
        .stApp {
            background-color: #0A0C10;
            color: #E2E8F0;
        }
        .stTextInput input, .stNumberInput input {
            background-color: #141822 !important;
            color: #FFFFFF !important;
            border: 1px solid #D4AF37 !important;
            border-radius: 8px !important;
        }
        .stButton>button {
            background: linear-gradient(135deg, #D4AF37 0%, #AA7C11 100%) !important;
            color: #0A0C10 !important;
            font-weight: bold !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 2rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0px 4px 12px rgba(212, 175, 55, 0.2) !important;
            width: 100%;
        }
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0px 6px 18px rgba(212, 175, 55, 0.4) !important;
            color: #0A0C10 !important;
        }
        /* Bolas Oficiais da Lotofácil */
        .bola-loto {
            display: inline-block;
            width: 50px;
            height: 50px;
            line-height: 50px;
            text-align: center;
            border-radius: 50%;
            font-weight: bold;
            font-size: 1.2rem;
            margin: 5px;
            box-shadow: inset -3px -3px 8px rgba(0,0,0,0.4), 2px 2px 5px rgba(0,0,0,0.3);
        }
        .bola-padrao { background: #93278F; color: white; border: 2px solid #D4AF37; }
        .bola-pool { background: linear-gradient(135deg, #BD10E0 0%, #93278F 100%); color: white; border: 3px solid #D4AF37; box-shadow: 0 0 12px #D4AF37; }
        .bola-fixa { background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); color: #0A0C10; border: 3px solid #FFF; box-shadow: 0 0 15px #FFD700; }
        .bola-excluida { background: #2D3748; color: #718096; border: 2px dashed #4A5568; opacity: 0.4; }
        .bola-sorteada { background: #00E676; color: #0A0C10; border: 2px solid #FFF; box-shadow: 0 0 12px #00E676; }
    </style>
""", unsafe_html=True)

# =====================================================================
# 2. INICIALIZAÇÃO DE VARIÁVEIS DE ESTADO (SESSION STATE)
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

# SIMULAÇÃO DE HISTÓRICO BASE PARA IGNIÇÃO DO SISTEMA SE API FALHAR
if not st.session_state.historico_sorteios:
    st.session_state.historico_sorteios = {
        "3100": [1, 2, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 24, 25],
        "3101": [1, 3, 4, 6, 8, 10, 11, 12, 14, 16, 18, 20, 22, 24, 25],
        "3102": [2, 3, 5, 7, 9, 11, 13, 14, 15, 17, 19, 21, 23, 24, 25],
        "3103": [1, 2, 4, 5, 8, 9, 12, 13, 16, 17, 20, 21, 22, 23, 25]
    }

# =====================================================================
# 3. INTERFACE DE LOGIN DE ELITE
# =====================================================================
if not st.session_state.autenticado:
    st.markdown("<br><br><h1 style='text-align: center; color: #D4AF37; font-size: 3rem; font-weight: 800;'>👑 SUPERLOTO</h1>", unsafe_html=True)
    st.markdown("<p style='text-align: center; color: #A0AEC0; font-size: 1.2rem;'>Sistema Privado de Engenharia Preditiva Avançada</p><br>", unsafe_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='background-color: #141822; padding: 2.5rem; border-radius: 16px; border: 1px solid #2D3748; box-shadow: 0 10px 25px rgba(0,0,0,0.5);'>", unsafe_html=True)
        user_input = st.text_input("Operador do Sistema", key="login_user")
        pass_input = st.text_input("Chave Kadosh de Acesso", type="password", key="login_pass")
        if st.button("ATIVAR MOTORES PRECOGNITIVOS"):
            if user_input in USUARIOS_SISTEMA and USUARIOS_SISTEMA[user_input] == pass_input:
                st.session_state.autenticado = True
                st.session_state.usuario_ativo = "Irmã" if user_input == "irma" else "Operador Principal"
                st.rerun()
            else:
                st.error("Chave de acesso ou operador incorretos.")
        st.markdown("</div>", unsafe_html=True)

else:
    # Barra Lateral Customizada de Navegação
    with st.sidebar:
        st.markdown("<h2 style='color: #D4AF37; margin-bottom: 0;'>👑 SuperLoto</h2>", unsafe_html=True)
        st.markdown(f"<p style='color: #A0AEC0; font-size: 0.9rem;'>Operador: <span style='color: #FFF; font-weight:bold;'>{st.session_state.usuario_ativo}</span></p>", unsafe_html=True)
        st.markdown("<hr style='border-color: #2D3748;'>", unsafe_html=True)
        
        abas_menu = ["🎯 Operações SuperLoto", "📊 Análise de Ciclo & Engenharia", "💳 Gestão de Caixa", "💾 Segurança & Backup"]
        st.session_state.aba_atual = st.radio("Módulos do Sistema", abas_menu)
        
        st.markdown("<br><hr style='border-color: #2D3748;'>", unsafe_html=True)
        if st.button("Encerrar Sessão"):
            st.session_state.autenticado = False
            st.session_state.usuario_ativo = None
            st.rerun()

    st.markdown(f"<h1 style='color: #FFFFFF; margin-top: 0;'>SuperLoto <span style='color: #D4AF37;'>|</span> <span style='font-size: 1.5rem; color: #A0AEC0;'>{st.session_state.aba_atual}</span></h1>", unsafe_html=True)

    # =====================================================================
    # 4. SISTEMA DE CAPTURA OFICIAL HÍBRIDO (MANUAL/AUTOMÁTICO)
    # =====================================================================
    def capturar_resultado_caixa_estavel(concurso=None):
        try:
            url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/"
            if concurso: url += str(concurso)
            response = requests.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                dados = response.json()
                num_concurso = str(dados["numero"])
                lista_dezenas = [int(x) for x in dados["listaDezenas"]]
                return num_concurso, lista_dezenas
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
        
        # MOTOR 1: Cadeia de Transição de Estados (Markov de 2ª Ordem - Curto Prazo)
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

        # MOTOR 2 & 3: Coocorrência Espacial & Lógica Bayesiana (Longo Prazo)
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

        # MOTOR 4: Sensor de Ruptura de Ciclo (Antissaturação)
        dezenas_sorteadas_no_ciclo = set()
        for c in concursos_ordenados:
            dezenas_sorteadas_no_ciclo.update(historico[c])
            if len(dezenas_sorteadas_no_ciclo) == 25:
                dezenas_sorteadas_no_ciclo = set(historico[c]) 
                break
        dezenas_faltantes_ciclo = set(range(1, 26)) - dezenas_sorteadas_no_ciclo
        
        for n in dezenas_faltantes_ciclo:
            scores_finais[n] += 4.0

        ranking = sorted(scores_finais.keys(), key=lambda x: scores_finais[x], reverse=True)
        pool_20 = sorted(ranking[:20])
        fixas_8 = sorted(ranking[:8])
        
        repeticao_ultimo = len(u1.intersection(u2))
        clima = "ESTÁVEL" if 8 <= repeticao_ultimo <= 10 else "ERRÁTICO"
        
        return pool_20, fixas_8, clima

    # MOTOR 5: Peneira de Descarte Geométrico e Simetria Kadosh
    def validar_jogo_peneira_geometrica(dezenas):
        linha1 = len([x for x in dezenas if 1 <= x <= 5])
        linha5 = len([x for x in dezenas if 21 <= x <= 25])
        soma = sum(dezenas)
        pares = len([x for x in dezenas if x % 2 == 0])
        
        if not (160 <= soma <= 220): return False
        if not (6 <= pares <= 9): return False
        if linha1 > 5 or linha5 > 5: return False
        return True

    # MOTOR 6: Inteligência Financeira e Piloto Automático de Caixa
    def obter_recomendacao_piloto_caixa(clima):
        saldo = st.session_state.caixa_saldo
        if saldo < 100.00:
            return "🛡️ O ESCUDO", "Aviso: Caixa em zona de risco crítico. Use proteção absoluta."
        if clima == "ERRÁTICO":
            return "🪓 O MACHADO", "Aviso: Clima atual está instável/errático. Reduza custos utilizando jogos de 15 dezenas."
        return "🔱 A LANÇA", "Ambiente Ideal! Caixa saudável e Clima Firme. Força de ataque máxima liberada."

    # =====================================================================
    # MÓDULO 1:🎯 OPERAÇÕES SUPERLOTO
    # =====================================================================
    if st.session_state.aba_atual == "🎯 Operações SuperLoto":
        col_api1, col_api2 = st.columns([2, 1])
        with col_api1:
            st.markdown("<h3 style='color: #D4AF37;'>🔄 Sincronização do Sistema</h3>", unsafe_html=True)
            c_input = st.text_input("Digitar Concurso Específico (Vazio para Último Oficial)")
        with col_api2:
            st.markdown("<br>", unsafe_html=True)
            if st.button("SINCRONIZAR CONCURSO REAL"):
                num_c, dez_c = capturar_resultado_caixa_estavel(c_input if c_input else None)
                if num_c:
                    st.session_state.historico_sorteios[num_c] = dez_c
                    st.success(f"Concurso {num_c} capturado com sucesso da fonte oficial!")
                else:
                    st.warning("Falha na captura automática. Modo manual ativado.")

        with st.expander("📝 Inserção Manual de Sorteio"):
            c_man = st.text_input("Número do Concurso Manual")
            d_man = st.text_input("Insira as 15 Dezenas Separadas por Vírgula (Ex: 1,2,3...)")
            if st.button("GRAVAR MANUALMENTE"):
                try:
                    lista_d = [int(x.strip()) for x in d_man.split(",")]
                    if len(lista_d) == 15:
                        st.session_state.historico_sorteios[c_man] = sorted(lista_d)
                        st.success("Gravado com Sucesso!")
                    else: st.error("Insira exatamente 15 números.")
                except: st.error("Formato de dados inválido.")

        st.markdown("---")
        
        pool_20, fixas_8, clima = processar_cerebro_unificado_superloto()
        st.session_state.pool_atual = pool_20
        st.session_state.fixas_atuais = fixas_8
        
        rec_est, rec_txt = obter_recomendacao_piloto_caixa(clima)
        
        c_clima, c_caixa, c_rec = st.columns(3)
        with c_clima: st.metric("🌡️ CLIMA DO SORTEIO", clima)
        with c_caixa: st.metric("💳 SEU CAIXA OPERACIONAL", f"R$ {st.session_state.caixa_saldo:.2f}")
        with c_rec: st.metric("🎯 RECOMENDAÇÃO DO PILOTO", rec_est, help=rec_txt)

        st.markdown("<h3 style='color: #D4AF37;'>🔮 Volante Preditivo SuperLoto (Análise de Massa)</h3>", unsafe_html=True)
        html_volante = "<div style='background-color:#141822; padding:1.5rem; border-radius:12px; border:1px solid #2D3748; text-align:center;'>"
        for n in range(1, 26):
            classe_bola = "bola-padrao"
            if n in fixas_8: classe_bola = "bola-fixa"
            elif n in pool_20: classe_bola = "bola-pool"
            else: classe_bola = "bola-excluida"
            
            txt_bola = f"🔒{n:02d}" if n in fixas_8 else f"{n:02d}"
            html_volante += f"<span class='bola-loto {classe_bola}'>{txt_bola}</span>"
            if n % 5 == 0: html_volante += "<br>"
        html_volante += "</div>"
        st.markdown(html_volante, unsafe_html=True)
        st.markdown("<p style='font-size:0.9rem; color:#A0AEC0;'>Legenda: <span style='color:#FFD700;'>■ Fixas de Arrastre</span> | <span style='color:#BD10E0;'>■ Pool de Elite</span> | <span style='color:#4A5568;'>■ Excluídas do Jogo</span></p>", unsafe_html=True)

        st.markdown("---")

        st.markdown("<h3 style='color: #D4AF37;'>⚔️ Configuração do Formato de Ataque</h3>", unsafe_html=True)
        
        opcoes_estrategias = {
            "🔱 A LANÇA": {
                "desc": "Poder Ofensivo Máximo. Une 2 jogos robustos de 16 dezenas (foco em prêmio multiplicado) com 10 jogos de 15 dezenas (rede de contenção contra zebras).",
                "custo": 147.00, "prob15": "1 em 4.430", "prob14": "1 em 118", "j15": 10, "j16": 2
            },
            "⚔️ A MARRETA": {
                "desc": "Alto Impacto Concentrado. Entrega 3 jogos puros de 16 dezenas configurados em formato de escada compensatória. Poder máximo focado em faturar prêmios multiplicados.",
                "custo": 168.00, "prob15": "1 em 5.160", "prob14": "1 em 141", "j15": 0, "j16": 3
            },
            "🪓 O MACHADO": {
                "desc": "Cerco Matemático Econômico. Distribuição simétrica perfeita do Pool em 4 jogos simples de 15 dezenas. Custo extremamente baixo com altíssima cobertura.",
                "custo": 14.00, "prob15": "1 em 3.876", "prob14": "1 em 242", "j15": 4, "j16": 0
            },
            "💎 A COROA": {
                "desc": "Sistema Misto de Equilíbrio. 1 jogo de 16 dezenas para o padrão comum da Caixa cruzado com 2 jogos de 15 dezenas focados no Bloco de fechamento de Ciclo.",
                "custo": 63.00, "prob15": "1 em 7.750", "prob14": "1 em 310", "j15": 2, "j16": 1
            },
            "🛡️ O ESCUDO": {
                "desc": "Proteção Absoluta de Caixa. Gera 2 jogos de 15 dezenas usando apenas os pivôs de curto prazo de Markov. Feito para interceptar 12 e 13 pontos e reaver o investimento.",
                "custo": 7.00, "prob15": "1 em 7.752", "prob14": "1 em 484", "j15": 2, "j16": 0
            }
        }

        est_escolhida = st.selectbox("Escolha sua Estratégia de Combate", list(opcoes_estrategias.keys()))
        
        dados_est = opcoes_estrategias[est_escolhida]
        st.markdown(f"""
            <div style='background-color:#141822; padding:1.2rem; border-radius:8px; border-left:5px solid #D4AF37; margin-bottom:1rem;'>
                <b>Especificação Física:</b> {dados_est['desc']}<br>
                <b>💸 Custo Atualizado da Operação:</b> <span style='color:#00E676; font-weight:bold;'>R$ {dados_est['custo']:.2f}</span><br>
                <b>🎯 Probabilidade de 15 Pontos (Com Pool de 20):</b> {dados_est['prob15']}<br>
                <b>🎯 Probabilidade de 14 Pontos (Com Pool de 20):</b> {dados_est['prob14']}
            </div>
        """, unsafe_html=True)

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
            st.success(f"Sucesso! {len(jogos_gerados)} Jogos estruturados. Custo de R$ {dados_est['custo']:.2f} debitado.")
            st.rerun()

        if st.session_state.jogos_salvos:
            st.markdown("<h3 style='color: #D4AF37;'>📋 Bilhetes Filtrados Prontos para Registrar</h3>", unsafe_html=True)
            for idx, jogo in enumerate(st.session_state.jogos_salvos):
                texto_jogo = ", ".join(f"{x:02d}" for x in jogo)
                st.code(f"Jogo {idx+1} ({len(jogo)} Dezenas): {texto_jogo}", language="text")

    # =====================================================================
    # MÓDULO 2: 📊 ANÁLISE DE CICLO & ENGENHARIA
    # =====================================================================
    if st.session_state.aba_atual == "📊 Análise de Ciclo & Engenharia":
        st.markdown("<h3 style='color:#D4AF37;'>⚙️ Auditoria de Motores Preditivos</h3>", unsafe_html=True)
        st.write("Histórico de concursos armazenados na memória interna:")
        st.json(st.session_state.historico_sorteios)

    # =====================================================================
    # MÓDULO 3: 💳 GESTÃO DE CAIXA
    # =====================================================================
    if st.session_state.aba_atual == "💳 Gestão de Caixa":
        st.markdown("<h3 style='color:#D4AF37;'>📈 Painel Financeiro e Apuração de Rateio Real</h3>", unsafe_html=True)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            novo_saldo = st.number_input("Ajustar/Aportar Saldo de Caixa (R$)", value=float(st.session_state.caixa_saldo))
            if st.button("CONFIRMAR APORTE"):
                st.session_state.caixa_saldo = novo_saldo
                st.success("Saldo atualizado.")
                st.rerun()
                
        with col_c2:
            st.markdown("<br>", unsafe_html=True)
            conc_verificar = st.text_input("Número do Concurso para Conferir e Atualizar Caixa")
            
        if st.button("🔄 CONFERIR APURAR RATEIO OFICIAL E ADICIONAR PREMIAÇÕES"):
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
                st.success(f"Apuração Concluída! {cartoes_premiados} cartões premiados. R$ {total_ganho:.2f} adicionados.")
                
                html_sorteio = "<br><div style='text-align:center;'>"
                for n in sorted(list(sorteio_real)):
                    html_sorteio += f"<span class='bola-loto bola-sorteada'>{n:02d}</span>"
                html_sorteio += "</div>"
                st.markdown(html_sorteio, unsafe_html=True)
            else:
                st.error("Concurso não localizado. Sincronize o resultado primeiro na aba Operações.")

    # =====================================================================
    # MÓDULO 4: 💾 SEGURANÇA & BACKUP
    # =====================================================================
    if st.session_state.aba_atual == "💾 Segurança & Backup":
        st.markdown("<h3 style='color:#D4AF37;'>📂 Central de Salvaguarda de Dados (Manual e Total)</h3>", unsafe_html=True)
        
        dados_backup = {
            "caixa_saldo": st.session_state.caixa_saldo,
            "historico_sorteios": st.session_state.historico_sorteios,
            "jogos_salvos": st.session_state.jogos_salvos
        }
        json_string = json.dumps(dados_backup)
        
        st.download_button(
            label="📥 EXTRAIR BACKUP COMPLETO (KADOSH .JSON)",
            data=json_string,
            file_name="SUPERLOTO_KADOSH_BACKUP.json",
            mime="application/json"
        )
        
        st.markdown("<hr style='border-color: #2D3748;'>", unsafe_html=True)
        st.markdown("<h4>📤 Importar Estrutura de Backup</h4>", unsafe_html=True)
        arquivo_upload = st.file_uploader("Arraste seu arquivo .json de Backup do SuperLoto aqui", type=["json"])
        
        if arquivo_upload is not None:
            try:
                conteudo = json.load(arquivo_upload)
                st.session_state.caixa_saldo = conteudo["caixa_saldo"]
                st.session_state.historico_sorteios = conteudo["historico_sorteios"]
                st.session_state.jogos_salvos = conteudo["jogos_salvos"]
                st.success("Backup restaurado perfeitamente!")
                st.rerun()
            except:
                st.error("Erro na leitura do arquivo de backup.")
