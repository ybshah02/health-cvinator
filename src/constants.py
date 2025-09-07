SUCCESS_STATIC_CONTENT_LOADED = "✅ Loaded {num_docs} static content files"
SUCCESS_CONTEXT_PROCESSED = "✅ Processed {num_docs} uploaded files"
SUCCESS_COVER_LETTER_GENERATED = "✅ Cover letter generated successfully!"

ERROR_API_KEY_MISSING = "Please set your GOOGLE_API_KEY environment variable"
ERROR_RESUME_MISSING = "Please provide your resume content"
ERROR_GENERATING_COVER_LETTER = "Error generating cover letter: {error}"
ERROR_EXTRACTING_JOB_INFO = "Error extracting job info: {error}"

SUPPORTED_FILE_TYPES = ['pdf', 'txt']
PDF_MIME_TYPE = "application/pdf"
TEXT_MIME_TYPE = "text/plain"

DEFAULT_PDF_FILENAME = "cover_letter.pdf"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-lite"
DEFAULT_TEMPERATURE = 0.7

LABEL_GENERATE_COVER_LETTER = "🚀 Generate Cover Letter"
LABEL_DOWNLOAD_PDF = "📥 Download PDF"
LABEL_JOB_URL = "Job URL (optional)"
LABEL_JOB_DESCRIPTION = "Job Description (optional)"
LABEL_RESUME_CONTENT = "Resume Content"
LABEL_RESUME_UPLOAD = "Or Upload Resume File"
LABEL_ADDITIONAL_CONTEXT = "Additional Context (optional)"
LABEL_COVER_LETTER = "Cover Letter"

HELP_JOB_URL = "Paste the job posting URL to automatically extract job description"
HELP_JOB_DESCRIPTION = "Paste the job description or requirements here (optional)"
HELP_RESUME_CONTENT = "Paste your resume content here. Include your skills, experience, education, and any relevant details."
HELP_RESUME_UPLOAD = "Upload a PDF or text file containing your resume"
HELP_ADDITIONAL_CONTEXT = "Any additional information you'd like to include in the cover letter"
HELP_CONTEXT_FILES = "Upload additional PDF or text files with examples or instructions"
