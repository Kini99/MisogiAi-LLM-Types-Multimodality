import streamlit as st
import requests
import os
from PIL import Image
from io import BytesIO
import google.generativeai as genai
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Load environment variables
load_dotenv(".env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Multimodal QA Agent", layout="centered")
st.title("🖼️ Multimodal QA Agent (Gemini 2.0 Flash)")

st.markdown("""
Upload an image or provide an image URL, ask a question about it, and get an answer from Gemini 2.0 Flash!
""")

# Image input
img_source = st.radio("Image Source", ["Upload", "URL"])
img = None
img_bytes = None

if img_source == "Upload":
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img_bytes = uploaded_file.read()
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
else:
    img_url = st.text_input("Enter image URL:")
    if img_url:
        try:
            response = requests.get(img_url)
            img_bytes = response.content
            img = Image.open(BytesIO(img_bytes)).convert("RGB")
        except Exception as e:
            st.error(f"Failed to load image: {e}")

question = st.text_input("Ask a question about the image:")

if st.button("Ask") and img and question:
    st.image(img, caption="Input Image", use_container_width=True)
    st.write("**Question:**", question)
    try:
        # Gemini 2.0 Flash Vision + Language
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content([
            {
                "mime_type": "image/jpeg",
                "data": img_bytes
            },
            question
        ])
        answer = response.text
        st.success(f"**Answer:** {answer}")

        # Try to visualize bounding boxes if present in the response
        if hasattr(response, 'candidates'):
            for cand in response.candidates:
                if hasattr(cand, 'bounding_boxes') and cand.bounding_boxes:
                    st.write("Detected bounding boxes:")
                    fig, ax = plt.subplots()
                    ax.imshow(img)
                    for box in cand.bounding_boxes:
                        x, y, w, h = box['x'], box['y'], box['width'], box['height']
                        rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor='r', facecolor='none')
                        ax.add_patch(rect)
                    st.pyplot(fig)
    except Exception as e:
        st.warning(f"Multimodal analysis failed: {e}. Falling back to text-only LLM.")
        # Fallback: text-only
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            fallback_prompt = f"Image could not be analyzed. Here is the user's question: {question}"
            response = model.generate_content([fallback_prompt])
            answer = response.text
            st.info(f"**Text-only Answer:** {answer}")
        except Exception as e2:
            st.error(f"Text-only fallback also failed: {e2}")

st.markdown("---")
st.markdown("Built with [Gemini 2.0 Flash](https://ai.google.dev/)") 