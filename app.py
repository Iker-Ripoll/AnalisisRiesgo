import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json
from anthropic import Anthropic
from io import StringIO
import time

# Configuración de página
st.set_page_config(
    page_title="Asesor de Inversión Personalizado",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar inicialmente colapsado
)

# ----- DEFINICIÓN DE CONSTANTES Y DATOS -----

# Definir los portafolios disponibles
PORTFOLIOS = {
    "Conservador": {
        "assets": {
            "TLT": 0.20,  # iShares 20+ Year Treasury Bond ETF
            "LQD": 0.20,  # iShares iBoxx $ Investment Grade Corporate Bond ETF
            "MSFT": 0.15, # Microsoft
            "JNJ": 0.10,  # Johnson & Johnson
            "KO": 0.10,   # The Coca-Cola Company
            "PG": 0.10,   # Procter & Gamble
            "VYM": 0.10,  # Vanguard High Dividend Yield ETF
            "AAPL": 0.05, # Apple
        },
        "expected_return": 0.058,
        "standard_deviation": 0.084,
        "variance": 0.0071,
        "sharpe_ratio": 0.45,
        "description": "Este portafolio presenta una varianza muy baja debido a una alta proporción de bonos (40%) y acciones de baja volatilidad. Es ideal para inversores conservadores, cercanos a la jubilación o con baja tolerancia al riesgo. Prioriza la preservación del capital y la generación de ingresos sobre el crecimiento."
    },
    "Moderado": {
        "assets": {
            "LQD": 0.15,   # iShares iBoxx $ Investment Grade Corporate Bond ETF
            "IEF": 0.10,   # iShares 7-10 Year Treasury Bond ETF
            "AAPL": 0.15,  # Apple
            "MSFT": 0.15,  # Microsoft
            "GOOGL": 0.10, # Alphabet
            "LLY": 0.10,   # Eli Lilly
            "JPM": 0.08,   # JPMorgan Chase
            "VTI": 0.07,   # Vanguard Total Stock Market ETF
            "EFA": 0.05,   # iShares MSCI EAFE ETF
            "AMZN": 0.05,  # Amazon
        },
        "expected_return": 0.087,
        "standard_deviation": 0.146,
        "variance": 0.0213,
        "sharpe_ratio": 0.53,
        "description": "La varianza de este portafolio es moderada debido al balance entre activos de renta fija (25%) y renta variable (75%). Incluye una mezcla de acciones de crecimiento y valor con diversificación entre sectores. Adecuado para inversores con horizonte de medio a largo plazo (5-15 años) que buscan un crecimiento razonable con volatilidad controlada."
    },
    "Agresivo": {
        "assets": {
            "NVDA": 0.25,  # NVIDIA
            "TSLA": 0.15,  # Tesla
            "QQQ": 0.15,   # Invesco QQQ Trust
            "AAPL": 0.10,  # Apple
            "ARKK": 0.10,  # ARK Innovation ETF
            "LLY": 0.08,   # Eli Lilly
            "AMD": 0.07,   # Advanced Micro Devices
            "LIT": 0.05,   # Global X Lithium & Battery Tech ETF
            "BITO": 0.03,  # Bitcoin ETF
            "EEM": 0.02,   # iShares MSCI Emerging Markets ETF
        },
        "expected_return": 0.135,
        "standard_deviation": 0.282,
        "variance": 0.0795,
        "sharpe_ratio": 0.44,
        "description": "Este portafolio presenta una alta varianza debido a su concentración en activos de alto crecimiento y tecnología. Es adecuado para inversores con alto horizonte temporal (>15 años) y alta tolerancia al riesgo. Busca maximizar el crecimiento a largo plazo aceptando una volatilidad significativa a corto plazo."
    }
}

