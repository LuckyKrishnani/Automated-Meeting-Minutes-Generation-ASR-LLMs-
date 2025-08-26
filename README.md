# Automated Meeting Minutes Generator

An AI-powered system that transforms meeting recordings into structured, professional minutes using Automatic Speech Recognition (ASR) and Large Language Models (LLMs).

## Features

🎤 **Audio Processing**: Supports multiple audio/video formats (MP3, WAV, MP4, AVI, MOV, MKV)
🤖 **AI Transcription**: Uses Whisper for accurate speech-to-text conversion
📝 **Smart Summarization**: Leverages LLMs (Qwen-2.5-7B, LLaMA-3.1-8B) for intelligent content analysis
📋 **Structured Output**: Generates summaries, key decisions, and action items
📄 **Multiple Formats**: Export results as JSON, HTML, or PDF
📊 **Quality Metrics**: Evaluates transcription and summarization accuracy
🐳 **Docker Support**: Easy deployment with containerization

## Quick Start with Docker (Recommended)

1. Clone the repository:
\`\`\`bash
git clone <repository-url>
cd meeting-minutes-generator
\`\`\`

2. Run the Docker setup script:
\`\`\`bash
chmod +x scripts/docker_setup.sh
./scripts/docker_setup.sh
\`\`\`

3. Start the application:
\`\`\`bash
docker-compose up -d
\`\`\`

4. Access the application at `http://localhost:8501`

### Docker Commands

\`\`\`bash
# Start the application
docker-compose up -d

# Start with nginx reverse proxy (production)
docker-compose --profile production up -d

# View logs
docker-compose logs -f meeting-minutes-app

# Stop the application
docker-compose down

# Rebuild after code changes
docker-compose build --no-cache
\`\`\`

## Manual Installation

1. Clone the repository:
\`\`\`bash
git clone <repository-url>
cd meeting-minutes-generator
\`\`\`

2. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. Install additional system dependencies:
\`\`\`bash
# For audio processing (optional - FFmpeg)
# On Ubuntu/Debian:
sudo apt-get install ffmpeg

# On macOS:
brew install ffmpeg

# On Windows:
# Download from https://ffmpeg.org/download.html
\`\`\`

## Usage

1. Start the Streamlit application:
\`\`\`bash
streamlit run app.py
\`\`\`

2. Open your browser and navigate to `http://localhost:8501`

3. Upload your meeting recording (audio or video file)

4. Fill in meeting details (title, date, participants)

5. Configure processing options in the sidebar

6. Click "Generate Meeting Minutes" to process

7. Download results in your preferred format

## System Architecture

\`\`\`
Meeting Recording → Audio Processing → Speech Recognition → Text Summarization → Output Generation
                                ↓                           ↓                    ↓
                           FFmpeg/Audio              Whisper ASR         LLM Processing
                           Preprocessing                                  (Qwen/LLaMA)
\`\`\`

## Configuration Options

- **Model Selection**: Choose between Qwen-2.5-7B-Instruct or LLaMA-3.1-8B-Instruct
- **Output Formats**: Select JSON, HTML, and/or PDF export
- **Audio Processing**: Adjust chunk length for processing
- **Summary Length**: Control maximum summary word count

## Output Structure

Generated meeting minutes include:

- **Meeting Information**: Title, date, participants, duration
- **Executive Summary**: Concise overview of key points
- **Key Decisions**: Important decisions made during the meeting
- **Action Items**: Tasks assigned with owners and due dates
- **Next Steps**: Follow-up actions and future plans
- **Full Transcript**: Complete transcription of the meeting

## Evaluation Metrics

The system provides quality assessment using:

- **Transcription**: Word Error Rate (WER), Character Error Rate (CER), BLEU Score
- **Summarization**: ROUGE-1, ROUGE-2, ROUGE-L, Semantic Similarity

## Technical Stack

- **Frontend**: Streamlit
- **Audio Processing**: FFmpeg
- **Speech Recognition**: OpenAI Whisper
- **Language Models**: Qwen-2.5-7B-Instruct, LLaMA-3.1-8B-Instruct
- **Output Generation**: Custom HTML/PDF generators
- **Evaluation**: Custom metrics implementation
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx (optional, for production)

## Docker Configuration

The application includes comprehensive Docker support:

- **Multi-stage Dockerfile**: Optimized for production with system dependencies
- **Docker Compose**: Easy orchestration with health checks and volume mounts
- **Nginx Integration**: Optional reverse proxy for production deployments
- **Volume Persistence**: Uploads, outputs, and models are persisted
- **Health Monitoring**: Built-in health checks for container monitoring

### Environment Variables

The Docker setup supports the following environment variables:

- `STREAMLIT_SERVER_PORT`: Port for Streamlit (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: 0.0.0.0)
- `PYTHONPATH`: Python path (default: /app)

## Limitations

- Demo version uses simulated processing for some components
- Real implementation requires actual model downloads and setup
- Processing time depends on file size and model complexity
- Quality depends on audio clarity and speaker separation

## Future Enhancements

- Speaker diarization for multi-speaker identification
- Real-time processing capabilities
- Integration with calendar systems
- Custom template support
- Advanced evaluation metrics
- Cloud deployment options

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
