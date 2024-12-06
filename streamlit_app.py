import streamlit as st
import os
import subprocess
from PIL import Image
import tempfile

# Virtualenv activation function
def activate_virtualenv():
    virtualenv_name = "kraken_env"
    virtualenv_path = os.path.expanduser(f"~/.virtualenvs/{virtualenv_name}/bin/activate")
    activate_command = f"bash -c 'source {virtualenv_path} && which kraken'"
    process = subprocess.run(activate_command, shell=True, capture_output=True, text=True)
    if process.returncode != 0:
        raise EnvironmentError(f"Failed to activate virtualenv: {process.stderr}")
    kraken_path = process.stdout.strip()
    return kraken_path

# Set up Streamlit app
st.title("OCR with Kraken")
st.write("Upload an image, and we'll extract the text using Kraken OCR.")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "tiff"])

with st.sidebar:
    st.header("OCR Settings")
    custom_model = st.text_input("Path to Custom Kraken Model (optional)", "")
    layout_analysis = st.checkbox("Enable Layout Analysis", value=False)
    binarization = st.checkbox("Enable Binarization", value=True)
    output_format = st.selectbox("Output Format", ["Plain Text", "JSON"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.read())
        input_image_path = tmp_file.name

    st.image(input_image_path, caption="Uploaded Image", use_column_width=True)

    if st.button("Run OCR"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_output:
            output_path = tmp_output.name

        # Activate the virtualenv and get the Kraken executable
        try:
            kraken_executable = activate_virtualenv()
        except EnvironmentError as e:
            st.error(f"Error activating virtual environment: {e}")
            st.stop()

        # Build Kraken OCR command
        command = [kraken_executable, "-i", input_image_path, output_path, "ocr"]
        if custom_model:
            command.extend(["-m", custom_model])
        if layout_analysis:
            command.append("-l")
        if not binarization:
            command.append("--no-binarization")
        if output_format == "JSON":
            command.extend(["--output-format", "json"])

        # Run Kraken
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                st.error(f"Error running Kraken OCR: {result.stderr}")
            else:
                with open(output_path, "r") as f:
                    ocr_text = f.read()
                st.subheader("OCR Output")
                if output_format == "Plain Text":
                    st.text_area("Extracted Text", ocr_text, height=300)
                else:
                    st.json(ocr_text)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

        os.remove(input_image_path)
        os.remove(output_path)
