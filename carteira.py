import streamlit as st
import sqlite3
import hashlib
import os
import shutil

# Configurações do Banco
DB_NAME = "carteira_quant.db"

# --- SEGURANÇA COM HASH (SHA256) ---
def verificar_credenciais(usuario, senha):
    # O hash abaixo é o SHA256 estrito da senha "Bahia2026"
    hash_correto = "9200fa4644026da68997ef05dc6b5fe73229239a5ca2d699e69777f97b6ec340"
    # Limpeza de espaços em branco e conversão para bytes
    senha_limpa = senha.strip()
    hash_digitado = hashlib.sha256(senha_limpa.encode('utf-8')).hexdigest()
    # Comparação final
    return usuario.strip() == "yurygabriel1.40@gmail.com" and hash_digitado == hash_correto

# --- INTERFACE PRINCIPAL ---
def main():
    st.set_page_config(page_title="Mesa Quant v45.0", layout="wide")
    
    # Inicializa estado de autenticação
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
        
    # Tela de Login
    if not st.session_state["autenticado"]:
        st.title("🔐 Terminal Quantitativo v45.0")
        user = st.text_input("E-mail")
        pwd = st.text_input("Senha", type="password")
        
        if st.button("Entrar"):
            if verificar_credenciais(user, pwd):
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Credenciais inválidas.")
        return

    # Área Protegida (Após Login)
    st.title("🛰️ Terminal Quantitativo Pro v45.0")
    st.success("Acesso concedido com sucesso!")
    st.write("Bem-vindo ao painel de controle.")

if __name__ == "__main__":
    main()





