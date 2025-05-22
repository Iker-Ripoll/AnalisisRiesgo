import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass
from typing import Dict, List, Tuple
import anthropic

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Tolerancia al Riesgo",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f4e79;
    text-align: center;
    margin-bottom: 1rem;
}
.sub-header {
    font-size: 1.2rem;
    color: #666;
    text-align: center;
    margin-bottom: 2rem;
}
.question-container {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
    border-left: 4px solid #1f4e79;
}
.result-container {
    background-color: #e8f4fd;
    padding: 2rem;
    border-radius: 15px;
    border: 2px solid #1f4e79;
    margin: 2rem 0;
}
.portfolio-container {
    background-color: #f0f8ff;
    padding: 2rem;
    border-radius: 15px;
    border: 2px solid #4a90e2;
    margin: 2rem 0;
}
.metric-card {
    background-color: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

@dataclass
class Question:
    id: int
    text: str
    options: List[Dict[str, any]]

@dataclass
class RiskProfile:
    score: int
    profile_name: str
    risk_aversion_a: float
    description: str
    color: str

@dataclass
class Portfolio:
    name: str
    composition: Dict[str, float]
    expected_return: float
    std_deviation: float
    variance: float
    sharpe_ratio: float
    characteristics: str

class RiskToleranceCalculator:
    def __init__(self):
        self.questions = [
            Question(
                id=1,
                text="Solo 60 días después de invertir dinero, el precio cae 20%. Asumiendo que los fundamentos no han cambiado, ¿qué harías?",
                options=[
                    {"value": "a", "text": "Vender para evitar más preocupaciones y probar algo diferente", "points": 1},
                    {"value": "b", "text": "No hacer nada y esperar a que la inversión se recupere", "points": 2},
                    {"value": "c", "text": "Comprar más. Era una buena inversión antes; ahora es una inversión barata también", "points": 3}
                ]
            ),
            Question(
                id=2,
                text="Tu inversión cayó 20%, pero es parte de un portafolio para objetivos a 5 años. ¿Qué harías?",
                options=[
                    {"value": "a", "text": "Vender", "points": 1},
                    {"value": "b", "text": "No hacer nada", "points": 2},
                    {"value": "c", "text": "Comprar más", "points": 3}
                ]
            ),
            Question(
                id=3,
                text="¿Qué harías si el objetivo fuera a 15 años?",
                options=[
                    {"value": "a", "text": "Vender", "points": 1},
                    {"value": "b", "text": "No hacer nada", "points": 2},
                    {"value": "c", "text": "Comprar más", "points": 3}
                ]
            ),
            Question(
                id=4,
                text="¿Qué harías si el objetivo fuera a 30 años?",
                options=[
                    {"value": "a", "text": "Vender", "points": 1},
                    {"value": "b", "text": "No hacer nada", "points": 2},
                    {"value": "c", "text": "Comprar más", "points": 3}
                ]
            ),
            Question(
                id=5,
                text="El precio de tu inversión para el retiro sube 25% un mes después de comprarla. Los fundamentos no han cambiado. Después de celebrar, ¿qué haces?",
                options=[
                    {"value": "a", "text": "Venderla y asegurar las ganancias", "points": 1},
                    {"value": "b", "text": "Mantenerla y esperar más ganancias", "points": 2},
                    {"value": "c", "text": "Comprar más; podría subir más", "points": 3}
                ]
            ),
            Question(
                id=6,
                text="Estás invirtiendo para el retiro en 15 años. ¿Qué preferirías hacer?",
                options=[
                    {"value": "a", "text": "Invertir en un fondo del mercado monetario, renunciando a grandes ganancias pero asegurando el capital", "points": 1},
                    {"value": "b", "text": "Invertir 50-50 en fondos de bonos y acciones, buscando crecimiento con algo de protección", "points": 2},
                    {"value": "c", "text": "Invertir en fondos de crecimiento agresivo que fluctúen significativamente pero con potencial de grandes ganancias", "points": 3}
                ]
            ),
            Question(
                id=7,
                text="¡Acabas de ganar un gran premio! Pero ¿cuál eliges?",
                options=[
                    {"value": "a", "text": "$2,000 en efectivo", "points": 1},
                    {"value": "b", "text": "50% de probabilidad de ganar $5,000", "points": 2},
                    {"value": "c", "text": "20% de probabilidad de ganar $15,000", "points": 3}
                ]
            )
        ]
        
        self.risk_profiles = {
            "conservador": RiskProfile(
                score=(7, 14),
                profile_name="Inversionista Conservador",
                risk_aversion_a=5.0,
                description="Prefiere seguridad y estabilidad. Evita riesgos altos y busca preservar el capital.",
                color="#dc3545"
            ),
            "moderado": RiskProfile(
                score=(15, 19),
                profile_name="Inversionista Moderado",
                risk_aversion_a=3.5,
                description="Busca un equilibrio entre riesgo y rendimiento. Acepta cierta volatilidad por mejores retornos.",
                color="#ffc107"
            ),
            "agresivo": RiskProfile(
                score=(20, 21),
                profile_name="Inversionista Agresivo",
                risk_aversion_a=2.0,
                description="Tiene alta tolerancia al riesgo. Busca maximizar rendimientos a largo plazo.",
                color="#28a745"
            )
        }

        self.portfolios = {
            "conservador": Portfolio(
                name="Portafolio Conservador",
                composition={
                    "Bonos del Tesoro (TLT)": 20,
                    "Bonos Corporativos (LQD)": 20,
                    "Microsoft (MSFT)": 15,
                    "Johnson & Johnson (JNJ)": 10,
                    "The Coca-Cola (KO)": 10,
                    "Procter & Gamble (PG)": 10,
                    "Vanguard High Dividend (VYM)": 10,
                    "Apple (AAPL)": 5
                },
                expected_return=5.8,
                std_deviation=8.4,
                variance=0.71,
                sharpe_ratio=0.45,
                characteristics="Alta proporción de bonos (40%). Acciones de baja beta. Sectores defensivos. Ideal para preservación de capital."
            ),
            "moderado": Portfolio(
                name="Portafolio Moderado",
                composition={
                    "Bonos Corporativos (LQD)": 15,
                    "Bonos del Tesoro (IEF)": 10,
                    "Apple (AAPL)": 15,
                    "Microsoft (MSFT)": 15,
                    "Alphabet (GOOGL)": 10,
                    "Eli Lilly (LLY)": 10,
                    "JPMorgan Chase (JPM)": 8,
                    "Vanguard Total Stock (VTI)": 7,
                    "iShares MSCI EAFE (EFA)": 5,
                    "Amazon (AMZN)": 5
                },
                expected_return=8.7,
                std_deviation=14.6,
                variance=2.13,
                sharpe_ratio=0.53,
                characteristics="Balance 25% renta fija, 75% renta variable. Diversificación sectorial. Exposición internacional limitada."
            ),
            "agresivo": Portfolio(
                name="Portafolio Agresivo",
                composition={
                    "NVIDIA (NVDA)": 25,
                    "Tesla (TSLA)": 15,
                    "Invesco QQQ (QQQ)": 15,
                    "Apple (AAPL)": 10,
                    "ARK Innovation (ARKK)": 10,
                    "Eli Lilly (LLY)": 8,
                    "AMD": 7,
                    "Global X Lithium (LIT)": 5,
                    "Bitcoin ETF (BITO)": 3,
                    "iShares Emerging Markets (EEM)": 2
                },
                expected_return=13.5,
                std_deviation=28.2,
                variance=7.95,
                sharpe_ratio=0.44,
                characteristics="Alto crecimiento y tecnología. Exposición a criptomonedas. Mercados emergentes. Alta volatilidad."
            )
        }

    def calculate_score(self, answers: Dict[int, str]) -> Tuple[int, RiskProfile]:
        total_score = 0
        breakdown = {"a": 0, "b": 0, "c": 0}
        
        for question_id, answer in answers.items():
            question = next(q for q in self.questions if q.id == question_id)
            option = next(opt for opt in question.options if opt["value"] == answer)
            total_score += option["points"]
            breakdown[answer] += 1
        
        for profile in self.risk_profiles.values():
            if isinstance(profile.score, tuple):
                if profile.score[0] <= total_score <= profile.score[1]:
                    return total_score, profile, breakdown
        
        return total_score, self.risk_profiles["conservador"], breakdown

    def get_recommended_portfolio(self, risk_aversion_a: float) -> Portfolio:
        if risk_aversion_a >= 4.5:
            return self.portfolios["conservador"]
        elif risk_aversion_a >= 3.0:
            return self.portfolios["moderado"]
        else:
            return self.portfolios["agresivo"]

def get_claude_analysis(profile, portfolio):
    try:
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        
        prompt = f"""
        Basándote en la teoría moderna de portafolios y el documento de Markowitz sobre asignación de capital, analiza la siguiente información del inversionista:

        PERFIL DEL INVERSIONISTA:
        - Tipo: {profile.profile_name}
        - Coeficiente de aversión al riesgo (A): {profile.risk_aversion_a}
        - Descripción: {profile.description}

        PORTAFOLIO RECOMENDADO:
        - Nombre: {portfolio.name}
        - Rendimiento esperado: {portfolio.expected_return}%
        - Desviación estándar: {portfolio.std_deviation}%
        - Ratio de Sharpe: {portfolio.sharpe_ratio}
        - Características: {portfolio.characteristics}

        Proporciona un análisis conciso (máximo 200 palabras) que incluya:
        1. Por qué este portafolio es adecuado para su coeficiente A
        2. Ventajas y riesgos principales
        3. Recomendación de seguimiento

        Usa un tono profesional pero accesible.
        """
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    except Exception as e:
        return f"Análisis no disponible temporalmente. Error: {str(e)}"

def main():
    st.markdown('<h1 class="main-header">📈 Calculadora de Tolerancia al Riesgo</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Determina tu coeficiente de aversión al riesgo y recibe tu portafolio personalizado</p>', unsafe_allow_html=True)
    
    calculator = RiskToleranceCalculator()
    
    with st.sidebar:
        st.header("ℹ️ Información")
        st.markdown("""
        ### ¿Qué es el Coeficiente A?
        
        El coeficiente de aversión al riesgo (A) determina tu portafolio ideal:
        
        - **A = 5.0**: Conservador
        - **A = 3.5**: Moderado  
        - **A = 2.0**: Agresivo
        
        ### Análisis con IA
        Utilizamos Claude AI para analizar tu perfil y recomendar el portafolio óptimo basado en la teoría de Markowitz.
        """)

    st.subheader("Cuestionario de Tolerancia al Riesgo")
    st.markdown("Responde las siguientes preguntas para determinar tu perfil de riesgo:")
    
    answers = {}
    
    for i, question in enumerate(calculator.questions):
        st.markdown(f'<div class="question-container">', unsafe_allow_html=True)
        st.markdown(f"**Pregunta {i+1}:** {question.text}")
        
        options_text = [f"{opt['value'].upper()}. {opt['text']}" for opt in question.options]
        selected = st.radio(
            f"Selecciona tu respuesta:",
            options=options_text,
            key=f"q_{question.id}",
            index=None
        )
        
        if selected:
            answers[question.id] = selected[0].lower()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if len(answers) == len(calculator.questions):
        if st.button("🎯 Obtener Mi Portafolio Recomendado", type="primary", use_container_width=True):
            score, profile, breakdown = calculator.calculate_score(answers)
            recommended_portfolio = calculator.get_recommended_portfolio(profile.risk_aversion_a)
            
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.subheader("🎯 Tu Perfil de Inversionista")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Puntuación", f"{score} puntos")
            with col2:
                st.metric("Perfil", profile.profile_name.replace("Inversionista ", ""))
            with col3:
                st.metric("Coeficiente A", f"{profile.risk_aversion_a}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="portfolio-container">', unsafe_allow_html=True)
            st.subheader(f"📊 {recommended_portfolio.name}")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                composition_df = pd.DataFrame([
                    {"Activo": asset, "Porcentaje": percentage}
                    for asset, percentage in recommended_portfolio.composition.items()
                ])
                
                fig = px.pie(composition_df, values='Porcentaje', names='Activo',
                           title="Composición del Portafolio")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Rendimiento Esperado", f"{recommended_portfolio.expected_return}%")
                st.metric("Desviación Estándar", f"{recommended_portfolio.std_deviation}%")
                st.metric("Varianza", f"{recommended_portfolio.variance}%")
                st.metric("Ratio de Sharpe", f"{recommended_portfolio.sharpe_ratio}")
            
            st.markdown("### 🎯 Características del Portafolio")
            st.write(recommended_portfolio.characteristics)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.spinner("🤖 Generando análisis personalizado con IA..."):
                claude_analysis = get_claude_analysis(profile, recommended_portfolio)
                
                st.markdown("### 🤖 Análisis Personalizado")
                st.markdown(f"""
                <div style="background-color: #f0f8ff; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #4a90e2;">
                    {claude_analysis}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info(f"📝 Completa todas las preguntas ({len(answers)}/{len(calculator.questions)})")

if __name__ == "__main__":
    main()