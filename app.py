import streamlit as st
import openai
import os

# Cargar la API Key desde Streamlit secrets o variables de entorno
api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("No se encontró la API Key. Asegúrate de configurarla en Streamlit secrets o como variable de entorno.")
    st.stop()

# Inicializar OpenAI
client = openai.OpenAI(api_key=api_key)

def generar_reporte(datos_usuario):
    """Genera un reporte basado en los datos ingresados por el usuario usando OpenAI."""
    try:
        prompt = f"Genera un reporte nutricional basado en los siguientes datos: {datos_usuario}"
        
        respuesta = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}]
        )
        
        return respuesta.choices[0].message.content

    except openai.OpenAIError as e:
        st.error(f"Error al comunicarse con OpenAI: {e}")
        return None

# Interfaz en Streamlit
def main():
    st.title("Nutricionista Virtual 🍏")
    
    # Formulario de entrada
    nombre = st.text_input("Nombre")
    edad = st.number_input("Edad", min_value=1, max_value=120, step=1)
    altura = st.number_input("Altura (cm)", min_value=50, max_value=250, step=1)
    peso = st.number_input("Peso (kg)", min_value=10, max_value=300, step=1)
    objetivo = st.selectbox("Objetivo", ["Pérdida de peso", "Mantenimiento", "Ganancia muscular"])
    
    if st.button("Generar Reporte"):
        datos_usuario = {
            "nombre": nombre,
            "edad": edad,
            "altura": altura,
            "peso": peso,
            "objetivo": objetivo
        }
        
        reporte = generar_reporte(datos_usuario)
        
        if reporte:
            st.subheader("Tu Reporte Nutricional 📄")
            st.write(reporte)

if __name__ == "__main__":
    main()
