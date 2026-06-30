import streamlit as st
import sqlite3
import hashlib
import os
import shutil
import smtplib
from datetime import datetime
from email.message import EmailMessage

# Configurações
DB_NAME = "carteira_quant.db"

# --- SEGURANÇA COM HASH (SHA256) ---
def verificar_credenciais(usuario, senha):
    # Hash da senha "Bahia2026"
    hash_correto = "9200fa4644026da68997ef05dc6b5fe73229239a5ca2d699e69777f97b6ec340"
    hash_digitado = hashlib.sha256(senha.strip().encode()).hexdigest()
    return usuario.strip() == "yurygabriel1.40@gmail.com" and hash_digitado == hash_correto

def realizar_backup_banco():
    if os.path.exists(DB_NAME):
        if not os.path.exists("backup_financas"): os.makedirs("backup_financas")
        shutil.copy2(DB_NAME, f"backup_financas/backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db")

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

    # --- ÁREA LOGADA (SEU TERMINAL) ---
    st.title("🛰️ Terminal Quantitativo Pro v45.0")
    st.success("Acesso concedido com segurança HASH ativa!")
    
    # Aqui você pode adicionar as tabelas e gráficos do seu sistema
    st.write("Bem-vindo ao seu ambiente de trabalho.")

if __name__ == "__main__":
    main()




