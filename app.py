import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import httpx
import json

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Asesor de Inversión", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    body { background-color: #ffffff; color: #000000; }
    .main { background-color: #ffffff; }
    h1, h2, h3 { color: #1DA1F2; }
    .stButton>button { background-color: #1DA1F2; color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("💼 Asesor de Inversión Personalizado")

# --- API KEY y PROMPT COMPLETO PARA CLAUDE ---
API_KEY = "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"


PROMPT_CLAUDE = """
PROMPT PARA ANÁLISIS DE RESULTADOS DEL CUESTIONARIO DE PERFIL DE INVERSIÓN
Como analista experto en riesgos de inversión con más de 20 años de experiencia, tu misión es analizar detalladamente las respuestas proporcionadas por el cliente en el cuestionario de perfil de riesgo e inversión. Basándote en esta información, determinarás:

El perfil de riesgo del cliente (bajo, medio o alto)
La capacidad de inversión del cliente (baja, media o alta)
El portafolio óptimo entre los 9 disponibles (combinación de nivel de riesgo y cantidad de inversión)

METODOLOGÍA DE ANÁLISIS:
SISTEMA DE PUNTUACIÓN
Asigna puntos a cada respuesta según la siguiente estructura general:

Respuestas conservadoras/adversas al riesgo: 1-2 puntos
Respuestas moderadas/equilibradas: 3-4 puntos
Respuestas agresivas/propensas al riesgo: 5-6 puntos

Para categorías específicas, aplica la siguiente ponderación sobre el total de puntos posibles:

Sección 1 (Datos Personales y Situación Financiera): 20%
Sección 2 (Experiencia y Conocimientos): 15%
Sección 3 (Tolerancia al Riesgo): 25%
Sección 4 (Objetivos de Inversión): 15%
Sección 5 (Circunstancias Personales): 10%
Sección 6 (Factores Psicológicos): 10%
Sección 7 (Capacidad Financiera): 5%

EVALUACIÓN DEL PERFIL DE RIESGO
Factores Objetivos (60% del peso total)

Edad y horizonte temporal
Experiencia y conocimiento financiero
Respuestas directas sobre preferencias de riesgo
Objetivos financieros establecidos
Situación financiera actual

Factores Psicológicos y Comportamentales (40% del peso total)

Reacciones ante pérdidas o crisis
Comportamiento en escenarios hipotéticos
Sesgos psicológicos identificados
Consistencia en las respuestas relacionadas con riesgo
Actitud general hacia la incertidumbre

Determinación del Nivel de Riesgo

Nivel de Riesgo Bajo: 0-40% del total de puntos ponderados
Nivel de Riesgo Medio: 41-70% del total de puntos ponderados
Nivel de Riesgo Alto: 71-100% del total de puntos ponderados

EVALUACIÓN DE LA CAPACIDAD DE INVERSIÓN
Factores Determinantes (porcentajes equitativos)

Ingresos actuales
Patrimonio total y porcentaje destinado a inversión
Estabilidad laboral y de ingresos
Nivel de endeudamiento
Capacidad de ahorro mensual
Fondo de emergencia existente
Obligaciones financieras
Necesidades de liquidez
Expectativas de ingresos futuros

Determinación de la Capacidad de Inversión

Capacidad de Inversión Baja: 0-40% del total de puntos ponderados
Capacidad de Inversión Media: 41-70% del total de puntos ponderados
Capacidad de Inversión Alta: 71-100% del total de puntos ponderados

ANÁLISIS DE CONSISTENCIA
Realiza un análisis de consistencia entre las respuestas para identificar:

Contradicciones entre tolerancia al riesgo declarada y comportamiento real
Discrepancias entre objetivos y horizonte temporal
Incoherencias entre capacidad financiera y expectativas de rendimiento
Sesgos comportamentales que puedan afectar las decisiones de inversión

BANDERAS ROJAS A DETECTAR
Identifica posibles banderas rojas como:

Expectativas irrealistas de rendimiento
Necesidad de liquidez incompatible con objetivos
Exceso de confianza en conocimientos financieros
Aversión extrema o propensión excesiva al riesgo
Situación financiera precaria (alto endeudamiento, sin fondo de emergencia)
Inconsistencia significativa en las respuestas

RECOMENDACIÓN DE PORTAFOLIO
Matriz de Selección de Portafolio (9 opciones)
Basado en la combinación de perfil de riesgo y capacidad de inversión:
Capacidad/RiesgoRiesgo BajoRiesgo MedioRiesgo AltoInversión BajaPortafolio 1Portafolio 2Portafolio 3Inversión MediaPortafolio 4Portafolio 5Portafolio 6Inversión AltaPortafolio 7Portafolio 8Portafolio 9
Descripción de los Portafolios
Portafolios de Riesgo Bajo:

Portafolio 1 (Inversión Baja): Enfocado en preservación de capital, principalmente instrumentos de renta fija de alta calidad, fondos del mercado monetario y depósitos a plazo.
Portafolio 4 (Inversión Media): Preservación de capital con exposición limitada a instrumentos de mayor rendimiento, 80% renta fija de alta calidad, 20% renta variable conservadora.
Portafolio 7 (Inversión Alta): Enfoque conservador pero con mayor diversificación, 70% renta fija, 25% renta variable de baja volatilidad, 5% inversiones alternativas conservadoras.

Portafolios de Riesgo Medio:

Portafolio 2 (Inversión Baja): Balance entre seguridad y crecimiento, 65% renta fija, 30% renta variable, 5% alternativas.
Portafolio 5 (Inversión Media): Crecimiento moderado, 50% renta fija, 40% renta variable diversificada, 10% alternativas.
Portafolio 8 (Inversión Alta): Crecimiento con diversificación amplia, 40% renta fija, 45% renta variable global, 15% alternativas e inversiones internacionales.

Portafolios de Riesgo Alto:

Portafolio 3 (Inversión Baja): Enfoque en crecimiento, 30% renta fija, 60% renta variable, 10% alternativas de mayor riesgo.
Portafolio 6 (Inversión Media): Crecimiento agresivo, 20% renta fija, 65% renta variable con énfasis en sectores de crecimiento, 15% alternativas.
Portafolio 9 (Inversión Alta): Máximo crecimiento, 10% renta fija, 70% renta variable con exposición a mercados emergentes y sectores disruptivos, 20% alternativas e inversiones de alto potencial.

Ajustes Complementarios
Realiza ajustes al portafolio base recomendado considerando:

Objetivos específicos del cliente
Restricciones particulares identificadas
Circunstancias especiales mencionadas
Preferencias expresadas en el cuestionario

ANÁLISIS DE FACTORES COMPORTAMENTALES
Sesgos Comportamentales a Identificar

Aversión a Pérdidas

Identifica si el cliente muestra excesiva preocupación por las pérdidas versus ganancias potenciales
Evalúa reacciones declaradas ante escenarios de pérdida
Considéra la consistencia entre respuestas teóricas y comportamiento descrito


Exceso de Confianza

Compara el nivel de conocimiento declarado con la experiencia real demostrada
Evalúa expectativas de rendimiento versus conocimiento y experiencia
Identifica posible sobreestimación de habilidades predictivas


Comportamiento de Manada

Detecta tendencia a seguir el comportamiento del mercado general
Evalúa respuestas sobre reacciones ante noticias del mercado
Identifica posible susceptibilidad a pánico financiero


Anclaje

Identifica si el cliente ancla sus expectativas en rendimientos pasados o referencias específicas
Analiza si hay fijación con un nivel de rendimiento particular


Sesgo de Recencia

Evalúa si las respuestas están influenciadas por eventos financieros recientes
Detecta si el cliente da más peso a experiencias recientes que a patrones de largo plazo



Correcciones Basadas en Factores Comportamentales

Si se detecta aversión extrema a pérdidas: Considera reducir un nivel el perfil de riesgo recomendado
Si se detecta exceso de confianza: Considera reducir un nivel el perfil de riesgo recomendado
Si se detecta comportamiento de manada: Sugiere estrategias con rebalanceo automático
Si se detecta anclaje en rendimientos irreales: Ajusta expectativas en la recomendación final
Si se detecta sesgo de recencia: Enfatiza el horizonte temporal y perspectiva histórica

FORMATO DEL REPORTE FINAL
1. Resumen Ejecutivo

Perfil de riesgo determinado: BAJO, MEDIO o ALTO
Capacidad de inversión determinada: BAJA, MEDIA o ALTA
Portafolio recomendado (número y descripción breve)
Principales consideraciones especiales

2. Análisis Detallado

Evaluación por secciones del cuestionario
Puntuaciones obtenidas en cada categoría
Factores determinantes en la recomendación
Análisis de consistencia y posibles sesgos identificados

3. Recomendación de Portafolio

Descripción completa del portafolio recomendado
Composición de activos sugerida
Rendimientos históricos de referencia
Nivel de riesgo asociado (volatilidad esperada)
Horizonte temporal recomendado
Ajustes personalizados según circunstancias particulares

4. Consideraciones Adicionales

Recomendaciones complementarias personalizadas
Banderas rojas identificadas y cómo abordarlas
Posibles escenarios adversos y cómo preparararse
Frecuencia recomendada de revisión del portafolio

5. Próximos Pasos

Proceso de implementación recomendado
Frecuencia sugerida de revisión
Circunstancias que justificarían reconsiderar el perfil o la estrategia

INTERPRETACIÓN FINAL
Concluye con una interpretación completa y personalizada que integre todos los factores analizados, presentando una visión holística del perfil del inversionista y la justificación clara de la recomendación realizada. Asegúrate de que el lenguaje sea accesible pero profesional, educando al cliente sobre los conceptos relevantes sin usar jerga excesivamente técnica.
Recuerda que cada recomendación debe equilibrar los factores matemáticos (puntuación) con el juicio experto para capturar matices que un sistema puramente cuantitativo podría pasar por alto. La meta final es una recomendación que no solo sea técnicamente apropiada sino también práctica y alineada con la realidad psicológica y financiera del cliente.
"""

# --- FUNCIÓN PARA CONSULTAR A CLAUDE ---
async def analizar_con_claude(respuestas):
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": "claude-3-opus-20240229",
        "messages": [
            {"role": "system", "content": PROMPT_CLAUDE},
            {"role": "user", "content": json.dumps(respuestas)}
        ],
        "max_tokens": 1500,
        "temperature": 0.5
    }
    async with httpx.AsyncClient() as client:
        r = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
        return r.json()["content"]

# --- INICIO DEL FORMULARIO ---
respuestas = {}
with st.form("formulario_perfil"):
    st.subheader("📝 Cuestionario de Perfil de Riesgo")

    # SECCIÓN 1
    with st.expander("1. Datos Personales y Situación Financiera"):
        respuestas["Edad"] = st.radio("Edad", [
            "Menor de 25 años", "Entre 26 y 35 años", "Entre 36 y 45 años", "Entre 46 y 55 años", "Entre 56 y 65 años", "Mayor de 65 años"])
        respuestas["Situación laboral"] = st.radio("¿Cuál es su situación laboral actual?", [
            "Empleado tiempo completo", "Empleado tiempo parcial", "Empresario/Autónomo", "Jubilado", "Sin empleo actual"])
        respuestas["Ingreso anual"] = st.radio("Su ingreso anual se encuentra en el rango de:", [
            "Menos de $30,000", "Entre $30,000 y $60,000", "Entre $60,001 y $100,000",
            "Entre $100,001 y $150,000", "Entre $150,001 y $250,000", "Más de $250,000"])
        respuestas["% patrimonio a invertir"] = st.radio("¿Qué porcentaje de su patrimonio total planea invertir?", [
            "Menos del 10%", "Entre 11% y 25%", "Entre 26% y 40%", "Entre 41% y 60%", "Más del 60%"])
        respuestas["Horizonte de inversión"] = st.radio("¿Cuánto tiempo podría mantener sus inversiones sin necesitar acceso a ellas?", [
            "Menos de 1 año", "Entre 1 y 2 años", "Entre 3 y 5 años", "Entre 6 y 10 años", "Más de 10 años"])
        respuestas["Fondo de emergencia"] = st.radio("¿Tiene usted un fondo de emergencia equivalente a 3-6 meses de gastos?", [
            "Sí, tengo un fondo de emergencia que cubre 6 meses o más",
            "Sí, tengo un fondo que cubre entre 3 y 5 meses",
            "Parcialmente, tengo ahorros que cubren 1-2 meses",
            "No tengo un fondo de emergencia"])
        respuestas["Nivel de endeudamiento"] = st.radio("¿Cuál es su nivel actual de endeudamiento en relación con sus ingresos anuales?", [
            "No tengo deudas", "Menos del 25% de mis ingresos anuales", "Entre 26% y 50%",
            "Entre 51% y 100%", "Más del 100% de mis ingresos anuales"])
        respuestas["Ahorro mensual"] = st.radio("¿Qué porcentaje de sus ingresos mensuales destina al ahorro e inversión?", [
            "Menos del 5%", "Entre 5% y 10%", "Entre 11% y 20%", "Entre 21% y 30%", "Más del 30%"])

    # SECCIÓN 2 (multiselect incluido)
    with st.expander("2. Experiencia y Conocimientos"):
        respuestas["Nivel de conocimiento"] = st.radio("¿Cómo describiría su nivel de conocimiento sobre inversiones?", [
            "Principiante", "Básico", "Intermedio", "Avanzado", "Experto"])
        respuestas["Experiencia previa"] = st.multiselect("¿Cuál ha sido su experiencia previa con inversiones?", [
            "Ninguna", "Depósitos", "Bonos", "Fondos o ETFs", "Acciones",
            "Bienes raíces", "Materias primas", "Criptomonedas", "Derivados", "Capital privado"])
        respuestas["Términos que comprende"] = st.multiselect("¿Cuáles términos financieros entiende completamente?", [
            "Interés compuesto", "Diversificación", "Renta fija y variable", "P/E",
            "Beta y correlación", "Rendimiento ajustado", "Derivados financieros", "Estructura de capital",
            "Opciones", "Coberturas"])
        respuestas["Frecuencia de revisión"] = st.radio("¿Con qué frecuencia revisa sus inversiones?", [
            "Diariamente", "Semanalmente", "Mensualmente", "Trimestralmente", "Semestralmente", "Anualmente"])
        respuestas["Rendimiento histórico personal"] = st.radio("¿Cómo ha sido su rendimiento en inversiones previas?", [
            "No tengo experiencia", "Principalmente negativo", "Mixto más pérdidas", "Equilibrado",
            "Mixto más ganancias", "Principalmente positivo"])
        respuestas["Fuentes de información"] = st.multiselect("¿Cómo obtiene información para invertir?", [
            "No busco información", "Noticias", "Webs especializadas", "Análisis financiero",
            "Asesor profesional", "Libros y cursos", "Foros", "Investigación propia"])

    enviado = st.form_submit_button("Enviar Cuestionario")

if enviado:
    st.success("✅ Cuestionario enviado. Analizando con Claude...")
    import asyncio
    resultado = asyncio.run(analizar_con_claude(respuestas))
    st.subheader("🔍 Resultado de Claude AI")
    st.markdown(resultado)

    st.header("📊 Portafolio Simulado")
    portafolio = {"Tesla": 0.4, "Apple": 0.3, "Microsoft": 0.3}
    monto = st.number_input("💰 Ingresa el monto a invertir:", min_value=1000, step=1000)

    if monto:
        tickers = list(portafolio.keys())
        data = yf.download(tickers, period="1d")['Adj Close']
        precios = data.iloc[0].to_dict()

        df = pd.DataFrame({
            "Empresa": tickers,
            "% del Portafolio": [portafolio[t] for t in tickers],
            "Precio Actual": [precios[t] for t in tickers],
            "Monto Invertido": [monto * portafolio[t] for t in tickers]
        })
        df["Acciones"] = df["Monto Invertido"] / df["Precio Actual"]
        df["Ganancia/Perdida $"] = 0
        df["Ganancia/Perdida %"] = 0

        fig = px.pie(df, names="Empresa", values="% del Portafolio", title="Distribución del Portafolio")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)
