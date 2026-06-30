import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import sqlite3
import hashlib
import logging
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# --- CONFIGURAÇÃO ---
logging.basicConfig(level=logging.INFO)
DB_NAME = "mesa_quant_definitiva.db"

# ==============================================================================
# 1. NÚCLEO DE DADOS E SEGURANÇA
# ==============================================================================
class NucleoOperacional:
    def __init__(self):
        self._inicializar_banco()

    def _inicializar_banco(self):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ativos (
                    ticker TEXT PRIMARY KEY, classe TEXT, 
                    quantidade REAL, preco_medio REAL, peso INTEGER
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS configuracoes (
                    chave TEXT PRIMARY KEY, valor REAL
                )
            """)
            
            # Populando valores iniciais de exemplo se o banco estiver vazio
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ativos")
            if cursor.fetchone()[0] == 0:
                iniciais = [
                    ("KLBN4.SA", "Ações", 100, 4.10, 3),
                    ("BBAS3.SA", "Ações", 50, 26.50, 3),
                    ("MXRF11.SA", "FIIs", 200, 10.05, 4),
                    ("RESERVA", "Segurança", 1, 5000.0, 0)
                ]
                conn.executemany("INSERT INTO ativos VALUES (?, ?, ?, ?, ?)", iniciais)
            conn.commit()

    @staticmethod
    def verificar_acesso(user, pwd):
        email_correto = "yurygabriel1.40@gmail.com"
        hash_correto = "aa78f445e7b478beec6ac69594a3c6cc50cf9171405ef4471808d4dd0485d600"
        return user.strip() == email_correto and hashlib.sha256(pwd.strip().encode()).hexdigest() == hash_correto

# ==============================================================================
# 2. MOTOR DE INTELIGÊNCIA ARTIFICIAL E FUNDAMENTOS
# ==============================================================================
class AnalisadorGlobal:
    @staticmethod
    @st.cache_data(ttl=3600)
    def prever_tendencia_e_fundamentos(ticker):
        resultado = {"tendencia": "Estável", "confianca": 0.0, "score": 0, "alertas": [], "preco": 0.0}
        try:
            # --- PARTE 1: FUNDAMENTOS ---
            obj = yf.Ticker(ticker)
            info = obj.info
            resultado['preco'] = info.get('currentPrice', info.get('previousClose', 0.0))
            
            pl = info.get('trailingPE', 0)
            pvp = info.get('priceToBook', 0)
            roe = info.get('returnOnEquity', 0) * 100
            
            if 0 < pl < 15 and 0 < pvp < 1.6: resultado['score'] += 1
            else: resultado['alertas'].append("Valuation Esticado")
            if roe > 12: resultado['score'] += 1
            else: resultado['alertas'].append("ROE Baixo")

            # --- PARTE 2: MACHINE LEARNING (Tendência) ---
            historico = obj.history(period="1y")
            if len(historico) > 40:
                historico['Retorno'] = historico['Close'].pct_change()
                historico['Media_5d'] = historico['Close'].rolling(window=5).mean()
                historico['Media_20d'] = historico['Close'].rolling(window=20).mean()
                historico['Volatilidade'] = historico['Retorno'].rolling(window=10).std()
                historico['Alvo'] = np.where(historico['Close'].shift(-1) > historico['Close'], 1, 0)
                historico = historico.dropna()

                X = historico[['Close', 'Media_5d', 'Media_20d', 'Volatilidade']]
                y = historico['Alvo']

                modelo = RandomForestClassifier(n_estimators=30, random_state=42)
                modelo.fit(X, y)

                ultimo_reg = np.array([X.iloc[-1]])
                previsao = modelo.predict(ultimo_reg)
                prob = modelo.predict_proba(ultimo_reg)[0][1] * 100

                resultado['tendencia'] = "Alta" if previsao[0] == 1 and prob > 55 else "Baixa"
                resultado['confianca'] = prob
                
        except Exception as e:
            logging.error(f"Erro ao analisar {ticker}: {e}")
        return resultado

# ==============================================================================
# 3. INTERFACE GRÁFICA (A MESA DE OPERAÇÕES)
# ==============================================================================
def main():
    st.set_page_config(page_title="Mesa Quant Master", layout="wide")
    nucleo = NucleoOperacional()

    if "auth" not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        st.title("🔐 Acesso Restrito - Autenticação")
        u = st.text_input("E-mail corporativo")
        p = st.text_input("Chave de segurança", type="password")
        if st.button("Autenticar") and nucleo.verificar_acesso(u, p):
            st.session_state.auth = True
            st.rerun()
        return

    st.title("🛰️ Terminal Quantitativo Master v20.0+")
    
    # Organização das 4 frentes do seu projeto
    t_carteira, t_raiox, t_agente, t_simulador = st.tabs([
        "📊 Custódia & Reserva", 
        "🔬 Scanner (IA + Raio-X)", 
        "⚡ Agente de Execução", 
        "🎯 Simulador de Independência"
    ])

    # --- ABA 1: CUSTÓDIA E RESERVA ---
    with t_carteira:
        st.subheader("Posição Patrimonial Atual")
        with sqlite3.connect(DB_NAME) as conn:
            df = pd.read_sql("SELECT * FROM ativos", conn)
        
        reserva = df[df['ticker'] == 'RESERVA']['preco_medio'].sum()
        carteira = df[df['ticker'] != 'RESERVA']
        
        patrimonio_bolsa = (carteira['quantidade'] * carteira['preco_medio']).sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Patrimônio em Bolsa", f"R$ {patrimonio_bolsa:,.2f}")
        c2.metric("Reserva de Emergência", f"R$ {reserva:,.2f}")
        c3.metric("Capital Consolidado", f"R$ {(patrimonio_bolsa + reserva):,.2f}")
        
        st.dataframe(carteira, use_container_width=True, hide_index=True)

    # --- ABA 2: SCANNER (Machine Learning + Fundamentos) ---
    with t_raiox:
        st.subheader("Radar de Oportunidades")
        ticker_alvo = st.text_input("Ticker para auditar (ex: VALE3.SA):").upper()
        if st.button("Acionar IA e Raio-X"):
            with st.spinner(f"Analisando dados globais de {ticker_alvo}..."):
                analise = AnalisadorGlobal.prever_tendencia_e_fundamentos(ticker_alvo)
                if analise['preco'] > 0:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Cotação Atual:** R$ {analise['preco']:.2f}")
                        st.markdown(f"**Score Fundamentalista:** {analise['score']}/2 Pontos")
                        for alerta in analise['alertas']: st.warning(f"Alerta: {alerta}")
                    with c2:
                        cor = "green" if analise['tendencia'] == "Alta" else "red"
                        st.markdown(f"**Decisão da IA:** :{cor}[{analise['tendencia']}]")
                        st.markdown(f"**Confiança do Algoritmo:** {analise['confianca']:.1f}%")
                else:
                    st.error("Ativo não encontrado ou sem dados suficientes.")

    # --- ABA 3: AGENTE DE EXECUÇÃO E REBALANCEAMENTO ---
    with t_agente:
        st.subheader("Agente Automático de Aportes")
        aporte = st.number_input("Caixa para Aporte Hoje (R$):", min_value=0.0, value=1500.0)
        
        if st.button("Gerar Ordem de Compra"):
            ativos_validos = carteira[carteira['quantidade'] > 0]
            if not ativos_validos.empty:
                verba_por_ativo = aporte / len(ativos_validos)
                compras = []
                for _, row in ativos_validos.iterrows():
                    analise = AnalisadorGlobal.prever_tendencia_e_fundamentos(row['ticker'])
                    preco = analise['preco'] if analise['preco'] > 0 else row['preco_medio']
                    
                    if analise['tendencia'] == "Alta":
                        qtd = int(verba_por_ativo // preco)
                        if qtd > 0:
                            compras.append({"Ativo": row['ticker'], "Comprar": qtd, "Preço Teto": f"R$ {preco:.2f}"})
                
                if compras:
                    st.success("Lista de compras otimizada gerada!")
                    st.table(pd.DataFrame(compras))
                    st.caption("A IA filtrou automaticamente os ativos em tendência de baixa, focando seu dinheiro onde há probabilidade de alta.")
                else:
                    st.warning("A IA determinou que o mercado está volátil. Mantenha o caixa na Reserva.")

    # --- ABA 4: SIMULADOR DE INDEPENDÊNCIA FINANCEIRA ---
    with t_simulador:
        st.subheader("Linha do Tempo de Renda Passiva")
        meta_renda = st.number_input("Qual a sua meta de dividendos mensais? (R$):", value=5000.0)
        aporte_mensal = st.number_input("Quanto você aportará religiosamente por mês? (R$):", value=1500.0)
        
        if st.button("Simular Linha do Tempo"):
            yield_mensal = 0.008 # Assumindo média de 0.8% ao mês
            patrimonio_alvo = meta_renda / yield_mensal
            
            saldo = patrimonio_bolsa
            meses = 0
            while saldo < patrimonio_alvo and meses < 600: # Limite de 50 anos
                saldo += aporte_mensal + (saldo * yield_mensal)
                meses += 1
            
            anos, meses_res = divmod(meses, 12)
            st.info(f"Para atingir R$ {meta_renda:,.2f} de renda passiva (requer R$ {patrimonio_alvo:,.2f} investidos):")
            st.success(f"Mantendo aportes de R$ {aporte_mensal:,.2f}, você atingirá a liberdade em **{anos} anos e {meses_res} meses**.")

if __name__ == "__main__":
    main()










