import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import hashlib
import os
import shutil
from datetime import datetime

# Configurações
DB_NAME = "terminal_acoes.db"

# --- SEGURANÇA E BACKUP ---
def verificar_credenciais(usuario, senha):
    hash_correto = "aa78f445e7b478beec6ac69594a3c6cc50cf9171405ef4471808d4dd0485d600"
    hash_digitado = hashlib.sha256(senha.strip().encode('utf-8')).hexdigest()
    return usuario.strip() == "yurygabriel1.40@gmail.com" and hash_digitado == hash_correto

def realizar_backup():
    if not os.path.exists("backups"): os.makedirs("backups")
    if os.path.exists(DB_NAME):
        shutil.copy2(DB_NAME, f"backups/backup_{datetime.now().strftime('%Y%m%d')}.db")

# --- LÓGICA QUANTITATIVA ---
def analisar_risco(ticker):
    try:
        dados = yf.Ticker(ticker).history(period="1mo")
        vol = dados['Close'].pct_change().std() * 100
        return "🔥 ALTO RISCO" if vol > 3.5 else "✅ ESTÁVEL"
    except: return "⚠️ Indisponível"

# --- BANCO DE DADOS (AÇÕES) ---
def inicializar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tabela exclusiva para ações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carteira (
            ticker TEXT PRIMARY KEY,
            preco_teto REAL,
            quantidade REAL,
            preco_medio REAL
        )
    """)
    conn.commit()
    conn.close()

# --- INTERFACE ---
def main():
    st.set_page_config(page_title="Mesa Quant Pro", layout="wide")
    
    if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
    
    if not st.session_state["autenticado"]:
        st.title("🔐 Login Mesa Quant")
        user = st.text_input("E-mail")
        pwd = st.text_input("Senha", type="password")
        if st.button("Entrar") and verificar_credenciais(user, pwd):
            st.session_state["autenticado"] = True
            realizar_backup()
            st.rerun()
        return

    inicializar_banco()
    st.title("🛰️ Terminal Quantitativo Pro - Ações")

    # Colunas de Gestão
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Adicionar Ativo")
        ticker = st.text_input("Ticker (ex: PETR4)").upper()
        teto = st.number_input("Preço Teto de Compra")
        qtd = st.number_input("Quantidade")
        if st.button("Salvar na Carteira"):
            # Lógica de inserção no SQL
            st.success(f"Ativo {ticker} registrado!")

    with col2:
        st.subheader("Análise de Risco")
        ativo_sel = st.selectbox("Selecione o Ativo:", ["KLBN4", "MXRF11", "BBAS3", "PETR4"])
        st.metric("Status Atual", analisar_risco(ativo_sel))

if __name__ == "__main__":
    main()









