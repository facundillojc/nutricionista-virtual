import streamlit as st
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# Función para generar el PDF
def generar_pdf(datos_usuario):
    try:
        # Crear un buffer para almacenar el archivo PDF
        buffer = BytesIO()
        
        # Crear un lienzo de ReportLab para generar el PDF
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Escribir el contenido en el PDF
        c.drawString(100, 750, f"Reporte Nutricional de {datos_usuario['nombre']}")
        c.drawString(100, 730, f"Edad: {datos_usuario['edad']} años")
        c.drawString(100, 710, f"Peso: {datos_usuario['peso']} kg")
        c.drawString(100, 690, f"Estatura: {datos_usuario['estatura']} cm")
        c.drawString(100, 670, f"Nivel de actividad: {datos_usuario['actividad']}")
        c.drawString(100, 650, f"Patologías: {datos_usuario['patologias']}")
        c.drawString(100, 630, f"Restricciones alimenticias: {datos_usuario['restricciones']}")
        
        c.drawString(100, 610, "Recomendaciones alimenticias:")
        y_position = 590
        for recomendacion in datos_usuario['recomendaciones']:
            c.drawString(100, y_position, f"• {recomendacion}")
            y_position -= 20
        
        # Finalizar y guardar el archivo PDF
        c.showPage()
        c.save()
        
        # Mover el buffer al inicio para poder leer el archivo
        buffer.seek(0)
        
        # Devolver el buffer como archivo PDF
        return buffer
    
    except Exception as e:
        st.error(f"Error generando el PDF: {e}")
        return None

# Función para mostrar la barra de progreso
def mostrar_barra_progreso():
    try:
        progreso = st.progress(0)
        mensaje = st.empty()
        mensaje.markdown("Generando tu reporte, por favor espera...")
        
        # Simular un proceso largo con una barra de progreso
        for i in range(100):
            time.sleep(0.05)  # Simula tiempo de procesamiento
            progreso.progress(i + 1)
        
        # Finalizar la barra de progreso
        mensaje.empty()
    
    except Exception as e:
        st.error(f"Error mostrando la barra de progreso: {e}")

# Función principal de la aplicación
def app():
    try:
        st.title("Generador de Reporte Nutricional")
        
        # Mensaje de depuración para verificar que se carga la aplicación correctamente
        st.write("Aplicación cargada correctamente.")

        # Datos de ejemplo (esto lo podrías reemplazar por un formulario en vivo)
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

        # Botón para generar el reporte
        if st.button("Generar Reporte"):
            # Depuración: Verificar si el botón funciona
            st.write("Generando reporte...")
            
            # Mostrar barra de progreso mientras se genera el reporte
            mostrar_barra_progreso()

            # Generar el reporte PDF
            pdf_buffer = generar_pdf(datos_usuario)
            
            if pdf_buffer:
                st.write("PDF generado con éxito.")
                # Mostrar el reporte
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
            else:
                st.error("Hubo un error al generar el reporte PDF.")
    
    except Exception as e:
        st.error(f"Error en la aplicación: {e}")

# Ejecutar la aplicación
if __name__ == "__main__":
    app()
