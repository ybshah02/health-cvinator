from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langchain.memory import ConversationBufferMemory

from .config import Config
from .document_processor import DocumentProcessor
from .web_scraper import WebScraper
from .pdf_generator import PDFGenerator

class CoverLetterGenerator:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=Config.GEMINI_MODEL,
            temperature=Config.GEMINI_TEMPERATURE,
            google_api_key=Config.GOOGLE_API_KEY
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.document_processor = DocumentProcessor()
        self.web_scraper = WebScraper()
        self.pdf_generator = PDFGenerator()
    
    def load_static_content(self) -> int:
        return self.document_processor.load_static_content()
    
    def load_context_files(self, files) -> int:
        return self.document_processor.load_context_files(files)
    
    def extract_job_info(self, job_url: str) -> str:
        return self.web_scraper.extract_job_info(job_url)
    
    def generate_cover_letter(
        self, 
        resume_text: str, 
        job_description: str, 
        job_url: str = "", 
        additional_context: str = "",
        job_title: str = "",
        company_name: str = ""
    ) -> str:
        system_prompt = self._get_system_prompt()
        context = self._get_context_from_documents(resume_text, job_description)
        prompt = self._build_prompt(
            system_prompt, context, resume_text, 
            job_description, job_url, additional_context,
            job_title, company_name
        )
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            raise Exception(f"Error generating cover letter: {str(e)}")
    
    def create_pdf(self, cover_letter_text: str, filename: str = "cover_letter.pdf") -> bytes:
        return self.pdf_generator.create_pdf(cover_letter_text, filename)
    
    def _get_system_prompt(self) -> str:
        return """You are an expert career counselor and cover letter specialist. Your task is to generate a professional, compelling cover letter following these 5 key rules:

1. Strong self-introduction with an engaging hook
2. Highlight relevant experience & achievements  
3. Connect background to the company's mission & values
4. End with a confident & strong closing statement
5. Ensure formatting is clean, professional, and ATS-friendly

The tone should be professional yet engaging, within one page (250-400 words). Make the cover letter concise, structured, and impactful while keeping the candidate's unique experiences and voice.

IMPORTANT: Return ONLY plain text without any markdown formatting, HTML tags, or special characters. Do not use **bold**, *italics*, # headers, or any other markdown syntax."""
    
    def _get_context_from_documents(self, resume_text: str, job_description: str) -> str:
        if not self.document_processor.vectorstore:
            return ""
        
        query = f"resume: {resume_text[:500]} job: {job_description[:500]}"
        return self.document_processor.search_similar_documents(query)
    
    def _build_prompt(
        self, 
        system_prompt: str, 
        context: str, 
        resume_text: str, 
        job_description: str, 
        job_url: str, 
        additional_context: str,
        job_title: str = "",
        company_name: str = ""
    ) -> str:
        # Use provided values or extract from job description/URL
        if not company_name:
            company_name = self._extract_company_name(job_description, job_url)
        if not job_title:
            job_title = self._extract_job_title(job_description, job_url)
        
        return f"""
        {system_prompt}
        
        CONTEXT FROM EXAMPLES/INSTRUCTIONS:
        {context}
        
        JOB INFORMATION:
        Position: {job_title}
        Company: {company_name}
        Job Description: {job_description}
        Job URL: {job_url}
        
        CANDIDATE BACKGROUND:
        Resume: {resume_text}
        Additional Context: {additional_context}
        
        Please generate a professional cover letter using this template structure:
        
        "I am applying for the {job_title} position at {company_name}. Here is the job description: {job_description}
        
        My background: [Extract years of experience and industry from resume]
        Key skills: [List relevant skills from resume that match job requirements]
        Major quantifiable achievements: [Extract 1-2 quantifiable accomplishments from resume]
        Connection to the company: [Based on job description and company info, explain why interested]
        
        Write a concise, engaging, and professional cover letter following the 5 rules:
        1. Strong self-introduction with an engaging hook
        2. Highlight relevant experience & achievements
        3. Connect my background to the company's mission & values
        4. End with a confident & strong closing statement
        5. Ensure formatting is clean, professional, and ATS-friendly
        
        The tone should be professional yet engaging, within one page (250-400 words)."
        """
    
    def _extract_company_name(self, job_description: str, job_url: str) -> str:
        """Extract company name from job description or URL"""
        if not job_description and not job_url:
            return "[Company Name]"
        
        # Try to extract from job description first
        if job_description:
            # Look for common patterns
            lines = job_description.split('\n')
            for line in lines[:10]:  # Check first 10 lines
                line = line.strip()
                if any(keyword in line.lower() for keyword in ['at ', 'company:', 'employer:', 'organization:']):
                    # Extract company name after these keywords
                    for keyword in ['at ', 'company:', 'employer:', 'organization:']:
                        if keyword in line.lower():
                            company = line.split(keyword, 1)[1].strip()
                            if company and len(company) < 100:  # Reasonable company name length
                                return company
        
        # Try to extract from URL
        if job_url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(job_url)
                domain = parsed.netloc
                if domain:
                    # Remove common job site domains
                    job_sites = ['indeed.com', 'linkedin.com', 'glassdoor.com', 'monster.com', 'ziprecruiter.com']
                    for site in job_sites:
                        if site in domain:
                            return "[Company Name]"
                    # Extract company from domain
                    company = domain.split('.')[0]
                    if company and len(company) > 2:
                        return company.title()
            except:
                pass
        
        return "[Company Name]"
    
    def _extract_job_title(self, job_description: str, job_url: str) -> str:
        """Extract job title from job description or URL"""
        if not job_description and not job_url:
            return "[Job Title]"
        
        # Try to extract from job description first
        if job_description:
            lines = job_description.split('\n')
            for line in lines[:5]:  # Check first 5 lines
                line = line.strip()
                if line and len(line) < 100:  # Reasonable title length
                    # Skip lines that are clearly not titles
                    if not any(skip in line.lower() for skip in ['description', 'requirements', 'qualifications', 'responsibilities']):
                        return line
        
        # Try to extract from URL
        if job_url:
            try:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(job_url)
                query_params = parse_qs(parsed.query)
                
                # Common job title parameters
                for param in ['title', 'job_title', 'position', 'role']:
                    if param in query_params:
                        title = query_params[param][0]
                        if title and len(title) < 100:
                            return title.replace('-', ' ').replace('_', ' ').title()
                
                # Try to extract from path
                path_parts = parsed.path.split('/')
                for part in path_parts:
                    if part and len(part) > 3 and len(part) < 50:
                        # Skip common non-title parts
                        if not any(skip in part.lower() for skip in ['jobs', 'careers', 'apply', 'search']):
                            return part.replace('-', ' ').replace('_', ' ').title()
            except:
                pass
        
        return "[Job Title]"
    
    def improve_cover_letter(self, existing_cover_letter: str) -> str:
        """Improve an existing cover letter using the 5 rules"""
        system_prompt = """You are an expert career counselor and cover letter specialist. Your task is to improve an existing cover letter by ensuring it follows these 5 key rules:

1. Strong self-introduction with an engaging hook
2. Highlight relevant experience & achievements  
3. Connect background to the company's mission & values
4. End with a confident & strong closing statement
5. Ensure formatting is clean, professional, and ATS-friendly

The tone should be professional yet engaging, within one page (250-400 words). Make the cover letter concise, structured, and impactful while keeping the candidate's unique experiences and voice.

IMPORTANT: Return ONLY plain text without any markdown formatting, HTML tags, or special characters. Do not use **bold**, *italics*, # headers, or any other markdown syntax."""
        
        prompt = f"""
        {system_prompt}
        
        EXISTING COVER LETTER:
        {existing_cover_letter}
        
        Please improve this cover letter by:
        1. Strengthening the opening hook to grab attention
        2. Making experience & achievements more quantifiable & impactful
        3. Showing a stronger connection to the company's mission & values
        4. Improving the closing statement with a more compelling call to action
        5. Ensuring conciseness, structured formatting, and professional tone (250-400 words, 1 page)
        
        Rewrite it while keeping the unique experiences and voice, but making it more engaging and aligned with best practices.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            raise Exception(f"Error improving cover letter: {str(e)}")
    
    def improve_cover_letter_with_prompt(self, cover_letter: str, custom_prompt: str) -> str:
        """Improve an existing cover letter using a custom prompt"""
        system_prompt = """You are an expert career coach and cover letter writer. Your task is to improve existing cover letters based on specific instructions provided by the user.

IMPORTANT: Return ONLY plain text without any markdown formatting, HTML tags, or special characters. Do not use **bold**, *italics*, # headers, or any other markdown syntax."""
        
        prompt = f"""
        {system_prompt}
        
        Here is the existing cover letter:
        {cover_letter}
        
        Improvement instructions:
        {custom_prompt}
        
        Please rewrite the cover letter following the improvement instructions while maintaining the core message and personal experiences.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            raise Exception(f"Error improving cover letter: {str(e)}")
