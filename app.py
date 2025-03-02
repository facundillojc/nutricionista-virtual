import streamlit as st
import requests
import time
from datetime import datetime
import pandas as pd
import base64

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

# Función para generar un PDF descargable (versión simple con HTML)
def get_pdf_download_link(html_content, filename="plan_nutricional.pdf", text="Descargar plan como PDF"):
    # Esta es una versión simplificada, idealmente usarías una biblioteca como ReportLab o WeasyPrint
    # Para este ejemplo, simplemente proporcionamos un enlace que instruye al usuario a imprimir como PDF
    html = f"""
    <div id="pdf-content" style="display:none">
        {html_content}
    </div>
    <a href="#" onclick="printContent(); return false;" class="download-button">{text}</a>
    <script>
        function printContent() {{
            var content = document.getElementById('pdf-content').innerHTML;
            var printWindow = window.open('', '_blank');
            printWindow.document.write('<html><head><title>Plan Nutricional</title>');
            printWindow.document.write('<style>body {{ font-family: Arial; padding: 20px; }}</style>');
            printWindow.document.write('</head><body>');
            printWindow.document.write(content);
            printWindow.document.write('</body></html>');
            printWindow.document.close();
            printWindow.focus();
            printWindow.print();
        }}
    </script>
    """
    return html

