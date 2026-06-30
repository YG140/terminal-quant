
import streamlit as st
import hashlib

def verificar_credenciais(usuario, senha):
    # O hash que o seu celular gerou:
    hash_correto = "aa78f445e7b478beec6ac69594a3c6cc50cf9171405ef4471808d4dd0485d600"
    
    # Processa a senha
    senha_limpa = senha.strip()
    hash_digitado = hashlib.sha256(senha_limpa.encode('utf-8')).hexdigest()
    
    # Verifica usuário e hash
    return usuario.strip() == "yurygabriel1.40@gmail.com" and hash_digitado == hash_correto

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

    # Área Protegida
    st.title("🛰️ Terminal Quantitativo Pro v45.0")
    st.success("Acesso concedido com sucesso!")

if __name__ == "__main__":
    main()






