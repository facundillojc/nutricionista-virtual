import streamlit as st
import openai

# Cargar la API Key de los secretos de Streamlit
openai.api_key = st.secrets["OPENAI_API_KEY"]

def validar_reporte(reporte):
    """Valida que no haya alimentos en conflicto entre patologías."""
    reglas = [
        ("azúcar", ["diabetes"]),
        ("sal", ["hipertensión"]),
        ("proteína alta", ["enfermedad renal crónica"]),
    ]
    errores = []
    for alimento, patologias in reglas:
        for patologia in patologias:
            if patologia in reporte.lower() and alimento in reporte.lower():
                errores.append(f"Conflicto detectado: {alimento} en pacientes con {patologia}.")
    return errores

def generar_reporte(datos_usuario):
    """Genera el reporte nutricional utilizando GPT-4o."""
    prompt = f"""
    Eres un nutricionista clínico experto en dietas para pacientes con diversas patologías.
    Basado en la siguiente información del usuario:
    
    - Edad: {datos_usuario['edad']}
    - Peso: {datos_usuario['peso']} kg
    - Altura: {datos_usuario['altura']} cm
    - Patologías: {', '.join(datos_usuario['patologias'])}
    - Preferencias alimenticias: {datos_usuario['preferencias']}
    
    Sigue estas reglas al hacer recomendaciones:
    1. Evita alimentos perjudiciales para las patologías del usuario.
    2. Si hay conflictos entre patologías, prioriza la opción más segura.
    3. Explica claramente el porqué de cada recomendación.
    4. Proporciona un plan semanal detallado con desayuno, almuerzo y cena.
    
    Genera el reporte en un tono claro, estructurado y profesional.
    """
    
    respuesta = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}]
    )
    return respuesta["choices"][0]["message"]["content"]

def main():
    st.title("Nutricionista Virtual Especializado")
    st.write("Ingrese sus datos para recibir un plan nutricional personalizado.")
    
    edad = st.number_input("Edad", min_value=1, max_value=120, step=1)
    peso = st.number_input("Peso (kg)", min_value=20.0, max_value=200.0, step=0.1)
    altura = st.number_input("Altura (cm)", min_value=100, max_value=220, step=1)
    patologias = st.text_area("Patologías diagnosticadas (separadas por coma)").split(",")
    preferencias = st.text_area("Preferencias alimenticias o restricciones")
    
    if st.button("Generar Reporte"):
        datos_usuario = {
            "edad": edad,
            "peso": peso,
            "altura": altura,
            "patologias": [p.strip().lower() for p in patologias],
            "preferencias": preferencias
        }
        reporte = generar_reporte(datos_usuario)
        errores = validar_reporte(reporte)
        
        if errores:
            st.error("Se detectaron posibles errores en el reporte:")
            for error in errores:
                st.write(f"- {error}")
        else:
            st.success("Reporte generado con éxito")
            st.text_area("Reporte Nutricional", reporte, height=300)
            
if __name__ == "__main__":
    main()
