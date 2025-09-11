"""
Performance optimization configuration for Streamlit deployment
"""
import os

class PerformanceConfig:
    """Configuration for optimizing app performance on Streamlit Community Cloud"""
    
    # Streamlit specific optimizations
    STREAMLIT_SERVER_HEADLESS = True
    STREAMLIT_SERVER_ENABLE_CORS = False
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION = False
    
    # Memory optimizations
    MAX_MEMORY_USAGE_MB = 512
    ENABLE_MEMORY_MONITORING = True
    
    # Caching configurations
    ENABLE_STREAMLIT_CACHING = True
    CACHE_TTL_SECONDS = 3600  # 1 hour
    
    # File processing optimizations
    MAX_FILE_SIZE_MB = 10
    ENABLE_FILE_COMPRESSION = True
    
    # API optimizations
    REQUEST_TIMEOUT_SECONDS = 5
    MAX_RETRIES = 2
    ENABLE_REQUEST_CACHING = True
    
    # Vector store optimizations
    VECTOR_STORE_BATCH_SIZE = 100
    ENABLE_VECTOR_STORE_CACHING = True
    
    # Web scraping optimizations
    ENABLE_AGGRESSIVE_CACHING = True
    SKIP_SELENIUM_IF_POSSIBLE = True
    
    @classmethod
    def get_streamlit_config(cls):
        """Get Streamlit configuration for performance"""
        return {
            'server.headless': cls.STREAMLIT_SERVER_HEADLESS,
            'server.enableCORS': cls.STREAMLIT_SERVER_ENABLE_CORS,
            'server.enableXsrfProtection': cls.STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION,
            'browser.gatherUsageStats': False,
            'theme.base': 'light',
            'theme.primaryColor': '#1f77b4',
            'theme.backgroundColor': '#ffffff',
            'theme.secondaryBackgroundColor': '#f0f2f6',
            'theme.textColor': '#262730'
        }
    
    @classmethod
    def apply_environment_variables(cls):
        """Apply performance-related environment variables"""
        os.environ.setdefault('STREAMLIT_SERVER_HEADLESS', str(cls.STREAMLIT_SERVER_HEADLESS))
        os.environ.setdefault('STREAMLIT_SERVER_ENABLE_CORS', str(cls.STREAMLIT_SERVER_ENABLE_CORS))
        os.environ.setdefault('STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION', str(cls.STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION))
