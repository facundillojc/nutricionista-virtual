import streamlit as st
import requests
import time
from datetime import datetime
import pandas as pd
import base64
import json

# Configurar la API key de Hugging Face desde secrets
hf_api_key = st.secrets["HF_API_TOKEN"]
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": f"Bearer {hf_api_key}"}

# Función para convertir un DataFrame a CSV descargable
def get_csv_download_link(df, filename="plan_nutricional.csv", text="Descargar plan como CSV"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-button">{text}</a>'
    return href

# Función para convertir el reporte a HTML descargable
def get_html_download_link(html_content, filename="plan_nutricional.html", text="Descargar plan como HTML"):
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}" class="download-button">{text}</a>'
    return href

# Configuración de la página
st.set_page_config(
    page_title="NutriPlan Premium",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"  # Mejor para móviles
)

# Estilos CSS personalizados para una apariencia premium y responsive
st.markdown(
    """
    <style>
    /* Fuentes y estilos generales */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #D4AF37;         /* Dorado premium */
        --primary-light: #F5E7A3;   /* Dorado claro */
        --primary-dark: #A67C00;    /* Dorado oscuro */
        --secondary: #3A3A3A;       /* Gris oscuro */
        --accent: #BD9E39;          /* Acento dorado */
        --background: #121212;      /* Fondo negro mate */
        --card-bg: #1E1E1E;         /* Fondo de tarjetas */
        --text-light: #FAFAFA;      /* Texto claro */
        --text-dark: #121212;       /* Texto oscuro */
        --border: #2A2A2A;          /* Bordes */
        --success: #4CAF50;         /* Verde para éxito */
        --info: #2196F3;            /* Azul para información */
    }
    
    body {
        font-family: 'Montserrat', sans-serif;
        background-color: var(--background);
        color: var(--text-light);
        line-height: 1.6;
    }
    
    /* Contenedores */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .card {
        background-color: var(--card-bg);
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: transform 0.3s, box-shadow 0.3s;
        border: 1px solid rgba(212, 175, 55, 0.1);  /* Borde dorado sutil */
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 25px rgba(212, 175, 55, 0.15);  /* Sombra dorada al hacer hover */
    }
    
    /* Formulario */
    .form-section {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    
    .form-group {
        margin-bottom: 15px;
    }
    
    .form-label {
        font-weight: 500;
        margin-bottom: 8px;
        display: block;
        color: var(--text-light);
    }
    
    /* Botones */
    .stButton>button {
        background-color: var(--primary);
        color: var(--text-dark);  /* Texto oscuro para contraste con dorado */
        font-weight: 600;
        padding: 12px 30px;
        border-radius: 30px;
        border: none;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s;
        width: 100%;
        margin-top: 15px;
    }
    
    .stButton>button:hover {
        background-color: var(--primary-light);
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);  /* Sombra dorada */
        transform: translateY(-2px);
    }
    
    /* Encabezados */
    h1, h2, h3, h4, h5 {
        font-weight: 700;
        margin-top: 0;
        color: var(--text-light);
    }
    
    .title-accent {
        color: var(--primary);  /* Título dorado */
        font-weight: 700;
    }
    
    /* Reportes y resultados */
    .report-container {
        background-color: var(--card-bg);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        color: var(--text-light);
        font-size: 16px;
        line-height: 1.8;
        margin: 20px 0;
        max-height: 800px;
        overflow-y: auto;
        border: 1px solid rgba(212, 175, 55, 0.2);  /* Borde dorado sutil */
    }
    
    .report-section {
        margin-bottom: 20px;
        padding-bottom: 20px;
        border-bottom: 1px solid var(--border);
    }
    
    .report-section:last-child {
        border-bottom: none;
    }
    
    .report-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        border-bottom: 2px solid var(--primary);  /* Línea dorada bajo encabezado */
        padding-bottom: 10px;
    }
    
    .report-date {
        font-size: 14px;
        color: var(--primary-light);  /* Fecha en dorado claro */
    }
    
    /* Barra lateral personalizada */
    .sidebar .sidebar-content {
        background-color: var(--card-bg);
        padding: 20px;
    }
    
    /* Inputs y Selects */
    .stTextInput>div>div>input, 
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select,
    .stTextArea>div>textarea {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--border);
        border-radius: 10px;
        color: var(--text-light);
        padding: 12px 15px;
        font-size: 16px;
        transition: all 0.3s;
    }
    
    .stTextInput>div>div>input:focus, 
    .stNumberInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.2);  /* Sombra dorada al enfocar */
    }
    
    /* Elementos de progreso */
    .step-progress {
        display: flex;
        justify-content: space-between;
        margin-bottom: 30px;
        position: relative;
    }
    
    .step-progress:after {
        content: '';
        position: absolute;
        top: 14px;
        left: 0;
        width: 100%;
        height: 2px;
        background-color: var(--border);
        z-index: 1;
    }
    
    .step {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: var(--card-bg);
        border: 2px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        color: var(--text-light);
        position: relative;
        z-index: 2;
    }
    
    .step.active {
        background-color: var(--primary);
        border-color: var(--primary);
        color: var(--text-dark);  /* Texto oscuro para contraste */
    }
    
    .step.completed {
        background-color: var(--primary-dark);
        border-color: var(--primary-dark);
    }
    
    /* Estilos para dispositivos móviles */
    @media (max-width: 768px) {
        .card {
            padding: 15px;
        }
        
        .report-container {
            padding: 15px;
            font-size: 14px;
        }
        
        .stButton>button {
            padding: 10px 20px;
            font-size: 14px;
        }
        
        .step-progress {
            margin-bottom: 20px;
        }
        
        .step {
            width: 25px;
            height: 25px;
            font-size: 12px;
        }
    }
    
    /* Estilos para los botones de descarga */
    .download-button {
        display: inline-block;
        background-color: var(--primary);
        color: var(--text-dark);  /* Texto oscuro para contraste */
        font-weight: 600;
        padding: 10px 20px;
        border-radius: 30px;
        text-decoration: none;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 14px;
        transition: all 0.3s;
        margin-right: 10px;
        margin-top: 15px;
    }
    
    .download-button:hover {
        background-color: var(--primary-light);
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);  /* Sombra dorada */
        transform: translateY(-2px);
    }
    
    /* Progress bar custom styling */
    .stProgress > div > div > div {
        background-color: var(--primary);  /* Barra de progreso dorada */
    }
    
    /* Personalización de la barra de progreso premium */
    .premium-progress-container {
        background-color: rgba(30, 30, 30, 0.8);
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 0 30px rgba(212, 175, 55, 0.2);
        position: relative;
        margin: 20px 0;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }
    
    .premium-progress-title {
        text-align: center;
        font-weight: 600;
        margin-bottom: 20px;
        color: var(--primary);
    }
    
    .premium-progress-bar {
        height: 20px;
        background-color: var(--secondary);
        border-radius: 10px;
        overflow: hidden;
        position: relative;
        margin-bottom: 10px;
        box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
    }
    
    .premium-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-dark) 0%, var(--primary) 100%);
        border-radius: 10px;
        transition: width 0.5s ease;
        position: relative;
    }
    
    .premium-progress-fill:after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(
            45deg, 
            rgba(255,255,255,0.1) 25%, 
            transparent 25%, 
            transparent 50%, 
            rgba(255,255,255,0.1) 50%, 
            rgba(255,255,255,0.1) 75%, 
            transparent 75%, 
            transparent
        );
        background-size: 20px 20px;
        animation: move 2s linear infinite;
        border-radius: 10px;
    }
    
    @keyframes move {
        0% {
            background-position: 0 0;
        }
        100% {
            background-position: 40px 0;
        }
    }
    
    .premium-progress-text {
        text-align: center;
        font-weight: 600;
        margin-top: 5px;
        font-size: 14px;
    }
    
    .premium-progress-status {
        font-size: 12px;
        color: var(--primary-light);
        text-align: center;
        margin-top: 10px;
        font-style: italic;
    }
    
    /* Estilos para métricas personalizadas */
    .metric-container {
        background-color: rgba(30, 30, 30, 0.6);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 3px solid var(--primary);
    }
    
    .metric-title {
        font-size: 14px;
        color: var(--text-light);
        margin-bottom: 5px;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 600;
        color: var(--primary);
    }
    
    .metric-subtitle {
        font-size: 12px;
        color: var(--primary-light);
        margin-top: 5px;
    }
    
    /* Tarjetas de información */
    .info-card {
        background-color: rgba(33, 150, 243, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 3px solid var(--info);
    }
    
    /* Estilizando las pestañas del reporte */
    .report-tabs {
        display: flex;
        border-bottom: 1px solid var(--border);
        margin-bottom: 20px;
    }
    
    .report-tab {
        padding: 10px 20px;
        cursor: pointer;
        transition: all 0.3s;
        border-bottom: 3px solid transparent;
        margin-right: 10px;
    }
    
    .report-tab.active {
        border-bottom: 3px solid var(--primary);
        color: var(--primary);
        font-weight: 600;
    }
    
    .report-tab:hover:not(.active) {
        color: var(--primary-light);
    }
    
    /* Estilizando notificaciones */
    .notification {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: var(--primary);
        color: var(--text-dark);
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        z-index: 9999;
        animation: fadeIn 0.5s, fadeOut 0.5s 4.5s;
        opacity: 0;
        font-weight: 500;
    }
    
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    
    @keyframes fadeOut {
        from {opacity: 1;}
        to {opacity: 0;}
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Inicializar variables de sesión
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'report' not in st.session_state:
    st.session_state.report = None
if 'patologias_list' not in st.session_state:
    st.session_state.patologias_list = []
if 'restricciones_list' not in st.session_state:
    st.session_state.restricciones_list = []
if 'progress_state' not in st.session_state:
    st.session_state.progress_state = {}

# Funciones para navegación entre pasos
def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

# Guardar datos del usuario
def save_user_data(key, value):
    st.session_state.user_data[key] = value

# Función para la barra de progreso premium personalizada
def premium_progress_bar(progress_percent, message="Procesando...", key="default"):
    progress_html = f"""
    <div class="premium-progress-container">
        <div class="premium-progress-title">Generando Plan Nutricional Premium</div>
        <div class="premium-progress-bar">
            <div class="premium-progress-fill" style="width: {progress_percent}%;"></div>
        </div>
        <div class="premium-progress-text">{progress_percent}% Completado</div>
        <div class="premium-progress-status">{message}</div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

# Función para mostrar métricas personalizadas
def custom_metric(title, value, subtitle=None):
    metric_html = f"""
    <div class="metric-container">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {f'<div class="metric-subtitle">{subtitle}</div>' if subtitle else ''}
    </div>
    """
    return metric_html

# Función para generar el reporte nutricional con Mixtral-8x7B-Instruct
def generar_reporte(datos_usuario):
    # Definir mensajes de progreso para dar apariencia premium
    progress_messages = [
        "Analizando datos personales...",
        "Evaluando perfil nutricional...",
        "Calculando necesidades calóricas...",
        "Analizando patologías específicas...",
        "Evaluando restricciones alimenticias...",
        "Consultando base de conocimiento nutricional...",
        "Diseñando plan alimenticio personalizado...",
        "Elaborando recomendaciones...",
        "Optimizando el plan según tus objetivos...",
        "Finalizando y preparando tu plan premium..."
    ]
    
    # Crear el contenedor para la barra de progreso
    progress_placeholder = st.empty()
    
    # Simular progreso con mensajes dinámicos
    for i in range(0, 101, 10):
        message_index = min(i // 10, len(progress_messages) - 1)
        premium_progress_bar(i, progress_messages[message_index], key="reporte")
        time.sleep(0.5)  # Simular carga para una mejor experiencia
        progress_placeholder.empty()
        progress_placeholder = st.empty()
    
    # Ahora construimos el prompt para el modelo
    prompt = f"""
    [INST] Genera un plan de alimentación personalizado premium para:
    - Nombre: {datos_usuario['nombre']}
    - Edad: {datos_usuario['edad']} años
    - Género: {datos_usuario.get('genero', 'No especificado')}
    - Peso: {datos_usuario['peso']} kg
    - Estatura: {datos_usuario['estatura']} cm
    - Nivel de actividad: {datos_usuario['actividad']}
    - Objetivo principal: {datos_usuario.get('objetivo', 'No especificado')}
    - Patologías: {", ".join(datos_usuario['patologias']) if datos_usuario['patologias'] else "Ninguna"}
    - Restricciones alimenticias: {", ".join(datos_usuario['restricciones']) if datos_usuario['restricciones'] else "Ninguna"}
    - Comentarios adicionales: {datos_usuario.get('comentarios', 'Ninguno')}
    
    Estructura tu respuesta en secciones claramente identificadas con títulos en negrita:

    **RESUMEN PERSONALIZADO**
    - Incluye un breve resumen personalizado llamando al usuario por su nombre.
    - Calcula y menciona el IMC y sus implicaciones.
    - Estima las calorías diarias recomendadas según peso, altura, edad, género y nivel de actividad.
    - Relaciona el plan con el objetivo principal del usuario.
    
    **ANÁLISIS DE PATOLOGÍAS**
    - Si hay patologías, realiza un análisis detallado de cada una.
    - Proporciona recomendaciones nutricionales específicas para cada patología.
    - Enumera alimentos beneficiosos y perjudiciales para cada condición.
    
    **PLAN ALIMENTICIO SEMANAL**
    - Proporciona un plan de alimentación estructurado para 7 días.
    - Para cada día incluye: desayuno, media mañana, almuerzo, merienda y cena.
    - Especifica cantidades aproximadas (ej. 1 taza, 100g) para cada alimento.
    - Sugiere horarios ideales para cada comida.
    - Asegúrate que cada comida sea apropiada para las patologías mencionadas.
    - Asegúrate que el plan sea realista y fácil de seguir.
    
    **RECOMENDACIONES ADICIONALES**
    - Incluye consejos sobre hidratación diaria recomendada.
    - Si es relevante, menciona suplementos que podrían beneficiar al usuario.
    - Da consejos sobre la preparación de alimentos para maximizar los beneficios nutricionales.
    - Incluye recomendaciones personalizadas según el objetivo principal del usuario.
    
    Usa un tono natural, profesional y motivador en español. Evita tecnicismos excesivos y explica cualquier término especializado. El plan debe ser realista, detallado y fácil de seguir. [/INST]
    """
    
    # Realizar la llamada a la API
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 2500,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False
        }
    }
    
    try:
        # Llamada real a la API
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        result = response.json()
        return result[0]["generated_text"]
    except requests.exceptions.RequestException as e:
        # Manejo de errores amigable
        error_message = "Hubo un problema al generar tu plan nutricional."
        if hasattr(response, "status_code"):
            if response.status_code == 503:
                error_message = "Nuestro servicio de nutrición premium está experimentando alta demanda en este momento. Por favor, intenta nuevamente en unos minutos."
            elif response.status_code == 400:
                error_message = "Hubo un problema con tus datos. Por favor, verifica la información ingresada e intenta nuevamente."
            else:
                error_message = f"Error al generar tu plan ({response.status_code}). Por favor, intenta nuevamente o contacta a soporte."
        return error_message

