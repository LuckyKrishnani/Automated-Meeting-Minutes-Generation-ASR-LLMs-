import streamlit as st
import os
import tempfile
import json
from datetime import datetime
import pandas as pd
from pathlib import Path

# Import our custom modules
from src.audio_processor import AudioProcessor
from src.transcriber import Transcriber
from src.summarizer import MeetingSummarizer
from src.output_generator import OutputGenerator
from src.evaluator import Evaluator

def main():
    st.set_page_config(
        page_title="Meeting Minutes Generator",
        page_icon="📝",
        layout="wide"
    )
    
    st.title("📝 Automated Meeting Minutes Generator")
    st.markdown("Transform your meeting recordings into structured minutes with AI")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        model_choice = st.selectbox(
            "Choose Summarization Model",
            ["qwen2.5-7b-instruct", "llama-3.1-8b-instruct"],
            help="Select the language model for generating summaries"
        )
        
        # Output format selection
        output_formats = st.multiselect(
            "Output Formats",
            ["JSON", "HTML", "PDF"],
            default=["JSON", "HTML"],
            help="Choose which formats to generate"
        )
        
        # Advanced settings
        with st.expander("Advanced Settings"):
            chunk_length = st.slider("Audio Chunk Length (seconds)", 10, 60, 30)
            max_summary_length = st.slider("Max Summary Length (words)", 100, 1000, 500)
    
    # Main interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Meeting Recording")
        
        uploaded_file = st.file_uploader(
            "Choose an audio or video file",
            type=['mp3', 'wav', 'mp4', 'avi', 'mov', 'mkv'],
            help="Supported formats: MP3, WAV, MP4, AVI, MOV, MKV"
        )
        
        if uploaded_file is not None:
            st.success(f"File uploaded: {uploaded_file.name}")
            st.info(f"File size: {uploaded_file.size / (1024*1024):.2f} MB")
            
            # Meeting metadata
            st.subheader("Meeting Information")
            meeting_title = st.text_input("Meeting Title", value="Team Meeting")
            meeting_date = st.date_input("Meeting Date", value=datetime.now().date())
            participants = st.text_area("Participants (one per line)", 
                                      placeholder="John Doe\nJane Smith\nBob Johnson")
    
    with col2:
        st.header("🎯 Processing Status")
        
        if uploaded_file is not None:
            if st.button("🚀 Generate Meeting Minutes", type="primary"):
                process_meeting(uploaded_file, meeting_title, meeting_date, 
                              participants, model_choice, output_formats, 
                              chunk_length, max_summary_length)
    
    # Display recent results
    display_recent_results()

def process_meeting(uploaded_file, title, date, participants, model_choice, 
                   output_formats, chunk_length, max_summary_length):
    """Process the uploaded meeting file and generate minutes"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
        # Initialize processors
        audio_processor = AudioProcessor()
        transcriber = Transcriber()
        summarizer = MeetingSummarizer(model_choice)
        output_generator = OutputGenerator()
        
        # Step 1: Process audio
        status_text.text("🎵 Processing audio file...")
        progress_bar.progress(20)
        
        processed_audio = audio_processor.process_file(temp_path, chunk_length)
        
        # Step 2: Transcribe audio
        status_text.text("🎤 Transcribing speech to text...")
        progress_bar.progress(40)
        
        transcript = transcriber.transcribe(processed_audio)
        
        # Step 3: Generate summary
        status_text.text("🤖 Generating meeting minutes...")
        progress_bar.progress(60)
        
        meeting_data = {
            'title': title,
            'date': str(date),
            'participants': [p.strip() for p in participants.split('\n') if p.strip()],
            'transcript': transcript
        }
        
        minutes = summarizer.generate_minutes(meeting_data, max_summary_length)
        
        # Step 4: Generate outputs
        status_text.text("📄 Generating output files...")
        progress_bar.progress(80)
        
        output_files = output_generator.generate_outputs(minutes, output_formats)
        
        # Step 5: Save results
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        # Display results
        display_results(minutes, output_files)
        
        # Clean up
        os.unlink(temp_path)
        
    except Exception as e:
        st.error(f"Error processing meeting: {str(e)}")
        progress_bar.empty()
        status_text.empty()

def display_results(minutes, output_files):
    """Display the generated meeting minutes and download links"""
    
    st.success("🎉 Meeting minutes generated successfully!")
    
    # Display summary
    st.subheader("📋 Meeting Summary")
    st.write(minutes.get('summary', 'No summary available'))
    
    # Display key decisions
    if minutes.get('key_decisions'):
        st.subheader("🎯 Key Decisions")
        for i, decision in enumerate(minutes['key_decisions'], 1):
            st.write(f"{i}. {decision}")
    
    # Display action items
    if minutes.get('action_items'):
        st.subheader("✅ Action Items")
        for item in minutes['action_items']:
            st.write(f"• **{item.get('assignee', 'Unassigned')}**: {item.get('task', '')}")
    
    # Download buttons
    st.subheader("📥 Download Results")
    col1, col2, col3 = st.columns(3)
    
    for i, (format_name, file_data) in enumerate(output_files.items()):
        col = [col1, col2, col3][i % 3]
        with col:
            st.download_button(
                label=f"Download {format_name}",
                data=file_data,
                file_name=f"meeting_minutes.{format_name.lower()}",
                mime=get_mime_type(format_name)
            )

def get_mime_type(format_name):
    """Get MIME type for different formats"""
    mime_types = {
        'JSON': 'application/json',
        'HTML': 'text/html',
        'PDF': 'application/pdf'
    }
    return mime_types.get(format_name, 'text/plain')

def display_recent_results():
    """Display recent processing results"""
    st.header("📊 Recent Results")
    
    # This would typically load from a database or file system
    # For demo purposes, showing placeholder data
    if st.checkbox("Show evaluation metrics"):
        st.subheader("📈 Quality Metrics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Transcription Accuracy", "94.2%", "2.1%")
        with col2:
            st.metric("Summary Quality (ROUGE)", "0.78", "0.05")
        with col3:
            st.metric("Processing Time", "2.3 min", "-0.5 min")

if __name__ == "__main__":
    main()
