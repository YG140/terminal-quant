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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    email TEXT PRIMARY KEY, hash_senha TEXT
                )
            """)
            
            cursor = conn.cursor()
            
            # Posições Iniciais (Mantendo seus ativos preferidos)
            cursor.execute("SELECT COUNT(*) FROM ativos")
            if cursor.fetchone()[0] == 0:
                iniciais = [
                    ("KLBN4.SA", "Ações", 100, 4.10, 3),
                    ("BBAS3.SA", "Ações", 50, 26.50, 3),
                    ("MXRF11.SA", "FIIs", 200, 10.05, 4),
                    ("RESERVA", "Segurança", 1, 5000.0, 0)
                ]
                conn.executemany("INSERT INTO ativos VALUES (?, ?, ?, ?, ?)", iniciais)
                
            # Usuário Mestre Inicial
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            if cursor.fetchone()[0] == 0:
                email_padrao = "yurygabriel1.40@gmail.com"
                hash_padrao = "aa78f445e7b478beec6ac69594a3c6cc50cf9171405ef4471808d4dd0485d600"
                conn.execute("INSERT INTO usuarios VALUES (?, ?)", (email_padrao, hash_padrao))
                
            conn.commit()

    @staticmethod
    def verificar_acesso(user, pwd):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hash_senha FROM usuarios WHERE email=?", (user.strip(),))
            row = cursor.fetchone()
            if row:
                hash_banco = row[0]
                hash_input = hashlib.sha256(pwd.strip().encode()).hexdigest()
                return hash_input == hash_banco
        return False

    @staticmethod
    def atualizar_senha(user, nova_senha):
        with sqlite3.connect(DB_NAME) as conn:
            novo_hash = hashlib.sha256(nova_senha.strip().encode()).hexdigest()
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET hash_senha=? WHERE email=?", (novo_hash, user.strip()))
            conn.commit()
            return cursor.rowcount > 0

# ==============================================================================
# 2. MOTOR DE INTELIGÊNCIA ARTIFICIAL E FUNDAMENTOS
# ==============================================================================
class AnalisadorGlobal:
    
    @staticmethod
    def calcular_dy_real_fii(ticker_obj, preco_atual):
        try:
            proventos = ticker_obj.actions
            if proventos.empty: return 0.0
            
            # Remove fuso horário para evitar conflito
            proventos.index = proventos.index.tz_localize(None) 
            hoje = pd.Timestamp.today().tz_localize(None)
            
            proventos_ano = proventos[proventos.index >= (hoje - pd.Timedelta(days=365))]
            total_dividendos = proventos_ano['Dividends'].sum()
            
            if preco_atual > 0:
                return (total_dividendos / preco_atual) * 100
            return 0.0
        except Exception:
            return 0.0

    @staticmethod
    @st.cache_data(ttl=3600)
    def auditar_ativo(ticker):
        resultado = {
            "tipo": "Desconhecido", "preco": 0.0, "score": 0, "score_max": 5, 
            "alertas": [], "aprovado": False, "tendencia": "Estável", 
            "confianca": 0.0, "metricas": {}
        }
        
        try:
            obj = yf.Ticker(ticker)
            info = obj.info
            preco_atual = info.get('currentPrice', info.get('previousClose', 0.0))
            if preco_atual == 0.0:
                return resultado
            
            resultado['preco'] = preco_atual
            
            # Identificação Automática: Ação ou FII
            if ticker.endswith("11.SA") or "fundo" in info.get("longName", "").lower():
                resultado['tipo'] = "FII"
                resultado['score_max'] = 2
                
                pvp = info.get('priceToBook', 0)
                dy_real = AnalisadorGlobal.calcular_dy_real_fii(obj, preco_atual)
                
                resultado['metricas'] = {"P/VP": pvp, "DY Real (12m)": f"{dy_real:.2f}%"}
                
                if 0.85 <= pvp <= 1.04: resultado['score'] += 1
                else: resultado['alertas'].append("P/VP fora do equilíbrio (Caro ou Desconto Excessivo)")
                
                if dy_real >= 8.0: resultado['score'] += 1
                else: resultado['alertas'].append("Rendimento de Dividendos muito baixo (< 8%)")
                
                resultado['aprovado'] = resultado['score'] >= 2
                
            else:
                resultado['tipo'] = "Ação"
                pl = info.get('trailingPE', 0)
                pvp = info.get('priceToBook', 0)
                ev_ebitda = info.get('enterpriseToEbitda', 0)
                liquidez = info.get('currentRatio', 0)
                margem = info.get('profitMargins', 0) * 100
                roe = info.get('returnOnEquity', 0) * 100
                roic = info.get('returnOnAssets', 0) * 100
                
                resultado['metricas'] = {
                    "P/L": pl, "P/VP": pvp, "EV/EBITDA": ev_ebitda, 
                    "Liquidez Corrente": liquidez, "Margem Líquida": f"{margem:.2f}%", 
                    "ROE": f"{roe:.2f}%", "ROIC Proxy": f"{roic:.2f}%"
                }
                
                if 0 < pl < 15 and 0 < pvp < 1.6: resultado['score'] += 1
                else: resultado['alertas'].append("Valuation Esticado (Preço acima do justo)")
                
                if liquidez >= 1.2: resultado['score'] += 1
                else: resultado['alertas'].append("Liquidez Curto Prazo frágil")
                
                if margem > 10: resultado['score'] += 1
                else: resultado['alertas'].append("Margem de lucro baixa")
                
                if roe > 12: resultado['score'] += 1
                else: resultado['alertas'].append("ROE abaixo do ideal")
                
                if roic > 5: resultado['score'] += 1
                
                resultado['aprovado'] = resultado['score'] >= 4

            # --- MACHINE LEARNING (Tendência de Curto Prazo) ---
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
    st.set_page_config(page_title="Mesa Quant Master v5.0", layout="wide")
    nucleo = NucleoOperacional()

    if "auth" not in st.session_state: st.session_state.auth = False
    if "esqueci_senha" not in st.session_state: st.session_state.esqueci_senha = False

    # --- SISTEMA DE LOGIN ---
    if not st.session_state.auth:
        st.title("🔐 Acesso Restrito")
        
        if st.session_state.esqueci_senha:
            st.subheader("🔄 Redefinição de Senha")
            with st.form("form_recuperacao"):
                email_rec = st.text_input("E-mail cadastrado")
                chave_mestra = st.text_input("Chave Mestra de Segurança", type="password")
                nova_senha = st.text_input("Digite a Nova Senha", type="password")
                
                if st.form_submit_button("Alterar Senha"):
                    if chave_mestra == "quant2026": 
                        if nucleo.atualizar_senha(email_rec, nova_senha):
                            st.success("✅ Senha alterada com sucesso!")
                        else:
                            st.error("Usuário não encontrado.")
                    else:
                        st.error("Chave Mestra incorreta!")
            
            if st.button("⬅️ Voltar ao Login"):
                st.session_state.esqueci_senha = False
                st.rerun()
                
        else:
            with st.form("form_login"):
                u = st.text_input("E-mail corporativo")
                p = st.text_input("Chave de segurança", type="password")
                submitted = st.form_submit_button("Entrar ↵")
                
                if submitted:
                    if nucleo.verificar_acesso(u, p):
                        st.session_state.auth = True
                        st.rerun()
                    else:
                        st.error("❌ Credenciais inválidas.")
            
            if st.button("Esqueci minha senha"):
                st.session_state.esqueci_senha = True
                st.rerun()
        return

    # --- PAINEL PRINCIPAL ---
    col1, col2 = st.columns([8, 1])
    with col1:
        st.title("🛰️ Terminal Quantitativo Master v5.0")
    with col2:
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()
    
    t_carteira, t_raiox, t_agente, t_simulador = st.tabs([
        "📊 Custódia & Reserva", 
        "🔬 Scanner Profissional", 
        "⚡ Agente de Aportes", 
        "🎯 Simulador Passivo"
    ])

    # --- ABA 1: CUSTÓDIA E RESERVA ---
    with t_carteira:
        st.subheader("Posição Patrimonial Atual")
        with sqlite3.connect(DB_NAME) as conn:
            df = pd.read_sql("SELECT * FROM ativos", conn)
        
        reserva = df[df['ticker'] == 'RESERVA']['preco_medio'].sum() if not df[df['ticker'] == 'RESERVA'].empty else 0.0
        carteira = df[df['ticker'] != 'RESERVA']
        patrimonio_bolsa = (carteira['quantidade'] * carteira['preco_medio']).sum() if not carteira.empty else 0.0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Patrimônio em Bolsa", f"R$ {patrimonio_bolsa:,.2f}")
        c2.metric("Reserva de Emergência", f"R$ {reserva:,.2f}")
        c3.metric("Capital Consolidado", f"R$ {(patrimonio_bolsa + reserva):,.2f}")
        
        st.dataframe(carteira, use_container_width=True, hide_index=True)

    # --- ABA 2: SCANNER ---
    with t_raiox:
        st.subheader("Radar de Oportunidades (Ações e FIIs)")
        ticker_alvo = st.text_input("Ticker para auditar (ex: VALE3.SA ou MXRF11.SA):").upper()
        
        if st.button("Acionar Raio-X Institucional"):
            with st.spinner(f"Processando varredura quantitativa em {ticker_alvo}..."):
                analise = AnalisadorGlobal.auditar_ativo(ticker_alvo)
                
                if analise['preco'] > 0:
                    st.markdown(f"### Ativo: {ticker_alvo} ({analise['tipo']})")
                    c1, c2, c3 = st.columns(3)
                    
                    with c1:
                        st.markdown(f"**Cotação Atual:** R$ {analise['preco']:.2f}")
                        cor_v = "green" if analise['aprovado'] else "red"
                        st.markdown(f"**Veredito Fundamentalista:** :{cor_v}[{analise['score']}/{analise['score_max']} Pontos]")
                        if analise['aprovado']:
                            st.success("Ativo Seguro para Aporte.")
                        else:
                            st.error("Risco Elevado. Reprovado.")
                            for alerta in analise['alertas']: 
                                st.warning(f"⚠️ {alerta}")
                    
                    with c2:
                        st.markdown("**Métricas Extraídas:**")
                        for k, v in analise['metricas'].items():
                            if isinstance(v, float):
                                st.text(f"{k}: {v:.2f}")
                            else:
                                st.text(f"{k}: {v}")
                                
                    with c3:
                        cor_t = "green" if analise['tendencia'] == "Alta" else "red"
                        st.markdown(f"**IA Machine Learning:** :{cor_t}[{analise['tendencia']}]")
                        st.markdown(f"**Probabilidade de Alta:** {analise['confianca']:.1f}%")
                else:
                    st.error("Ativo não encontrado ou falha na extração de dados do Yahoo Finance.")

    # --- ABA 3: AGENTE DE EXECUÇÃO ---
    with t_agente:
        st.subheader("Agente Automático de Aportes")
        aporte = st.number_input("Caixa para Aporte Hoje (R$):", min_value=0.0, value=1500.0)
        
        if st.button("Processar Filtros e Gerar Ordem"):
            ativos_validos = carteira[carteira['quantidade'] > 0]
            
            if not ativos_validos.empty:
                compras = []
                ativos_aprovados = []
                
                with st.spinner("Analisando todos os ativos da carteira sob critérios rígidos..."):
                    for _, row in ativos_validos.iterrows():
                        analise = AnalisadorGlobal.auditar_ativo(row['ticker'])
                        # Só compra se passar no crivo institucional (Score >= 4 p/ ações ou >= 2 p/ FIIs)
                        if analise['aprovado'] and analise['tendencia'] == "Alta":
                            ativos_aprovados.append({"ticker": row['ticker'], "preco": analise['preco']})
                
                if ativos_aprovados:
                    verba_por_ativo = aporte / len(ativos_aprovados)
                    total_gasto = 0
                    
                    for item in ativos_aprovados:
                        qtd = int(verba_por_ativo // item['preco'])
                        if qtd > 0:
                            custo = qtd * item['preco']
                            total_gasto += custo
                            compras.append({"Ativo": item['ticker'], "Cotas": qtd, "Custo Total": f"R$ {custo:.2f}"})
                    
                    if compras:
                        st.success("✅ Lista Otimizada: Apenas ativos sólidos e em tendência de alta.")
                        st.table(pd.DataFrame(compras))
                        st.info(f"**Total Alocado:** R$ {total_gasto:.2f} | **Troco Preservado:** R$ {(aporte - total_gasto):.2f}")
                    else:
                        st.warning("Nenhum ativo atingiu cotação suficiente para compra com a verba fracionada.")
                else:
                    st.error("🛡️ O mercado está volátil ou caro demais hoje. Nenhum ativo da sua carteira atingiu a margem de segurança exigida pelos profissionais. Capital preservado em caixa!")

    # --- ABA 4: SIMULADOR ---
    with t_simulador:
        st.subheader("Linha do Tempo de Renda Passiva")
        meta_renda = st.number_input("Meta de dividendos mensais (R$):", value=5000.0)
        aporte_mensal = st.number_input("Aporte mensal religioso (R$):", value=1500.0)
        
        if st.button("Simular Linha do Tempo"):
            yield_mensal = 0.008 
            patrimonio_alvo = meta_renda / yield_mensal
            
            saldo = patrimonio_bolsa
            meses = 0
            while saldo < patrimonio_alvo and meses < 600: 
                saldo += aporte_mensal + (saldo * yield_mensal)
                meses += 1
            
            anos, meses_res = divmod(meses, 12)
            st.info(f"Para atingir R$ {meta_renda:,.2f} de renda (exige R$ {patrimonio_alvo:,.2f} investidos):")
            st.success(f"Mantendo aportes de R$ {aporte_mensal:,.2f}, você será livre em **{anos} anos e {meses_res} meses**.")

if __name__ == "__main__":
    main()










