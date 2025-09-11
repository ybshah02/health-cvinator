import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = "gemini-2.5-flash-lite"
    GEMINI_TEMPERATURE = 0.7
    
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    MAX_SIMILARITY_SEARCH_RESULTS = 3
    ENABLE_VECTOR_SEARCH = True
    
    REQUEST_TIMEOUT = 5  # Reduced from 10 to 5 seconds for faster response
    MAX_JOB_DESCRIPTION_LENGTH = 3000
    
    PDF_PAGE_SIZE = "letter"
    PDF_TITLE_FONT_SIZE = 16
    PDF_BODY_FONT_SIZE = 12
    PDF_SPACING = 12
    
    @classmethod
    def validate_api_key(cls):
        return cls.GOOGLE_API_KEY is not None and cls.GOOGLE_API_KEY.strip() != ""
