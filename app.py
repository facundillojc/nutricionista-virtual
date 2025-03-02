import streamlit as st
import requests

# Configurar la API key de Hugging Face desde secrets
hf_api_key = st.secrets["HF_API_TOKEN"]
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"  # Corrección aquí
HEADERS = {"Authorization": f"Bearer {hf_api_key}"}

# Configuración de la página
st.set_page_config(page_title="Nutricionista Virtual", layout="wide")

# Estilos CSS personalizados para una apariencia premium
st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #1E1E1E;  /* Fondo negro mate */
        color: #F4F4F4;  /* Texto claro */
    }
    .report-container {
        background-color: #2A2A2A;  /* Fondo gris oscuro */
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);
        color: #F4F4F4;  /* Texto claro */
        font-size: 18px;
    }
    .stTextInput, .stNumberInput, .stTextArea {
        border-radius: 10px;
        background-color: #333333;  /* Fondo oscuro para inputs */
        color: #F4F4F4;  /* Texto claro */
        border: 1px solid #444444;  /* Borde oscuro */
    }
    .stButton>button {
        background-color: #FFD700;  /* Dorado */
        color: #1E1E1E;  /* Texto oscuro */
        font-size: 16px;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #FFB800;  /* Dorado más claro al pasar el mouse */
    }
    .sidebar .sidebar-content {
        background-color: #1E1E1E;  /* Fondo oscuro en el sidebar */
        color: #F4F4F4;  /* Texto claro */
        padding: 10px;
    }
    .sidebar .sidebar-header {
        font-size: 18px;
        font-weight: bold;
        color: #FFD700;  /* Color dorado en los títulos del sidebar */
    }
    .stSelectbox, .stMultiselect {
        background-color: #333333;  /* Fondo oscuro para select */
        color: #F4F4F4;  /* Texto claro */
        border: 1px solid #444444;  /* Borde oscuro */
    }
    .stMarkdown {
        color: #F4F4F4;  /* Texto claro */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Encabezado principal
st.title("Nutricionista Virtual")
st.markdown("### Obtén un plan de alimentación personalizado basado en tus necesidades")

# Sección de entrada de datos
st.sidebar.header("Ingresa tu información")
nombre = st.sidebar.text_input("Nombre")
edad = st.sidebar.number_input("Edad", min_value=1, max_value=100, step=1)
peso = st.sidebar.number_input("Peso (kg)", min_value=20.0, max_value=200.0, step=0.1)
estatura = st.sidebar.number_input("Estatura (cm)", min_value=100, max_value=220, step=1)
actividad = st.sidebar.selectbox("Nivel de actividad", ["Sedentario", "Ligero", "Moderado", "Activo", "Muy Activo"])
patologias = st.sidebar.text_area("Patologías (separadas por coma)")
restricciones = st.sidebar.text_area("Restricciones alimenticias (separadas por coma)")

# Función para generar el reporte nutricional con Mistral-7B-Instruct
def generar_reporte(datos_usuario):
    prompt = f"""
    Genera un plan de alimentación personalizado para:
    - Nombre: {datos_usuario['nombre']}
    - Edad: {datos_usuario['edad']} años
    - Peso: {datos_usuario['peso']} kg
    - Estatura: {datos_usuario['estatura']} cm
    - Nivel de actividad: {datos_usuario['actividad']}
    - Patologías: {datos_usuario['patologias']}
    - Restricciones alimenticias: {datos_usuario['restricciones']}
    
    **Análisis de las patologías:**
    - Realiza un análisis detallado de las patologías que el usuario presenta.
    - Proporciona recomendaciones nutricionales personalizadas considerando cada patología.
    - Informa sobre alimentos que deben evitarse debido a cada patología, y por qué.
    - Ofrece alternativas alimenticias que sean apropiadas para las patologías mencionadas.

    Debes proporcionar una dieta equilibrada y adecuada para la persona basada en sus datos, y un análisis detallado de las patologías.
    """

    # Llamada a la API de Hugging Face
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 1000,  # Aumentado para reportes más largos
            "temperature": 0.7,  # Controla la creatividad
            "top_p": 0.9         # Para respuestas más coherentes
        }
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    
    # Verificación de la respuesta
    if response.status_code == 200:
        result = response.json()
        return result[0]["generated_text"]
    else:
        return f"Error al consultar el modelo: {response.status_code} - {response.text}"

# Botón para generar el reporte
if st.sidebar.button("Generar Reporte Nutricional"):
    if nombre and edad and peso and estatura and actividad:
        datos_usuario = {
            "nombre": nombre,
            "edad": edad,
            "peso": peso,
            "estatura": estatura,
            "actividad": actividad,
            "patologias": patologias,
            "restricciones": restricciones,
        }
        
        with st.spinner("Generando tu reporte nutricional..."):
            reporte = generar_reporte(datos_usuario)
        
        # Mostrar el reporte en una caja estilizada
        st.markdown("## Reporte Nutricional Personalizado")
        st.markdown(f"<div class='report-container'><p>{reporte}</p></div>", unsafe_allow_html=True)
    else:
        st.warning("Por favor, completa todos los campos obligatorios para generar el reporte.")