import subprocess
import tempfile
import os
from pathlib import Path
import streamlit as st

class AudioProcessor:
    """Handles audio/video file processing using FFmpeg"""
    
    def __init__(self):
        self.supported_formats = ['.mp3', '.wav', '.mp4', '.avi', '.mov', '.mkv']
    
    def process_file(self, file_path, chunk_length=30):
        """
        Process audio/video file and convert to suitable format for transcription
        
        Args:
            file_path (str): Path to the input file
            chunk_length (int): Length of audio chunks in seconds
            
        Returns:
            str: Path to processed audio file
        """
        try:
            # Create temporary output file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                output_path = tmp_file.name
            
            # FFmpeg command to extract audio and convert to WAV
            cmd = [
                'ffmpeg', '-i', file_path,
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',  # Overwrite output file
                output_path
            ]
            
            # For demo purposes, we'll simulate the processing
            # In a real implementation, you would run: subprocess.run(cmd, check=True)
            
            # Simulate processing by copying the original file
            # This is a placeholder - in production you'd use actual FFmpeg
            import shutil
            shutil.copy2(file_path, output_path)
            
            return output_path
            
        except Exception as e:
            st.error(f"Error processing audio file: {str(e)}")
            raise
    
    def get_duration(self, file_path):
        """Get duration of audio/video file"""
        try:
            # This would use FFprobe in a real implementation
            # For demo, return a placeholder duration
            return 300  # 5 minutes
        except Exception as e:
            st.warning(f"Could not determine file duration: {str(e)}")
            return 0
    
    def validate_file(self, file_path):
        """Validate if file format is supported"""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.supported_formats