# Información detallada de los activos
ASSET_INFO = {
    "TLT": {
        "name": "iShares 20+ Year Treasury Bond ETF",
        "description": "ETF que sigue el rendimiento de los bonos del Tesoro de EE.UU. con vencimientos superiores a 20 años. Ofrece exposición a la deuda pública a largo plazo con respaldo del gobierno estadounidense.",
        "type": "Bonos",
        "risk": "Bajo"
    },
    "LQD": {
        "name": "iShares iBoxx $ Investment Grade Corporate Bond ETF",
        "description": "ETF que sigue bonos corporativos de grado de inversión en dólares estadounidenses. Proporciona exposición a deuda de alta calidad emitida por empresas estadounidenses.",
        "type": "Bonos",
        "risk": "Bajo-Medio"
    },
    "IEF": {
        "name": "iShares 7-10 Year Treasury Bond ETF",
        "description": "ETF que sigue el rendimiento de los bonos del Tesoro de EE.UU. con vencimientos entre 7 y 10 años. Ofrece una duración intermedia con respaldo del gobierno estadounidense.",
        "type": "Bonos",
        "risk": "Bajo"
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "description": "Líder mundial en software, servicios en la nube (Azure), y hardware. Sus ingresos provienen principalmente de software empresarial, servicios en la nube, y productos como Xbox y Surface.",
        "type": "Tecnología",
        "risk": "Medio"
    },
    "JNJ": {
        "name": "Johnson & Johnson",
        "description": "Empresa diversificada de atención médica con operaciones en productos farmacéuticos, dispositivos médicos y productos de consumo. Conocida por su estabilidad y dividendos consistentes.",
        "type": "Salud",
        "risk": "Bajo-Medio"
    },
    "KO": {
        "name": "The Coca-Cola Company",
        "description": "Empresa líder mundial en bebidas no alcohólicas. Posee más de 200 marcas y opera en más de 200 países. Conocida por su estabilidad y dividendos crecientes durante décadas.",
        "type": "Consumo Básico",
        "risk": "Bajo"
    },
    "PG": {
        "name": "Procter & Gamble",
        "description": "Multinacional de bienes de consumo con marcas líderes en productos de higiene personal, limpieza del hogar y cuidado personal. Conocida por su estabilidad y dividendos crecientes.",
        "type": "Consumo Básico",
        "risk": "Bajo"
    },
    "VYM": {
        "name": "Vanguard High Dividend Yield ETF",
        "description": "ETF que sigue acciones de empresas que pagan dividendos relativamente altos. Proporciona exposición a empresas establecidas con flujos de efectivo estables.",
        "type": "Renta Variable (Dividendos)",
        "risk": "Medio"
    },
    "AAPL": {
        "name": "Apple Inc.",
        "description": "Empresa tecnológica líder en diseño y fabricación de dispositivos electrónicos de consumo, software y servicios en línea. Conocida por iPhone, Mac, iPad y servicios como Apple Music y iCloud.",
        "type": "Tecnología",
        "risk": "Medio"
    },
    "GOOGL": {
        "name": "Alphabet Inc. (Google)",
        "description": "Conglomerado tecnológico multinacional propietario de Google. Sus ingresos provienen principalmente de publicidad digital, pero también invierte en IA, computación en la nube y otros proyectos.",
        "type": "Tecnología",
        "risk": "Medio"
    },
    "LLY": {
        "name": "Eli Lilly and Company",
        "description": "Empresa farmacéutica global que desarrolla y comercializa medicamentos para diversas condiciones médicas. Conocida por sus tratamientos para la diabetes, oncología y medicamentos para la obesidad.",
        "type": "Salud",
        "risk": "Medio"
    },
    "JPM": {
        "name": "JPMorgan Chase & Co.",
        "description": "Banco multinacional y empresa de servicios financieros. Es uno de los bancos más grandes del mundo por activos y opera en banca de inversión, comercial y de consumo.",
        "type": "Financiero",
        "risk": "Medio"
    },
    "VTI": {
        "name": "Vanguard Total Stock Market ETF",
        "description": "ETF que sigue el rendimiento de todo el mercado de valores de EE.UU., incluyendo empresas de pequeña, mediana y gran capitalización. Ofrece amplia diversificación.",
        "type": "Renta Variable (Diversificado)",
        "risk": "Medio"
    },
    "EFA": {
        "name": "iShares MSCI EAFE ETF",
        "description": "ETF que sigue acciones de mercados desarrollados fuera de Norteamérica. Incluye empresas de Europa, Australasia y Lejano Oriente.",
        "type": "Renta Variable (Internacional)",
        "risk": "Medio-Alto"
    },
    "AMZN": {
        "name": "Amazon.com, Inc.",
        "description": "Empresa de tecnología y comercio electrónico. Sus negocios incluyen tienda online, AWS (servicios en la nube), entretenimiento digital y dispositivos inteligentes.",
        "type": "Tecnología/Consumo Discrecional",
        "risk": "Medio-Alto"
    },
    "NVDA": {
        "name": "NVIDIA Corporation",
        "description": "Empresa de tecnología especializada en el diseño de GPU, chips para IA y plataformas computacionales. Líder en soluciones para centros de datos, gaming y vehículos autónomos.",
        "type": "Tecnología (Semiconductores)",
        "risk": "Alto"
    },
    "TSLA": {
        "name": "Tesla, Inc.",
        "description": "Empresa de vehículos eléctricos, energía limpia y tecnología. Diseña y fabrica automóviles eléctricos, baterías para el hogar y soluciones de energía solar.",
        "type": "Consumo Discrecional/Tecnología",
        "risk": "Alto"
    },
    "QQQ": {
        "name": "Invesco QQQ Trust",
        "description": "ETF que sigue el índice Nasdaq-100, que incluye las 100 empresas no financieras más grandes que cotizan en el Nasdaq. Alta concentración en tecnología.",
        "type": "Renta Variable (Tecnología)",
        "risk": "Alto"
    },
    "ARKK": {
        "name": "ARK Innovation ETF",
        "description": "ETF gestionado activamente que invierte en empresas disruptivas e innovadoras en áreas como genómica, automatización, IA, fintech y tecnologías emergentes.",
        "type": "Renta Variable (Innovación)",
        "risk": "Muy Alto"
    },
    "AMD": {
        "name": "Advanced Micro Devices, Inc.",
        "description": "Empresa de semiconductores que diseña y produce microprocesadores, chipsets y soluciones gráficas. Compite con Intel y NVIDIA en varios segmentos.",
        "type": "Tecnología (Semiconductores)",
        "risk": "Alto"
    },
    "LIT": {
        "name": "Global X Lithium & Battery Tech ETF",
        "description": "ETF que invierte en la cadena de valor completa del litio, desde la minería hasta la producción de baterías. Exposición al crecimiento de vehículos eléctricos.",
        "type": "Renta Variable (Sectorial)",
        "risk": "Alto"
    },
    "BITO": {
        "name": "ProShares Bitcoin Strategy ETF",
        "description": "ETF que invierte en contratos de futuros de Bitcoin. Proporciona exposición al precio del Bitcoin sin necesidad de poseer directamente la criptomoneda.",
        "type": "Activo Alternativo (Cripto)",
        "risk": "Muy Alto"
    },
    "EEM": {
        "name": "iShares MSCI Emerging Markets ETF",
        "description": "ETF que sigue acciones de mercados emergentes como China, India, Brasil y otros. Ofrece exposición a economías en desarrollo con alto potencial de crecimiento.",
        "type": "Renta Variable (Mercados Emergentes)",
        "risk": "Alto"
    }
}

