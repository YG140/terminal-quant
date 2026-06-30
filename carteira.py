import streamlit as st
import hashlib

def verificar_credenciais(usuario, senha):
    # Hash correto esperado para "Bahia2026"
    hash_alvo = "9200fa4644026da68997ef05dc6b5fe73229239a5ca2d699e69777f97b6ec340"
    
    # Processa a senha
    senha_limpa = senha.strip()
    hash_digitado = hashlib.sha256(senha_limpa.encode('utf-8')).hexdigest()
    
    # Diagnóstico: Se não bater, mostra o hash na tela
    if hash_digitado != hash_alvo:
        st.error(f"Erro de Hash! O que o sistema calculou foi: {hash_digitado}")
        return False
        
    # Verifica usuário
    return usuario.strip() == "yurygabriel1.40@gmail.com"

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
                st.rerun()
            else:
                st.error("Credenciais inválidas.")
        return

    st.title("🛰️ Terminal Quantitativo Pro v45.0")
    st.success("Acesso concedido com sucesso!")

if __name__ == "__main__":
    main()






