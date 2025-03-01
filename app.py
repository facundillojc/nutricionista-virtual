import streamlit as st
import openai

# Configurar la API key de OpenAI desde secrets
oai_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=oai_key)

# Configuración de la página
st.set_page_config(page_title="Nutricionista Virtual", layout="wide")

# Estilos CSS personalizados para una apariencia más deportiva y premium
st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f4f4f4;
        color: #333;
    }
    .report-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.1);
    }
    .stTextInput, .stNumberInput, .stTextArea {
        border-radius: 5px;
    }
    .stButton>button {
        background-color: #008CBA;
        color: white;
        font-size: 16px;
        border-radius: 10px;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #005F73;
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

# Función para generar el reporte nutricional
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
    Debes proporcionar una dieta equilibrada y adecuada para la persona basada en sus datos.
    """
    
    respuesta = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}]
    )
    return respuesta.choices[0].message.content

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
        
        reporte = generar_reporte(datos_usuario)
        
        # Mostrar el reporte en una caja estilizada
        st.markdown("## Reporte Nutricional Personalizado")
        st.markdown(f"<div class='report-container'><p>{reporte}</p></div>", unsafe_allow_html=True)
    else:
        st.warning("Por favor, completa todos los campos obligatorios para generar el reporte.")
