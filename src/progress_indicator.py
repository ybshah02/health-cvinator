import streamlit as st
import time
from typing import Optional

class ProgressIndicator:
    """Enhanced progress indicator for better user feedback"""
    
    @staticmethod
    def show_progress_with_steps(steps: list, current_step: int, message: str = ""):
        """Show progress with step indicators"""
        progress = current_step / len(steps)
        
        # Create columns for progress bar and step indicators
        col1, col2 = st.columns([3, 1])
        
        with col1:
            progress_bar = st.progress(progress)
            if message:
                st.caption(message)
        
        with col2:
            st.caption(f"Step {current_step}/{len(steps)}")
    
    @staticmethod
    def show_loading_with_animation(message: str, duration: Optional[float] = None):
        """Show loading animation with optional duration"""
        placeholder = st.empty()
        
        if duration:
            end_time = time.time() + duration
            while time.time() < end_time:
                placeholder.info(f"⏳ {message}")
                time.sleep(0.1)
        else:
            placeholder.info(f"⏳ {message}")
    
    @staticmethod
    def show_processing_steps(steps: list):
        """Show processing steps with checkmarks"""
        for i, step in enumerate(steps):
            if i < len(steps) - 1:
                st.success(f"✅ {step}")
            else:
                st.info(f"🔄 {step}")
    
    @staticmethod
    def clear_progress():
        """Clear all progress indicators"""
        st.empty()
