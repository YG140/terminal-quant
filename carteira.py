import streamlit as st
import sqlite3
import hashlib
import os
import shutil
import pandas as pd
from datetime import datetime

# Configurações
DB_NAME = "carteira_quant.db"

# --- SEGURANÇA (Hash Validado) ---
def verificar_credenciais(usuario, senha):
    hash_correto = "aa78f445e7b478beec6ac69594a3c6cc50cf9171405ef4471808d4dd0485d600"
    hash_digitado = hashlib.sha256(senha.strip().encode('utf-8')).hexdigest()
    return usuario.strip() == "yurygabriel1.40@gmail.com" and hash_digitado == hash_correto

# --- MÓDULO DE BANCO DE DADOS ---
def inicializar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS tb_ativos (ticker TEXT PRIMARY KEY, preco_teto REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tb_transacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, ticker TEXT, tipo TEXT, quantidade REAL, preco REAL)")
    conn.commit()
    conn.close()

def processar_arquivo_bancario(uploaded_file, ticker):
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
        df['ticker'] = ticker.upper()
        
        conn = sqlite3.connect(DB_NAME)
        df.to_sql('tb_transacoes', conn, if_exists='append', index=False)
        conn.close()
        st.success(f"✅ Transações de {ticker.upper()} importadas!")
    except Exception as e:
        st.error(f"Erro ao importar: {e}")

# --- INTERFACE ---
def main():
    st.set_page_config(page_title="Mesa Quant v45.0", layout="wide")
    
    if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
    
    if not st.session_state["autenticado"]:
        st.title("🔐 Terminal Quantitativo v45.0")
        user = st.text_input("E-mail")
        pwd = st.text_input("Senha", type="password")
        if st.button("Entrar") and verificar_credenciais(user, pwd):
            st.session_state["autenticado"] = True
            st.rerun()
        return

    inicializar_banco()
    st.title("🛰️ Terminal Quantitativo Pro")

    # Aba de Importação
    with st.expander("📥 Importar Transações de Ações"):
        arquivo = st.file_uploader("CSV de corretora", type=["csv"])
        ticker_input = st.text_input("Ticker do ativo:")
        if st.button("Processar") and arquivo and ticker_input:
            processar_arquivo_bancario(arquivo, ticker_input)

    # Exibição da Carteira (Resumo)
    st.subheader("📊 Minha Carteira")
    conn = sqlite3.connect(DB_NAME)
    try:
        df_carteira = pd.read_sql("SELECT ticker, SUM(quantidade) as qtd, AVG(preco) as preco_medio FROM tb_transacoes GROUP BY ticker", conn)
        if not df_carteira.empty:
            st.dataframe(df_carteira, use_container_width=True)
        else:
            st.info("Nenhuma transação registrada.")
    except:
        st.warning("Banco de dados vazio.")
    conn.close()

if __name__ == "__main__":
    main()









