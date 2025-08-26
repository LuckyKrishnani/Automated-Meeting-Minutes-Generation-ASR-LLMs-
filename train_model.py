"""
Script to fine-tune a causal language model on the MeetingBank dataset
"""

import torch
from datasets import load_dataset
from typing import Dict
import os

# Try different import approaches
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
except ImportError:
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
        from transformers import Trainer
    except ImportError:
        print("Error: Cannot import required transformers components.")
        print("Please run: pip install --upgrade transformers")
        exit(1)

def prepare_training_data() -> Dict:
    """Load and preprocess the MeetingBank dataset."""
    print("Loading MeetingBank dataset...")
    try:
        dataset = load_dataset("huuuyeah/meetingbank")
        print(f"Dataset loaded successfully. Train samples: {len(dataset['train'])}")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        raise

    def format_example(example):
        transcript = example.get("transcript", "")
        summary = example.get("summary", "")

        # Create a single text for causal language modeling
        formatted_text = f"""Analyze this meeting transcript and generate structured minutes:

Transcript: {transcript}

Minutes: Summary: {summary}
Key Decisions: [extract from transcript]
Action Items: [extract from transcript]
Next Steps: [extract from transcript]<|endoftext|>"""

        return {"text": formatted_text}

    formatted_dataset = dataset.map(format_example, remove_columns=dataset["train"].column_names)
    return formatted_dataset

def fine_tune_model(model_name: str = "microsoft/DialoGPT-small"):  # Using smaller model for testing
    """Fine-tune a model on MeetingBank dataset."""
    print(f"Loading model and tokenizer: {model_name} ...")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Add padding token if it doesn't exist
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
        )
        
        # Enable gradient checkpointing to save memory
        model.gradient_checkpointing_enable()
        
    except Exception as e:
        print(f"Error loading model: {e}")
        raise

    print("Preparing dataset...")
    dataset = prepare_training_data()
    
    # Take a smaller subset for testing (remove this for full training)
    dataset["train"] = dataset["train"].select(range(min(100, len(dataset["train"]))))
    print(f"Using {len(dataset['train'])} samples for training")

    def tokenize_function(examples):
        # Tokenize the combined text
        tokenized = tokenizer(
            examples["text"],
            truncation=True,
            max_length=512,  # Reduced max length
            padding=True,
            return_tensors=None
        )
        
        # For causal LM, labels are the same as input_ids
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized

    print("Tokenizing dataset...")
    tokenized_dataset = dataset.map(
        tokenize_function, 
        batched=True,
        remove_columns=dataset["train"].column_names
    )

    print("Setting up training arguments...")
    
    # Check transformers version and use appropriate parameters
    try:
        import transformers
        version = transformers.__version__
        print(f"Transformers version: {version}")
    except:
        version = "unknown"
    
    # Create training arguments with version compatibility
    training_args_dict = {
        "output_dir": "./fine_tuned_meeting_model",
        "num_train_epochs": 1,
        "per_device_train_batch_size": 1,
        "gradient_accumulation_steps": 8,
        "warmup_steps": 10,
        "logging_steps": 5,
        "save_steps": 50,
        "learning_rate": 5e-5,
        "push_to_hub": False,
    }
    
    # Add version-specific parameters
    if torch.cuda.is_available():
        training_args_dict["fp16"] = True
    
    # Try different parameter names for evaluation strategy
    try:
        training_args = TrainingArguments(
            **training_args_dict,
            evaluation_strategy="no",
        )
    except TypeError:
        try:
            training_args = TrainingArguments(
                **training_args_dict,
                eval_strategy="no",
            )
        except TypeError:
            # Older versions might not have this parameter at all
            training_args = TrainingArguments(**training_args_dict)

    print("Initializing Trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        tokenizer=tokenizer,
    )

    print("Starting fine-tuning...")
    try:
        trainer.train()
    except Exception as e:
        print(f"Training error: {e}")
        raise

    print("Saving fine-tuned model...")
    trainer.save_model("./fine_tuned_meeting_model")
    tokenizer.save_pretrained("./fine_tuned_meeting_model")
    print("Training complete! Model saved to ./fine_tuned_meeting_model")

def test_model():
    """Test the fine-tuned model"""
    print("Testing fine-tuned model...")
    try:
        tokenizer = AutoTokenizer.from_pretrained("./fine_tuned_meeting_model")
        model = AutoModelForCausalLM.from_pretrained("./fine_tuned_meeting_model")
        
        test_input = """Analyze this meeting transcript and generate structured minutes:

Transcript: We discussed the quarterly budget and decided to increase marketing spend by 20%.

Minutes:"""
        
        inputs = tokenizer(test_input, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=100, temperature=0.7)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("Generated output:")
        print(result)
        
    except Exception as e:
        print(f"Error testing model: {e}")

if __name__ == "__main__":
    try:
        # Check if CUDA is available
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name()}")
            print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        
        fine_tune_model()
        
        # Test the model after training
        if os.path.exists("./fine_tuned_meeting_model"):
            test_model()
            
    except Exception as e:
        print(f"Script failed: {e}")
        import traceback
        traceback.print_exc()