# Cuestionario para determinar la aversión al riesgo
RISK_QUESTIONS = [
    {
        "id": 1,
        "question": "¿Cuál es su principal objetivo al invertir?",
        "options": [
            {"text": "Preservar el capital y evitar pérdidas", "score": 1},
            {"text": "Generar ingresos estables (dividendos, intereses)", "score": 2},
            {"text": "Crecimiento moderado con riesgo controlado", "score": 3},
            {"text": "Maximizar el crecimiento, aceptando alta volatilidad", "score": 4}
        ]
    },
    {
        "id": 2,
        "question": "¿Cuál es su horizonte de inversión?",
        "options": [
            {"text": "Menos de 3 años", "score": 1},
            {"text": "Entre 3 y 7 años", "score": 2},
            {"text": "Entre 7 y 15 años", "score": 3},
            {"text": "Más de 15 años", "score": 4}
        ]
    },
    {
        "id": 3,
        "question": "Imagínese que su inversión ha caído un 20% en tres meses. ¿Cuál sería su reacción más probable?",
        "options": [
            {"text": "Vender todo inmediatamente para evitar más pérdidas", "score": 1},
            {"text": "Vender una parte y mantener el resto", "score": 2},
            {"text": "No hacer nada y esperar que se recupere", "score": 3},
            {"text": "Invertir más aprovechando los precios más bajos", "score": 4}
        ]
    },
    {
        "id": 4,
        "question": "¿Qué afirmación describe mejor su conocimiento sobre inversiones?",
        "options": [
            {"text": "Tengo muy poco conocimiento sobre inversiones", "score": 1},
            {"text": "Entiendo los conceptos básicos de acciones, bonos y fondos", "score": 2},
            {"text": "Tengo buen conocimiento y experiencia previa invirtiendo", "score": 3},
            {"text": "Tengo conocimientos avanzados y experiencia inversora", "score": 4}
        ]
    },
    {
        "id": 5,
        "question": "Para un portafolio de inversión a largo plazo, ¿qué alternativa preferiría?",
        "options": [
            {"text": "100% en inversiones de bajo riesgo (bonos, fondos monetarios)", "score": 1},
            {"text": "70% bajo riesgo, 30% alto riesgo", "score": 2},
            {"text": "30% bajo riesgo, 70% alto riesgo", "score": 3},
            {"text": "100% en inversiones de alto riesgo (acciones crecimiento, criptomonedas)", "score": 4}
        ]
    },
    {
        "id": 6,
        "question": "Si tuviera que elegir entre estas opciones de inversión, ¿cuál preferiría?",
        "options": [
            {"text": "5% de rendimiento anual garantizado", "score": 1},
            {"text": "50% probabilidad de ganar 10% y 50% de ganar 2%", "score": 2},
            {"text": "50% probabilidad de ganar 15% y 50% de perder 3%", "score": 3},
            {"text": "50% probabilidad de ganar 25% y 50% de perder 10%", "score": 4}
        ]
    },
    {
        "id": 7,
        "question": "¿Qué proporción de sus ahorros totales planea invertir en estos portafolios?",
        "options": [
            {"text": "Menos del 20% de mis ahorros", "score": 1},
            {"text": "Entre 20% y 40% de mis ahorros", "score": 2},
            {"text": "Entre 40% y 60% de mis ahorros", "score": 3},
            {"text": "Más del 60% de mis ahorros", "score": 4}
        ]
    },
    {
        "id": 8,
        "question": "Si su inversión aumenta un 30% en un mes, ¿qué haría?",
        "options": [
            {"text": "Vender todo para asegurar las ganancias", "score": 1},
            {"text": "Vender una parte para recuperar la inversión inicial", "score": 2},
            {"text": "No hacer nada y mantener la inversión", "score": 3},
            {"text": "Invertir más en el mismo portafolio", "score": 4}
        ]
    },
    {
        "id": 9,
        "question": "¿Cuál es su fuente principal de ingresos?",
        "options": [
            {"text": "Ingresos variables o sin empleo estable", "score": 1},
            {"text": "Empleo estable pero sin potencial de crecimiento significativo", "score": 2},
            {"text": "Empleo estable con potencial de crecimiento", "score": 3},
            {"text": "Múltiples fuentes de ingresos o negocio propio estable", "score": 4}
        ]
    },
    {
        "id": 10,
        "question": "¿Qué porcentaje de pérdida en el valor de su portafolio podría tolerar en un año sin vender?",
        "options": [
            {"text": "Menos del 5%", "score": 1},
            {"text": "Entre 5% y 15%", "score": 2},
            {"text": "Entre 15% y 30%", "score": 3},
            {"text": "Más del 30%", "score": 4}
        ]
    }
]

# ----- FUNCIONES DE UTILIDAD -----

