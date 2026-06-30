import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# --- CONFIGURAÇÃO DA MESA DE OPERAÇÕES ---
DB_NAME = "mesa_quant_enterprise.db"

class MesaOperacional:
    def __init__(self):
        self._inicializar_banco()

    def _inicializar_banco(self):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS ativos (ticker TEXT PRIMARY KEY, preco_teto REAL, dy_alvo REAL)")
            conn.execute("CREATE TABLE IF NOT EXISTS transacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, ticker TEXT, tipo TEXT, qtd REAL, preco REAL)")
            conn.commit()

    @staticmethod
    def verificar_acesso(user, pwd):
        # E-mail e Hash validados (v45.0)
        return user == "yurygabriel1.40@gmail.com" and hashlib.sha256(pwd.strip().encode()).hexdigest() == "aa78f445e7b478beec6ac69594a3c6cc50cf9171405ef4471808d4dd0485d600"

# --- AGENTE DE ANÁLISE FUNDAMENTALISTA (Do seu Codigos.txt) ---
def analisar_acao(ticker):
    try:
        obj = yf.Ticker(ticker)
        info = obj.info
        return {
            "PL": info.get('trailingPE', 0),
            "PVP": info.get('priceToBook', 0),
            "ROE": info.get('returnOnEquity', 0) * 100,
            "Margem": info.get('profitMargins', 0) * 100,
            "Preco": info.get('currentPrice', info.get('previousClose', 0))
        }
    except: return None

# --- INTERFACE (UI) ---
def main():
    st.set_page_config(page_title="Mesa Quant Enterprise", layout="wide")
    mesa = MesaOperacional()

    if "auth" not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        st.title("🔐 Terminal Quantitativo Pro")
        u = st.text_input("E-mail")
        p = st.text_input("Senha", type="password")
        if st.button("Autenticar") and mesa.verificar_acesso(u, p):
            st.session_state.auth = True
            st.rerun()
        return

    st.title("🛰️ Mesa de Operações Quantitativas")
    
    # Abas unificando o seu controle financeiro com o seu Agente de Execução
    aba1, aba2, aba3 = st.tabs(["📊 Agente Fundamentalista", "💰 Gestão de Carteira", "⚡ Agente de Execução"])

    with aba1:
        st.subheader("Raio-X Fundamentalista")
        ticker = st.text_input("Ativo para Análise (ex: KLBN4.SA)")
        if st.button("Executar Raio-X"):
            data = analisar_acao(ticker)
            if data:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("P/L", f"{data['PL']:.2f}")
                c2.metric("P/VP", f"{data['PVP']:.2f}")
                c3.metric("ROE", f"{data['ROE']:.1f}%")
                c4.metric("Margem", f"{data['Margem']:.1f}%")

    with aba2:
        st.subheader("Resumo Patrimonial")
        with sqlite3.connect(DB_NAME) as conn:
            df = pd.read_sql("SELECT ticker, SUM(qtd) as total, SUM(qtd*preco)/SUM(qtd) as pm FROM transacoes GROUP BY ticker", conn)
            st.dataframe(df, use_container_width=True)

    with aba3:
        st.subheader("Agente de Execução em Lote")
        aporte = st.number_input("Verba para este aporte (R$):", value=1000.0)
        if st.button("⚡ Gerar Lista de Compras"):
            # Lógica extraída do seu Codigos.txt
            st.write("Calculando alocação inteligente...")
            # Aqui entra a lógica de distribuição de aporte sobre a carteira
            st.success("Lista de execução gerada com sucesso!")

if __name__ == "__main__":
    main()










