#!/usr/bin/env python3
"""
Script to download and setup required models for the meeting minutes generator
Including automatic FFmpeg download and setup
"""

import os
import sys
import platform
import zipfile
import subprocess
from pathlib import Path
import urllib.request
import shutil

def get_system_info():
    """Get system information for FFmpeg download"""
    system = platform.system().lower()
    architecture = platform.machine().lower()
    
    if system == "windows":
        if "64" in architecture or "amd64" in architecture:
            return "windows", "win64"
        else:
            return "windows", "win32"
    elif system == "darwin":  # macOS
        return "macos", "universal"
    elif system == "linux":
        if "64" in architecture or "amd64" in architecture:
            return "linux", "amd64"
        else:
            return "linux", "i386"
    else:
        return "unknown", "unknown"

def download_file(url, destination, description="file"):
    """Download a file with progress indication"""
    try:
        print(f"📥 Downloading {description}...")
        
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                print(f"\r⏳ Progress: {percent}%", end="", flush=True)
        
        urllib.request.urlretrieve(url, destination, progress_hook)
        print(f"\n✅ Downloaded {description} successfully")
        return True
    except Exception as e:
        print(f"\n❌ Failed to download {description}: {e}")
        return False

def download_and_setup_ffmpeg():
    """Download and setup FFmpeg automatically"""
    system, arch = get_system_info()
    
    if system == "unknown":
        print("❌ Unsupported operating system for automatic FFmpeg download")
        print("💡 Please download manually from: https://ffmpeg.org/download.html")
        return False
    
    # Create ffmpeg directory
    ffmpeg_dir = Path("ffmpeg")
    ffmpeg_dir.mkdir(exist_ok=True)
    
    # FFmpeg download URLs
    urls = {
        ("windows", "win64"): "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
        ("windows", "win32"): "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
        ("macos", "universal"): "https://evermeet.cx/ffmpeg/ffmpeg-5.1.2.zip",
        ("linux", "amd64"): "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz",
        ("linux", "i386"): "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz"
    }
    
    url = urls.get((system, arch))
    if not url:
        print(f"❌ No FFmpeg download available for {system} {arch}")
        return False
    
    # Determine file extension and download path
    if url.endswith('.zip'):
        download_path = ffmpeg_dir / "ffmpeg.zip"
    elif url.endswith('.tar.xz'):
        download_path = ffmpeg_dir / "ffmpeg.tar.xz"
    else:
        download_path = ffmpeg_dir / "ffmpeg_download"
    
    # Download FFmpeg
    if not download_file(url, download_path, "FFmpeg"):
        return False
    
    # Extract FFmpeg
    try:
        print("📦 Extracting FFmpeg...")
        
        if download_path.suffix == '.zip':
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(ffmpeg_dir)
        elif download_path.suffix == '.xz':
            import tarfile
            with tarfile.open(download_path, 'r:xz') as tar_ref:
                tar_ref.extractall(ffmpeg_dir)
        
        print("✅ FFmpeg extracted successfully")
        
        # Find the FFmpeg executable
        ffmpeg_exe = find_ffmpeg_executable(ffmpeg_dir)
        if ffmpeg_exe:
            # Add to PATH for current session
            current_path = os.environ.get('PATH', '')
            ffmpeg_bin_dir = str(ffmpeg_exe.parent)
            if ffmpeg_bin_dir not in current_path:
                os.environ['PATH'] = ffmpeg_bin_dir + os.pathsep + current_path
            
            print(f"✅ FFmpeg executable found at: {ffmpeg_exe}")
            
            # Clean up download file
            download_path.unlink()
            
            return True
        else:
            print("❌ Could not find FFmpeg executable after extraction")
            return False
            
    except Exception as e:
        print(f"❌ Failed to extract FFmpeg: {e}")
        return False

def find_ffmpeg_executable(search_dir):
    """Find FFmpeg executable in the given directory"""
    possible_names = ['ffmpeg', 'ffmpeg.exe']
    
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.lower() in possible_names:
                return Path(root) / file
    
    return None

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg is available")
            return True
        else:
            print("❌ FFmpeg not working properly")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found in system PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg check timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {e}")
        return False

