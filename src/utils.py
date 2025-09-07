import streamlit as st
from typing import Optional

def validate_inputs(resume_text: str, job_description: str, api_key: str) -> tuple[bool, Optional[str]]:
    if not api_key:
        return False, "Please set your GOOGLE_API_KEY environment variable"
    
    if not resume_text.strip():
        return False, "Please provide your resume content"
    
    return True, None

def display_error(error_message: str):
    st.error(error_message)

def display_success(message: str):
    st.success(message)

def display_warning(message: str):
    st.warning(message)
