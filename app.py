import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import time

# Función para generar el PDF con estilo usando ReportLab
def generar_pdf(datos_usuario):
    # Crear un objeto de archivo en memoria
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Estilo del PDF
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, f"Reporte de {datos_usuario['nombre']}")
    
    # Agregar datos con un poco de estilo
    y_position = 730
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y_position, f"Edad: {datos_usuario['edad']} años")
    y_position -= 20
    c.setFont("Helvetica", 12)
    c.drawString(100, y_position, f"Peso: {datos_usuario['peso']} kg")
    y_position -= 20
    c.drawString(100, y_position, f"Estatura: {datos_usuario['estatura']} cm")
    y_position -= 20
    c.drawString(100, y_position, f"Nivel de actividad: {datos_usuario['actividad']}")
    y_position -= 20
    c.drawString(100, y_position, f"Patologías: {datos_usuario['patologias']}")
    y_position -= 20
    c.drawString(100, y_position, f"Restricciones alimenticias: {datos_usuario['restricciones']}")
    
    # Agregar una lista con viñetas
    y_position -= 20
    c.setFont("Helvetica", 12)
    c.drawString(100, y_position, "Recomendaciones alimenticias:")
    y_position -= 20
    
    for recomendacion in datos_usuario['recomendaciones']:
        c.drawString(120, y_position, f"• {recomendacion}")
        y_position -= 20
    
    # Guardar el PDF en el buffer
    c.showPage()
    c.save()
    buffer.seek(0)
    
    return buffer

# Función para mostrar la barra de progreso
def mostrar_barra_progreso():
    progreso = st.progress(0)
    mensaje = st.empty()
    mensaje.markdown("Generando tu reporte, por favor espera...")
    
    for i in range(100):
        time.sleep(0.05)  # Simula tiempo de procesamiento
        progreso.progress(i + 1)
    
    # Una vez que el reporte está listo, eliminamos la barra de progreso
    mensaje.empty()

# Función principal de Streamlit
def app():
    st.title("Generador de Reporte Nutricional")
    
    # Datos de ejemplo
    datos_usuario = {
        'nombre': 'Juan Pérez',
        'edad': 30,
        'peso': 75,
        'estatura': 175,
        'actividad': 'Moderada',
        'patologias': 'Ninguna',
        'restricciones': 'Ninguna',
        'recomendaciones': [
            'Incluir más vegetales en la dieta',
            'Beber más agua',
            'Hacer ejercicio regularmente'
        ]
    }

    # Botón de generación de reporte
    if st.button("Generar Reporte"):
        # Mostrar barra de progreso mientras se genera el reporte
        mostrar_barra_progreso()

        # Generar el reporte PDF
        pdf_buffer = generar_pdf(datos_usuario)
        
        # Mostrar el reporte en pantalla
        st.subheader(f"Reporte de {datos_usuario['nombre']}")
        st.text(f"Edad: {datos_usuario['edad']} años")
        st.text(f"Peso: {datos_usuario['peso']} kg")
        st.text(f"Estatura: {datos_usuario['estatura']} cm")
        st.text(f"Nivel de actividad: {datos_usuario['actividad']}")
        st.text(f"Patologías: {datos_usuario['patologias']}")
        st.text(f"Restricciones alimenticias: {datos_usuario['restricciones']}")
        
        st.subheader("Recomendaciones alimenticias:")
        for recomendacion in datos_usuario['recomendaciones']:
            st.text(f"• {recomendacion}")

        # Botón para descargar el PDF
        st.download_button(
            label="Descargar Reporte en PDF",
            data=pdf_buffer,
            file_name="reporte_nutricional.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    app()
