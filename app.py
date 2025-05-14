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
        return r.json()["content"][0]["text"]  # ✅ CORREGIDO


# --- INICIO DEL FORMULARIO ---
# --- FORMULARIO DE PERFIL DE RIESGO COMPLETO ---
respuestas = {}

with st.form("formulario_perfil"):
    st.subheader("📝 Cuestionario de Perfil de Riesgo e Inversión")

    # --- SECCIÓN 1: Datos Personales y Situación Financiera ---
    with st.expander("1. Datos Personales y Situación Financiera"):
        respuestas["Edad"] = st.radio("Edad", ["Menor de 25 años", "26-35", "36-45", "46-55", "56-65", "Mayor de 65"])
        respuestas["Situación Laboral"] = st.radio("Situación Laboral", ["Empleado tiempo completo", "Empleado tiempo parcial", "Empresario/Autónomo", "Jubilado", "Sin empleo actual"])
        respuestas["Ingreso Anual"] = st.radio("Ingreso Anual", ["<30k", "30k-60k", "60k-100k", "100k-150k", "150k-250k", ">250k"])
        respuestas["% Patrimonio a Invertir"] = st.radio("% Patrimonio a Invertir", ["<10%", "11-25%", "26-40%", "41-60%", ">60%"])
        respuestas["Horizonte Temporal"] = st.radio("¿Cuánto tiempo puede mantener su inversión?", ["<1 año", "1-2 años", "3-5 años", "6-10 años", ">10 años"])
        respuestas["Fondo de Emergencia"] = st.radio("¿Cuenta con fondo de emergencia?", ["Sí (6+ meses)", "Sí (3-5 meses)", "Parcial (1-2 meses)", "No tengo"])
        respuestas["Nivel de Endeudamiento"] = st.radio("Nivel de Endeudamiento", ["Sin deudas", "<25%", "26-50%", "51-100%", ">100%"])
        respuestas["% Ahorro Mensual"] = st.radio("% de ingresos al ahorro/inversión", ["<5%", "5-10%", "11-20%", "21-30%", ">30%"])

    # --- SECCIÓN 2: Experiencia y Conocimientos ---
    with st.expander("2. Experiencia y Conocimientos"):
        respuestas["Nivel de Conocimiento"] = st.radio("Nivel de conocimiento en inversiones", ["Principiante", "Básico", "Intermedio", "Avanzado", "Experto"])
        respuestas["Experiencia Previa"] = st.multiselect("Experiencia previa en:", ["Ninguna", "Depósitos", "Bonos", "Fondos/ETFs", "Acciones", "Bienes Raíces", "Materias Primas", "Criptomonedas", "Derivados", "Capital Privado"])
        respuestas["Términos que Comprende"] = st.multiselect("Términos Financieros que entiende:", ["Interés Compuesto", "Diversificación", "Renta fija/variable", "P/E Ratio", "Beta/Correlación", "Riesgo Ajustado", "Derivados", "Estructura Capital", "Opciones", "Coberturas"])
        respuestas["Frecuencia Revisión"] = st.radio("Frecuencia de revisión de inversiones", ["Diario", "Semanal", "Mensual", "Trimestral", "Semestral", "Anual"])
        respuestas["Rendimiento Histórico"] = st.radio("Historial de rendimiento en inversiones", ["Sin experiencia", "Principalmente negativo", "Más pérdidas que ganancias", "Equilibrado", "Más ganancias que pérdidas", "Principalmente positivo"])
        respuestas["Fuentes de Información"] = st.multiselect("¿Cómo toma decisiones de inversión?", ["No investigo", "Noticias", "Webs Financieras", "Análisis de expertos", "Asesor financiero", "Libros/cursos", "Foros", "Investigación propia"])

    # --- SECCIÓN 3: Tolerancia al Riesgo ---
    with st.expander("3. Tolerancia al Riesgo"):
        respuestas["Reacción a Pérdida 20%"] = st.radio("Si pierde 20% en un mes, ¿qué haría?", ["Vender todo", "Vender parcial", "Esperar", "Mantener", "Comprar más"])
        respuestas["Reacción a Pérdida 15%"] = st.radio("Inversión pierde 15% en 6 meses, fundamentos intactos. ¿Qué hace?", ["Vender", "Vender y diversificar", "Mantener", "Promediar", "Comprar más"])
        respuestas["Escenario Preferido"] = st.radio("¿Qué escenario de riesgo/rendimiento prefiere?", ["0% pérdida, hasta 5% ganancia", "5% pérdida, hasta 10% ganancia", "15% pérdida, hasta 20% ganancia", "25% pérdida, hasta 35% ganancia", "40% pérdida, hasta 60% ganancia"])
        respuestas["Portafolio Hipotético"] = st.radio("Elija un portafolio hipotético:", ["100% bajo riesgo", "75% bajo / 25% moderado", "50% bajo / 50% moderado", "25% bajo / 75% alto", "100% alto riesgo"])
        respuestas["Reacción a Volatilidad"] = st.radio("¿Cómo se siente ante alta volatilidad?", ["Muy ansioso", "Preocupado", "Neutral", "Interesado", "Emocionado"])
        respuestas["Actitud hacia Pérdidas"] = st.radio("Actitud ante pérdidas financieras:", ["Evito riesgos", "Acepto pequeñas pérdidas", "Acepto pérdidas temporales", "Acepto grandes pérdidas", "Aprendo de las pérdidas"])
        respuestas["Reacción a Crisis Financieras"] = st.radio("¿Cómo actuó o actuaría ante crisis como 2008 o COVID?", ["Vender todo", "Vender parcial", "Esperar", "Mantener", "Comprar más"])
        respuestas["Preocupaciones de Inversión"] = st.radio("¿Qué le preocupa más al invertir?", ["Perder capital", "No alcanzar objetivos", "Perder contra inflación", "No aprovechar oportunidades", "Perder rendimientos altos"])
        respuestas["Comparación con Mercado"] = st.radio("Si rinde 10% menos que el mercado, ¿cómo se sentiría?", ["Muy insatisfecho", "Insatisfecho pero comprendo", "Neutral", "Relativamente satisfecho", "No me afecta"])
        respuestas["Escala Tranquilidad/Rendimiento"] = st.radio("¿Prefiere tranquilidad o rendimiento?", ["Dormir tranquilo", "Más tranquilidad", "Equilibrio", "Más rendimiento", "Máximo rendimiento"])

    # --- SECCIÓN 4: Objetivos de Inversión ---
    with st.expander("4. Objetivos de Inversión"):
        respuestas["Objetivo Principal"] = st.radio("¿Cuál es su principal objetivo de inversión?", ["Preservar capital", "Ingreso pasivo", "Crecimiento moderado", "Crecimiento agresivo", "Especulativo"])
        respuestas["Motivo Ahorro"] = st.multiselect("¿Para qué está ahorrando?", ["Fondo emergencia", "Compra corto plazo", "Compra mediano plazo", "Educación", "Independencia financiera", "Jubilación", "Legado", "Crecimiento patrimonial"])
        respuestas["Uso del Capital"] = st.radio("¿En cuánto tiempo planea usar este capital?", ["<1 año", "1-3 años", "4-7 años", "8-15 años", ">15 años"])
        respuestas["Retiros Anuales"] = st.radio("¿Qué porcentaje podría retirar anualmente?", ["<2%", "2-4%", "4-6%", "6-8%", ">8%"])
        respuestas["Fuentes de Jubilación"] = st.radio("¿Tiene otras fuentes de ingresos para jubilación?", ["No, es la principal", "Sí, importante", "Sí, complementaria", "Sí, diversificada"])
        respuestas["Importancia de Liquidez"] = st.radio("¿Qué tan importante es la liquidez para usted?", ["Extremadamente importante", "Muy importante", "Moderadamente importante", "Poco importante", "No importante"])
        respuestas["Rendimiento Esperado"] = st.radio("Rendimiento anual esperado:", ["1-3%", "4-6%", "7-9%", "10-12%", ">12%"])
        respuestas["Objetivo Patrimonial"] = st.radio("Objetivo final de patrimonio:", ["Mantener poder adquisitivo", "Crecimiento modesto", "Duplicar capital", "Triplicar/cuadruplicar", "Multiplicar x5 o más"])

    # --- SECCIÓN 5: Circunstancias Personales ---
    with st.expander("5. Circunstancias Personales"):
        respuestas["Dependientes Económicos"] = st.radio("¿Tiene dependientes económicos?", ["No", "Dependen parcialmente", "Dependen totalmente", "Otros recursos"])
        respuestas["Estabilidad Ingresos"] = st.radio("Estabilidad de ingresos", ["Muy estable", "Estable", "Moderada", "Variable", "Inestable"])
        respuestas["Obligaciones Financieras"] = st.radio("Nivel de obligaciones financieras", ["Sin deudas", "Deudas menores", "Deudas moderadas", "Deudas significativas"])
        respuestas["Gastos Fijos"] = st.radio("¿Qué % de sus gastos son fijos?", ["<30%", "30-50%", "51-70%", ">70%"])
        respuestas["Capacidad sin Ingresos"] = st.radio("¿Cuánto tiempo mantendría su nivel de vida sin ingresos?", ["<3 meses", "3-6 meses", "7-12 meses", ">12 meses"])

    # --- SECCIÓN 6: Factores Psicológicos ---
    with st.expander("6. Factores Psicológicos"):
        respuestas["Toma de Decisiones"] = st.radio("¿Cómo toma decisiones importantes?", ["Evita riesgos", "Riesgos calculados", "Equilibrado", "Moderadamente arriesgado", "Arriesgado por oportunidad"])
        respuestas["Reacción a Pérdidas Financieras"] = st.radio("¿Cómo reacciona ante pérdidas económicas?", ["Afecta mucho", "Incomoda, pero aprende", "Analiza y sigue", "Lo ve como aprendizaje", "Le afecta poco"])
        respuestas["Actitud hacia el Dinero"] = st.radio("¿Qué frase lo define mejor?", ["Pájaro en mano", "Precavido", "El dinero debe trabajar", "Sin riesgo no hay recompensa", "Audaz"])
        respuestas["Lotería Hipotética"] = st.radio("¿Qué prefiere en una lotería?", ["$1,000 seguros", "50% de $3,000", "25% de $8,000", "10% de $30,000", "1% de $500,000"])
        respuestas["Ansiedad en Finanzas"] = st.radio("¿Cómo se siente al tomar decisiones financieras importantes?", ["Muy ansioso", "Algo ansioso", "Neutral", "Confiado", "Muy confiado"])
        respuestas["Preferencia Salario"] = st.radio("¿Qué prefiere en su trabajo?", ["Fijo", "Probablemente fijo", "Indiferente", "Probablemente variable", "Variable alto riesgo"])
        respuestas["Estilo de Planificación"] = st.radio("¿Cómo se describe como planificador?", ["Meticuloso", "Organizado", "Equilibrado", "Adaptable", "Espontáneo"])
        respuestas["Reacción a Noticias Negativas"] = st.radio("¿Qué hace ante malas noticias del mercado?", ["Vendería", "Esperaría", "Mantendría calma", "Buscaría oportunidades", "Ignoraría ruido"])

    # --- SECCIÓN 7: Capacidad Financiera ---
    with st.expander("7. Capacidad Financiera"):
        respuestas["% de Patrimonio"] = st.radio("¿Qué % de su patrimonio representa esta inversión?", ["<10%", "10-25%", "26-50%", "51-75%", ">75%"])
        respuestas["Tiempo Acumulando Capital"] = st.radio("¿Cuánto tardó en reunir este capital?", ["<1 año", "1-3 años", "4-7 años", "8-15 años", ">15 años"])
        respuestas["Impacto Pérdida 30%"] = st.radio("Si pierde 30%, ¿cómo afecta su vida?", ["Impacto severo", "Impacto significativo", "Moderado", "Leve", "Sin impacto"])
        respuestas["Capacidad de Aportar Más"] = st.radio("¿Puede seguir aportando a esta inversión?", ["No", "Limitada", "Moderada", "Buena", "Excelente"])
        respuestas["Expectativas Ingresos Futuros"] = st.radio("¿Espera recibir fondos extra (herencias, bonos)?", ["No", "Pequeñas posibilidades", "Probable moderado", "Definitivamente significativo", "Muy significativo"])

    # --- Enviar ---
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
