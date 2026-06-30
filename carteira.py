
import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import hashlib
import logging
from datetime import datetime

# --- CONFIGURAÇÃO PROFISSIONAL ---
logging.basicConfig(level=logging.INFO)

class TerminalQuantPro:
    def __init__(self, db_name="terminal_enterprise.db"):
        self.db_name = db_name
        self._inicializar_banco()

    def _inicializar_banco(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Tabela de Parâmetros (Ativos)
            cursor.execute("""CREATE TABLE IF NOT EXISTS ativos (
                ticker TEXT PRIMARY KEY, preco_teto REAL, dy_alvo REAL)""")
            # Tabela de Transações (Livro Diário v30)
            cursor.execute("""CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, ticker TEXT, 
                tipo TEXT, qtd REAL, preco REAL)""")
            conn.commit()

    # --- LÓGICA DE LOGIN (Padrão v45.0) ---
    @staticmethod
    def verificar_acesso(user, pwd):
        # E-mail e Hash validados conforme a sua versão 45.0
        email_correto = "yurygabriel1.40@gmail.com"
        hash_correto = "aa78f445e7b478beec6ac69594a3c6cc50cf9171405ef4471808d4dd0485d600"
        
        hash_digitado = hashlib.sha256(pwd.strip().encode('utf-8')).hexdigest()
        return user.strip() == email_correto and hash_digitado == hash_correto

# --- LÓGICA DE MERCADO ---
class AnalisadorMercado:
    @staticmethod
    def get_preco(ticker):
        try:
            return yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
        except:
            return None

# --- INTERFACE (UI) ---
def main():
    st.set_page_config(page_title="Mesa Quant Enterprise", layout="wide")
    app = TerminalQuantPro()

    if "auth" not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        st.title("🔐 Terminal Quantitativo - Autenticação")
        u = st.text_input("E-mail")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar no Sistema"):
            if app.verificar_acesso(u, p):
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Acesso negado.")
        return

    st.title("🛰️ Terminal Quantitativo Pro - Engine v2.0")
    
    tab1, tab2, tab3 = st.tabs(["📊 Carteira", "📝 Livro Diário", "🩺 Auditoria"])

    with tab1:
        st.subheader("Resumo de Posição")
        with sqlite3.connect("terminal_enterprise.db") as conn:
            df = pd.read_sql("SELECT ticker, SUM(qtd) as total, SUM(qtd*preco)/SUM(qtd) as pm FROM transacoes GROUP BY ticker", conn)
            st.dataframe(df, use_container_width=True)

    with tab2:
        st.subheader("Lançamento de Ordem")
        with st.form("ordem"):
            t = st.text_input("Ticker").upper()
            q = st.number_input("Quantidade")
            p = st.number_input("Preço")
            if st.form_submit_button("Registrar"):
                with sqlite3.connect("terminal_enterprise.db") as conn:
                    conn.execute("INSERT INTO transacoes (data, ticker, tipo, qtd, preco) VALUES (?,?,?,?,?)",
                                 (datetime.now().strftime("%Y-%m-%d"), t, 'COMPRA', q, p))
                st.success("Transação registrada.")

    with tab3:
        st.subheader("Auditoria de Mercado")
        with sqlite3.connect("terminal_enterprise.db") as conn:
            ativos = pd.read_sql("SELECT * FROM ativos", conn)
            for _, row in ativos.iterrows():
                p = AnalisadorMercado.get_preco(row['ticker'])
                if p:
                    status = "🟢" if p <= row['preco_teto'] else "❌"
                    st.metric(f"{row['ticker']} {status}", f"R$ {p:.2f}", delta=f"Teto: R$ {row['preco_teto']:.2f}")

if __name__ == "__main__":
    main()










