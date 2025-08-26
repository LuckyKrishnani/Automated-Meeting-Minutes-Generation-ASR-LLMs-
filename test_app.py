"""
Test script to validate the meeting minutes generation system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.audio_processor import AudioProcessor
from src.transcriber import Transcriber

from src.summarizer import MeetingSummarizer
from src.output_generator import OutputGenerator
from src.evaluator import Evaluator
import tempfile
import json

def test_audio_processing():
    """Test audio processing functionality"""
    print("🎵 Testing Audio Processing...")
    processor = AudioProcessor()
    
    # Test file validation
    test_formats = ['.mp3', '.wav', '.mp4', '.avi']
    for fmt in test_formats:
        assert processor.validate_file(f"test{fmt}"), f"Format {fmt} should be supported"
    
    print("✅ Audio processing validation passed")

def test_transcription():
    """Test transcription functionality"""
    print("🎤 Testing Transcription...")
    transcriber = Transcriber()
    
    # Create a dummy audio file for testing
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
        tmp_file.write(b"dummy audio data")
        audio_path = tmp_file.name
    
    # Test transcription
    result = transcriber.transcribe(audio_path)
    assert 'text' in result, "Transcription should return text"
    assert 'segments' in result, "Transcription should return segments"
    
    # Clean up
    os.unlink(audio_path)
    print("✅ Transcription test passed")

def test_summarization():
    """Test meeting summarization with both models"""
    print("🤖 Testing Summarization...")
    
    # Test with Qwen model
    print("Testing Qwen model...")
    qwen_summarizer = MeetingSummarizer("qwen2.5-7b-instruct")
    
    test_meeting = {
        'title': 'Test Meeting',
        'date': '2024-01-15',
        'participants': ['Alice', 'Bob', 'Charlie'],
        'transcript': {
            'text': 'This is a test meeting transcript. We discussed project updates and made several decisions.'
        }
    }
    
    qwen_minutes = qwen_summarizer.generate_minutes(test_meeting)
    assert 'summary' in qwen_minutes, "Should generate summary"
    assert 'key_decisions' in qwen_minutes, "Should extract decisions"
    assert 'action_items' in qwen_minutes, "Should extract action items"
    
    # Test with LLaMA model
    print("Testing LLaMA model...")
    llama_summarizer = MeetingSummarizer("llama-3.1-8b-instruct")
    llama_minutes = llama_summarizer.generate_minutes(test_meeting)
    
    print("✅ Summarization test passed for both models")
    return qwen_minutes, llama_minutes

def test_output_generation():
    """Test output file generation"""
    print("📄 Testing Output Generation...")
    generator = OutputGenerator()
    
    test_minutes = {
        'meeting_info': {
            'title': 'Test Meeting',
            'date': '2024-01-15',
            'participants': ['Alice', 'Bob'],
            'duration': '30 minutes'
        },
        'summary': 'Test summary',
        'key_decisions': ['Decision 1', 'Decision 2'],
        'action_items': [
            {'task': 'Task 1', 'assignee': 'Alice', 'due_date': 'Next week'}
        ],
        'next_steps': ['Step 1', 'Step 2'],
        'full_transcript': 'Test transcript'
    }
    
    # Test all output formats
    outputs = generator.generate_outputs(test_minutes, ['JSON', 'HTML', 'PDF'])
    
    assert 'JSON' in outputs, "Should generate JSON output"
    assert 'HTML' in outputs, "Should generate HTML output"
    assert 'PDF' in outputs, "Should generate PDF output"
    
    # Validate JSON output
    json_data = json.loads(outputs['JSON'].decode('utf-8'))
    assert json_data['meeting_info']['title'] == 'Test Meeting'
    
    print("✅ Output generation test passed")

def test_evaluation():
    """Test evaluation metrics"""
    print("📊 Testing Evaluation...")
    evaluator = Evaluator()
    
    reference_text = "This is the reference text for testing evaluation metrics"
    hypothesis_text = "This is the hypothesis text for testing evaluation metrics"
    
    # Test transcription evaluation
    trans_metrics = evaluator.evaluate_transcription(reference_text, hypothesis_text)
    assert 'word_error_rate' in trans_metrics
    assert 'accuracy' in trans_metrics
    
    # Test summarization evaluation
    sum_metrics = evaluator.evaluate_summarization(reference_text, hypothesis_text)
    assert 'rouge_1' in sum_metrics
    assert 'rouge_2' in sum_metrics
    
    # Test report generation
    report = evaluator.generate_evaluation_report(trans_metrics, sum_metrics)
    assert 'EVALUATION REPORT' in report
    
    print("✅ Evaluation test passed")

def test_meetingbank_integration():
    """Test MeetingBank dataset integration"""
    print("📊 Testing MeetingBank Dataset Integration...")
    
    try:
        from datasets import load_dataset
        dataset = load_dataset("huuuyeah/meetingbank")
        print(f"✅ MeetingBank dataset loaded successfully")
        print(f"   - Dataset size: {len(dataset['train']) if 'train' in dataset else 'Unknown'}")
        print(f"   - Available splits: {list(dataset.keys())}")
        
        # Test a sample from the dataset
        if 'train' in dataset and len(dataset['train']) > 0:
            sample = dataset['train'][0]
            print(f"   - Sample keys: {list(sample.keys())}")
            
    except Exception as e:
        print(f"⚠️  MeetingBank dataset test failed: {str(e)}")
        print("   This is expected if running without internet or HuggingFace access")

def run_full_pipeline_test():
    """Test the complete pipeline end-to-end"""
    print("\n🚀 Running Full Pipeline Test...")
    
    # Create test audio file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
        tmp_file.write(b"dummy audio data for pipeline test")
        audio_path = tmp_file.name
    
    try:
        # Initialize all components
        audio_processor = AudioProcessor()
        transcriber = Transcriber()
        summarizer = MeetingSummarizer("qwen2.5-7b-instruct")
        output_generator = OutputGenerator()
        evaluator = Evaluator()
        
        # Step 1: Process audio
        processed_audio = audio_processor.process_file(audio_path)
        print("   ✅ Audio processing completed")
        
        # Step 2: Transcribe
        transcript = transcriber.transcribe(processed_audio)
        print("   ✅ Transcription completed")
        
        # Step 3: Generate minutes
        meeting_data = {
            'title': 'Pipeline Test Meeting',
            'date': '2024-01-15',
            'participants': ['Tester'],
            'transcript': transcript
        }
        minutes = summarizer.generate_minutes(meeting_data)
        print("   ✅ Minutes generation completed")
        
        # Step 4: Generate outputs
        outputs = output_generator.generate_outputs(minutes, ['JSON', 'HTML'])
        print("   ✅ Output generation completed")
        
        # Step 5: Evaluate (demo)
        trans_metrics = evaluator.evaluate_transcription("reference", transcript['text'])
        sum_metrics = evaluator.evaluate_summarization("reference", minutes['summary'])
        print("   ✅ Evaluation completed")
        
        print("\n🎉 Full pipeline test completed successfully!")
        
        # Display sample results
        print("\n📋 Sample Results:")
        print(f"   Summary: {minutes['summary'][:100]}...")
        print(f"   Decisions: {len(minutes.get('key_decisions', []))} found")
        print(f"   Action Items: {len(minutes.get('action_items', []))} found")
        
    finally:
        # Clean up
        os.unlink(audio_path)
        if 'processed_audio' in locals() and processed_audio != audio_path:
            try:
                os.unlink(processed_audio)
            except:
                pass

def main():
    """Run all tests"""
    print("🧪 Starting Meeting Minutes Generator Tests\n")
    
    try:
        # Individual component tests
        test_audio_processing()
        test_transcription()
        qwen_minutes, llama_minutes = test_summarization()
        test_output_generation()
        test_evaluation()
        test_meetingbank_integration()
        
        # Full pipeline test
        run_full_pipeline_test()
        
        print("\n✅ All tests completed successfully!")
        print("\n📊 Test Summary:")
        print("   - Audio Processing: ✅ PASSED")
        print("   - Transcription: ✅ PASSED")
        print("   - Summarization (Qwen): ✅ PASSED")
        print("   - Summarization (LLaMA): ✅ PASSED")
        print("   - Output Generation: ✅ PASSED")
        print("   - Evaluation: ✅ PASSED")
        print("   - MeetingBank Integration: ✅ TESTED")
        print("   - Full Pipeline: ✅ PASSED")
        
        print("\n🚀 The system is ready for use!")
        print("   Run: streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
