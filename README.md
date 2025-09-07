# 📝 AI Cover Letter Generator

A powerful Streamlit application that uses LangChain and OpenAI to generate high-quality, personalized cover letters for healthcare positions. Perfect for entry-level roles like phlebotomy assistants and other healthcare support positions.

## ✨ Features

- **AI-Powered Generation**: Uses GPT-4 to create professional, tailored cover letters
- **Context Learning**: Upload CV examples and instructions to train the AI on your preferred style
- **Job URL Integration**: Automatically extract job descriptions from job posting URLs
- **PDF Export**: Generate and download professional PDF cover letters
- **Healthcare Focus**: Specialized prompts for healthcare and medical support positions
- **Vector Search**: Intelligent context retrieval from uploaded documents

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google API key (for Gemini)

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd cvinator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Google API key**
   - Copy `env_example.txt` to `.env`
   - Add your Google API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   - The app will automatically open at `http://localhost:8501`
   - If not, manually navigate to the URL shown in your terminal

## 📖 How to Use

### Step 1: Configure API Key
- Enter your Google API key in the sidebar
- The app will validate the key and show a success message

### Step 2: Upload Context Files (Optional but Recommended)
- Upload PDF or text files containing:
  - Example cover letters you like
  - CV templates or examples
  - Specific instructions or preferences
- The AI will learn from these to match your style

### Step 3: Provide Job Information
- **Job URL**: Paste the job posting URL (optional)
  - The app will automatically extract the job description
- **Job Description**: Manually paste the job requirements if no URL is provided

### Step 4: Add Your Resume
- Paste your resume content in the text area
- Include skills, experience, education, and relevant details

### Step 5: Additional Context (Optional)
- Add any specific points you want emphasized
- Include particular achievements or experiences to highlight

### Step 6: Generate Cover Letter
- Click "🚀 Generate Cover Letter"
- Wait for the AI to process and generate your personalized cover letter
- Review the generated content
- Download as PDF for your application

## 🎯 Best Practices

### For Healthcare Positions
- Emphasize attention to detail and patient care orientation
- Highlight any relevant certifications or training
- Mention experience with medical terminology or procedures
- Show enthusiasm for helping patients and healthcare teams

### Context Files
- Upload 2-3 example cover letters you admire
- Include any specific formatting or tone preferences
- Add industry-specific terminology or phrases you prefer

### Resume Content
- Include all relevant healthcare experience
- Mention any phlebotomy training or certifications
- Highlight soft skills like communication and empathy
- Include any volunteer work in healthcare settings

## 🔧 Technical Details

### Architecture
- **Frontend**: Streamlit for user interface
- **AI Engine**: LangChain with Google Gemini Pro
- **Document Processing**: PyPDF2, BeautifulSoup for web scraping
- **Vector Storage**: FAISS for semantic search
- **PDF Generation**: ReportLab for professional formatting

### Key Components

**Core Modules:**
- `CoverLetterGenerator`: Main class orchestrating the entire process
- `DocumentProcessor`: Handles loading and processing of context files
- `WebScraper`: Extracts job information from URLs
- `PDFGenerator`: Creates professional PDF documents
- `Config`: Centralized configuration management
- `Utils`: Helper functions and validation
- `Constants`: Application-wide constants and messages

**Architecture Benefits:**
- **Modular Design**: Each component has a single responsibility
- **Easy Testing**: Individual modules can be tested in isolation
- **Maintainable**: Changes to one module don't affect others
- **Extensible**: New features can be added without modifying existing code
- **Reusable**: Components can be used in other projects

## 📁 Project Structure

```
cvinator/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── env_example.txt          # Environment variables template
├── README.md               # This file
└── src/                    # Source code modules
    ├── __init__.py         # Package initialization
    ├── config.py           # Configuration management
    ├── constants.py        # Application constants
    ├── utils.py            # Utility functions
    ├── cover_letter_generator.py  # Main AI generation logic
    ├── document_processor.py      # Document loading and processing
    ├── pdf_generator.py           # PDF generation utilities
    └── web_scraper.py            # Web scraping utilities
```

## 🛠️ Customization

### Modifying the AI Prompt
Edit the `_get_system_prompt` method in `src/cover_letter_generator.py` to:
- Change the tone or style
- Focus on different industries
- Adjust length requirements
- Add specific formatting instructions

### Adding New File Types
Extend the `DocumentProcessor` class in `src/document_processor.py` to support:
- Word documents (.docx)
- Markdown files (.md)
- Other text formats

### Styling the PDF
Modify the `PDFGenerator` class in `src/pdf_generator.py` to:
- Change fonts or formatting
- Add headers or footers
- Adjust spacing and layout
- Include company logos

### Configuration Changes
Update `src/config.py` to modify:
- OpenAI model settings
- Document processing parameters
- PDF formatting options
- Web scraping timeouts

## 🐛 Troubleshooting

### Common Issues

**"Please enter your Google API key"**
- Make sure you've entered a valid Google API key in the sidebar
- Check that the key has sufficient credits

**"Error extracting job info"**
- The job URL might be protected or require authentication
- Try copying the job description manually instead

**"Failed to generate cover letter"**
- Check your internet connection
- Verify your Google API key is valid
- Ensure you've provided both resume and job description

**PDF download not working**
- Check your browser's download settings
- Try a different browser if issues persist

### Getting Help
- Check the Streamlit logs in your terminal for detailed error messages
- Ensure all dependencies are installed correctly
- Verify your OpenAI API key has the necessary permissions

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## ⚠️ Important Notes

- This application requires a Google API key and will consume API credits
- Always review generated cover letters before submitting
- The AI generates content based on your inputs - ensure accuracy
- Keep your API key secure and never share it publicly

---

**Happy job hunting! 🎯**
