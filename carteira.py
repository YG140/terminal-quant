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

# --- MÓDULOS DE SEGURANÇA E BACKUP ---
def verificar_credenciais(usuario, senha):
    return usuario == "yurygabriel1.40@gmail.com" and hashlib.sha256(senha.encode()).hexdigest() == "9200fa4644026da68997ef05dc6b5fe73229239a5ca2d699e69777f97b6ec340"

def realizar_backup_banco():
    if not os.path.exists("backup_financas"): os.makedirs("backup_financas")
    shutil.copy2(DB_NAME, f"backup_financas/backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db")

def enviar_alerta_oportunidade(ticker, preco_atual):
    # Lembre-se: Use uma Senha de App do Google aqui
    email_usuario = "yurygabriel1.40@gmail.com"
    senha_app = "SUA_SENHA_DE_APP_AQUI" 
    msg = EmailMessage()
    msg['Subject'] = f"🚨 OPORTUNIDADE: {ticker} em Ponto de Compra!"
    msg['From'] = email_usuario
    msg['To'] = email_usuario
    msg.set_content(f"O ativo {ticker} está R$ {preco_atual:.2f}. Dentro do preço teto.")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_usuario, senha_app)
            smtp.send_message(msg)
    except: pass

# --- MÓDULO DE IMPORTAÇÃO E BANCO ---
def inicializar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS tb_ativos_v39 (ticker TEXT PRIMARY KEY, preco_teto_compra REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tb_transacoes_v39 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, ticker TEXT, tipo TEXT, quantidade REAL, preco REAL)")
    conn.commit()
    conn.close()

def processar_arquivo_bancario(uploaded_file):
    df = pd.read_csv(uploaded_file)
    conn = sqlite3.connect(DB_NAME)
    df.to_sql('tb_transacoes_v39', conn, if_exists='append', index=False)
    conn.close()
    st.success("✅ Extrato processado!")

# --- INTERFACE PRINCIPAL ---
def main():
    st.set_page_config(page_title="Mesa Quant v45.0", layout="wide")
    
    if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
        
    if not st.session_state["autenticado"]:
        st.title("🔐 Terminal Quantitativo v45.0")
        user = st.text_input("E-mail")
        pwd = st.text_input("Senha", type="password")
        if st.button("Entrar") and verificar_credenciais(user, pwd):
            st.session_state["autenticado"] = True
            realizar_backup_banco()
            st.rerun()
        return

    inicializar_banco()
    st.title("🛰️ Terminal Quantitativo Pro v45.0")
    
    with st.expander("📥 Importar Extrato Bancário"):
        arquivo = st.file_uploader("Suba o CSV do seu banco:", type=["csv"])
        if st.button("Processar Extrato"): processar_arquivo_bancario(arquivo)

if __name__ == "__main__":
    main()
