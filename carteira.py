
import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import hashlib
import os
import shutil
import smtplib
from datetime import datetime
from email.message import EmailMessage

# Configurações
DB_NAME = "carteira_quant.db"

# --- MÓDULO DE SEGURANÇA (Hash Validado) ---
def verificar_credenciais(usuario, senha):
    # Hash oficial validado pelo seu dispositivo
    hash_correto = "aa78f445e7b478beec6ac69594a3c6cc50cf9171405ef4471808d4dd0485d600"
    hash_digitado = hashlib.sha256(senha.strip().encode('utf-8')).hexdigest()
    return usuario.strip() == "yurygabriel1.40@gmail.com" and hash_digitado == hash_correto

def realizar_backup_banco():
    if os.path.exists(DB_NAME):
        if not os.path.exists("backup_financas"):
            os.makedirs("backup_financas")
        shutil.copy2(DB_NAME, f"backup_financas/backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db")

def enviar_alerta_oportunidade(ticker, preco_atual):
    email_usuario = "yurygabriel1.40@gmail.com"
    senha_app = "dzdcamwbmrejscal" 
    msg = EmailMessage()
    msg['Subject'] = f"🚨 OPORTUNIDADE: {ticker} em Ponto de Compra!"
    msg['From'] = email_usuario
    msg['To'] = email_usuario
    msg.set_content(f"O ativo {ticker} está R$ {preco_atual:.2f}. Dentro do preço teto.")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_usuario, senha_app)
            smtp.send_message(msg)
    except Exception: 
        pass

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
        df = pd.read_csv(uploaded_file)
        conn = sqlite3.connect(DB_NAME)
        df.to_sql('tb_transacoes_v39', conn, if_exists='append', index=False)
        conn.close()
        st.success("✅ Extrato processado e salvo no banco!")

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
        if st.button("Processar Extrato"): 
            processar_arquivo_bancario(arquivo)

if __name__ == "__main__":
    main()






