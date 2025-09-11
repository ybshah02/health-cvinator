import requests
from bs4 import BeautifulSoup
from typing import Optional
import time
import random
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

from .config import Config

class WebScraper:
    @staticmethod
    def _check_chrome_installed():
        """Check if Chrome is installed on the system"""
        import os
        chrome_paths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium'
        ]
        return any(os.path.exists(path) for path in chrome_paths) or shutil.which('google-chrome') or shutil.which('chromium-browser')
    
    @staticmethod
    def _setup_selenium_driver():
        """Setup Chrome driver with options to avoid detection"""
        # Check if Chrome is installed
        if not WebScraper._check_chrome_installed():
            raise Exception("Chrome browser not found. Please install Google Chrome or try copying the job description manually.")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            # Use system Chrome (we know this works from testing)
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
            
        except Exception as e:
            # Fallback to webdriver-manager if system Chrome fails
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                return driver
            except Exception as e2:
                raise Exception(f"Failed to setup browser: {str(e)}. Fallback also failed: {str(e2)}. Please try copying the job description manually.")
    
    @staticmethod
    def _extract_with_selenium(job_url: str) -> str:
        """Extract job info using Selenium for JavaScript-heavy sites"""
        driver = None
        try:
            driver = WebScraper._setup_selenium_driver()
            driver.get(job_url)
            
            # Reduced wait time for faster response
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Try to find job description elements
            job_selectors = [
                "div[id*='jobDescription']",
                "div[class*='jobDescription']", 
                "div[class*='job-description']",
                "div[class*='description']",
                "div[data-testid*='jobDescription']",
                "div[data-testid*='description']",
                "main",
                "article"
            ]
            
            job_content = None
            for selector in job_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if len(text) > 200:  # Look for substantial content
                            job_content = element
                            break
                    if job_content:
                        break
                except:
                    continue
            
            if not job_content:
                # Fallback to page source
                job_content = driver.find_element(By.TAG_NAME, "body")
            
            text = job_content.text
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Remove unwanted content
            unwanted_phrases = [
                'cookie', 'privacy policy', 'terms of service', 'sign in', 'log in',
                'create account', 'apply now', 'share this job', 'save job',
                'indeed.com', 'linkedin.com', 'glassdoor.com', 'skip to main content',
                'navigation', 'menu', 'footer', 'header'
            ]
            
            for phrase in unwanted_phrases:
                text = text.replace(phrase, '')
            
            if len(text.strip()) < 100:
                raise Exception("Could not extract sufficient job information from the page.")
            
            return text[:Config.MAX_JOB_DESCRIPTION_LENGTH]
            
        except TimeoutException:
            raise Exception("Page took too long to load. The site may be slow or blocking requests.")
        except WebDriverException as e:
            raise Exception(f"Browser error: {str(e)}")
        except Exception as e:
            raise Exception(f"Selenium extraction failed: {str(e)}")
        finally:
            if driver:
                driver.quit()
    
    @staticmethod
    def extract_job_info(job_url: str) -> str:
        # For Indeed and LinkedIn, try Selenium first, but fall back gracefully
        if "indeed.com" in job_url.lower() or "linkedin.com" in job_url.lower():
            try:
                return WebScraper._extract_with_selenium(job_url)
            except Exception as selenium_error:
                # If Selenium fails, try requests as fallback
                try:
                    return WebScraper._extract_with_requests(job_url)
                except Exception as requests_error:
                    # If both fail, provide helpful error message
                    if "Chrome browser not found" in str(selenium_error):
                        raise Exception("Chrome browser not installed. Please install Google Chrome or copy and paste the job description manually.")
                    elif "Failed to setup browser" in str(selenium_error):
                        raise Exception("Browser setup failed. Please copy and paste the job description manually.")
                    else:
                        raise Exception(f"Could not extract job information from this site. Please copy and paste the job description manually.")
        else:
            # For other sites, try requests first (faster)
            try:
                return WebScraper._extract_with_requests(job_url)
            except Exception as requests_error:
                # If requests fails, try Selenium as fallback
                try:
                    return WebScraper._extract_with_selenium(job_url)
                except Exception as selenium_error:
                    raise Exception(f"Could not extract job information. Please copy and paste the job description manually.")
    
    @staticmethod
    def _extract_with_requests(job_url: str) -> str:
        """Fallback method using requests for simpler sites"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Reduced delay for faster response
        time.sleep(random.uniform(0.5, 1.5))
        
        response = requests.get(job_url, headers=headers, timeout=Config.REQUEST_TIMEOUT)
        
        if response.status_code == 403:
            raise Exception("Access denied (403). This job site may block automated requests.")
        elif response.status_code == 404:
            raise Exception("Job posting not found (404). Please check the URL and try again.")
        elif response.status_code != 200:
            raise Exception(f"Failed to fetch job URL (HTTP {response.status_code}).")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Try to find job-specific content
        job_content = soup.find('div', {'id': 'jobDescriptionText'}) or \
                     soup.find('div', {'class': 'jobsearch-jobDescriptionText'}) or \
                     soup.find('div', {'class': 'job-description'}) or \
                     soup.find('div', {'class': 'description'}) or \
                     soup.find('main') or \
                     soup.find('article') or \
                     soup
        
        text = job_content.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Remove common unwanted text
        unwanted_phrases = [
            'cookie', 'privacy policy', 'terms of service', 'sign in', 'log in',
            'create account', 'apply now', 'share this job', 'save job',
            'indeed.com', 'linkedin.com', 'glassdoor.com'
        ]
        
        for phrase in unwanted_phrases:
            text = text.replace(phrase, '')
        
        if len(text.strip()) < 100:
            raise Exception("Could not extract sufficient job information from the page.")
        
        return text[:Config.MAX_JOB_DESCRIPTION_LENGTH]
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        return url.startswith(('http://', 'https://')) and len(url.strip()) > 0
