import streamlit as st
import sqlite3
import os
import shutil
import smtplib
from datetime import datetime
from email.message import EmailMessage

# Configurações
DB_NAME = "carteira_quant.db"

# --- MÓDULO DE SEGURANÇA CORRIGIDO ---
def verificar_credenciais(usuario, senha):
    # Verificação direta para garantir o seu acesso agora
    return usuario.strip() == "yurygabriel1.40@gmail.com" and senha.strip() == "Bahia2026"

def realizar_backup_banco():
    if os.path.exists(DB_NAME):
        if not os.path.exists("backup_financas"):
            os.makedirs("backup_financas")
        shutil.copy2(DB_NAME, f"backup_financas/backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db")

def enviar_alerta_oportunidade(ticker, preco_atual):
    email_usuario = "yurygabriel1.40@gmail.com"
    senha_app = "dzdcamwbmrejscal" 
    msg = EmailMessage()
    msg['Subject'] = f"🚨 OPORTUNIDADE: {ticker}"
    msg['From'] = email_usuario
    msg['To'] = email_usuario
    msg.set_content(f"O ativo {ticker} está R$ {preco_atual:.2f}.")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_usuario, senha_app)
            smtp.send_message(msg)
    except: pass

# --- INTERFACE PRINCIPAL ---
def main():
    st.set_page_config(page_title="Mesa Quant v45.0", layout="wide")
    
    if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
        
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

    st.title("🛰️ Terminal Quantitativo Pro v45.0")
    st.success("Acesso concedido!")

if __name__ == "__main__":
    main()



