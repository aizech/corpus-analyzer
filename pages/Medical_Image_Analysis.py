import os
import io
import streamlit as st
import pydicom
import numpy as np
from agno.media import Image as AgnoImage
from agents.medical_agent import agent
from PIL import Image as PILImage
from config import config
import datetime


# Set page config
st.set_page_config(
    page_title=f"{config.APP_NAME} - Medical Image Analysis",
    page_icon="🩺",
    layout="wide",
)

# Logo in sidebar
st.logo(config.LOGO_TEXT_PATH,
    size="large",
    icon_image=config.LOGO_ICON_PATH
)

def main():
    with st.sidebar:
        st.info(
            "This tool provides AI-powered analysis of medical imaging data using "
            "advanced computer vision and radiological expertise."
        )
        st.warning(
            "DISCLAIMER: This tool is for show cases and informational purposes only. "
            "All analyses should be reviewed by qualified healthcare professionals. "
            "Do not make medical decisions based solely on this analysis."
        )

    # Page title
    one_cola = st.columns([1])[0]
    with one_cola:
        col1a, col2a = st.columns([1, 5])

        with col1a:
            team_image = config.ASSETS_DIR / "godsinwhite_radiologist.png" 
            st.image(team_image, width=100)
        with col2a:
            st.markdown("""
            # Medical Imaging Diagnosis Agent  
            Upload a medical image for professional analysis
            """, unsafe_allow_html=True)

    # Create containers for better organization
    upload_container = st.container()
    image_container = st.container()
    analysis_container = st.container()

    with upload_container:
        uploaded_file = st.file_uploader(
            "Upload medical image",
            type=["jpg", "jpeg", "png", "dicom", "dcm"],
            help="Supported formats: JPG, JPEG, PNG, DICOM, DCM",
            label_visibility="collapsed",
        )

    if uploaded_file is not None:
        with image_container:
            # Check if file is DICOM or regular image
            file_extension = uploaded_file.name.split('.')[-1].lower()

            if file_extension in ['dicom', 'dcm'] or uploaded_file.type == 'application/dicom':
                # Handle DICOM files
                try:
                    uploaded_file.seek(0)
                    dicom_data = pydicom.dcmread(uploaded_file)

                    img_array = dicom_data.pixel_array
                    img_array = img_array / img_array.max() * 255
                    img_array = img_array.astype(np.uint8)

                    pil_image = PILImage.fromarray(img_array)
                    if len(img_array.shape) == 2:
                        pil_image = pil_image.convert('RGB')
                except Exception as e:
                    st.error(f"Error processing DICOM file: {str(e)}")
                    st.stop()
            else:
                pil_image = PILImage.open(uploaded_file)

            # Resize the image for display
            width, height = pil_image.size
            aspect_ratio = width / height
            new_width = 500
            new_height = int(new_width / aspect_ratio)
            resized_image = pil_image.resize((new_width, new_height))

            # Center the preview image, but keep the controls full-width below
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(
                    resized_image,
                    caption="Uploaded Medical Image",
                    width="stretch",
                )

        with image_container:
            analyze_button = st.button(
                ":material/search: Analyze Image", type="primary", width="stretch"
            )

            if "additional_info" not in st.session_state:
                st.session_state.additional_info = ""

            prompt_templates = {
                "Answer in English": "Answer in English.",
                "Antworte auf Deutsch": "Antworte auf Deutsch.",
                "Radiology-style report": (
                    "Provide a radiology-style report with:\n"
                    "- Modality and study type (if apparent)\n"
                    "- Key findings\n"
                    "- Impression (most likely diagnosis + differential)\n"
                    "- Recommended next steps\n"
                    "Keep it concise."
                ),
                "Explain for patient": "Explain the findings in simple, patient-friendly language.",
                "Focus: red flags": "Focus on urgent findings / red flags and what to do next.",
                "Add patient context": (
                    "Patient context:\n"
                    "- Age: \n"
                    "- Sex: \n"
                    "- Symptoms: \n"
                    "- Relevant history: \n"
                    "- Clinical question: \n"
                ),
            }

            colp0, colp1, colp2, colp3, colp4 = st.columns([1.2, 6, 1, 1, 1])
            with colp0:
                st.caption("Quick prompts")
            with colp1:
                selected_template = st.selectbox(
                    "Quick prompts",
                    options=list(prompt_templates.keys()),
                    index=0,
                    key="quick_prompt_selector",
                    label_visibility="collapsed",
                )
            with colp2:
                if st.button(
                    ":material/input:",
                    width="stretch",
                    help="Replace the text field with this template",
                ):
                    st.session_state.additional_info = prompt_templates[selected_template]
                    st.rerun()
            with colp3:
                if st.button(
                    ":material/playlist_add:",
                    width="stretch",
                    help="Append this template to the text field",
                ):
                    existing = (st.session_state.additional_info or "").strip()
                    addition = prompt_templates[selected_template].strip()
                    st.session_state.additional_info = (
                        f"{existing}\n\n{addition}" if existing else addition
                    )
                    st.rerun()
            with colp4:
                if st.button(
                    ":material/delete:",
                    width="stretch",
                    help="Clear the text field",
                ):
                    st.session_state.additional_info = ""
                    st.rerun()

            additional_info = st.text_area(
                "Provide additional context about the image (e.g., patient history, symptoms)",
                placeholder="Enter any relevant information here...  e.g. Antworte auf Deutsch",
                key="additional_info",
                height=250,
            )

        with analysis_container:
            if analyze_button:
                image_path = "temp_medical_image.png"
                # Save the resized image
                resized_image.save(image_path, format="PNG")
                
                # Add DICOM metadata to additional info if available
                if file_extension == 'dicom' or uploaded_file.type == 'application/dicom':
                    try:
                        uploaded_file.seek(0)
                        dicom_data = pydicom.dcmread(uploaded_file)
                        dicom_info = f"\n\nDICOM Metadata:\n"
                        for tag in ['PatientID', 'PatientName', 'PatientAge', 'PatientSex', 'Modality', 'StudyDescription']:
                            if hasattr(dicom_data, tag) and getattr(dicom_data, tag) != '':
                                dicom_info += f"- {tag}: {getattr(dicom_data, tag)}\n"
                        
                        if additional_info:
                            additional_info += dicom_info
                        else:
                            additional_info = dicom_info
                    except Exception as e:
                        st.warning(f"Could not extract DICOM metadata: {str(e)}")

                with st.spinner(":material/cycle: Analyzing image... Please wait."):
                    try:
                        # Read the image file as binary
                        with open(image_path, "rb") as f:
                            image_bytes = f.read()
                        # creating an instance of Image
                        agno_image = AgnoImage(content=image_bytes, format="png")

                        prompt = (
                            f"Analyze this medical image considering the following context: {additional_info}"
                            if additional_info
                            else "Analyze this medical image and provide detailed findings."
                            + "\n\n"
                            + "If you are not sure about the diagnosis, please provide a possible diagnosis."
                            + "\n\n"
                            + "Answer in the language of the user. If it is not given, answer English."
                        )
                        model = "gpt-5"
                        response = agent.run(prompt, images=[agno_image], model=model)
                        st.markdown("### :material/diagnosis: Analysis Results")
                        st.markdown("---")
                        if hasattr(response, "content"):
                            st.markdown(response.content)
                        elif isinstance(response, str):
                            st.markdown(response)
                        elif isinstance(response, dict) and "content" in response:
                            st.markdown(response["content"])
                        else:
                            st.markdown(str(response))
                        st.markdown("---")
                        st.caption(
                            "Note: This analysis is generated by AI and should be reviewed by "
                            "a qualified healthcare professional."
                        )

                    except Exception as e:
                        st.error(f"Analysis error: {str(e)}")
                        st.info(
                            "Please try again or contact support if the issue persists."
                        )
                        print(f"Detailed error: {e}")
                    finally:
                        if os.path.exists(image_path):
                            os.remove(image_path)

    else:
        st.info(":material/upload: Please upload a medical image to begin analysis")


if __name__ == "__main__":
    main()