# Crear la interfaz principal
with st.container():
    st.markdown("<h1 style='text-align: center;'><span class='title-accent'>Nutri</span>Plan Premium</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; margin-bottom: 40px;'>Obtén un plan nutricional personalizado basado en tus necesidades específicas</p>", unsafe_allow_html=True)

# Mostrar barra de progreso de pasos
step_progress = st.container()
with step_progress:
    st.markdown(
        f"""
        <div class="step-progress">
            <div class="step {'completed' if st.session_state.step > 1 else 'active' if st.session_state.step == 1 else ''}">1</div>
            <div class="step {'completed' if st.session_state.step > 2 else 'active' if st.session_state.step == 2 else ''}">2</div>
            <div class="step {'completed' if st.session_state.step > 3 else 'active' if st.session_state.step == 3 else ''}">3</div>
            <div class="step {'active' if st.session_state.step == 4 else ''}">4</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Contenido según el paso actual
if st.session_state.step == 1:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("## Información Personal")
        st.markdown("Comencemos con tus datos básicos para personalizar tu plan nutricional premium.")
        
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre completo", 
                                  value=st.session_state.user_data.get('nombre', ''), 
                                  placeholder="Ej. María García")
            save_user_data('nombre', nombre)
            
            edad = st.number_input("Edad (años)", 
                                  min_value=1, max_value=120, 
                                  value=st.session_state.user_data.get('edad', 30), 
                                  step=1)
            save_user_data('edad', edad)
        
        with col2:
            genero = st.selectbox("Género", 
                               options=["Femenino", "Masculino", "Otro"],
                               index=["Femenino", "Masculino", "Otro"].index(st.session_state.user_data.get('genero', "Femenino")))
            save_user_data('genero', genero)
            
            objetivo = st.selectbox("Objetivo principal", 
                                  options=["Perder peso", "Mantener peso", "Ganar masa muscular", "Mejorar salud general", "Controlar una condición médica", "Mejorar rendimiento deportivo"],
                                  index=["Perder peso", "Mantener peso", "Ganar masa muscular", "Mejorar salud general", "Controlar una condición médica", "Mejorar rendimiento deportivo"].index(st.session_state.user_data.get('objetivo', "Mejorar salud general")))
            save_user_data('objetivo', objetivo)
        
        # Mostrar info adicional según el objetivo seleccionado
        if objetivo == "Controlar una condición médica":
            st.info("En el siguiente paso podrás indicar tus patologías específicas para personalizar al máximo tu plan nutricional.")
        
        if st.button("Continuar", key="btn_step1"):
            next_step()
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.step == 2:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("## Medidas y Actividad Física")
        st.markdown("Estos datos nos ayudarán a calcular tus necesidades calóricas y adaptar el plan a tu estilo de vida.")
        
        col1, col2 = st.columns(2)
        with col1:
            peso = st.number_input("Peso actual (kg)", 
                                 min_value=20.0, max_value=300.0, 
                                 value=st.session_state.user_data.get('peso', 70.0), 
                                 step=0.1)
            save_user_data('peso', peso)
            
            estatura = st.number_input("Estatura (cm)", 
                                     min_value=50, max_value=250, 
                                     value=st.session_state.user_data.get('estatura', 170), 
                                     step=1)
            save_user_data('estatura', estatura)
        
        with col2:
            actividad = st.select_slider("Nivel de actividad física",
                                      options=["Sedentario", "Ligero", "Moderado", "Activo", "Muy Activo"],
                                      value=st.session_state.user_data.get('actividad', "Moderado"))
            save_user_data('actividad', actividad)
            
        # ✅ Explicación del nivel de actividad seleccionado
        actividad_descripciones = {
            "Sedentario": "Poca o ninguna actividad física.",
            "Ligero": "Ejercicio ligero 1-3 veces por semana.",
            "Moderado": "Ejercicio moderado 3-5 veces por semana.",
            "Activo": "Ejercicio intenso 6-7 veces por semana.",
            "Muy Activo": "Entrenamiento físico muy intenso o trabajo físico exigente."
        }
        st.markdown(f"**Descripción:** {actividad_descripciones[actividad]}")
        
        # ✅ Botón "Continuar"
        if st.button("Continuar", key="btn_step2"):
            next_step()

        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.step == 3:
    with st.container():
        st.markdown("## Preferencias y Restricciones")
        restricciones = st.text_area("Restricciones alimenticias (si aplica)", value=st.session_state.user_data.get('restricciones', ''))
        save_user_data('restricciones', restricciones)
        
        if st.button("Continuar", key="btn_step3"):
            next_step()

elif st.session_state.step == 4:
    with st.container():
        st.markdown("## Generando tu Plan Nutricional")
        st.write("Presiona el botón para generar tu reporte nutricional personalizado.")
        # Botón para generar el reporte
if st.sidebar.button("Generar Reporte Nutricional"):
    if nombre and edad and peso and estatura and actividad:
        datos_usuario = {
            "nombre": nombre,
            "edad": edad,
            "peso": peso,
            "estatura": estatura,
            "actividad": actividad,
        }
        
        with st.spinner("Generando tu reporte nutricional..."):
            reporte = generar_reporte(datos_usuario)
        
        # Mostrar el reporte en una caja estilizada
        st.markdown("## Reporte Nutricional Personalizado")
        st.markdown(f"<div class='report-container'><p>{reporte}</p></div>", unsafe_allow_html=True)
    else:
        st.warning("Por favor, completa todos los campos obligatorios para generar el reporte.")