import streamlit as st
import itertools
import random
import json
from datetime import datetime
from collections import Counter
from fpdf import FPDF

st.set_page_config(page_title="LotoPro — IA e Fechamentos", page_icon="🤖", layout="wide")

# --- DADOS: 50 ÚLTIMOS SORTEIOS ---
# Cole aqui a lista completa dos 50 sorteios (excluindo o 3693)
HISTORICO_50 = [
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], # Exemplo 1
    # ... adicione os outros 49 aqui ...
]

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.title("🔒 Acesso Restrito - LotoPro")
    senha = st.text_input("Senha de Acesso:", type="password")
    if st.button("Entrar", type="primary"):
        if senha == "7777":
            st.session_state.autenticado = True
            st.rerun()
    st.stop()
def obter_dezenas_inteligentes():
    frequencia = Counter([num for sorteio in HISTORICO_50 for num in sorteio])
    return [numero for numero, contagem in frequencia.most_common(18)]

def validar_jogo(jogo):
    soma = sum(jogo)
    impares = len([x for x in jogo if x % 2 != 0])
    return 180 <= soma <= 220 and 6 <= impares <= 9

def gerar_pdf(bilhetes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Recibo Oficial LotoPro", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    for i, b in enumerate(bilhetes):
        pdf.cell(200, 10, f"Jogo {i+1}: {sorted(b['dezenas'])}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

if 'banca_saldo' not in st.session_state: st.session_state.banca_saldo = 200.0
if 'lote_ativo' not in st.session_state: st.session_state.lote_ativo = None 
st.title("🤖 LotoPro — Piloto Automático")
menu = st.sidebar.radio("Navegação", ["1. Gerador", "2. Recibo", "3. Conferência"])

if menu == "1. Gerador":
    dezenas_elite = obter_dezenas_inteligentes()
    st.info(f"📊 Dezenas Elite (Top 18): {sorted(dezenas_elite)}")
    
    if st.button("Executar Robô"):
        candidatos = list(itertools.combinations(dezenas_elite, 15))
        jogos = [list(j) for j in random.sample(candidatos, 5) if validar_jogo(j)]
        st.session_state.lote_ativo = {"bilhetes": [{"dezenas": j, "tipo": 15} for j in jogos]}
        st.success("Jogos gerados!")
        pdf_data = gerar_pdf(st.session_state.lote_ativo["bilhetes"])
        st.download_button("📥 Descarregar PDF", pdf_data, "Meus_Jogos.pdf", "application/pdf")

elif menu == "2. Recibo":
    if st.session_state.lote_ativo:
        for i, b in enumerate(st.session_state.lote_ativo["bilhetes"]):
            st.write(f"Bilhete {i+1}: {sorted(b['dezenas'])}")

elif menu == "3. Conferência":
    st.write("Conferência manual do Concurso 3693 (Sincronize pessoalmente).")
