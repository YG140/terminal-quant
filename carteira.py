import streamlit as st
import sqlite3
import hashlib
import os
import shutil
import pandas as pd
from datetime import datetime

# Configurações
DB_NAME = "carteira_quant.db"

# --- MÓDULO DE SEGURANÇA ---
def verificar_credenciais(usuario, senha):
    # Hash validado para "Bahia2026"
    hash_correto = "aa78f445e7b478beec6ac69594a3c6cc50cf9171405ef4471808d4dd0485d600"
    hash_digitado = hashlib.sha256(senha.strip().encode('utf-8')).hexdigest()
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

def processar_arquivo_bancario(uploaded_file):
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            # Limpeza de colunas para garantir compatibilidade
            df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
            
            # Verificação de colunas mínimas necessárias
            colunas_necessarias = ['data', 'ticker', 'tipo', 'quantidade', 'preco']
            for col in colunas_necessarias:
                if col not in df.columns:
                    st.error(f"Erro: O arquivo CSV não contém a coluna obrigatória: {col}")
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

    # Painel Principal
    inicializar_banco()
    st.title("🛰️ Terminal Quantitativo Pro v45.0")
    
    with st.expander("📥 Importar Extrato Bancário"):
        arquivo = st.file_uploader("Suba o CSV do seu banco:", type=["csv"])
        if st.button("Processar Extrato"): 
            processar_arquivo_bancario(arquivo)

if __name__ == "__main__":
    main()