# Función para obtener datos en tiempo real
@st.cache_data(ttl=60)  # Actualiza cada minuto
def get_real_time_data(tickers):
    """Obtiene datos de precios en tiempo real para un conjunto de tickers."""
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d", interval="1m")
            if not hist.empty:
                data[ticker] = {
                    "price": hist['Close'].iloc[-1],
                    "change": (hist['Close'].iloc[-1] - hist['Open'].iloc[0]) / hist['Open'].iloc[0] * 100
                }
            else:
                data[ticker] = {"price": 0, "change": 0}
        except Exception as e:
            st.warning(f"No se pudieron obtener datos para {ticker}: {e}")
            data[ticker] = {"price": 0, "change": 0}
    return data

@st.cache_data(ttl=86400)  # Actualiza cada día
def get_historical_data(tickers, period="1mo"):
    """Obtiene datos históricos para análisis y gráficos."""
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if not hist.empty:
                data[ticker] = hist['Close']
        except Exception as e:
            st.warning(f"No se pudieron obtener datos históricos para {ticker}: {e}")
    return pd.DataFrame(data)

# Función para calcular el coeficiente de aversión al riesgo
def calculate_risk_aversion(responses):
    """
    Calcula el coeficiente de aversión al riesgo (A) basado en las respuestas.
    Convierte los puntajes en una escala de 1-4 a un coeficiente de aversión al riesgo de 1-6.
    Un puntaje alto indica baja aversión al riesgo, por lo que invertimos la escala.
    """
    # Sumar todas las puntuaciones
    total_score = sum(responses)
    
    # Puntaje mínimo posible (10) y máximo posible (40)
    min_score = len(responses)
    max_score = len(responses) * 4
    
    # Normalizar a escala A (1-6)
    # Invertimos la escala porque un puntaje alto indica baja aversión al riesgo
    normalized_score = 6 - 5 * ((total_score - min_score) / (max_score - min_score))
    
    return round(normalized_score, 2)

# Función para consultar a Claude y analizar el perfil
def analyze_with_claude(responses, api_key):
    """
    Envía los resultados del cuestionario a Claude para análisis y recomendación de portafolio.
    """
    client = Anthropic(api_key=api_key)
    
    # Calcular coeficiente de aversión al riesgo
    risk_aversion = calculate_risk_aversion(responses)
    
    # Preparar el prompt para Claude
    prompt = f"""
    Soy un experto en finanzas analizando los resultados de un cuestionario de perfil de riesgo. 
    Basándome en la Teoría Moderna de Portafolios, voy a recomendar un portafolio de inversión.
    
    Resultados del cuestionario (puntajes 1-4, donde 1 es más conservador y 4 más agresivo):
    {responses}
    
    El coeficiente de aversión al riesgo (A) calculado es: {risk_aversion} en una escala de 1-6
    (donde 1 indica baja aversión al riesgo y 6 alta aversión al riesgo).
    
    Tengo disponibles tres portafolios:
    
    1. Conservador:
       - Rendimiento esperado: 5.8%
       - Desviación estándar: 8.4%
       - Varianza: 0.71%
       - Ratio de Sharpe: 0.45
    
    2. Moderado:
       - Rendimiento esperado: 8.7%
       - Desviación estándar: 14.6%
       - Varianza: 2.13%
       - Ratio de Sharpe: 0.53
    
    3. Agresivo:
       - Rendimiento esperado: 13.5%
       - Desviación estándar: 28.2%
       - Varianza: 7.95%
       - Ratio de Sharpe: 0.44
    
    Usando la fórmula de utilidad U = E(r) - ½Aσ² (donde E(r) es el rendimiento esperado y σ² es la varianza),
    determinaré cuál de estos portafolios maximiza la utilidad del inversor dado su coeficiente de aversión al riesgo.
    
    También calcularé la asignación óptima entre el portafolio riesgoso recomendado y un activo libre de riesgo
    con un rendimiento actual del 4%.
    
    Por favor, proporciona:
    1. Los cálculos de utilidad para cada portafolio
    2. El portafolio recomendado basado en el mayor valor de utilidad
    3. La asignación óptima entre el portafolio riesgoso y el activo libre de riesgo
    4. Una explicación breve y clara de por qué este portafolio es adecuado para el perfil del inversor
    
    Formato de respuesta:
    ```json
    {
      "portfolio_utilities": {
        "Conservador": [valor],
        "Moderado": [valor],
        "Agresivo": [valor]
      },
      "recommended_portfolio": "[nombre]",
      "optimal_allocation": [valor decimal entre 0 y 1],
      "explanation": "[explicación]"
    }
    ```
    
    Proporciona solo el JSON como respuesta, sin texto adicional.
    """
    
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0,
            system="Eres un asesor financiero experto que analiza perfiles de riesgo y recomienda portafolios óptimos basados en principios de economía financiera.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        result = response.content[0].text
        try:
            # Extraer el JSON de la respuesta
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0]
            else:
                json_str = result
            return json.loads(json_str)
        except Exception as e:
            st.error(f"Error al parsear la respuesta de Claude: {e}")
            st.error(f"Respuesta original: {result}")
            return None
    except Exception as e:
        st.error(f"Error al comunicarse con la API de Claude: {e}")
        return None