# Configuración de la página
st.set_page_config(
    page_title="NutriPlan Premium",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para una apariencia premium y responsive
st.markdown(
    """
    <style>
    /* Fuentes y estilos generales */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #4CAF50;
        --primary-light: #80E884;
        --primary-dark: #087f23;
        --secondary: #1E4620;
        --accent: #FFD700;
        --background: #121212;
        --card-bg: #1E1E1E;
        --text-light: #FAFAFA;
        --text-dark: #121212;
        --border: #2A2A2A;
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
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.4);
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
        color: var(--text-light);
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
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
        transform: translateY(-2px);
    }
    
    /* Encabezados */
    h1, h2, h3, h4, h5 {
        font-weight: 700;
        margin-top: 0;
        color: var(--text-light);
    }
    
    .title-accent {
        color: var(--accent);
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
    }
    
    .report-date {
        font-size: 14px;
        color: #888;
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
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
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
        color: var(--text-light);
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
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
        transform: translateY(-2px);
    }
    
    /* Progress bar custom styling */
    .stProgress > div > div > div {
        background-color: var(--primary);
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

# Funciones para navegación entre pasos
def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def goto_step(step):
    st.session_state.step = step

# Guardar datos del usuario
def save_user_data(key, value):
    st.session_state.user_data[key] = value
    
# Función para generar el reporte nutricional con Mixtral-8x7B-Instruct
def generar_reporte(datos_usuario):
    prompt = f"""
    [INST] Genera un plan de alimentación personalizado para:
    - Nombre: {datos_usuario['nombre']}
    - Edad: {datos_usuario['edad']} años
    - Peso: {datos_usuario['peso']} kg
    - Estatura: {datos_usuario['estatura']} cm
    - Nivel de actividad: {datos_usuario['actividad']}
    - Patologías: {", ".join(datos_usuario['patologias']) if datos_usuario['patologias'] else "Ninguna"}
    - Restricciones alimenticias: {", ".join(datos_usuario['restricciones']) if datos_usuario['restricciones'] else "Ninguna"}
    
    Estructura tu respuesta en secciones claramente identificadas con títulos en negrita:

    **RESUMEN PERSONALIZADO**
    - Incluye un breve resumen personalizado llamando al usuario por su nombre.
    - Calcula y menciona el IMC y sus implicaciones.
    - Estima las calorías diarias recomendadas según peso, altura, edad y nivel de actividad.
    
    **ANÁLISIS DE PATOLOGÍAS**
    - Si hay patologías, realiza un análisis detallado de cada una.
    - Proporciona recomendaciones nutricionales específicas para cada patología.
    - Enumera alimentos beneficiosos y perjudiciales para cada condición.
    
    **PLAN ALIMENTICIO DIARIO**
    - Proporciona un plan de alimentación estructurado para 7 días.
    - Para cada día incluye desayuno, media mañana, almuerzo, merienda y cena.
    - Especifica cantidades aproximadas (ej. 1 taza, 100g) y horarios sugeridos.
    - Asegúrate que cada comida sea apropiada para las patologías mencionadas.
    
    **RECOMENDACIONES ADICIONALES**
    - Incluye consejos específicos sobre hidratación.
    - Menciona suplementos recomendados si aplica.
    - Da consejos sobre preparación de alimentos para maximizar beneficios nutricionales.
    
    Usa un tono natural, profesional y motivador en español. Evita tecnicismos excesivos y explica cualquier término especializado. Personaliza el plan para que sea realista y fácil de seguir. [/INST]
    """
    
    # Llamada a la API de Hugging Face
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 2500,        # Aumentado para permitir más detalle
            "temperature": 0.7,        # Balance entre creatividad y coherencia
            "top_p": 0.9,             # Para respuestas enfocadas
            "return_full_text": False  # Solo devuelve la respuesta generada
        }
    }
    try:
        # Simular carga para una mejor experiencia de usuario (opcional)
        progress_bar = st.progress(0)
        for i in range(101):
            time.sleep(0.05)  # Simular procesamiento
            progress_bar.progress(i)
        
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP
        result = response.json()
        progress_bar.empty()
        return result[0]["generated_text"]
    except requests.exceptions.RequestException as e:
        progress_bar.empty()
        # Manejo de errores con mensajes claros
        if hasattr(response, "status_code"):
            if response.status_code == 503:
                return "El servicio de Hugging Face está temporalmente no disponible (Error 503). Por favor, intenta de nuevo en unos minutos."
            elif response.status_code == 400:
                return "Error en la solicitud al modelo (Error 400). Verifica el formato o la disponibilidad del modelo."
            return f"Error al consultar el modelo: {response.status_code} - {str(e)}"
        return f"Error al consultar el modelo: {str(e)}"

# Crear la interfaz principal
st.markdown("<h1 style='text-align: center;'><span class='title-accent'>Nutri</span>Plan Premium</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; margin-bottom: 40px;'>Obtén un plan nutricional personalizado basado en tus necesidades específicas</p>", unsafe_allow_html=True)

# Mostrar barra de progreso de pasos
col1, col2, col3, col4 = st.columns(4)
step_cols = [col1, col2, col3, col4]

# Indicadores de progreso
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
        st.markdown("Comencemos con tus datos básicos para personalizar tu plan nutricional.")
        
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
                                  options=["Perder peso", "Mantener peso", "Ganar masa muscular", "Mejorar salud", "Mejorar rendimiento deportivo"],
                                  index=["Perder peso", "Mantener peso", "Ganar masa muscular", "Mejorar salud", "Mejorar rendimiento deportivo"].index(st.session_state.user_data.get('objetivo', "Mejorar salud")))
            save_user_data('objetivo', objetivo)
        
        if st.button("Siguiente"):
            next_step()
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.step == 2:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("## Medidas y Actividad Física")
        st.markdown("Estos datos nos ayudarán a calcular tus necesidades calóricas diarias.")
        
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
            
            # Mostrar explicación del nivel de actividad seleccionado
            actividad_descripciones = {
                "Sedentario": "Poco o ningún ejercicio, trabajo de oficina",
                "Ligero": "Ejercicio ligero 1-3 días/semana",
                "Moderado": "Ejercicio moderado 3-5 días/semana",
                "Activo": "Ejercicio intenso 6-7 días/semana",
                "Muy Activo": "Ejercicio muy intenso, entrenamiento físico o trabajo físico diario"
            }
            st.info(actividad_descripciones[actividad])
            
            # Mostrar IMC calculado
            if peso and estatura:
                imc = peso / ((estatura/100) ** 2)
                imc_categoria = ""
                if imc < 18.5:
                    imc_categoria = "Bajo peso"
                elif imc < 25:
                    imc_categoria = "Peso normal"
                elif imc < 30:
                    imc_categoria = "Sobrepeso"
                else:
                    imc_categoria = "Obesidad"
                
                st.metric("IMC (Índice de Masa Corporal)", f"{imc:.1f}", f"{imc_categoria}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Atrás"):
                prev_step()
        with col2:
            if st.button("Siguiente", key="next_step_2"):
                next_step()
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.step == 3:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("## Patologías y Restricciones")
        st.markdown("Esta información es crucial para adaptar el plan a tus necesidades específicas.")
        
        # Lista de patologías comunes para sugerir
        patologias_comunes = [
            "Diabetes Tipo 2",
            "Hipertensión",
            "Colesterol alto",
            "Hipotiroidismo",
            "Hipertiroidismo",
            "Celiaquía",
            "Síndrome de intestino irritable (SII)",
            "Reflujo gastroesofágico",
            "Obesidad",
            "Gota",
            "Artritis",
            "Osteoporosis",
            "Anemia",
            "Insuficiencia renal",
            "Hígado graso"
        ]
        
        # Lista de restricciones alimenticias comunes
        restricciones_comunes = [
            "Vegetariano",
            "Vegano",
            "Sin gluten",
            "Sin lactosa",
            "Sin azúcar",
            "Sin frutos secos",
            "Bajo en sodio",
            "Bajo en carbohidratos",
            "Kosher",
            "Halal",
            "Sin mariscos",
            "Sin huevo",
            "Sin soja",
            "Sin maíz",
            "FODMAP bajo"
        ]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Patologías")
            
            # Agregar patología personalizada
            nueva_patologia = st.text_input("Añadir patología (opcional)", key="nueva_patologia")
            if st.button("Agregar patología") and nueva_patologia:
                if nueva_patologia not in st.session_state.patologias_list:
                    st.session_state.patologias_list.append(nueva_patologia)
            
            # Seleccionar de lista predefinida
            patologia_seleccionada = st.selectbox("Seleccionar de lista común", 
                                                 options=[""] + patologias_comunes,
                                                 index=0,
                                                 key="patologia_select")
            if st.button("Añadir de lista") and patologia_seleccionada:
                if patologia_seleccionada not in st.session_state.patologias_list:
                    st.session_state.patologias_list.append(patologia_seleccionada)
            
            # Mostrar lista actual y permitir eliminación
            st.markdown("#### Patologías agregadas:")
            for i, patologia in enumerate(st.session_state.patologias_list):
                col_p1, col_p2 = st.columns([4, 1])
                with col_p1:
                    st.markdown(f"{patologia}")
                with col_p2:
                    if st.button("❌", key=f"del_pat_{i}"):
                        st.session_state.patologias_list.pop(i)
                        st.experimental_rerun()
            
            save_user_data('patologias', st.session_state.patologias_list)
        
        with col2:
            st.markdown("### Restricciones Alimenticias")
            
            # Agregar restricción personalizada
            nueva_restriccion = st.text_input("Añadir restricción (opcional)", key="nueva_restriccion")
            if st.button("Agregar restricción") and nueva_restriccion:
                if nueva_restriccion not in st.session_state.restricciones_list:
                    st.session_state.restricciones_list.append(nueva_restriccion)
            
            # Seleccionar de lista predefinida
            restriccion_seleccionada = st.selectbox("Seleccionar de lista común", 
                                                   options=[""] + restricciones_comunes,
                                                   index=0,
                                                   key="restriccion_select")
            if st.button("Añadir de lista") and restriccion_seleccionada:
                if restriccion_seleccionada not in st.session_state.restricciones_list:
                    st.session_state.restricciones_list.append(restriccion_seleccionada)
            
            # Mostrar lista actual y permitir eliminación
            st.markdown("#### Restricciones agregadas:")
            for i, restriccion in enumerate(st.session_state.restricciones_list):
                col_r1, col_r2 = st.columns([4, 1])
                with col_r1:
                    st.markdown(f"{restriccion}")
                with col_r2:
                    if st.button("❌", key=f"del_res_{i}"):
                        st.session_state.restricciones_list.pop(i)
                        st.experimental_rerun()
            
            save_user_data('restricciones', st.session_state.restricciones_list)
        
        # Comentarios adicionales
        st.markdown("### Comentarios Adicionales")
        comentarios = st.text_area("Cualquier información adicional relevante para tu plan nutricional",
                                  value=st.session_state.user_data.get('comentarios', ''),
                                  placeholder="Ej. Preferencias de alimentos, horarios especiales, etc.",
                                  height=100)
        save_user_data('comentarios', comentarios)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Atrás", key="prev_step_3"):
                prev_step()
        with col2:
            if st.button("Generar Plan Nutricional"):
                # Validar datos mínimos
                if not st.session_state.user_data.get('nombre') or not st.session_state.user_data.get('peso') or not st.session_state.user_data.get('estatura'):
                    st.error("Por favor completa al menos tu nombre, peso y estatura para generar el plan.")
                else:
                    # Generar reporte
                    with st.spinner("Generando tu plan nutricional personalizado..."):
                        reporte = generar_reporte(st.session_state.user_data)
                        st.session_state.report = reporte
                        next_step()
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.step == 4:
    with st.container():
        if st.session_state.report:
            # Encabezado del reporte
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("## Tu Plan Nutricional Personalizado")
            st.markdown(f"<div class='report-header'><h3>Reporte para: {st.session_state.user_data.get('nombre', 'Usuario')}</h3><div class='report-date'>Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div></div>", unsafe_allow_html=True)
            
            # Sección de resumen de datos del usuario
            st.markdown("### Información del usuario")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Edad", f"{st.session_state.user_data.get('edad', '-')} años")
                st.metric("Género", st.session_state.user_data.get('genero', '-'))
            with col2:
                st.metric("Peso", f"{st.session_state.user_data.get('peso', '-')} kg")