import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import anthropic

# Configuración de la página
st.set_page_config(
    page_title="Portfolio Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS estilo Apple
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* Header Navigation */
    .nav-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        padding: 1rem 0;
        margin: -1rem -1rem 3rem -1rem;
        position: sticky;
        top: 0;
        z-index: 1000;
    }
    
    .nav-content {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 0 2rem;
    }
    
    .nav-item {
        display: inline-block;
        margin: 0 2rem;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        cursor: pointer;
        border: none;
        background: transparent;
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .nav-item:not(.active) {
        color: #8e8e93;
        background: rgba(142, 142, 147, 0.1);
    }
    
    .nav-item:not(.active):hover {
        background: rgba(142, 142, 147, 0.2);
        transform: translateY(-2px);
    }
    
    /* Main Content */
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1d1d1f 0%, #667eea 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1rem;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        font-weight: 400;
        color: #6d6d70;
        text-align: center;
        margin-bottom: 4rem;
        line-height: 1.4;
    }
    
    /* Question Styling */
    .question-wrapper {
        margin: 3rem 0;
    }
    
    .question-text {
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem;
        font-weight: 600;
        color: #1d1d1f;
        margin-bottom: 2rem;
        text-align: center;
        line-height: 1.3;
    }
    
    .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        align-items: center;
    }
    
    .stRadio > div > label {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(0, 0, 0, 0.05);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        width: 100%;
        max-width: 600px;
        transition: all 0.3s ease;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 500;
        color: #1d1d1f;
        position: relative;
    }
    
    .stRadio > div > label:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Selected radio button styling */
    .stRadio > div > label[data-baseweb="radio"] > div:first-child > div[data-testid="stMarkdownContainer"] {
        display: none;
    }
    
    /* Hide default radio button */
    .stRadio > div > label > div:first-child {
        display: none !important;
    }
    
    /* Selected state for radio options */
    .stRadio > div > label:has(input:checked) {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-color: #667eea;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
        transform: translateY(-2px);
    }
    
    /* Alternative approach for selected state */
    .stRadio div[role="radiogroup"] label[data-baseweb="radio"] {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(0, 0, 0, 0.05);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        width: 100%;
        max-width: 600px;
        transition: all 0.3s ease;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 500;
        color: #1d1d1f;
    }
    
    .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .stRadio div[role="radiogroup"] input[type="radio"]:checked + div {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        border: 2px solid #667eea !important;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.25) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Primary Button */
    .primary-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 25px;
        color: white;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 1rem 3rem;
        margin: 3rem auto;
        display: block;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .primary-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.4);
    }
    
    /* Progress Bar */
    .progress-container {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 25px;
        height: 8px;
        margin: 2rem auto;
        max-width: 400px;
        overflow: hidden;
    }
    
    .progress-bar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        border-radius: 25px;
        transition: width 0.3s ease;
    }
    
    /* Result Cards */
    .result-hero {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 3rem;
        margin: 3rem 0;
        text-align: center;
        border: 1px solid rgba(0, 0, 0, 0.05);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
    }
    
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
    }
    
    .metric-value {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
        color: #8e8e93;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* AI Analysis */
    .ai-analysis {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 250, 0.95) 100%);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 3rem;
        margin: 3rem 0;
        border: 1px solid rgba(102, 126, 234, 0.1);
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.1);
    }
    
    .ai-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #1d1d1f;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .ai-content {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 400;
        color: #1d1d1f;
        line-height: 1.6;
        text-align: center;
    }
    
    /* Asset Cards */
    .asset-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .asset-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .asset-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
    }
    
    .asset-name {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: #1d1d1f;
        margin-bottom: 0.5rem;
    }
    
    .asset-description {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 400;
        color: #6d6d70;
        line-height: 1.5;
        margin-bottom: 1rem;
    }
    
    .asset-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 1rem;
    }
    
    .asset-sector {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
        color: #8e8e93;
    }
    
    .asset-percentage {
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Investment Input */
    .investment-section {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 3rem;
        margin: 3rem 0;
        text-align: center;
        border: 1px solid rgba(0, 0, 0, 0.05);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
    }
    
    /* Portfolio Monitor */
    .portfolio-header {
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .performance-positive {
        color: #30d158;
        font-weight: 700;
    }
    
    .performance-negative {
        color: #ff453a;
        font-weight: 700;
    }
    
    /* Portfolio Status Section */
    .portfolio-status {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 3rem;
        margin: 2rem 0;
        border: 1px solid rgba(0, 0, 0, 0.05);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
    }
    
    .status-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #1d1d1f;
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .status-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .status-card {
        background: rgba(248, 249, 250, 0.8);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        text-align: center;
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .status-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
    }
    
    .status-value {
        font-family: 'Inter', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }
    
    .status-label {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: #6d6d70;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .status-change {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    /* Positions Section */
    .positions-section {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 3rem;
        margin: 3rem 0;
        border: 1px solid rgba(0, 0, 0, 0.05);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
    }
    
    .positions-title {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #1d1d1f;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .positions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1.5rem;
    }
    
    .position-card {
        background: rgba(248, 249, 250, 0.9);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .position-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
    }
    
    .position-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .position-symbol {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: #1d1d1f;
    }
    
    .position-allocation {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .position-name {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
        color: #8e8e93;
        margin-bottom: 1rem;
    }
    
    .position-metrics {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }
    
    .position-metric {
        text-align: center;
    }
    
    .position-metric-value {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #1d1d1f;
        margin-bottom: 0.25rem;
    }
    
    .position-metric-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        font-weight: 500;
        color: #8e8e93;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Charts Section */
    .charts-section {
        margin: 3rem 0;
    }
    
    .chart-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 2rem 0;
        border: 1px solid rgba(0, 0, 0, 0.05);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
    }
    
    .chart-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #1d1d1f;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Plotly customization */
    .js-plotly-plot {
        border-radius: 20px;
        overflow: hidden;
    }
    
    /* Hide Streamlit elements */
    .stDeployButton {
        display: none;
    }
    
    #MainMenu {
        visibility: hidden;
    }
    
    footer {
        visibility: hidden;
    }
    
    header {
        visibility: hidden;
    }
    
    .stNumberInput > div > div > input {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 12px;
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        text-align: center;
        padding: 1rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 25px;
        color: white;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 1rem 3rem;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.4);
    }
    
    /* Radio button selection fix */
    div[data-testid="stRadio"] > div {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        align-items: center;
    }
    
    div[data-testid="stRadio"] > div > label {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(20px);
        border: 2px solid rgba(0, 0, 0, 0.05) !important;
        border-radius: 16px !important;
        padding: 1.5rem 2rem !important;
        width: 100% !important;
        max-width: 600px !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        color: #1d1d1f !important;
    }
    
    div[data-testid="stRadio"] > div > label:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
        border-color: rgba(102, 126, 234, 0.3) !important;
    }
    
    div[data-testid="stRadio"] > div > label[data-checked="true"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%) !important;
        border: 2px solid #667eea !important;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.25) !important;
        transform: translateY(-2px) !important;
    }
    
    div[data-testid="stRadio"] label > div:first-child {
        display: none !important;
    }
    
    div[data-testid="stRadio"] input[type="radio"] {
        display: none !important;
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

def render_navigation():
    pages = {
        "questionnaire": "Evaluación",
        "results": "Análisis", 
        "portfolio": "Portafolio"
    }
    
    nav_html = '<div class="nav-container"><div class="nav-content">'
    
    for page_key, page_name in pages.items():
        active_class = "active" if st.session_state.get("page", "questionnaire") == page_key else ""
        nav_html += f'<button class="nav-item {active_class}" onclick="window.parent.postMessage({{type: \'streamlit:setComponentValue\', value: \'{page_key}\'}}, \'*\')">{page_name}</button>'
    
    nav_html += '</div></div>'
    st.markdown(nav_html, unsafe_allow_html=True)

def page_questionnaire():
    st.markdown("""
    <div class="main-container">
        <h1 class="hero-title">Portfolio Intelligence</h1>
        <p class="hero-subtitle">Descubre tu perfil de inversión ideal a través de nuestro análisis avanzado</p>
    </div>
    """, unsafe_allow_html=True)
    
    questionnaire = QuestionnaireSystem()
    answers = {}
    
    with st.container():
        for question in questionnaire.questions:
            st.markdown(f"""
            <div class="main-container">
                <div class="question-wrapper">
                    <div class="question-text">{question['text']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            options = [opt["text"] for opt in question["options"]]
            selected = st.radio(
                "",
                options,
                key=f"q_{question['id']}",
                index=None,
                label_visibility="collapsed"
            )
            
            if selected:
                for opt in question["options"]:
                    if opt["text"] == selected:
                        answers[question["id"]] = opt["value"]
                        break
    
    progress = len(answers) / len(questionnaire.questions)
    
    st.markdown(f"""
    <div class="main-container">
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress * 100}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if len(answers) == len(questionnaire.questions):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Analizar Perfil", type="primary", use_container_width=True):
                risk_score = questionnaire.calculate_risk_score(answers)
                st.session_state.risk_score = risk_score
                st.session_state.page = "results"
                st.rerun()
    else:
        st.markdown(f"""
        <div class="main-container" style="text-align: center; margin: 3rem 0;">
            <p style="font-family: 'Inter', sans-serif; font-size: 1.1rem; color: #8e8e93;">
                Progreso: {len(answers)}/{len(questionnaire.questions)} preguntas completadas
            </p>
        </div>
        """, unsafe_allow_html=True)

def page_results():
    if "risk_score" not in st.session_state:
        st.warning("Complete primero el cuestionario de evaluación")
        return
    
    portfolio_manager = PortfolioManager()
    portfolio = portfolio_manager.get_portfolio_by_risk_score(st.session_state.risk_score)
    
    st.markdown("""
    <div class="main-container">
        <h1 class="hero-title">Tu Perfil de Inversión</h1>
        <p class="hero-subtitle">Análisis personalizado basado en inteligencia artificial</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas principales
    st.markdown(f"""
    <div class="main-container">
        <div class="result-hero">
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-value">{st.session_state.risk_score:.1f}</div>
                    <div class="metric-label">Puntuación de Riesgo</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{portfolio['expected_return']}%</div>
                    <div class="metric-label">Rendimiento Esperado</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{portfolio['std_deviation']}%</div>
                    <div class="metric-label">Volatilidad</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Análisis con IA
    with st.spinner(""):
        claude_analysis = get_claude_analysis(st.session_state.risk_score, portfolio)
        
        st.markdown(f"""
        <div class="main-container">
            <div class="ai-analysis">
                <div class="ai-title">Recomendación de Experto</div>
                <div class="ai-content">{claude_analysis}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Composición del portafolio
    st.markdown(f"""
    <div class="main-container">
        <h2 style="font-family: 'Inter', sans-serif; font-size: 2.2rem; font-weight: 700; color: #1d1d1f; text-align: center; margin: 3rem 0 2rem 0;">{portfolio['name']}</h2>
        <div class="asset-grid">
    """, unsafe_allow_html=True)
    
    for asset_code, asset_info in portfolio["assets"].items():
        st.markdown(f"""
            <div class="asset-card">
                <div class="asset-name">{asset_info['name']} ({asset_code})</div>
                <div class="asset-description">{asset_info['description']}</div>
                <div class="asset-meta">
                    <div class="asset-sector">{asset_info['sector']} • {asset_info['risk_level']}</div>
                    <div class="asset-percentage">{asset_info['percentage']}%</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Configuración de inversión
    st.markdown("""
    <div class="main-container">
        <div class="investment-section">
            <h3 style="font-family: 'Inter', sans-serif; font-size: 1.8rem; font-weight: 700; color: #1d1d1f; margin-bottom: 2rem;">Configurar Inversión</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        investment_amount = st.number_input(
            "Monto a invertir (USD)",
            min_value=1000,
            max_value=10000000,
            value=10000,
            step=1000,
            format="%d",
            label_visibility="collapsed"
        )
        
        if st.button("Proceder con el Análisis", type="primary", use_container_width=True):
            st.session_state.investment_amount = investment_amount
            st.session_state.selected_portfolio = portfolio
            st.session_state.page = "portfolio"
            st.rerun()

def page_portfolio():
    if "selected_portfolio" not in st.session_state:
        st.warning("Configure primero su portafolio en la sección anterior")
        return
    
    portfolio = st.session_state.selected_portfolio
    investment_amount = st.session_state.investment_amount
    portfolio_manager = PortfolioManager()
    
    performance_data = portfolio_manager.generate_performance_data(portfolio)
    
    # Cálculos de rendimiento
    current_value = investment_amount * (performance_data["portfolio_values"][-1] / 100)
    total_return = current_value - investment_amount
    total_return_pct = (current_value / investment_amount - 1) * 100
    
    st.markdown("""
    <div class="main-container portfolio-header">
        <h1 class="hero-title">Monitor de Portafolio</h1>
        <p class="hero-subtitle">Seguimiento en tiempo real de su inversión</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. ESTADO DEL PORTAFOLIO GENERAL (MEJORADO)
    performance_class = "performance-positive" if total_return_pct >= 0 else "performance-negative"
    daily_class = "performance-positive" if performance_data["current_portfolio_change"] >= 0 else "performance-negative"
    ytd_class = "performance-positive" if performance_data["ytd_portfolio_change"] >= 0 else "performance-negative"
    
    st.markdown(f"""
    <div class="main-container">
        <div class="portfolio-status">
            <div class="status-title">Estado del Portafolio</div>
            <div class="status-grid">
                <div class="status-card">
                    <div class="status-value">${current_value:,.0f}</div>
                    <div class="status-label">Valor Total</div>
                </div>
                <div class="status-card">
                    <div class="status-value">${investment_amount:,.0f}</div>
                    <div class="status-label">Inversión Inicial</div>
                </div>
                <div class="status-card">
                    <div class="status-value ${total_return:+,.0f}</div>
                    <div class="status-label">Ganancia/Pérdida</div>
                    <div class="status-change {performance_class}">{total_return_pct:+.3f}%</div>
                </div>
                <div class="status-card">
                    <div class="status-value {daily_class}">{performance_data["current_portfolio_change"]:+.3f}%</div>
                    <div class="status-label">Cambio Diario</div>
                </div>
                <div class="status-card">
                    <div class="status-value {ytd_class}">{performance_data["ytd_portfolio_change"]:+.3f}%</div>
                    <div class="status-label">Rendimiento Anual</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. POSICIONES ABIERTAS
    st.markdown("""
    <div class="main-container">
        <div class="positions-section">
            <div class="positions-title">Posiciones Abiertas</div>
            <div class="positions-grid">
    """, unsafe_allow_html=True)
    
    for asset_code, asset_info in portfolio["assets"].items():
        asset_data = performance_data["asset_data"][asset_code]
        asset_investment = investment_amount * (asset_info["percentage"] / 100)
        current_asset_value = asset_investment * (asset_data["values"][-1] / 100)
        asset_return = current_asset_value - asset_investment
        
        change_class = "performance-positive" if asset_data["ytd_change"] >= 0 else "performance-negative"
        daily_change_class = "performance-positive" if asset_data["current_change"] >= 0 else "performance-negative"
        
        st.markdown(f"""
                <div class="position-card">
                    <div class="position-header">
                        <div class="position-symbol">{asset_code}</div>
                        <div class="position-allocation">{asset_info['percentage']}%</div>
                    </div>
                    <div class="position-name">{asset_info['name']}</div>
                    <div class="position-metrics">
                        <div class="position-metric">
                            <div class="position-metric-value">${current_asset_value:,.0f}</div>
                            <div class="position-metric-label">Valor Actual</div>
                        </div>
                        <div class="position-metric">
                            <div class="position-metric-value ${asset_return:+,.0f}</div>
                            <div class="position-metric-label">P&L</div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
                        <span style="font-family: 'Inter', sans-serif; font-size: 0.9rem; color: #8e8e93;">Diario:</span>
                        <span class="{daily_change_class}" style="font-family: 'Inter', sans-serif; font-size: 0.9rem; font-weight: 600;">{asset_data['current_change']:+.2f}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-family: 'Inter', sans-serif; font-size: 0.9rem; color: #8e8e93;">Anual:</span>
                        <span class="{change_class}" style="font-family: 'Inter', sans-serif; font-size: 0.9rem; font-weight: 600;">{asset_data['ytd_change']:+.2f}%</span>
                    </div>
                </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. GRÁFICA CIRCULAR MODERNA CON COLORES VIBRANTES
    asset_names = []
    asset_values = []
    # Colores más vibrantes y menos pastel
    asset_colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C', '#E67E22', '#34495E', '#F1C40F']
    
    for i, (asset_code, asset_info) in enumerate(portfolio["assets"].items()):
        asset_investment = investment_amount * (asset_info["percentage"] / 100)
        current_asset_value = asset_investment * (performance_data["asset_data"][asset_code]["values"][-1] / 100)
        
        asset_names.append(asset_code)
        asset_values.append(current_asset_value)
    
    fig_donut = go.Figure(data=[go.Pie(
        labels=asset_names,
        values=asset_values,
        hole=0.6,
        textinfo='label+percent',
        textposition='auto',
        marker=dict(
            colors=asset_colors[:len(asset_names)],
            line=dict(color='#FFFFFF', width=4)
        ),
        textfont=dict(
            family="Inter",
            size=14,
            color="white"
        ),
        hovertemplate='<b>%{label}</b><br>Valor: $%{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>'
    )])
    
    fig_donut.add_annotation(
        text=f"<b>Total</b><br>${current_value:,.0f}",
        x=0.5, y=0.5,
        font_size=22,
        font_family="Inter",
        font_color="#1d1d1f",
        showarrow=False
    )
    
    fig_donut.update_layout(
        showlegend=False,
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=40, l=40, r=40),
        font=dict(family="Inter")
    )
    
    st.markdown("""
    <div class="main-container">
        <div class="chart-container">
            <div class="chart-title">Distribución del Portafolio</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.plotly_chart(fig_donut, use_container_width=True)
    
    # 4. GRÁFICA HISTÓRICA DEL PORTAFOLIO
    portfolio_values_scaled = [investment_amount * (val / 100) for val in performance_data["portfolio_values"]]
    
    fig_portfolio = go.Figure()
    
    # Área de relleno
    fig_portfolio.add_trace(go.Scatter(
        x=performance_data["dates"],
        y=portfolio_values_scaled,
        fill='tonexty',
        mode='none',
        fillcolor='rgba(52, 152, 219, 0.15)',
        name='Área'
    ))
    
    # Línea principal
    fig_portfolio.add_trace(go.Scatter(
        x=performance_data["dates"],
        y=portfolio_values_scaled,
        mode='lines',
        name='Valor del Portafolio',
        line=dict(
            color='#3498DB',
            width=4,
            shape='spline',
            smoothing=0.3
        ),
        hovertemplate='<b>Fecha:</b> %{x}<br><b>Valor:</b> $%{y:,.0f}<extra></extra>'
    ))
    
    # Línea de inversión inicial
    fig_portfolio.add_hline(
        y=investment_amount,
        line_dash="dash",
        line_color="#95A5A6",
        line_width=3,
        annotation_text="Inversión Inicial",
        annotation_position="top right"
    )
    
    fig_portfolio.update_layout(
        title={
            'text': "Evolución Histórica del Portafolio",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'family': 'Inter', 'size': 24, 'color': '#1d1d1f'}
        },
        xaxis_title="",
        yaxis_title="Valor (USD)",
        hovermode='x unified',
        showlegend=False,
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12),
        margin=dict(t=80, b=60, l=80, r=60)
    )
    
    fig_portfolio.update_xaxes(
        gridcolor='rgba(0,0,0,0.1)',
        showline=False,
        tickfont=dict(color='#8e8e93')
    )
    fig_portfolio.update_yaxes(
        gridcolor='rgba(0,0,0,0.1)',
        showline=False,
        tickformat='$,.0f',
        tickfont=dict(color='#8e8e93')
    )
    
    st.markdown("""
    <div class="main-container">
        <div class="chart-container">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.plotly_chart(fig_portfolio, use_container_width=True)

def main():
    # Inicializar navegación
    if "page" not in st.session_state:
        st.session_state.page = "questionnaire"
    
    # Renderizar navegación
    render_navigation()
    
    # Renderizar página actual
    if st.session_state.page == "questionnaire":
        page_questionnaire()
    elif st.session_state.page == "results":
        page_results()
    elif st.session_state.page == "portfolio":
        page_portfolio()

if __name__ == "__main__":
    main()