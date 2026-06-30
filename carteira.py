import streamlit as st
import sqlite3
import hashlib
import os
import shutil
import pandas as pd
from datetime import datetime

# Configurações do Banco
DB_NAME = "carteira_quant.db"

# --- SEGURANÇA COM HASH (SHA256) ---
def verificar_credenciais(usuario, senha):
    # Hash validado para "Bahia2026"
    hash_correto = "aa78f445e7b478beec6ac69594a3c6cc50cf9171405ef4471808d4dd0485d600"
    senha_limpa = senha.strip()
    hash_digitado = hashlib.sha256(senha_limpa.encode('utf-8')).hexdigest()
    return usuario.strip() == "yurygabriel1.40@gmail.com" and hash_digitado == hash_correto

def realizar_backup_banco():
    if os.path.exists(DB_NAME):
        if not os.path.exists("backup_financas"):
            os.makedirs("backup_financas")
        shutil.copy2(DB_NAME, f"backup_financas/backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db")

# --- MÓDULO DE BANCO DE DADOS ---
def inicializar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS tb_ativos_v39 (ticker TEXT PRIMARY KEY, preco_teto_compra REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tb_transacoes_v39 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, ticker TEXT, tipo TEXT, quantidade REAL, preco REAL)")
    conn.commit()
    conn.close()

def processar_arquivo_bancario(uploaded_file, ticker_manual):
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
        
        # Injeta o ticker manual se não existir
        df['ticker'] = ticker_manual.upper()
        
        # Verifica colunas necessárias
        colunas_obrigatorias = ['data', 'ticker', 'tipo', 'quantidade', 'preco']
        for col in colunas_obrigatorias:
            if col not in df.columns:
                st.error(f"Erro: O arquivo não contém a coluna obrigatória: {col}")
                return

        conn = sqlite3.connect(DB_NAME)
        df.to_sql('tb_transacoes_v39', conn, if_exists='append', index=False)
        conn.close()
        st.success("✅ Extrato processado e salvo com sucesso!")
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")

# --- INTERFACE PRINCIPAL ---
def main():
    st.set_page_config(page_title="Mesa Quant v45.0", layout="wide")
    
    if "autenticado" not in st.session_state: 
        st.session_state["autenticado"] = False
        
    if not st.session_state["autenticado"]:
        st.title("🔐 Terminal Quantitativo v45.0")
        user = st.text_input("E-mail")
        pwd = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if verificar_credenciais(user, pwd):
                st.session_state["autenticado"] = True
                realizar_backup_banco()
                st.rerun()
            else:
                st.error("Credenciais inválidas.")
        return

    # Painel Principal após Login
    inicializar_banco()
    st.title("🛰️ Terminal Quantitativo Pro v45.0")
    
    with st.expander("📥 Importar Extrato Bancário"):
        arquivo = st.file_uploader("Suba o CSV do seu banco:", type=["csv"])
        ticker_input = st.text_input("Digite o ticker das operações (ex: PETR4):")
        
        if st.button("Processar Extrato"):
            if arquivo and ticker_input:
                processar_arquivo_bancario(arquivo, ticker_input)
            else:
                st.warning("Por favor, selecione o arquivo e digite o ticker.")

if __name__ == "__main__":
    main()








