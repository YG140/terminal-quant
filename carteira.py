import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import sqlite3
import hashlib
import logging
import smtplib
from email.message import EmailMessage
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# --- CONFIGURAÇÃO ---
logging.basicConfig(level=logging.INFO)
DB_NAME = "mesa_quant_definitiva.db"

# ==============================================================================
# 1. NÚCLEO DE DADOS, SEGURANÇA E ALERTAS
# ==============================================================================
class NucleoOperacional:
    def __init__(self):
        self._inicializar_banco()

    def _inicializar_banco(self):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS ativos (ticker TEXT PRIMARY KEY, classe TEXT, quantidade REAL, preco_medio REAL, peso INTEGER)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS historico_patrimonio (mes_ano TEXT PRIMARY KEY, patrimonio REAL, proventos REAL)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS usuarios (email TEXT PRIMARY KEY, hash_senha TEXT)""")
            
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ativos")
            if cursor.fetchone()[0] == 0:
                conn.executemany("INSERT INTO ativos VALUES (?, ?, ?, ?, ?)", [
                    ("KLBN4.SA", "Ações", 100, 4.10, 3), ("BBAS3.SA", "Ações", 50, 26.50, 3),
                    ("MXRF11.SA", "FIIs", 200, 10.05, 4), ("RESERVA", "Segurança", 1, 5000.0, 0)
                ])
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            if cursor.fetchone()[0] == 0:
                conn.execute("INSERT INTO usuarios VALUES (?, ?)", ("yurygabriel1.40@gmail.com", "aa78f445e7b478beec6ac69594a3c6cc50cf9171405ef4471808d4dd0485d600"))
            conn.commit()

    @staticmethod
    def disparar_alerta_email(ticker, preco, motivo):
        EMAIL_ADDRESS = "seu_email@gmail.com" 
        EMAIL_PASSWORD = "sua_senha_de_app"
        msg = EmailMessage()
        msg['Subject'] = f"🚨 ALERTA QUANT: {ticker} Aprovado!"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg.set_content(f"O ativo {ticker} (R${preco:.2f}) passou nos filtros!\nMotivo: {motivo}")
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
        except Exception as e:
            st.error(f"Erro ao enviar alerta: {e}")

    @staticmethod
    def verificar_acesso(user, pwd):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hash_senha FROM usuarios WHERE email=?", (user.strip(),))
            row = cursor.fetchone()
            if row: return hashlib.sha256(pwd.strip().encode()).hexdigest() == row[0]
        return False

# ==============================================================================
# 2. MOTOR DE IA E FUNDAMENTOS
# ==============================================================================
class AnalisadorGlobal:
    @staticmethod
    @st.cache_data(ttl=3600)
    def prever_tendencia_e_fundamentos(ticker):
        resultado = {"tendencia": "Estável", "confianca": 0.0, "score": 0, "alertas": [], "preco": 0.0}
        try:
            obj = yf.Ticker(ticker)
            info = obj.info
            resultado['preco'] = info.get('currentPrice', info.get('previousClose', 0.0))
            
            # Fundamentos
            pl = info.get('trailingPE', 0)
            pvp = info.get('priceToBook', 0)
            roe = info.get('returnOnEquity', 0) * 100
            if 0 < pl < 15 and 0 < pvp < 1.6: resultado['score'] += 1
            if roe > 12: resultado['score'] += 1

            # Machine Learning
            hist = obj.history(period="1y")
            if len(hist) > 40:
                hist['Retorno'] = hist['Close'].pct_change()
                hist['Alvo'] = np.where(hist['Close'].shift(-1) > hist['Close'], 1, 0)
                hist = hist.dropna()
                X = hist[['Close', 'Retorno']]
                y = hist['Alvo']
                modelo = RandomForestClassifier(n_estimators=30, random_state=42).fit(X, y)
                prob = modelo.predict_proba(np.array([[hist['Close'].iloc[-1], hist['Retorno'].iloc[-1]]]))[0][1] * 100
                resultado['tendencia'] = "Alta" if prob > 55 else "Baixa"
                resultado['confianca'] = prob
        except: pass
        return resultado

# ==============================================================================
# 3. INTERFACE PRINCIPAL
# ==============================================================================
def main():
    st.set_page_config(page_title="Mesa Quant Master", layout="wide")
    nucleo = NucleoOperacional()
    
    if "auth" not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        st.title("🔐 Acesso Restrito")
        with st.form("form_login"):
            u = st.text_input("E-mail")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                if nucleo.verificar_acesso(u, p): st.session_state.auth = True; st.rerun()
        return

    st.title("🛰️ Terminal Quantitativo Master")
    t1, t2, t3, t4 = st.tabs(["📊 Custódia", "🔬 Scanner", "⚡ Agente de Execução", "🎯 Simulador"])

    with t1:
        with sqlite3.connect(DB_NAME) as conn:
            df = pd.read_sql("SELECT * FROM ativos", conn)
        st.dataframe(df, use_container_width=True)
        with st.form("add"):
            c1, c2, c3 = st.columns(3)
            t = c1.text_input("Ticker").upper()
            q = c2.number_input("Qtd", step=1.0)
            p = c3.number_input("Preço Médio", step=0.1)
            if st.form_submit_button("Salvar"):
                with sqlite3.connect(DB_NAME) as conn:
                    conn.execute("INSERT OR REPLACE INTO ativos VALUES (?, ?, ?, ?, 1)", (t, "Ação", q, p))
                st.rerun()

    with t2:
        ticker = st.text_input("Auditar Ticker:")
        if st.button("Analisar"):
            res = AnalisadorGlobal.prever_tendencia_e_fundamentos(ticker)
            st.write(res)

    with t3:
        if st.button("Rodar Scanner e Enviar Alertas"):
            with sqlite3.connect(DB_NAME) as conn:
                ativos = pd.read_sql("SELECT ticker FROM ativos", conn)
            for _, row in ativos.iterrows():
                res = AnalisadorGlobal.prever_tendencia_e_fundamentos(row['ticker'])
                if res['tendencia'] == "Alta":
                    nucleo.disparar_alerta_email(row['ticker'], res['preco'], "Ativo em tendência de alta pela IA")
                    st.success(f"✅ {row['ticker']} aprovado e e-mail enviado!")

    with t4:
        st.subheader("🎯 Planejador de Renda Passiva")
        meta_mensal = st.number_input("Quanto deseja receber de dividendos por mês? (R$):", min_value=100.0, value=2000.0, step=100.0)
        yield_estimado = st.slider("Yield Mensal Estimado (%)", 0.5, 1.5, 0.8) / 100
        
        if st.button("Calcular Gap de Aporte"):
            with sqlite3.connect(DB_NAME) as conn:
                df_ativos = pd.read_sql("SELECT * FROM ativos WHERE ticker != 'RESERVA'", conn)
            
            plano_de_acao = []
            for _, row in df_ativos.iterrows():
                ticker = row['ticker']
                res = AnalisadorGlobal.prever_tendencia_e_fundamentos(ticker)
                if res['preco'] > 0:
                    qtd_alvo = int((meta_mensal / len(df_ativos)) / (res['preco'] * yield_estimado))
                    gap = max(0, qtd_alvo - row['quantidade'])
                    plano_de_acao.append({
                        "Ativo": ticker,
                        "Qtd Atual": row['quantidade'],
                        "Qtd Alvo": qtd_alvo,
                        "Gap (Falta Comprar)": gap,
                        "Custo p/ Bater Meta (R$)": round(gap * res['preco'], 2)
                    })
            
            df_plano = pd.DataFrame(plano_de_acao)
            st.table(df_plano)
            csv = df_plano.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Plano de Ação (CSV)", csv, 'plano_aporte_meta.csv', 'text/csv')

if __name__ == "__main__":
    main()












