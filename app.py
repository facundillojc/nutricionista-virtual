import streamlit as st
import openai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from fpdf import FPDF
import time

# Set your OpenAI API key here
openai.api_key = 'your-openai-api-key'

# Function to generate PDF using ReportLab
def generate_report_with_reportlab(user_data):
    file_path = "/tmp/report.pdf"  # Temporary location to save the PDF
    c = canvas.Canvas(file_path, pagesize=letter)

    c.drawString(100, 750, "Reporte Nutricional")
    c.drawString(100, 730, f"Nombre: {user_data['name']}")
    c.drawString(100, 710, f"Edad: {user_data['age']}")
    c.drawString(100, 690, f"Peso: {user_data['weight']} kg")
    c.drawString(100, 670, f"Altura: {user_data['height']} cm")
    
    c.showPage()
    c.save()
    return file_path

# Function to generate PDF using FPDF
def generate_report_with_fpdf(user_data):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reporte Nutricional", ln=True, align='C')
    pdf.ln(10)  # Line break
    
    pdf.cell(200, 10, f"Nombre: {user_data['name']}")
    pdf.ln(10)
    pdf.cell(200, 10, f"Edad: {user_data['age']}")
    pdf.ln(10)
    pdf.cell(200, 10, f"Peso: {user_data['weight']} kg")
    pdf.ln(10)
    pdf.cell(200, 10, f"Altura: {user_data['height']} cm")

    file_path = "/tmp/report_fpdf.pdf"  # Temporary location to save the PDF
    pdf.output(file_path)
    return file_path

# Function to call OpenAI and get a response
def get_openai_response(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Streamlit UI
def main():
    st.title("Generador de Reporte Nutricional")
    st.write("Aplicación cargada correctamente.")
    
    # User data input form
    with st.form("user_data_form"):
        name = st.text_input("Nombre")
        age = st.number_input("Edad", min_value=0)
        weight = st.number_input("Peso (kg)", min_value=0.0, step=0.1)
        height = st.number_input("Altura (cm)", min_value=0)
        
        submit_button = st.form_submit_button("Generar Reporte")
    
    if submit_button:
        # User input data dictionary
        user_data = {
            "name": name,
            "age": age,
            "weight": weight,
            "height": height
        }

        # Progress bar for report generation
        progress_bar = st.progress(0)
        progress_text = st.empty()

        # Simulate report generation with incremental progress
        for i in range(1, 101):
            time.sleep(0.05)  # Simulating some processing time
            progress_bar.progress(i)
            progress_text.text(f"Generando reporte... {i}%")
        
        # Generate PDF
        if user_data["weight"] > 0 and user_data["height"] > 0:
            st.write("Generando reporte con ReportLab...")
            report_path = generate_report_with_reportlab(user_data)
        else:
            st.write("Generando reporte con FPDF...")
            report_path = generate_report_with_fpdf(user_data)

        # Provide the download link
        st.write(f"Reporte generado correctamente! Puedes [descargarlo aquí]({report_path}).")

        # Hide the progress bar once the report is generated
        progress_bar.empty()
        progress_text.empty()

        # Optionally, get additional nutritional advice from OpenAI
        prompt = f"Generar un consejo nutricional para una persona de {age} años, peso {weight} kg y altura {height} cm."
        nutritional_advice = get_openai_response(prompt)
        st.write("Consejo nutricional:")
        st.write(nutritional_advice)

if __name__ == "__main__":
    main()
