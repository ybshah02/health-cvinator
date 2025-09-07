import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from .config import Config

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=Config.PDF_TITLE_FONT_SIZE,
            spaceAfter=30,
            alignment=1
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=Config.PDF_BODY_FONT_SIZE,
            spaceAfter=Config.PDF_SPACING,
            leftIndent=0,
            rightIndent=0
        )
    
    def create_pdf(self, cover_letter_text: str, filename: str = "cover_letter.pdf") -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        story = []
        
        story.append(Paragraph("Cover Letter", self.title_style))
        story.append(Spacer(1, 20))
        
        paragraphs = cover_letter_text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), self.body_style))
                story.append(Spacer(1, Config.PDF_SPACING))
        
        doc.build(story)
        buffer.seek(0)
        
        return buffer.getvalue()
    
    def format_cover_letter_text(self, text: str) -> str:
        formatted_text = text.replace('\n', '<br/>')
        return formatted_text