def setup_whisper():
    """Setup Whisper model"""
    try:
        import whisper
        print("📥 Downloading Whisper model...")
        model = whisper.load_model("base")
        print("✅ Whisper model setup complete")
        return True
    except ImportError:
        print("❌ Whisper not installed. Install with: pip install openai-whisper")
        return False
    except Exception as e:
        print(f"❌ Error setting up Whisper: {e}")
        return False

def setup_llm_models():
    """Setup LLM models"""
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        models = [
            "Qwen/Qwen2.5-7B-Instruct",
            "meta-llama/Llama-3.1-8B-Instruct"
        ]
        
        for model_name in models:
            print(f"📥 Downloading {model_name}...")
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(model_name)
                print(f"✅ {model_name} setup complete")
            except Exception as e:
                print(f"⚠️  Could not download {model_name}: {e}")
        
        return True
    except ImportError:
        print("❌ Transformers not installed. Install with: pip install transformers torch")
        return False

def install_dependencies():
    """Install required Python packages"""
    dependencies = [
        "openai-whisper",
        "transformers",
        "torch",
        "streamlit",
        "pandas",
        "numpy",
        "python-docx",
        "Pillow"
    ]
    
    print("📦 Installing Python dependencies...")
    
    for package in dependencies:
        try:
            print(f"Installing {package}...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {package} installed successfully")
            else:
                print(f"⚠️  Warning installing {package}: {result.stderr}")
        except Exception as e:
            print(f"❌ Failed to install {package}: {e}")

def create_requirements_txt():
    """Create requirements.txt file"""
    requirements = """openai-whisper>=20231117
transformers>=4.35.0
torch>=2.0.0
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
python-docx>=0.8.11
Pillow>=10.0.0
accelerate>=0.24.0
sentencepiece>=0.1.99
protobuf>=3.20.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print("✅ Created requirements.txt")

def main():
    """Main setup function"""
    print("🚀 Setting up Meeting Minutes Generator...")
    print("=" * 60)
    
    success = True
    
    # Create requirements.txt
    create_requirements_txt()
    
    # Install dependencies
    install_choice = input("Install Python dependencies now? (Y/n): ").lower().strip()
    if install_choice != 'n':
        install_dependencies()
    
    print("\n" + "=" * 60)
    print("🎵 Setting up FFmpeg...")
    
    # Check if FFmpeg is already available
    if not check_ffmpeg():
        print("FFmpeg not found. Attempting automatic download...")
        
        download_choice = input("Download FFmpeg automatically? (Y/n): ").lower().strip()
        if download_choice != 'n':
            if download_and_setup_ffmpeg():
                # Check again after download
                if not check_ffmpeg():
                    print("⚠️  FFmpeg downloaded but not accessible. You may need to restart your terminal.")
                    success = False
            else:
                print("❌ Failed to download FFmpeg automatically")
                print("💡 Please download manually from: https://ffmpeg.org/download.html")
                success = False
        else:
            print("❌ FFmpeg setup skipped")
            success = False
    
    print("\n" + "=" * 60)
    print("🎤 Setting up Whisper...")
    
    # Setup Whisper
    if not setup_whisper():
        success = False
    
    print("\n" + "=" * 60)
    print("🤖 LLM Model Setup (Optional - Large Downloads)")
    
    # Setup LLM models (optional - these are large)
    setup_choice = input("Download LLM models now? This will take significant time and disk space (y/N): ").lower().strip()
    
    if setup_choice == 'y':
        if not setup_llm_models():
            print("⚠️  LLM models not set up, but system can still work with API calls")
    
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 Setup complete!")
        print("📝 Next steps:")
        print("   1. If FFmpeg was downloaded, restart your terminal")
        print("   2. Run: streamlit run app.py")
        print("   3. Upload audio files and generate meeting minutes!")
    else:
        print("⚠️  Setup completed with some issues. Check the messages above.")
        print("💡 You may still be able to run the app with limited functionality.")
    
    print("\n📁 Files created:")
    print("   - requirements.txt")
    if Path("ffmpeg").exists():
        print("   - ffmpeg/ (FFmpeg installation)")

if __name__ == "__main__":
    main()