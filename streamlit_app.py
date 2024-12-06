import streamlit as st
import os
import subprocess
from PIL import Image
import tempfile

# Virtualenv activation function
def activate_virtualenv():
    virtualenv_name = "kraken_env"
    virtualenv_path = os.path.expanduser(f"~/.virtualenvs/{virtualenv_name}/bin/activate")
    activate_command = f"source {virtualenv_path} && which kraken"
    process = subprocess.run(activate_command, shell=True, capture_output=True, text=True)
    if process.returncode != 0:
        raise EnvironmentError(f"Failed to activate virtualenv: {process.stderr}")
    kraken_path = process.stdout.strip()
    return kraken_path

# Set up Streamlit app
st.title("OCR with Kraken")
st.write("Upload an image, and we'll extract the text using Kraken OCR.")

# Upload image
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "tiff"])

# Select OCR options
with st.sidebar:
    st.header("OCR Settings")
    custom_model = st.text_input("Path to Custom Kraken Model (optional)", "")
    layout_analysis = st.checkbox("Enable Layout Analysis", value=False)
    binarization = st.checkbox("Enable Binarization", value=True)
    output_format = st.selectbox("Output Format", ["Plain Text", "JSON"])

if uploaded_file:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.read())
        input_image_path = tmp_file.name

    st.image(input_image_path, caption="Uploaded Image", use_column_width=True)

    # Run OCR on the uploaded image when the button is clicked
    if st.button("Run OCR"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_output:
            output_path = tmp_output.name

        # Build Kraken OCR command
        command = ["kraken", "-i", input_image_path, output_path, "ocr"]

        # Add model if provided
        if custom_model:
            command.extend(["-m", custom_model])

        # Enable/disable layout analysis
        if layout_analysis:
            command.append("-l")

        # Disable binarization if unchecked
        if not binarization:
            command.append("--no-binarization")

        # Set output format
        if output_format == "JSON":
            command.extend(["--output-format", "json"])

        # Run Kraken command
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                st.error(f"Error running Kraken OCR: {result.stderr}")
            else:
                # Display the OCR output
                with open(output_path, "r") as f:
                    ocr_text = f.read()
                st.subheader("OCR Output")
                if output_format == "Plain Text":
                    st.text_area("Extracted Text", ocr_text, height=300)
                elif output_format == "JSON":
                    st.json(ocr_text)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

        # Clean up temporary files
        os.remove(input_image_path)
        os.remove(output_path)

