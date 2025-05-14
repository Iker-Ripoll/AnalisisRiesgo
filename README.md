# 📊 Aplicación de Análisis de Riesgo e Inversión

Esta es una aplicación web interactiva desarrollada en **Python** con **Streamlit** que permite evaluar el perfil de riesgo de un inversionista a través de un cuestionario completo, conectarse con **Claude AI** para procesar las respuestas y recomendar uno de 9 portafolios de inversión. Además, muestra en tiempo real los precios y distribución de activos financieros usando datos de **Yahoo Finance**.

## 🛠️ Tecnologías Utilizadas
- [Streamlit](https://streamlit.io/) (interfaz web)
- [yfinance](https://pypi.org/project/yfinance/) (datos financieros)
- [pandas](https://pandas.pydata.org/) (análisis de datos)
- [plotly](https://plotly.com/python/) (gráficos interactivos)
- [httpx](https://www.python-httpx.org/) (requests asíncronos para Claude AI)

## 🚀 Funcionalidades
- 📄 **Cuestionario completo de perfil de riesgo** (7 secciones, 50+ preguntas)
- 🤖 **Conexión con Claude AI** vía API para analizar respuestas y sugerir portafolios
- 📈 **Visualización en tiempo real de precios** (Apple, Tesla, Microsoft)
- 🥧 **Gráfica de distribución del portafolio** en formato circular
- 💰 **Cálculo de inversión, cantidades y % ganancia/pérdida**

## 🔑 Requisitos
1. Python 3.10+
2. Librerías necesarias:
    ```bash
    pip install -r requirements.txt
    ```

## 📄 Estructura del Proyecto

