import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import anthropic

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Gestión de Portafolios",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS profesionales
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #2c3e50;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    .question-card {
        background: #ffffff;
        border: 1px solid #e8e9ea;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .result-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 2rem;
        margin: 1.5rem 0;
    }
    .portfolio-card {
        background: #ffffff;
        border: 1px solid #e8e9ea;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .metric-container {
        background: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e8e9ea;
    }
    .asset-info {
        background: #f8f9fa;
        border-left: 4px solid #3498db;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 4px 4px 0;
    }
    .sidebar-nav {
        background: #2c3e50;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .performance-positive {
        color: #27ae60;
        font-weight: 600;
    }
    .performance-negative {
        color: #e74c3c;
        font-weight: 600;
    }
    .ai-analysis {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

class QuestionnaireSystem:
    def __init__(self):
        self.questions = [
            {
                "id": 1,
                "text": "¿Cuál es tu experiencia previa en inversiones?",
                "options": [
                    {"text": "Sin experiencia", "value": 1},
                    {"text": "Experiencia básica (menos de 2 años)", "value": 3},
                    {"text": "Experiencia moderada (2-5 años)", "value": 6},
                    {"text": "Experiencia avanzada (más de 5 años)", "value": 9}
                ]
            },
            {
                "id": 2,
                "text": "¿Cuál es tu horizonte temporal de inversión?",
                "options": [
                    {"text": "Menos de 1 año", "value": 1},
                    {"text": "1-3 años", "value": 3},
                    {"text": "3-10 años", "value": 6},
                    {"text": "Más de 10 años", "value": 10}
                ]
            },
            {
                "id": 3,
                "text": "Si tu inversión perdiera 20% en un mes, ¿qué harías?",
                "options": [
                    {"text": "Vendería inmediatamente", "value": 1},
                    {"text": "Me preocuparía pero mantendría", "value": 4},
                    {"text": "Mantendría sin preocupación", "value": 7},
                    {"text": "Compraría más aprovechando la caída", "value": 10}
                ]
            },
            {
                "id": 4,
                "text": "¿Qué porcentaje de tus ingresos anuales representaría esta inversión?",
                "options": [
                    {"text": "Más del 50%", "value": 1},
                    {"text": "20-50%", "value": 4},
                    {"text": "10-20%", "value": 7},
                    {"text": "Menos del 10%", "value": 10}
                ]
            },
            {
                "id": 5,
                "text": "¿Cuál es tu principal objetivo de inversión?",
                "options": [
                    {"text": "Preservar capital", "value": 1},
                    {"text": "Ingresos estables", "value": 3},
                    {"text": "Crecimiento moderado", "value": 6},
                    {"text": "Crecimiento agresivo", "value": 10}
                ]
            },
            {
                "id": 6,
                "text": "¿Cómo reaccionarías ante volatilidad diaria en tu portafolio?",
                "options": [
                    {"text": "No podría tolerarla", "value": 1},
                    {"text": "Me causaría estrés", "value": 3},
                    {"text": "La aceptaría con reservas", "value": 6},
                    {"text": "No me afectaría", "value": 10}
                ]
            },
            {
                "id": 7,
                "text": "¿Qué nivel de pérdida máxima podrías aceptar en un año?",
                "options": [
                    {"text": "0-5%", "value": 1},
                    {"text": "5-15%", "value": 4},
                    {"text": "15-30%", "value": 7},
                    {"text": "Más del 30%", "value": 10}
                ]
            },
            {
                "id": 8,
                "text": "¿Prefieres inversiones que conozcas bien o explorar nuevas oportunidades?",
                "options": [
                    {"text": "Solo inversiones conocidas", "value": 1},
                    {"text": "Principalmente conocidas", "value": 4},
                    {"text": "Mezcla equilibrada", "value": 6},
                    {"text": "Explorar nuevas oportunidades", "value": 10}
                ]
            },
            {
                "id": 9,
                "text": "¿Con qué frecuencia planeas revisar tu portafolio?",
                "options": [
                    {"text": "Diariamente", "value": 2},
                    {"text": "Semanalmente", "value": 4},
                    {"text": "Mensualmente", "value": 7},
                    {"text": "Trimestralmente o menos", "value": 10}
                ]
            },
            {
                "id": 10,
                "text": "¿Cómo describirías tu situación financiera actual?",
                "options": [
                    {"text": "Necesito estos fondos pronto", "value": 1},
                    {"text": "Tengo algunas reservas", "value": 4},
                    {"text": "Tengo reservas adecuadas", "value": 7},
                    {"text": "Tengo abundantes reservas", "value": 10}
                ]
            }
        ]

    def calculate_risk_score(self, answers):
        total = sum(answers.values())
        return min(10, max(1, total / 10))

class PortfolioManager:
    def __init__(self):
        self.portfolios = {
            "conservative": {
                "name": "Portafolio Conservador",
                "risk_range": (1, 3),
                "expected_return": 5.8,
                "std_deviation": 8.4,
                "assets": {
                    "TLT": {
                        "name": "iShares 20+ Year Treasury Bond ETF",
                        "percentage": 25,
                        "description": "Bonos del Tesoro a largo plazo. Proporciona estabilidad y protección contra la inflación.",
                        "sector": "Renta Fija",
                        "risk_level": "Bajo"
                    },
                    "LQD": {
                        "name": "iShares Investment Grade Corporate Bond ETF",
                        "percentage": 20,
                        "description": "Bonos corporativos de alta calidad. Ofrece rendimientos superiores a los bonos del gobierno.",
                        "sector": "Renta Fija",
                        "risk_level": "Bajo-Medio"
                    },
                    "JNJ": {
                        "name": "Johnson & Johnson",
                        "percentage": 15,
                        "description": "Líder global en productos farmacéuticos y de consumo. Dividend aristocrat con historial sólido.",
                        "sector": "Salud",
                        "risk_level": "Bajo"
                    },
                    "PG": {
                        "name": "Procter & Gamble",
                        "percentage": 15,
                        "description": "Empresa de bienes de consumo básico. Marcas reconocidas mundialmente y dividendos estables.",
                        "sector": "Consumo Básico",
                        "risk_level": "Bajo"
                    },
                    "KO": {
                        "name": "The Coca-Cola Company",
                        "percentage": 10,
                        "description": "Gigante global de bebidas. Flujo de efectivo predecible y presencia internacional.",
                        "sector": "Consumo Básico",
                        "risk_level": "Bajo"
                    },
                    "VYM": {
                        "name": "Vanguard High Dividend Yield ETF",
                        "percentage": 10,
                        "description": "ETF que rastrea acciones de alta rentabilidad por dividendo. Diversificación sectorial.",
                        "sector": "Diversificado",
                        "risk_level": "Medio"
                    },
                    "MSFT": {
                        "name": "Microsoft Corporation",
                        "percentage": 5,
                        "description": "Líder en software y servicios en la nube. Crecimiento estable y dividendos crecientes.",
                        "sector": "Tecnología",
                        "risk_level": "Medio"
                    }
                }
            },
            "moderate": {
                "name": "Portafolio Moderado",
                "risk_range": (4, 7),
                "expected_return": 8.7,
                "std_deviation": 14.6,
                "assets": {
                    "AAPL": {
                        "name": "Apple Inc.",
                        "percentage": 20,
                        "description": "Empresa tecnológica líder en dispositivos móviles y servicios. Sólido flujo de efectivo.",
                        "sector": "Tecnología",
                        "risk_level": "Medio"
                    },
                    "MSFT": {
                        "name": "Microsoft Corporation",
                        "percentage": 15,
                        "description": "Dominante en software empresarial y computación en la nube. Crecimiento consistente.",
                        "sector": "Tecnología",
                        "risk_level": "Medio"
                    },
                    "LQD": {
                        "name": "iShares Investment Grade Corporate Bond ETF",
                        "percentage": 15,
                        "description": "Bonos corporativos de grado de inversión para estabilidad del portafolio.",
                        "sector": "Renta Fija",
                        "risk_level": "Bajo-Medio"
                    },
                    "GOOGL": {
                        "name": "Alphabet Inc.",
                        "percentage": 12,
                        "description": "Conglomerado tecnológico con dominio en búsquedas y publicidad digital.",
                        "sector": "Tecnología",
                        "risk_level": "Medio-Alto"
                    },
                    "JPM": {
                        "name": "JPMorgan Chase & Co.",
                        "percentage": 10,
                        "description": "Banco de inversión líder. Beneficiario de entornos de tasas de interés altas.",
                        "sector": "Financiero",
                        "risk_level": "Medio"
                    },
                    "LLY": {
                        "name": "Eli Lilly and Company",
                        "percentage": 10,
                        "description": "Farmacéutica con pipeline robusto, especialmente en diabetes y oncología.",
                        "sector": "Salud",
                        "risk_level": "Medio"
                    },
                    "VTI": {
                        "name": "Vanguard Total Stock Market ETF",
                        "percentage": 8,
                        "description": "Exposición amplia al mercado accionario estadounidense completo.",
                        "sector": "Diversificado",
                        "risk_level": "Medio"
                    },
                    "IEF": {
                        "name": "iShares 7-10 Year Treasury Bond ETF",
                        "percentage": 5,
                        "description": "Bonos del Tesoro de plazo medio para diversificación de renta fija.",
                        "sector": "Renta Fija",
                        "risk_level": "Bajo"
                    },
                    "EFA": {
                        "name": "iShares MSCI EAFE ETF",
                        "percentage": 5,
                        "description": "Exposición a mercados desarrollados internacionales para diversificación geográfica.",
                        "sector": "Internacional",
                        "risk_level": "Medio"
                    }
                }
            },
            "aggressive": {
                "name": "Portafolio Agresivo",
                "risk_range": (8, 10),
                "expected_return": 13.5,
                "std_deviation": 28.2,
                "assets": {
                    "NVDA": {
                        "name": "NVIDIA Corporation",
                        "percentage": 25,
                        "description": "Líder en GPUs y computación de IA. Beneficiario directo del boom de inteligencia artificial.",
                        "sector": "Tecnología",
                        "risk_level": "Alto"
                    },
                    "TSLA": {
                        "name": "Tesla, Inc.",
                        "percentage": 20,
                        "description": "Pioneer en vehículos eléctricos y energía sostenible. Alto potencial de crecimiento.",
                        "sector": "Automotriz/Energía",
                        "risk_level": "Alto"
                    },
                    "QQQ": {
                        "name": "Invesco QQQ Trust",
                        "percentage": 15,
                        "description": "ETF que rastrea el NASDAQ-100. Concentrado en tecnología de crecimiento.",
                        "sector": "Tecnología",
                        "risk_level": "Alto"
                    },
                    "ARKK": {
                        "name": "ARK Innovation ETF",
                        "percentage": 12,
                        "description": "ETF enfocado en empresas innovadoras disruptivas y tecnologías emergentes.",
                        "sector": "Innovación",
                        "risk_level": "Muy Alto"
                    },
                    "AMD": {
                        "name": "Advanced Micro Devices",
                        "percentage": 10,
                        "description": "Competidor clave en procesadores y GPUs. Beneficiario del crecimiento en computación.",
                        "sector": "Tecnología",
                        "risk_level": "Alto"
                    },
                    "LLY": {
                        "name": "Eli Lilly and Company",
                        "percentage": 8,
                        "description": "Farmacéutica innovadora con fuerte pipeline en tratamientos revolucionarios.",
                        "sector": "Salud",
                        "risk_level": "Medio-Alto"
                    },
                    "LIT": {
                        "name": "Global X Lithium & Battery Tech ETF",
                        "percentage": 5,
                        "description": "ETF especializado en tecnología de baterías y litio para vehículos eléctricos.",
                        "sector": "Materiales/Energía",
                        "risk_level": "Alto"
                    },
                    "BITO": {
                        "name": "ProShares Bitcoin Strategy ETF",
                        "percentage": 3,
                        "description": "Exposición a Bitcoin a través de futuros. Activo alternativo de alto riesgo.",
                        "sector": "Criptomonedas",
                        "risk_level": "Muy Alto"
                    },
                    "EEM": {
                        "name": "iShares MSCI Emerging Markets ETF",
                        "percentage": 2,
                        "description": "Exposición a mercados emergentes con alto potencial de crecimiento.",
                        "sector": "Emergentes",
                        "risk_level": "Alto"
                    }
                }
            }
        }

    def get_portfolio_by_risk_score(self, risk_score):
        for portfolio_key, portfolio in self.portfolios.items():
            min_risk, max_risk = portfolio["risk_range"]
            if min_risk <= risk_score <= max_risk:
                return portfolio
        return self.portfolios["moderate"]

    def generate_performance_data(self, portfolio, days=365):
        np.random.seed(42)
        dates = [datetime.now() - timedelta(days=days-i) for i in range(days)]
        
        expected_daily_return = portfolio["expected_return"] / 100 / 365
        daily_volatility = portfolio["std_deviation"] / 100 / np.sqrt(365)
        
        returns = np.random.normal(expected_daily_return, daily_volatility, days)
        cumulative_returns = np.cumprod(1 + returns)
        
        portfolio_values = cumulative_returns * 100
        
        asset_data = {}
        for asset_code, asset_info in portfolio["assets"].items():
            asset_vol = daily_volatility * (0.8 + 0.4 * np.random.random())
            asset_returns = np.random.normal(expected_daily_return * 1.1, asset_vol, days)
            asset_cumulative = np.cumprod(1 + asset_returns)
            asset_values = asset_cumulative * 100
            
            asset_data[asset_code] = {
                "values": asset_values,
                "current_change": (asset_values[-1] - asset_values[-2]) / asset_values[-2] * 100,
                "ytd_change": (asset_values[-1] - asset_values[0]) / asset_values[0] * 100
            }
        
        return {
            "dates": dates,
            "portfolio_values": portfolio_values,
            "asset_data": asset_data,
            "current_portfolio_change": (portfolio_values[-1] - portfolio_values[-2]) / portfolio_values[-2] * 100,
            "ytd_portfolio_change": (portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0] * 100
        }

def get_claude_analysis(risk_score, portfolio):
    try:
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        
        asset_list = ", ".join([f"{code} ({info['percentage']}%)" for code, info in portfolio["assets"].items()])
        
        prompt = f"""
        Como experto en gestión de portafolios y teoría moderna de inversiones, analiza el siguiente perfil:

        PERFIL DEL INVERSIONISTA:
        - Puntuación de tolerancia al riesgo: {risk_score:.1f}/10
        - Portafolio recomendado: {portfolio["name"]}
        - Rendimiento esperado: {portfolio["expected_return"]}%
        - Desviación estándar: {portfolio["std_deviation"]}%
        - Composición: {asset_list}

        Proporciona un análisis profesional de máximo 250 palabras que incluya:
        1. Justificación de por qué este portafolio es adecuado para el perfil de riesgo
        2. Ventajas principales de la composición seleccionada
        3. Riesgos a considerar
        4. Recomendaciones de seguimiento

        Usa un tono profesional y técnico apropiado para un asesor financiero.
        """
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    except Exception as e:
        return f"El análisis personalizado no está disponible en este momento. El portafolio ha sido seleccionado usando criterios cuantitativos basados en la teoría moderna de portafolios y su puntuación de riesgo de {risk_score:.1f}/10."

def page_questionnaire():
    st.markdown('<h1 class="main-header">Evaluación de Perfil de Riesgo</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Complete el cuestionario para determinar su perfil de inversión óptimo</p>', unsafe_allow_html=True)
    
    questionnaire = QuestionnaireSystem()
    answers = {}
    
    for question in questionnaire.questions:
        st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
        st.markdown(f"**Pregunta {question['id']}:** {question['text']}")
        
        options = [opt["text"] for opt in question["options"]]
        selected = st.radio(
            "Seleccione su respuesta:",
            options,
            key=f"q_{question['id']}",
            index=None
        )
        
        if selected:
            for opt in question["options"]:
                if opt["text"] == selected:
                    answers[question["id"]] = opt["value"]
                    break
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if len(answers) == len(questionnaire.questions):
        if st.button("Analizar Perfil de Riesgo", type="primary", use_container_width=True):
            risk_score = questionnaire.calculate_risk_score(answers)
            st.session_state.risk_score = risk_score
            st.session_state.page = "results"
            st.rerun()
    else:
        progress = len(answers) / len(questionnaire.questions)
        st.progress(progress)
        st.info(f"Progreso: {len(answers)}/{len(questionnaire.questions)} preguntas completadas")

def page_results():
    if "risk_score" not in st.session_state:
        st.warning("Complete primero el cuestionario de evaluación")
        return
    
    st.markdown('<h1 class="main-header">Resultado de Evaluación</h1>', unsafe_allow_html=True)
    
    portfolio_manager = PortfolioManager()
    portfolio = portfolio_manager.get_portfolio_by_risk_score(st.session_state.risk_score)
    
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Puntuación de Riesgo", f"{st.session_state.risk_score:.1f}/10")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Portafolio Recomendado", portfolio["name"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Rendimiento Esperado", f"{portfolio['expected_return']}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Análisis con IA
    with st.spinner("Generando análisis personalizado..."):
        claude_analysis = get_claude_analysis(st.session_state.risk_score, portfolio)
        
        st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
        st.subheader("Análisis Personalizado")
        st.markdown(claude_analysis)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("Composición del Portafolio")
    
    for asset_code, asset_info in portfolio["assets"].items():
        st.markdown(f'<div class="asset-info">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{asset_info['name']} ({asset_code})**")
            st.markdown(f"*{asset_info['description']}*")
            st.markdown(f"Sector: {asset_info['sector']} | Nivel de Riesgo: {asset_info['risk_level']}")
        
        with col2:
            st.metric("Asignación", f"{asset_info['percentage']}%")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("Configuración de Inversión")
    
    investment_amount = st.number_input(
        "Monto a invertir (USD)",
        min_value=1000,
        max_value=10000000,
        value=10000,
        step=1000,
        format="%d"
    )
    
    if st.button("Proceder con la Inversión", type="primary", use_container_width=True):
        st.session_state.investment_amount = investment_amount
        st.session_state.selected_portfolio = portfolio
        st.session_state.page = "portfolio"
        st.rerun()

def page_portfolio():
    if "selected_portfolio" not in st.session_state:
        st.warning("Configure primero su portafolio en la sección de resultados")
        return
    
    st.markdown('<h1 class="main-header">Monitor de Portafolio</h1>', unsafe_allow_html=True)
    
    portfolio = st.session_state.selected_portfolio
    investment_amount = st.session_state.investment_amount
    portfolio_manager = PortfolioManager()
    
    performance_data = portfolio_manager.generate_performance_data(portfolio)
    
    # Métricas principales
    current_value = investment_amount * (performance_data["portfolio_values"][-1] / 100)
    total_return = current_value - investment_amount
    total_return_pct = (current_value / investment_amount - 1) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Valor Actual", f"${current_value:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Ganancia/Pérdida", f"${total_return:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        change_class = "performance-positive" if total_return_pct >= 0 else "performance-negative"
        st.markdown(f'<div class="{change_class}">Rendimiento Total: {total_return_pct:.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        daily_change_class = "performance-positive" if performance_data["current_portfolio_change"] >= 0 else "performance-negative"
        st.markdown(f'<div class="{daily_change_class}">Cambio Diario: {performance_data["current_portfolio_change"]:.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráfico de rendimiento del portafolio
    st.subheader("Evolución del Portafolio")
    
    portfolio_values_scaled = [investment_amount * (val / 100) for val in performance_data["portfolio_values"]]
    
    fig_portfolio = go.Figure()
    fig_portfolio.add_trace(go.Scatter(
        x=performance_data["dates"],
        y=portfolio_values_scaled,
        mode='lines',
        name='Valor del Portafolio',
        line=dict(color='#3498db', width=2)
    ))
    
    fig_portfolio.add_hline(y=investment_amount, line_dash="dash", line_color="gray", 
                           annotation_text="Inversión Inicial")
    
    fig_portfolio.update_layout(
        title="Evolución del Valor del Portafolio",
        xaxis_title="Fecha",
        yaxis_title="Valor (USD)",
        hovermode='x unified',
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig_portfolio, use_container_width=True)
    
    # Desglose por activos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribución Actual")
        
        asset_names = []
        asset_values = []
        asset_percentages = []
        
        for asset_code, asset_info in portfolio["assets"].items():
            asset_investment = investment_amount * (asset_info["percentage"] / 100)
            current_asset_value = asset_investment * (performance_data["asset_data"][asset_code]["values"][-1] / 100)
            
            asset_names.append(f"{asset_code}")
            asset_values.append(current_asset_value)
            asset_percentages.append(asset_info["percentage"])
        
        fig_pie = px.pie(
            values=asset_values,
            names=asset_names,
            title="Valor por Activo"
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("Rendimiento por Activo")
        
        asset_performance_data = []
        for asset_code, asset_info in portfolio["assets"].items():
            asset_data = performance_data["asset_data"][asset_code]
            asset_investment = investment_amount * (asset_info["percentage"] / 100)
            current_asset_value = asset_investment * (asset_data["values"][-1] / 100)
            asset_return = current_asset_value - asset_investment
            
            asset_performance_data.append({
                "Activo": asset_code,
                "Inversión": asset_investment,
                "Valor Actual": current_asset_value,
                "Ganancia/Pérdida": asset_return,
                "Rendimiento %": asset_data["ytd_change"],
                "Cambio Diario %": asset_data["current_change"]
            })
        
        df_performance = pd.DataFrame(asset_performance_data)
        
        st.markdown("### Detalle de Rendimientos")
        for _, row in df_performance.iterrows():
            with st.expander(f"{row['Activo']} - {portfolio['assets'][row['Activo']]['name']}"):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Valor Actual", f"${row['Valor Actual']:,.2f}")
                with col_b:
                    st.metric("Ganancia/Pérdida", f"${row['Ganancia/Pérdida']:,.2f}")
                with col_c:
                    change_color = "normal" if row['Rendimiento %'] >= 0 else "inverse"
                    st.metric("Rendimiento", f"{row['Rendimiento %']:.2f}%", 
                            f"{row['Cambio Diario %']:.2f}% (24h)", delta_color=change_color)

def main():
    # Navegación
    if "page" not in st.session_state:
        st.session_state.page = "questionnaire"
    
    with st.sidebar:
        st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
        st.markdown("**Sistema de Gestión de Portafolios**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        pages = {
            "questionnaire": "1. Evaluación de Riesgo",
            "results": "2. Resultados y Configuración", 
            "portfolio": "3. Monitor de Portafolio"
        }
        
        for page_key, page_name in pages.items():
            if st.button(page_name, use_container_width=True, 
                        type="primary" if st.session_state.page == page_key else "secondary"):
                st.session_state.page = page_key
                st.rerun()
        
        st.markdown("---")
        st.markdown("**Información del Sistema**")
        st.markdown("Basado en la Teoría Moderna de Portafolios")
        st.markdown("Análisis cuantitativo de riesgo")
        st.markdown("Diversificación optimizada")
        st.markdown("Análisis de IA integrado")
    
    # Renderizar página actual
    if st.session_state.page == "questionnaire":
        page_questionnaire()
    elif st.session_state.page == "results":
        page_results()
    elif st.session_state.page == "portfolio":
        page_portfolio()

if __name__ == "__main__":
    main()