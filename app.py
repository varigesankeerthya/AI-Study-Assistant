
import streamlit as st
from google import genai
from dotenv import load_dotenv
from pypdf import PdfReader
import os

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Page settings
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚"
)

# App title
st.title("📚 AI Study Assistant")
st.write("Your personal AI learning partner!")

# Check API key
if not api_key:
    st.error("Gemini API key not found!")
    st.stop()

# Connect to Gemini
client = genai.Client(api_key=api_key)

# Initialize PDF text
pdf_text = ""

# PDF upload
uploaded_file = st.file_uploader(
    "📄 Upload your study PDF",
    type=["pdf"]
)

# Read PDF
if uploaded_file:
    try:
        pdf_reader = PdfReader(uploaded_file)

        for page in pdf_reader.pages:
            pdf_text += page.extract_text() or ""

        st.success("PDF uploaded and read successfully!")

        # PDF Summarization
        if st.button("📝 Summarize PDF"):
            if not pdf_text.strip():
                st.warning("No readable text found in this PDF.")
            else:
                with st.spinner("Generating summary..."):
                    try:
                        summary = client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=(
                                "Summarize this study material in simple "
                                "language. Include headings and important points:\n\n"
                                + pdf_text
                            ),
                            config={
                                "http_options": {
                                    "timeout": 30000
                                }
                            }
                        )

                        st.subheader("📖 PDF Summary")
                        st.write(summary.text)

                    except Exception as e:
                        st.error(f"Summary Error: {e}")

    except Exception as e:
        st.error(f"PDF Reading Error: {e}")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User question
user_input = st.chat_input("Ask your study question...")

if user_input:

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=(
                        "You are an AI Study Assistant. "
                        "Explain topics in simple language with examples.\n\n"
                        "Use the uploaded PDF content to answer questions "
                        "when relevant.\n\n"
                        + pdf_text
                        + "\n\nStudent question: "
                        + user_input
                    ),
                    config={
                        "http_options": {
                            "timeout": 30000
                        }
                    }
                )

                answer = response.text or "No response generated."
                st.write(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error(f"Gemini Error: {e}")
