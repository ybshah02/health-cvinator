import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

from src.cover_letter_generator import CoverLetterGenerator
from src.config import Config
from src.constants import *
from src.utils import validate_inputs, display_error, display_success, display_warning

load_dotenv()

st.set_page_config(
    page_title="Cover Letter Generator",
    page_icon="📝",
    layout="wide"
)

def main():
    st.sidebar.title("Leks CV Generator")
    
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Generate Cover Letter", "Improve Cover Letter"]
    )
    
    if page == "Generate Cover Letter":
        generate_page()
    elif page == "Improve Cover Letter":
        improve_page()

def generate_page():
    st.title("📝 Generate New Cover Letter")
    st.markdown("Generate professional cover letters for healthcare positions using AI")
    
    api_key = os.getenv("GOOGLE_API_KEY", "")
    
    if not api_key:
        st.error("Please set your GOOGLE_API_KEY environment variable")
        st.stop()
    
    if 'generator' not in st.session_state:
        st.session_state.generator = CoverLetterGenerator()
    
    st.session_state.generator.load_static_content()
    
    # Main content in a single column for better flow
    st.header("📄 Job Information")
    
    col_job1, col_job2 = st.columns([2, 1])
    with col_job1:
        job_url = st.text_input(
            LABEL_JOB_URL,
            help=HELP_JOB_URL
        )
    with col_job2:
        job_title = st.text_input(
            "Job Title (optional)",
            help="Enter the job title if not auto-detected"
        )
    
    company_name = st.text_input(
        "Company Name (optional)",
        help="Enter the company name if not auto-detected"
    )
    
    job_description = st.text_area(
        LABEL_JOB_DESCRIPTION,
        height=200,
        help=HELP_JOB_DESCRIPTION
    )
    
    if job_url and not job_description:
        with st.spinner("Extracting job information..."):
            try:
                extracted_info = st.session_state.generator.extract_job_info(job_url)
                if extracted_info:
                    job_description = extracted_info
                    st.text_area("Extracted Job Description", value=job_description, height=200)
            except Exception as e:
                st.warning(f"⚠️ {str(e)}")
                st.info("💡 **Tip**: You can still generate a cover letter by manually copying and pasting the job description into the text area above.")
    
    st.header("📋 Your Resume")
    
    resume_file = st.file_uploader(
        LABEL_RESUME_UPLOAD,
        type=SUPPORTED_FILE_TYPES,
        help=HELP_RESUME_UPLOAD
    )
    
    resume_text = ""
    if resume_file:
        with st.spinner("Processing resume file..."):
            if resume_file.type == "application/pdf":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(resume_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                try:
                    from langchain.document_loaders import PyPDFLoader
                    loader = PyPDFLoader(tmp_file_path)
                    docs = loader.load()
                    resume_text = "\n".join([doc.page_content for doc in docs])
                finally:
                    os.unlink(tmp_file_path)
            elif resume_file.type == "text/plain":
                resume_text = resume_file.getvalue().decode("utf-8")
        
        # Resume content is loaded but not displayed to keep UI clean
    
    st.header("📁 Context Files")
    
    context_files = st.file_uploader(
        "Upload context files",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        help=HELP_CONTEXT_FILES
    )
    
    if context_files:
        with st.spinner("Processing uploaded files..."):
            num_docs = st.session_state.generator.load_context_files(context_files)
            display_success(SUCCESS_CONTEXT_PROCESSED.format(num_docs=num_docs))
    
    additional_context = st.text_area(
        LABEL_ADDITIONAL_CONTEXT,
        height=100,
        help=HELP_ADDITIONAL_CONTEXT
    )
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.header("🔧 Generate Cover Letter")
        
        if st.button(LABEL_GENERATE_COVER_LETTER, type="primary", use_container_width=True):
            is_valid, error_message = validate_inputs(resume_text, job_description, api_key)
            
            if not is_valid:
                display_error(error_message)
            else:
                with st.spinner("Generating your cover letter..."):
                    try:
                        cover_letter = st.session_state.generator.generate_cover_letter(
                            resume_text, 
                            job_description, 
                            job_url, 
                            additional_context,
                            job_title,
                            company_name
                        )
                        
                        if cover_letter:
                            display_success(SUCCESS_COVER_LETTER_GENERATED)
                            
                            st.header("📝 Generated Cover Letter")
                            st.text_area(LABEL_COVER_LETTER, value=cover_letter, height=400)
                            
                            pdf_data = st.session_state.generator.create_pdf(cover_letter)
                            
                            st.download_button(
                                label=LABEL_DOWNLOAD_PDF,
                                data=pdf_data,
                                file_name=DEFAULT_PDF_FILENAME,
                                mime=PDF_MIME_TYPE,
                                use_container_width=True
                            )
                        else:
                            display_error("Failed to generate cover letter. Please check your inputs and try again.")
                    except Exception as e:
                        display_error(ERROR_GENERATING_COVER_LETTER.format(error=str(e)))

def improve_page():
    st.title("✨ Improve Existing Cover Letter")
    st.markdown("Upload your existing cover letter and specify what you'd like to improve")
    
    api_key = os.getenv("GOOGLE_API_KEY", "")
    
    if not api_key:
        st.error("Please set your GOOGLE_API_KEY environment variable")
        st.stop()
    
    if 'generator' not in st.session_state:
        st.session_state.generator = CoverLetterGenerator()
    
    st.session_state.generator.load_static_content()
    
    st.header("📄 Upload Cover Letter")
    
    cover_letter_file = st.file_uploader(
        "Upload your cover letter",
        type=['pdf', 'txt', 'docx'],
        help="Upload a PDF, TXT, or DOCX file containing your cover letter"
    )
    
    existing_cover_letter = ""
    
    if cover_letter_file:
        with st.spinner("Processing cover letter..."):
            try:
                if cover_letter_file.type == "application/pdf":
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(cover_letter_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    try:
                        from PyPDF2 import PdfReader
                        reader = PdfReader(tmp_file_path)
                        existing_cover_letter = "\n".join([page.extract_text() for page in reader.pages])
                    finally:
                        os.unlink(tmp_file_path)
                elif cover_letter_file.type == "text/plain":
                    existing_cover_letter = cover_letter_file.getvalue().decode("utf-8")
                elif cover_letter_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    st.warning("DOCX files are not yet supported. Please convert to PDF or TXT format.")
                    existing_cover_letter = ""
                
                if existing_cover_letter:
                    st.success("✅ Cover letter loaded successfully!")
                    st.text_area("Loaded Cover Letter", value=existing_cover_letter, height=200, disabled=True)
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    # Alternative: paste text directly
    st.markdown("**Or paste your cover letter directly:**")
    pasted_cover_letter = st.text_area(
        "Paste your cover letter here",
        height=200,
        help="Alternative to file upload - paste your cover letter text directly"
    )
    
    if pasted_cover_letter:
        existing_cover_letter = pasted_cover_letter
    
    st.header("🎯 Improvement Instructions")
    
    improvement_prompt = st.text_area(
        "What would you like to improve?",
        value="Improve it by ensuring it follows these 5 key rules of a good cover letter:\n1. Strengthen the opening hook to grab attention\n2. Make my experience & achievements more quantifiable & impactful\n3. Show a stronger connection to the company's mission & values\n4. Improve the closing statement with a more compelling call to action\n5. Ensure conciseness, structured formatting, and a professional tone (250-400 words, 1 page)\n\nPlease rewrite it while keeping my unique experiences and voice, but making it more engaging and aligned with best practices.",
        height=150,
        help="Describe what specific improvements you'd like to make to your cover letter"
    )
    
    if st.button("✨ Improve Cover Letter", type="primary", use_container_width=True):
        if existing_cover_letter.strip():
            with st.spinner("Improving your cover letter..."):
                try:
                    improved_letter = st.session_state.generator.improve_cover_letter_with_prompt(
                        existing_cover_letter, 
                        improvement_prompt
                    )
                    
                    if improved_letter:
                        display_success("✅ Cover letter improved successfully!")
                        
                        st.header("📝 Improved Cover Letter")
                        st.text_area("Improved Cover Letter", value=improved_letter, height=400)
                        
                        pdf_data = st.session_state.generator.create_pdf(improved_letter)
                        
                        st.download_button(
                            label=LABEL_DOWNLOAD_PDF,
                            data=pdf_data,
                            file_name="improved_cover_letter.pdf",
                            mime=PDF_MIME_TYPE,
                            use_container_width=True
                        )
                    else:
                        display_error("Failed to improve cover letter. Please try again.")
                except Exception as e:
                    display_error(f"Error improving cover letter: {str(e)}")
        else:
            display_error("Please upload a cover letter file or paste your cover letter text.")

if __name__ == "__main__":
    main()