# Función para obtener análisis de un activo específico mediante Claude
def get_asset_analysis(ticker, api_key):
    """Obtiene un análisis detallado de un activo usando Claude."""
    client = Anthropic(api_key=api_key)
    
    asset_info = ASSET_INFO.get(ticker, {"name": ticker})
    
    prompt = f"""
    Proporciona un breve análisis de inversión para {ticker} ({asset_info.get('name', '')}). 
    
    Incluye:
    1. Panorama general actual del activo (1-2 oraciones)
    2. Principales fortalezas (1-2 puntos clave)
    3. Principales riesgos (1-2 puntos clave)
    4. Perspectiva a corto y mediano plazo (1 oración)
    
    Mantén la respuesta concisa y enfocada en información útil para inversores.
    """
    
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            temperature=0.2,
            system="Eres un analista financiero experto que proporciona información breve, objetiva y valiosa sobre instrumentos de inversión.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"No se pudo obtener el análisis: {str(e)}"

# ----- MANEJO DE SECRETOS -----

# Función para configurar la API key
def setup_api_key():
    """Configura la API key de Claude desde el archivo .streamlit/secrets.toml o desde input."""
    # Intentamos obtener la API key desde secrets
    if 'api_key' not in st.session_state:
        try:
            # Primero intentamos obtener de secrets.toml
            st.session_state.api_key = st.secrets["CLAUDE_API_KEY"]
        except:
            # Si no está en secrets, pedimos al usuario
            if 'temp_api_key' not in st.session_state:
                st.session_state.temp_api_key = ""
            
            api_key = st.sidebar.text_input(
                "Introduce tu API key de Claude:",
                value=st.session_state.temp_api_key,
                type="password",
                help="Para proteger tu API key, crear un archivo .streamlit/secrets.toml con CLAUDE_API_KEY='tu-api-key'"
            )
            
            if api_key:
                st.session_state.temp_api_key = api_key
                st.session_state.api_key = api_key
    
    return 'api_key' in st.session_state

# ----- APLICACIÓN PRINCIPAL -----

