import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass
from typing import Dict, List, Tuple

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
.metric-card {
    background-color: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
}
.formula-box {
    background-color: #f0f8ff;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #4a90e2;
    margin: 1rem 0;
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

    def calculate_score(self, answers: Dict[int, str]) -> Tuple[int, RiskProfile]:
        total_score = 0
        breakdown = {"a": 0, "b": 0, "c": 0}
        
        for question_id, answer in answers.items():
            question = next(q for q in self.questions if q.id == question_id)
            option = next(opt for opt in question.options if opt["value"] == answer)
            total_score += option["points"]
            breakdown[answer] += 1
        
        # Determinar perfil de riesgo
        for profile in self.risk_profiles.values():
            if isinstance(profile.score, tuple):
                if profile.score[0] <= total_score <= profile.score[1]:
                    return total_score, profile, breakdown
        
        # Default a conservador si no encuentra match
        return total_score, self.risk_profiles["conservador"], breakdown

def main():
    st.markdown('<h1 class="main-header">📈 Calculadora de Tolerancia al Riesgo</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Determina tu coeficiente de aversión al riesgo (A) basado en la teoría moderna de portafolios</p>', unsafe_allow_html=True)
    
    # Inicializar calculator
    calculator = RiskToleranceCalculator()
    
    # Sidebar con información
    with st.sidebar:
        st.header("ℹ️ Información")
        st.markdown("""
        ### ¿Qué es el Coeficiente A?
        
        El coeficiente de aversión al riesgo (A) es un parámetro que mide qué tanto un inversionista evita el riesgo.
        
        **Valores típicos:**
        - **A = 2.0**: Agresivo
        - **A = 3.5**: Moderado  
        - **A = 5.0**: Conservador
        
        ### Fórmula de Asignación Óptima
        ```
        y* = [E(rp) - rf] / (A × σp²)
        ```
        
        Donde:
        - y* = proporción óptima en activo riesgoso
        - E(rp) = rendimiento esperado del portafolio
        - rf = tasa libre de riesgo
        - σp² = varianza del portafolio
        """)
        
        st.markdown("---")
        st.markdown("**Desarrollado con:**")
        st.markdown("🐍 Python + Streamlit")
        st.markdown("📊 Plotly para visualizaciones")
        st.markdown("📚 Teoría de Markowitz")

    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["🔍 Cuestionario", "📊 Resultados", "🧮 Calculadora"])
    
    with tab1:
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
        
        # Guardar respuestas en session state
        st.session_state.answers = answers
        
        # Botón para calcular
        if len(answers) == len(calculator.questions):
            if st.button("🎯 Calcular Mi Perfil de Riesgo", type="primary", use_container_width=True):
                score, profile, breakdown = calculator.calculate_score(answers)
                st.session_state.score = score
                st.session_state.profile = profile
                st.session_state.breakdown = breakdown
                st.success("✅ ¡Perfil calculado! Ve a la pestaña 'Resultados' para ver tu análisis completo.")
        else:
            st.info(f"📝 Completa todas las preguntas ({len(answers)}/{len(calculator.questions)})")
    
    with tab2:
        if 'score' in st.session_state:
            score = st.session_state.score
            profile = st.session_state.profile
            breakdown = st.session_state.breakdown
            
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.subheader("🎯 Tu Perfil de Inversionista")
            
            # Métricas principales
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Puntuación Total", f"{score} puntos")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Perfil", profile.profile_name)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Coeficiente A", f"{profile.risk_aversion_a}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Descripción del perfil
            st.markdown(f"""
            <div style="background-color: {profile.color}20; padding: 1rem; border-radius: 10px; border-left: 4px solid {profile.color}; margin: 1rem 0;">
                <h4 style="color: {profile.color}; margin: 0 0 0.5rem 0;">{profile.profile_name}</h4>
                <p style="margin: 0; color: #333;">{profile.description}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Gráfico de barras con breakdown
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📊 Desglose de Respuestas")
                breakdown_df = pd.DataFrame({
                    'Opción': ['A (Conservador)', 'B (Moderado)', 'C (Agresivo)'],
                    'Cantidad': [breakdown['a'], breakdown['b'], breakdown['c']],
                    'Puntos': [breakdown['a'] * 1, breakdown['b'] * 2, breakdown['c'] * 3],
                    'Color': ['#dc3545', '#ffc107', '#28a745']
                })
                
                fig = px.bar(breakdown_df, x='Opción', y='Cantidad', 
                           color='Color', color_discrete_map='identity',
                           title="Distribución de Respuestas")
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("🎭 Comparación de Perfiles")
                profiles_data = []
                for p in calculator.risk_profiles.values():
                    profiles_data.append({
                        'Perfil': p.profile_name.replace('Inversionista ', ''),
                        'Coeficiente A': p.risk_aversion_a,
                        'Tu Perfil': p.profile_name == profile.profile_name
                    })
                
                profiles_df = pd.DataFrame(profiles_data)
                fig2 = px.bar(profiles_df, x='Perfil', y='Coeficiente A',
                            color='Tu Perfil', 
                            color_discrete_map={True: profile.color, False: '#e0e0e0'},
                            title="Tu Posición vs Otros Perfiles")
                fig2.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Fórmula y explicación
            st.markdown('<div class="formula-box">', unsafe_allow_html=True)
            st.markdown("### 🧮 Fórmula de Asignación Óptima")
            st.latex(r"y^* = \frac{E(r_p) - r_f}{A \times \sigma_p^2}")
            st.markdown(f"**Con tu coeficiente A = {profile.risk_aversion_a}**, podrás calcular la proporción óptima de tu portafolio.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.info("🔍 Primero completa el cuestionario en la pestaña anterior para ver tus resultados.")
    
    with tab3:
        st.subheader("🧮 Calculadora de Asignación Óptima")
        st.markdown("*Próximamente: Calculadora completa con parámetros de mercado*")
        
        if 'profile' in st.session_state:
            profile = st.session_state.profile
            st.info(f"Tu coeficiente de aversión al riesgo: **A = {profile.risk_aversion_a}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                expected_return = st.number_input("Rendimiento Esperado del Portafolio (%)", 
                                               min_value=0.0, max_value=50.0, value=15.0, step=0.1)
                risk_free_rate = st.number_input("Tasa Libre de Riesgo (%)", 
                                               min_value=0.0, max_value=20.0, value=5.0, step=0.1)
            
            with col2:
                std_deviation = st.number_input("Desviación Estándar del Portafolio (%)", 
                                              min_value=0.1, max_value=100.0, value=20.0, step=0.1)
                
            if st.button("📊 Calcular Asignación Óptima"):
                # Convertir porcentajes a decimales
                E_rp = expected_return / 100
                rf = risk_free_rate / 100
                sigma_p = std_deviation / 100
                A = profile.risk_aversion_a
                
                # Calcular y*
                y_optimal = (E_rp - rf) / (A * sigma_p ** 2)
                
                # Mostrar resultados
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Proporción en Activo Riesgoso", f"{y_optimal:.1%}")
                with col2:
                    st.metric("Proporción en Activo Libre de Riesgo", f"{(1-y_optimal):.1%}")
                with col3:
                    st.metric("Ratio de Sharpe", f"{(E_rp - rf) / sigma_p:.3f}")
                
                # Interpretación
                if y_optimal > 1:
                    st.warning("⚠️ La asignación óptima sugiere apalancamiento (>100% en activos riesgosos)")
                elif y_optimal < 0:
                    st.error("❌ La asignación sugiere venta en corto del activo riesgoso")
                else:
                    st.success(f"✅ Asignación balanceada: {y_optimal:.1%} riesgoso, {(1-y_optimal):.1%} libre de riesgo")
        else:
            st.info("🔍 Completa primero el cuestionario para obtener tu coeficiente A.")

if __name__ == "__main__":
    main()