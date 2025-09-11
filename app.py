import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

# Apply performance optimizations
from src.performance_config import PerformanceConfig
PerformanceConfig.apply_environment_variables()

# Lazy imports to reduce initial load time
def get_cover_letter_generator():
    from src.cover_letter_generator import CoverLetterGenerator
    return CoverLetterGenerator

def get_config():
    from src.config import Config
    return Config

def get_constants():
    import src.constants as constants_module
    return {
        'SUCCESS_STATIC_CONTENT_LOADED': constants_module.SUCCESS_STATIC_CONTENT_LOADED,
        'SUCCESS_CONTEXT_PROCESSED': constants_module.SUCCESS_CONTEXT_PROCESSED,
        'SUCCESS_COVER_LETTER_GENERATED': constants_module.SUCCESS_COVER_LETTER_GENERATED,
        'ERROR_API_KEY_MISSING': constants_module.ERROR_API_KEY_MISSING,
        'ERROR_RESUME_MISSING': constants_module.ERROR_RESUME_MISSING,
        'ERROR_GENERATING_COVER_LETTER': constants_module.ERROR_GENERATING_COVER_LETTER,
        'ERROR_EXTRACTING_JOB_INFO': constants_module.ERROR_EXTRACTING_JOB_INFO,
        'SUPPORTED_FILE_TYPES': constants_module.SUPPORTED_FILE_TYPES,
        'PDF_MIME_TYPE': constants_module.PDF_MIME_TYPE,
        'TEXT_MIME_TYPE': constants_module.TEXT_MIME_TYPE,
        'DEFAULT_PDF_FILENAME': constants_module.DEFAULT_PDF_FILENAME,
        'DEFAULT_GEMINI_MODEL': constants_module.DEFAULT_GEMINI_MODEL,
        'DEFAULT_TEMPERATURE': constants_module.DEFAULT_TEMPERATURE,
        'LABEL_GENERATE_COVER_LETTER': constants_module.LABEL_GENERATE_COVER_LETTER,
        'LABEL_DOWNLOAD_PDF': constants_module.LABEL_DOWNLOAD_PDF,
        'LABEL_JOB_URL': constants_module.LABEL_JOB_URL,
        'LABEL_JOB_DESCRIPTION': constants_module.LABEL_JOB_DESCRIPTION,
        'LABEL_RESUME_CONTENT': constants_module.LABEL_RESUME_CONTENT,
        'LABEL_RESUME_UPLOAD': constants_module.LABEL_RESUME_UPLOAD,
        'LABEL_ADDITIONAL_CONTEXT': constants_module.LABEL_ADDITIONAL_CONTEXT,
        'LABEL_COVER_LETTER': constants_module.LABEL_COVER_LETTER,
        'HELP_JOB_URL': constants_module.HELP_JOB_URL,
        'HELP_JOB_DESCRIPTION': constants_module.HELP_JOB_DESCRIPTION,
        'HELP_RESUME_CONTENT': constants_module.HELP_RESUME_CONTENT,
        'HELP_RESUME_UPLOAD': constants_module.HELP_RESUME_UPLOAD,
        'HELP_ADDITIONAL_CONTEXT': constants_module.HELP_ADDITIONAL_CONTEXT,
        'HELP_CONTEXT_FILES': constants_module.HELP_CONTEXT_FILES,
    }

def get_utils():
    from src.utils import validate_inputs, display_error, display_success, display_warning
    return validate_inputs, display_error, display_success, display_warning

def get_progress_indicator():
    from src.progress_indicator import ProgressIndicator
    return ProgressIndicator

load_dotenv()