def main():
    # Configuración inicial del estado de sesión
    if 'page' not in st.session_state:
        st.session_state.page = 'questionnaire'  # Comenzamos directamente con el cuestionario
    if 'responses' not in st.session_state:
        st.session_state.responses = []
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'investment_amount' not in st.session_state:
        st.session_state.investment_amount = 10000
    if 'csv_generated' not in st.session_state:
        st.session_state.csv_generated = False
    
    # Configurar API key
    api_key_available = setup_api_key()
    
    # Botón para volver al cuestionario (en sidebar)
    if st.session_state.page != 'questionnaire':
        if st.sidebar.button("Volver al cuestionario"):
            st.session_state.page = 'questionnaire'
            st.session_state.responses = []
            st.session_state.analysis_result = None
            st.session_state.csv_generated = False
            st.experimental_rerun()
    
    # ----- PÁGINA: CUESTIONARIO -----
    if st.session_state.page == 'questionnaire':
        st.title("Cuestionario de Perfil de Riesgo de Inversión")
        
        st.markdown("""
        Por favor, responda las siguientes preguntas para determinar su perfil de riesgo como inversionista.
        Sus respuestas serán analizadas para recomendarle el portafolio más adecuado según su tolerancia al riesgo.
        """)
        
        # Formulario del cuestionario
        with st.form("risk_profile_form"):
            responses = []
            
            for i, q in enumerate(RISK_QUESTIONS):
                st.subheader(f"Pregunta {i+1}: {q['question']}")
                
                # Crear opciones de radio para cada pregunta
                options = [option["text"] for option in q["options"]]
                scores = [option["score"] for option in q["options"]]
                
                answer = st.radio(
                    f"Seleccione una opción:",
                    options,
                    key=f"q_{i}"
                )
                
                if answer:
                    idx = options.index(answer)
                    score = scores[idx]
                    responses.append(score)
                else:
                    responses.append(None)
            
            # Botón de envío
            submitted = st.form_submit_button("Enviar respuestas")
            
            if submitted:
                # Verificar que todas las preguntas fueron respondidas
                if None in responses:
                    st.error("Por favor, responda todas las preguntas antes de continuar.")
                elif not api_key_available:
                    st.error("Es necesario proporcionar una API key de Claude para analizar los resultados.")
                else:
                    st.session_state.responses = responses
                    
                    # Crear CSV con los resultados
                    results_df = pd.DataFrame({
                        'pregunta': [f"Pregunta {i+1}" for i in range(len(responses))],
                        'puntuacion': responses,
                        'timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * len(responses)
                    })
                    
                    # Guardar CSV
                    csv = results_df.to_csv(index=False)
                    
                    # Preparar para descargar
                    csv_str = StringIO()
                    results_df.to_csv(csv_str, index=False)
                    csv_str = csv_str.getvalue()
                    
                    # Descargar CSV automáticamente
                    st.download_button(
                        label="Descargar resultados (CSV)",
                        data=csv_str,
                        file_name=f"perfil_riesgo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_csv"
                    )
                    
                    st.session_state.csv_generated = True
                    
                    # Analizar con Claude
                    with st.spinner("Analizando su perfil de riesgo..."):
                        analysis_result = analyze_with_claude(responses, st.session_state.api_key)
                        
                        if analysis_result:
                            st.session_state.analysis_result = analysis_result
                            st.session_state.page = 'portfolio'
                            st.experimental_rerun()
                        else:
                            st.error("No se pudieron analizar los resultados. Por favor, intente nuevamente.")
    
    # ----- PÁGINA: PORTAFOLIO RECOMENDADO -----
    elif st.session_state.page == 'portfolio':
        if not st.session_state.analysis_result:
            st.error("No hay resultados de análisis disponibles. Por favor, complete el cuestionario.")
            st.session_state.page = 'questionnaire'
            st.experimental_rerun()
        else:
            analysis = st.session_state.analysis_result
            recommended = analysis["recommended_portfolio"]
            portfolio = PORTFOLIOS[recommended]
            
            st.title(f"Su Portafolio Recomendado: {recommended}")
            
            # Mostrar información del portafolio
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.subheader("Análisis de su Perfil de Riesgo")
                
                # Calcular coeficiente de aversión al riesgo
                risk_aversion = calculate_risk_aversion(st.session_state.responses)
                
                st.markdown(f"""
                **Coeficiente de Aversión al Riesgo (A):** {risk_aversion}
                
                **Portafolio Recomendado:** {recommended}
                
                **Utilidades Calculadas:**
                - Conservador: {analysis["portfolio_utilities"]["Conservador"]:.4f}
                - Moderado: {analysis["portfolio_utilities"]["Moderado"]:.4f}
                - Agresivo: {analysis["portfolio_utilities"]["Agresivo"]:.4f}
                
                **Asignación Óptima:** {analysis["optimal_allocation"]*100:.1f}% en el portafolio de riesgo y {(1-analysis["optimal_allocation"])*100:.1f}% en activos libres de riesgo
                
                **Características del Portafolio:**
                - Rendimiento Esperado Anual: {portfolio["expected_return"]*100:.1f}%
                - Desviación Estándar: {portfolio["standard_deviation"]*100:.1f}%
                - Ratio de Sharpe: {portfolio["sharpe_ratio"]:.2f}
                
                **Explicación:** {analysis["explanation"]}
                """)
            
            with col2:
                # Gráfico de comparación de portafolios
                st.subheader("Comparación de Portafolios")
                
                # Datos para el gráfico
                portfolios_data = {
                    'Portafolio': ['Conservador', 'Moderado', 'Agresivo'],
                    'Rendimiento': [PORTFOLIOS['Conservador']['expected_return']*100, 
                                   PORTFOLIOS['Moderado']['expected_return']*100, 
                                   PORTFOLIOS['Agresivo']['expected_return']*100],
                    'Riesgo': [PORTFOLIOS['Conservador']['standard_deviation']*100, 
                              PORTFOLIOS['Moderado']['standard_deviation']*100, 
                              PORTFOLIOS['Agresivo']['standard_deviation']*100],
                    'Utilidad': [analysis["portfolio_utilities"]["Conservador"],
                                analysis["portfolio_utilities"]["Moderado"],
                                analysis["portfolio_utilities"]["Agresivo"]]
                }
                
                # Resaltar el portafolio recomendado
                colors = ['lightgrey', 'lightgrey', 'lightgrey']
                if recommended == 'Conservador':
                    colors[0] = 'darkgreen'
                elif recommended == 'Moderado':
                    colors[1] = 'darkgreen'
                else:
                    colors[2] = 'darkgreen'
                
                # Crear gráfico de riesgo vs rendimiento
                fig = px.scatter(
                    portfolios_data, 
                    x='Riesgo', 
                    y='Rendimiento', 
                    size='Utilidad',
                    color='Portafolio',
                    size_max=20,
                    text='Portafolio',
                    title='Riesgo vs Rendimiento',
                    labels={'Riesgo': 'Riesgo (Desviación Estándar %)', 'Rendimiento': 'Rendimiento Esperado (%)'}
                )
                
                # Personalizar gráfico
                fig.update_traces(marker=dict(opacity=0.7), selector=dict(mode='markers'))
                fig.update_layout(height=400)
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Ingresar monto de inversión
            st.subheader("Simulación de Inversión")
            
            investment_amount = st.number_input(
                "Ingrese el monto a invertir (USD):",
                min_value=1000,
                max_value=10000000,
                value=st.session_state.investment_amount,
                step=1000,
                format="%d"
            )
            
            st.session_state.investment_amount = investment_amount
            
            if st.button("Ver Detalles del Portafolio"):
                st.session_state.page = 'details'
                st.experimental_rerun()
    
    # ----- PÁGINA: DETALLES DEL PORTAFOLIO -----
    elif st.session_state.page == 'details':
        if not st.session_state.analysis_result:
            st.error("No hay resultados de análisis disponibles. Por favor, complete el cuestionario.")
            st.session_state.page = 'questionnaire'
            st.experimental_rerun()
        else:
            analysis = st.session_state.analysis_result
            recommended = analysis["recommended_portfolio"]
            portfolio = PORTFOLIOS[recommended]
            assets = portfolio["assets"]
            investment_amount = st.session_state.investment_amount
            
            st.title(f"Detalles del Portafolio {recommended}")
            
            # Obtener datos en tiempo real
            with st.spinner("Obteniendo datos de mercado en tiempo real..."):
                real_time_data = get_real_time_data(list(assets.keys()))
            
            # Gráficos y análisis
            col1, col2 = st.columns([2, 3])
            
            with col1:
                st.subheader("Asignación de Activos")
                
                # Gráfico circular de asignación
                fig = px.pie(
                    names=list(assets.keys()),
                    values=list(assets.values()),
                    title=f"Distribución del Portafolio (Total: ${investment_amount:,.2f})",
                    hover_data=[f"${investment_amount * weight:,.2f}" for weight in assets.values()],
                    labels={'names': 'Activo', 'values': 'Porcentaje'},
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=500)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Mostrar asignación óptima
                st.info(f"""
                **Recomendación de asignación:**
                - {analysis["optimal_allocation"]*100:.1f}% (${investment_amount * analysis["optimal_allocation"]:,.2f}) en este portafolio de riesgo
                - {(1-analysis["optimal_allocation"])*100:.1f}% (${investment_amount * (1-analysis["optimal_allocation"]):,.2f}) en activos libres de riesgo
                """)
            
            with col2:
                st.subheader("Rendimiento en Tiempo Real")
                
                # Tabla con datos en tiempo real
                data_table = []
                
                for ticker, weight in assets.items():
                    ticker_data = real_time_data.get(ticker, {"price": 0, "change": 0})
                    investment = weight * investment_amount
                    actual_value = investment * (1 + ticker_data["change"]/100)
                    gain_loss = actual_value - investment
                    
                    data_table.append({
                        "Activo": ticker,
                        "Ticker": ticker,
                        "Inversión": f"${investment:,.2f}",
                        "Precio Actual": f"${ticker_data['price']:,.2f}",
                        "Cambio (%)": f"{ticker_data['change']:.2f}%",
                        "Valor Actual": f"${actual_value:,.2f}",
                        "Ganancia/Pérdida": f"${gain_loss:,.2f}",
                        "Peso (%)": f"{weight*100:.1f}%",
                        "Tipo": ASSET_INFO.get(ticker, {}).get("type", ""),
                        "Riesgo": ASSET_INFO.get(ticker, {}).get("risk", "")
                    })
                
                # Calcular totales
                total_investment = investment_amount
                total_current = sum([weight * investment_amount * (1 + real_time_data.get(ticker, {"change": 0})["change"]/100) for ticker, weight in assets.items()])
                total_gain_loss = total_current - total_investment
                total_change = (total_gain_loss / total_investment) * 100
                
                # Convertir a DataFrame
                df = pd.DataFrame(data_table)
                
                # Mostrar tabla
                st.dataframe(df, hide_index=True)
                
                # Mostrar resumen
                st.metric(
                    label="Valor Total del Portafolio", 
                    value=f"${total_current:,.2f}", 
                    delta=f"${total_gain_loss:,.2f} ({total_change:.2f}%)"
                )
            
            # Lista de activos con descripciones
            st.subheader("Detalles de los Activos")
            
            # Crear tabs para cada activo
            tabs = st.tabs([f"{ticker} - {ASSET_INFO.get(ticker, {}).get('name', ticker)}" for ticker in assets.keys()])
            
            for i, (ticker, tab) in enumerate(zip(assets.keys(), tabs)):
                with tab:
                    asset_info = ASSET_INFO.get(ticker, {})
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown(f"""
                        ### {asset_info.get('name', ticker)}
                        
                        **Tipo:** {asset_info.get('type', 'N/A')}
                        
                        **Nivel de Riesgo:** {asset_info.get('risk', 'N/A')}
                        
                        **Descripción:**
                        {asset_info.get('description', 'No hay descripción disponible.')}
                        
                        **Inversión en este activo:** ${investment_amount * assets[ticker]:,.2f} ({assets[ticker]*100:.1f}% del portafolio)
                        """)
                    
                    with col2:
                        # Análisis del activo con Claude
                        if api_key_available:
                            analysis_placeholder = st.empty()
                            analysis_placeholder.info("Obteniendo análisis del activo...")
                            
                            try:
                                asset_analysis = get_asset_analysis(ticker, st.session_state.api_key)
                                analysis_placeholder.markdown(f"""
                                **Análisis del Activo:**
                                
                                {asset_analysis}
                                """)
                            except Exception as e:
                                analysis_placeholder.warning(f"No se pudo obtener análisis: {e}")
                        else:
                            st.warning("Proporcione una API key de Claude para obtener análisis detallado de este activo.")
                        
                        # Datos históricos
                        try:
                            stock = yf.Ticker(ticker)
                            hist = stock.history(period="6mo")
                            
                            if not hist.empty:
                                fig = px.line(
                                    hist, 
                                    y='Close',
                                    title=f'Precio histórico de {ticker} (últimos 6 meses)',
                                    labels={'Close': 'Precio de cierre', 'Date': 'Fecha'}
                                )
                                fig.update_layout(showlegend=False, height=300)
                                st.plotly_chart(fig, use_container_width=True)
                        except:
                            st.warning(f"No se pudieron obtener datos históricos para {ticker}")
            
            # Botón para ir a la simulación
            if st.button("Ver Simulación de Rendimiento"):
                st.session_state.page = 'simulation'
                st.experimental_rerun()
    
    # ----- PÁGINA: SIMULACIÓN DE RENDIMIENTO -----
    elif st.session_state.page == 'simulation':
        if not st.session_state.analysis_result:
            st.error("No hay resultados de análisis disponibles. Por favor, complete el cuestionario.")
            st.session_state.page = 'questionnaire'
            st.experimental_rerun()
        else:
            analysis = st.session_state.analysis_result
            recommended = analysis["recommended_portfolio"]
            portfolio = PORTFOLIOS[recommended]
            investment_amount = st.session_state.investment_amount
            
            st.title(f"Simulación de Rendimiento del Portafolio {recommended}")
            
            # Opciones de simulación
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.subheader("Parámetros de Simulación")
                
                simulation_years = st.slider("Horizonte de inversión (años):", 1, 20, 5)
                simulation_days = simulation_years * 365
                
                confidence_level = st.slider("Nivel de confianza (%):", 70, 99, 95)
                
                st.markdown(f"""
                **Parámetros del Portafolio:**
                
                - Rendimiento Esperado Anual: {portfolio["expected_return"]*100:.1f}%
                - Desviación Estándar Anual: {portfolio["standard_deviation"]*100:.1f}%
                - Inversión Inicial: ${investment_amount:,.2f}
                - Horizonte: {simulation_years} años
                """)
                
                st.info(f"""
                **Estimaciones:**
                
                - Valor Esperado al final del periodo: ${investment_amount * (1 + portfolio["expected_return"])**simulation_years:,.2f}
                - Rendimiento Total Esperado: {((1 + portfolio["expected_return"])**simulation_years - 1) * 100:.1f}%
                """)
                
                if st.button("Ejecutar Nueva Simulación"):
                    st.experimental_rerun()
            
            with col2:
                st.subheader("Proyección de Rendimiento")
                
                # Simulación de rendimiento
                np.random.seed(42)  # Para reproducibilidad
                
                # Simulación de Monte Carlo
                num_simulations = 1000
                simulation_results = []
                
                # Parámetros anualizados
                annual_return = portfolio["expected_return"]
                annual_std = portfolio["standard_deviation"]
                
                # Parámetros diarios
                daily_return = annual_return/252
                daily_std = annual_std/np.sqrt(252)
                
                for _ in range(num_simulations):
                    # Generar rendimientos diarios
                    daily_returns = np.random.normal(daily_return, daily_std, simulation_days)
                    
                    # Calcular valor del portafolio a lo largo del tiempo
                    portfolio_value = [investment_amount]
                    for r in daily_returns:
                        portfolio_value.append(portfolio_value[-1] * (1 + r))
                    
                    simulation_results.append(portfolio_value)
                
                # Calcular percentiles
                df_simulation = pd.DataFrame(simulation_results).T
                df_simulation['mean'] = df_simulation.mean(axis=1)
                df_simulation['median'] = df_simulation.median(axis=1)
                df_simulation['lower'] = df_simulation.quantile(0.5 - confidence_level/200, axis=1)
                df_simulation['upper'] = df_simulation.quantile(0.5 + confidence_level/200, axis=1)
                
                # Crear gráfico de simulación
                fig = go.Figure()
                
                # Añadir área de confianza
                fig.add_trace(
                    go.Scatter(
                        x=list(range(simulation_days + 1)),
                        y=df_simulation['upper'],
                        fill=None,
                        mode='lines',
                        line=dict(color='rgba(0,100,80,0.2)'),
                        name=f'Límite superior ({confidence_level}%)'
                    )
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=list(range(simulation_days + 1)),
                        y=df_simulation['lower'],
                        fill='tonexty',
                        mode='lines',
                        line=dict(color='rgba(0,100,80,0.2)'),
                        name=f'Límite inferior ({confidence_level}%)'
                    )
                )
                
                # Añadir línea de valor esperado
                fig.add_trace(
                    go.Scatter(
                        x=list(range(simulation_days + 1)),
                        y=df_simulation['mean'],
                        mode='lines',
                        line=dict(color='rgb(0,100,80)', width=2),
                        name='Valor Esperado'
                    )
                )
                
                # Configurar diseño
                fig.update_layout(
                    title=f'Simulación de Monte Carlo ({num_simulations} simulaciones)',
                    xaxis_title='Días',
                    yaxis_title='Valor del Portafolio ($)',
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01
                    ),
                    height=500
                )
                
                # Configurar ejes
                fig.update_xaxes(
                    tickvals=[0, simulation_days/4, simulation_days/2, simulation_days*3/4, simulation_days],
                    ticktext=[
                        'Inicio',
                        f'{simulation_years/4:.1f} años',
                        f'{simulation_years/2:.1f} años',
                        f'{simulation_years*3/4:.1f} años',
                        f'{simulation_years} años'
                    ]
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Mostrar métricas clave
                final_values = df_simulation.iloc[-1]
                
                st.subheader("Resultados de la Simulación")
                
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                
                with metrics_col1:
                    st.metric(
                        label="Valor Esperado Final", 
                        value=f"${final_values['mean']:,.2f}",
                        delta=f"{(final_values['mean']/investment_amount - 1)*100:.1f}%"
                    )
                
                with metrics_col2:
                    st.metric(
                        label=f"Mejor Escenario ({(100-confidence_level)/2:.1f}%)", 
                        value=f"${final_values['upper']:,.2f}",
                        delta=f"{(final_values['upper']/investment_amount - 1)*100:.1f}%"
                    )
                
                with metrics_col3:
                    st.metric(
                        label=f"Peor Escenario ({(100-confidence_level)/2:.1f}%)", 
                        value=f"${final_values['lower']:,.2f}",
                        delta=f"{(final_values['lower']/investment_amount - 1)*100:.1f}%"
                    )

if __name__ == "__main__":
    main()