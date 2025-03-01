import streamlit as st
import openai
from fpdf import FPDF
import time

# Configurar la API key de OpenAI desde secrets
oai_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=oai_key)

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
    .stProgress>div {
        background-color: #FFD700 !important;  /* Color de barra de progreso */
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
    Debes proporcionar una dieta equilibrada y adecuada para la persona basada en sus datos, así como analizar las patologías.
    """
    
    # Simulación de progreso mientras se genera el reporte
    for i in range(1, 101):
        time.sleep(0.05)  # Simula tiempo de espera
        st.progress(i)  # Actualiza el progreso
    
    # Generar el reporte de OpenAI
    respuesta = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}]
    )
    return respuesta.choices[0].message.content

# Función para generar el PDF estilizado
def generar_pdf(reporte):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Título del reporte
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, 'Reporte Nutricional Personalizado', ln=True, align='C')
    pdf.ln(10)
    
    # Contenido del reporte
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, reporte)
    
    # Agregar más estilo (viñetas, subrayado, etc.)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(200, 10, 'Recomendaciones:', ln=True)
    pdf.set_font('Arial', '', 12)
    
    # Ejemplo de viñetas
    pdf.ln(5)
    pdf.cell(10, 10, "• ", ln=False)
    pdf.multi_cell(0, 10, "Mantener una dieta baja en azúcares para prevenir picos de glucosa.")
    pdf.cell(10, 10, "• ", ln=False)
    pdf.multi_cell(0, 10, "Asegúrate de consumir alimentos ricos en fibra para mejorar la digestión.")
    
    # Guardar el archivo PDF
    pdf_output = "/tmp/reporte_nutricional.pdf"
    pdf.output(pdf_output)
    
    return pdf_output

# Botón para generar el reporte
if st.sidebar.button("Generar Reporte Nutricional"):
    if nombre and edad and peso and estatura and actividad:
        # Mostrar la barra de progreso mientras se genera el reporte
        with st.spinner('Generando el reporte...'):
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

        # Generar el PDF estilizado y permitir la descarga
        pdf_file = generar_pdf(reporte)
        st.markdown(f'<a href="data:file/pdf;base64,{pdf_file}" download="Reporte_Nutricional.pdf">Descargar el reporte en PDF</a>', unsafe_allow_html=True)
    else:
        st.warning("Por favor, completa todos los campos obligatorios para generar el reporte.")