st.set_page_config(
    page_title="Cover Letter Generator",
    page_icon="📝",
    layout="wide"
)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_constants():
    """Cache constants to avoid reloading"""
    return get_constants()

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
    
    # Lazy load generator, constants, and utils
    if 'generator' not in st.session_state:
        ProgressIndicator = get_progress_indicator()
        with st.spinner("Initializing AI components..."):
            CoverLetterGenerator = get_cover_letter_generator()
            st.session_state.generator = CoverLetterGenerator()
    
    # Load static content only once and cache it
    if 'static_content_loaded' not in st.session_state:
        ProgressIndicator = get_progress_indicator()
        with st.spinner("Loading templates and examples..."):
            st.session_state.generator.load_static_content()
            st.session_state.static_content_loaded = True
    
    # Get constants and utils lazily with caching
    constants = get_cached_constants()
    validate_inputs, display_error, display_success, display_warning = get_utils()
    
    # Main content in a single column for better flow
    st.header("📄 Job Information")
    
    col_job1, col_job2 = st.columns([2, 1])
    with col_job1:
        job_url = st.text_input(
            constants['LABEL_JOB_URL'],
            help=constants['HELP_JOB_URL']
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
        constants['LABEL_JOB_DESCRIPTION'],
        height=200,
        help=constants['HELP_JOB_DESCRIPTION']
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
        constants['LABEL_RESUME_UPLOAD'],
        type=constants['SUPPORTED_FILE_TYPES'],
        help=constants['HELP_RESUME_UPLOAD']
    )
    
    resume_text = ""
    if resume_file:
        # Cache processed resume content to avoid reprocessing
        file_hash = hash(resume_file.getvalue())
        cache_key = f"resume_{file_hash}"
        
        if cache_key not in st.session_state:
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
                
                st.session_state[cache_key] = resume_text
        else:
            resume_text = st.session_state[cache_key]
        
        # Resume content is loaded but not displayed to keep UI clean
    
    st.header("📁 Context Files")
    
    context_files = st.file_uploader(
        "Upload context files",
        type=constants['SUPPORTED_FILE_TYPES'],
        accept_multiple_files=True,
        help=constants['HELP_CONTEXT_FILES']
    )
    
    if context_files:
        # Cache context files processing
        files_hash = hash(tuple(f.getvalue() for f in context_files))
        context_cache_key = f"context_{files_hash}"
        
        if context_cache_key not in st.session_state:
            with st.spinner("Processing uploaded files..."):
                num_docs = st.session_state.generator.load_context_files(context_files)
                st.session_state[context_cache_key] = num_docs
                display_success(constants['SUCCESS_CONTEXT_PROCESSED'].format(num_docs=num_docs))
        else:
            num_docs = st.session_state[context_cache_key]
            display_success(constants['SUCCESS_CONTEXT_PROCESSED'].format(num_docs=num_docs))
    
    additional_context = st.text_area(
        constants['LABEL_ADDITIONAL_CONTEXT'],
        height=100,
        help=constants['HELP_ADDITIONAL_CONTEXT']
    )
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.header("🔧 Generate Cover Letter")
        
        if st.button(constants['LABEL_GENERATE_COVER_LETTER'], type="primary", use_container_width=True):
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
                            display_success(constants['SUCCESS_COVER_LETTER_GENERATED'])
                            
                            st.header("📝 Generated Cover Letter")
                            st.text_area(constants['LABEL_COVER_LETTER'], value=cover_letter, height=400)
                            
                            pdf_data = st.session_state.generator.create_pdf(cover_letter)
                            
                            st.download_button(
                                label=constants['LABEL_DOWNLOAD_PDF'],
                                data=pdf_data,
                                file_name=constants['DEFAULT_PDF_FILENAME'],
                                mime=constants['PDF_MIME_TYPE'],
                                use_container_width=True
                            )
                        else:
                            display_error("Failed to generate cover letter. Please check your inputs and try again.")
                    except Exception as e:
                        display_error(constants['ERROR_GENERATING_COVER_LETTER'].format(error=str(e)))

def improve_page():
    st.title("✨ Improve Existing Cover Letter")
    st.markdown("Upload your existing cover letter and specify what you'd like to improve")
    
    api_key = os.getenv("GOOGLE_API_KEY", "")
    
    if not api_key:
        st.error("Please set your GOOGLE_API_KEY environment variable")
        st.stop()
    
    # Lazy load generator and constants
    if 'generator' not in st.session_state:
        with st.spinner("Initializing AI components..."):
            CoverLetterGenerator = get_cover_letter_generator()
            st.session_state.generator = CoverLetterGenerator()
    
    # Load static content only once and cache it
    if 'static_content_loaded' not in st.session_state:
        with st.spinner("Loading templates and examples..."):
            st.session_state.generator.load_static_content()
            st.session_state.static_content_loaded = True
    
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
                        from pypdf import PdfReader
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
                        validate_inputs, display_error, display_success, display_warning = get_utils()
                        display_success("✅ Cover letter improved successfully!")
                        
                        st.header("📝 Improved Cover Letter")
                        st.text_area("Improved Cover Letter", value=improved_letter, height=400)
                        
                        pdf_data = st.session_state.generator.create_pdf(improved_letter)
                        
                        constants = get_constants()
                        st.download_button(
                            label=constants['LABEL_DOWNLOAD_PDF'],
                            data=pdf_data,
                            file_name="improved_cover_letter.pdf",
                            mime=constants['PDF_MIME_TYPE'],
                            use_container_width=True
                        )
                    else:
                        validate_inputs, display_error, display_success, display_warning = get_utils()
                        display_error("Failed to improve cover letter. Please try again.")
                except Exception as e:
                    validate_inputs, display_error, display_success, display_warning = get_utils()
                    display_error(f"Error improving cover letter: {str(e)}")
        else:
            validate_inputs, display_error, display_success, display_warning = get_utils()
            display_error("Please upload a cover letter file or paste your cover letter text.")

if __name__ == "__main__":
    main()
