
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import sqlite3
import hashlib
import logging
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# --- CONFIGURAÇÃO E LOGS ---
logging.basicConfig(level=logging.INFO)
DB_NAME = "mesa_quant_master.db"

# ==============================================================================
# 1. NÚCLEO DE DADOS E SEGURANÇA
# ==============================================================================
class NucleoOperacional:
    def __init__(self):
        self._inicializar_banco()

    def _inicializar_banco(self):
        with sqlite3.connect(DB_NAME) as conn:
            # Fundindo Tabela de Ativos com Gestão de Peso e Classe
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ativos (
                    ticker TEXT PRIMARY KEY, classe TEXT, 
                    quantidade REAL, preco_medio REAL, peso INTEGER
                )
            """)
            conn.commit()

    @staticmethod
    def verificar_acesso(user, pwd):
        email_correto = "yurygabriel1.40@gmail.com"
        hash_correto = "aa78f445e7b478beec6ac69594a3c6cc50cf9171405ef4471808d4dd0485d600"
        return user.strip() == email_correto and hashlib.sha256(pwd.strip().encode()).hexdigest() == hash_correto

# ==============================================================================
# 2. MOTOR DE INTELIGÊNCIA ARTIFICIAL (Machine Learning)
# ==============================================================================
class MotorIA:
    @staticmethod
    def prever_tendencia(ticker):
        try:
            historico = yf.Ticker(ticker).history(period="1y")
            if len(historico) < 40: return "Dados Insuficientes", 0.0

            # Engenharia de Recursos (do seu código original)
            historico['Retorno'] = historico['Close'].pct_change()
            historico['Media_5d'] = historico['Close'].rolling(window=5).mean()
            historico['Media_20d'] = historico['Close'].rolling(window=20).mean()
            historico['Volatilidade'] = historico['Retorno'].rolling(window=10).std()
            historico['Alvo'] = np.where(historico['Close'].shift(-1) > historico['Close'], 1, 0)
            historico = historico.dropna()

            X = historico[['Close', 'Media_5d', 'Media_20d', 'Volatilidade']]
            y = historico['Alvo']

            # Treinamento do Modelo
            modelo = RandomForestClassifier(n_estimators=30, random_state=42)
            modelo.fit(X, y)

            ultimo_reg = np.array([X.iloc[-1]])
            previsao = modelo.predict(ultimo_reg)
            prob = modelo.predict_proba(ultimo_reg)[0][1] * 100

            tendencia = "Alta" if previsao[0] == 1 and prob > 55 else "Baixa"
            return tendencia, prob
        except Exception as e:
            logging.error(f"Erro IA em {ticker}: {e}")
            return "Erro", 0.0

# ==============================================================================
# 3. ANALISTA FUNDAMENTALISTA (Raio-X)
# ==============================================================================
class AnalistaFundamentalista:
    @staticmethod
    def avaliar_acao(ticker):
        try:
            info = yf.Ticker(ticker).info
            pl = info.get('trailingPE', 0)
            pvp = info.get('priceToBook', 0)
            liq_corr = info.get('currentRatio', 0)
            roe = info.get('returnOnEquity', 0) * 100
            
            pontos = 0
            alertas = []
            
            if 0 < pl < 15 and 0 < pvp < 1.6: pontos += 1
            else: alertas.append("Valuation Esticado")
            
            if liq_corr >= 1.2: pontos += 1
            else: alertas.append("Baixa Liquidez Corrente")
            
            if roe > 12: pontos += 1
            else: alertas.append("ROE abaixo de 12%")

            return {"pontos": pontos, "max": 3, "alertas": alertas, "preco": info.get('currentPrice', 0)}
        except:
            return None

# ==============================================================================
# 4. INTERFACE GRÁFICA (Streamlit)
# ==============================================================================
def main():
    st.set_page_config(page_title="Mesa Quant Master", layout="wide")
    nucleo = NucleoOperacional()

    if "auth" not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        st.title("🔐 Autenticação - Nível Institucional")
        u = st.text_input("E-mail corporativo")
        p = st.text_input("Chave de segurança", type="password")
        if st.button("Autenticar") and nucleo.verificar_acesso(u, p):
            st.session_state.auth = True
            st.rerun()
        return

    st.title("🛰️ Terminal Quantitativo Master")
    
    aba_carteira, aba_raiox, aba_agente = st.tabs(["📊 Gestão de Portfólio", "🔬 Raio-X Fundamentalista", "⚡ Agente de Alocação"])

    # --- ABA 1: CARTEIRA ---
    with aba_carteira:
        st.subheader("Custódia Atual")
        with sqlite3.connect(DB_NAME) as conn:
            df = pd.read_sql("SELECT ticker, classe, quantidade, preco_medio FROM ativos", conn)
            st.dataframe(df, use_container_width=True)

    # --- ABA 2: RAIO-X FUNDAMENTALISTA E IA ---
    with aba_raiox:
        st.subheader("Análise Profissional de Ativo")
        ticker_alvo = st.text_input("Digite o Ticker (ex: BBAS3.SA)").upper()
        
        if st.button("Executar Varredura Completa"):
            with st.spinner("Analisando balanços e rodando Machine Learning..."):
                # 1. Fundamentos
                raio_x = AnalistaFundamentalista.avaliar_acao(ticker_alvo)
                # 2. IA Predição
                tendencia_ia, conf_ia = MotorIA.prever_tendencia(ticker_alvo)
                
                if raio_x:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### 📚 Fundamentos")
                        st.metric("Score Fundamentalista", f"{raio_x['pontos']}/{raio_x['max']} Pontos")
                        if raio_x['alertas']:
                            st.warning("Alertas: " + ", ".join(raio_x['alertas']))
                        else:
                            st.success("Ativo Sólido! Sem alertas críticos.")
                    
                    with col2:
                        st.markdown("### 🤖 Cérebro de Machine Learning")
                        if tendencia_ia == "Alta":
                            st.success(f"Tendência de {tendencia_ia} (Confiança: {conf_ia:.1f}%)")
                        else:
                            st.error(f"Tendência de {tendencia_ia} (Confiança: {conf_ia:.1f}%)")
                else:
                    st.error("Não foi possível carregar dados do Yahoo Finance para este ativo.")

    # --- ABA 3: AGENTE DE ALOCAÇÃO ---
    with aba_agente:
        st.subheader("Agente de Compras em Lote")
        orcamento = st.number_input("Verba Disponível para Aporte (R$):", value=1000.0)
        
        if st.button("Calcular Alocação Inteligente"):
            with sqlite3.connect(DB_NAME) as conn:
                ativos_banco = pd.read_sql("SELECT ticker FROM ativos", conn)['ticker'].tolist()
            
            if not ativos_banco:
                st.info("Cadastre ativos na sua base de dados primeiro.")
            else:
                verba_por_ativo = orcamento / len(ativos_banco)
                lista_compras = []
                
                for t in ativos_banco:
                    preco = AnalistaFundamentalista.avaliar_acao(t)
                    if preco and preco['preco'] > 0:
                        qtd = int(verba_por_ativo // preco['preco'])
                        custo = qtd * preco['preco']
                        lista_compras.append({"Ativo": t, "Qtd Sugerida": qtd, "Custo (R$)": custo})
                
                if lista_compras:
                    st.table(pd.DataFrame(lista_compras))
                    st.success("Alocação calculada com base no orçamento e preços em tempo real!")

if __name__ == "__main__":
    main()










