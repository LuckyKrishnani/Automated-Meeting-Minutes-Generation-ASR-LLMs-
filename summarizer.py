import streamlit as st
from typing import Dict, List
import re
import time
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from datasets import load_dataset
import torch
import json


class MeetingSummarizer:
    """Generates structured meeting minutes using LLMs"""

    def __init__(self, model_name="qwen2.5-7b-instruct"):
        # Initialize with a default model name
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.meetingbank_dataset = None

        # Load LLM and dataset on initialization
        self._load_model()
        self._load_dataset()

    def _load_model(self):
        """Load the language model for summarization"""
        try:
            st.info(f"🤖 Loading {self.model_name} model...")

            # Choose proper model path based on name
            if "qwen" in self.model_name.lower():
                model_path = "Qwen/Qwen2.5-7B-Instruct"
            elif "llama" in self.model_name.lower():
                model_path = "meta-llama/Llama-3.1-8B-Instruct"
            else:
                model_path = self.model_name

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True
            )

            # Load model with FP16 precision and automatic device mapping (GPU if available)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )

            # Create pipeline for text generation
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                torch_dtype=torch.float16,
                device_map="auto"
            )

            st.success(f"✅ {self.model_name} model loaded successfully")

        except Exception as e:
            # If model fails, fallback to demo mode (no real LLM)
            st.error(f"Error loading LLM model: {str(e)}")
            st.warning("Falling back to demo mode...")
            self.model = "demo_mode"

    def _load_dataset(self):
        """Load MeetingBank dataset for training examples"""
        try:
            st.info("📊 Loading MeetingBank dataset...")
            self.meetingbank_dataset = load_dataset("huuuyeah/meetingbank")
            st.success("✅ MeetingBank dataset loaded successfully")
        except Exception as e:
            # Not critical, so just warn
            st.warning(f"Could not load MeetingBank dataset: {str(e)}")
            self.meetingbank_dataset = None

    def generate_minutes(self, meeting_data: Dict, max_length: int = 500) -> Dict:
        """
        Generate structured meeting minutes from transcript using real LLM.
        If LLM is not available, fallback to demo implementation.
        """
        try:
            # Extract transcript text
            transcript = meeting_data.get('transcript', {}).get('text', '')

            # If no model loaded, use demo mode
            if self.model == "demo_mode" or self.pipeline is None:
                return self._generate_demo_minutes(meeting_data, max_length)

            # Construct structured meeting minutes
            minutes = {
                'meeting_info': {
                    'title': meeting_data.get('title', 'Meeting'),
                    'date': meeting_data.get('date', ''),
                    'participants': meeting_data.get('participants', []),
                    'duration': self._estimate_duration(transcript)
                },
                'summary': self._generate_llm_summary(transcript, max_length),
                'key_decisions': self._extract_llm_decisions(transcript),
                'action_items': self._extract_llm_action_items(transcript),
                'next_steps': self._extract_llm_next_steps(transcript),
                'full_transcript': transcript
            }

            return minutes

        except Exception as e:
            st.error(f"Error generating meeting minutes: {str(e)}")
            return self._generate_demo_minutes(meeting_data, max_length)

    def _generate_llm_summary(self, transcript: str, max_length: int) -> str:
        """Generate summary using the loaded LLM"""
        # Create a prompt for summarization
        prompt = f"""
        Please analyze the following meeting transcript and provide a concise summary in {max_length} words or less.
        Focus on the main topics discussed, key points raised, and overall meeting outcomes.
        
        Transcript:
        {transcript[:2000]}  # Limit input length
        
        Summary:"""

        try:
            # Call the LLM pipeline
            response = self.pipeline(
                prompt,
                max_new_tokens=max_length,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

            # Extract summary text
            generated_text = response[0]['generated_text']
            summary = generated_text.split("Summary:")[-1].strip()
            return summary

        except Exception as e:
            st.warning(f"LLM summary generation failed: {str(e)}")
            return self._generate_demo_summary(transcript, max_length)

    def _extract_llm_decisions(self, transcript: str) -> List[str]:
        """Extract key decisions using LLM"""
        prompt = f"""
        Analyze this meeting transcript and extract the key decisions that were made.
        Return only the decisions as a numbered list.
        
        Transcript:
        {transcript[:1500]}
        
        Key Decisions:"""

        try:
            response = self.pipeline(
                prompt,
                max_new_tokens=200,
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

            # Extract only decision lines
            decisions_text = response[0]['generated_text'].split("Key Decisions:")[-1].strip()
            decisions = [d.strip() for d in decisions_text.split('\n') if d.strip() and not d.strip().isdigit()]
            return decisions[:5]  # Limit to 5 decisions

        except Exception as e:
            st.warning(f"LLM decision extraction failed: {str(e)}")
            return self._extract_demo_decisions(transcript)

    def _extract_llm_action_items(self, transcript: str) -> List[Dict]:
        """Extract action items (task, assignee, due date, priority) using LLM"""
        prompt = f"""
        Analyze this meeting transcript and extract action items with assignees and due dates.
        Format as: "Task - Assignee - Due Date - Priority"
        
        Transcript:
        {transcript[:1500]}
        
        Action Items:"""

        try:
            response = self.pipeline(
                prompt,
                max_new_tokens=300,
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

            items_text = response[0]['generated_text'].split("Action Items:")[-1].strip()
            action_items = []

            # Parse extracted action items
            for line in items_text.split('\n')[:5]:  # Limit to 5 items
                if '-' in line and line.strip():
                    parts = [p.strip() for p in line.split('-')]
                    if len(parts) >= 2:
                        action_items.append({
                            "task": parts[0],
                            "assignee": parts[1] if len(parts) > 1 else "Unassigned",
                            "due_date": parts[2] if len(parts) > 2 else "TBD",
                            "priority": parts[3] if len(parts) > 3 else "Medium"
                        })

            return action_items

        except Exception as e:
            st.warning(f"LLM action item extraction failed: {str(e)}")
            return self._extract_demo_action_items(transcript)

    def _extract_llm_next_steps(self, transcript: str) -> List[str]:
        """Extract next steps using LLM"""
        prompt = f"""
        Based on this meeting transcript, what are the logical next steps and follow-up actions?
        List them as bullet points.
        
        Transcript:
        {transcript[:1500]}
        
        Next Steps:"""

        try:
            response = self.pipeline(
                prompt,
                max_new_tokens=200,
                temperature=0.5,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

            steps_text = response[0]['generated_text'].split("Next Steps:")[-1].strip()
            # Clean and format bullet points
            next_steps = [s.strip().lstrip('•-*') for s in steps_text.split('\n') if s.strip()]
            return next_steps[:5]  # Limit to 5 steps

        except Exception as e:
            st.warning(f"LLM next steps extraction failed: {str(e)}")
            return self._extract_demo_next_steps(transcript)

    # ---------------- DEMO MODE FALLBACKS ---------------- #
    def _generate_demo_minutes(self, meeting_data: Dict, max_length: int) -> Dict:
        """Fallback demo implementation (used if no LLM available)"""
        time.sleep(2)  # Simulate processing delay
        transcript = meeting_data.get('transcript', {}).get('text', '')

        return {
            'meeting_info': {
                'title': meeting_data.get('title', 'Meeting'),
                'date': meeting_data.get('date', ''),
                'participants': meeting_data.get('participants', []),
                'duration': self._estimate_duration(transcript)
            },
            'summary': self._generate_demo_summary(transcript, max_length),
            'key_decisions': self._extract_demo_decisions(transcript),
            'action_items': self._extract_demo_action_items(transcript),
            'next_steps': self._extract_demo_next_steps(transcript),
            'full_transcript': transcript
        }

    def _generate_demo_summary(self, transcript: str, max_length: int) -> str:
        """Generate a demo summary"""
        return """
        The team meeting covered three main areas: marketing campaign progress, 
        budget analysis, and technical status updates. Key highlights include:
        
        • Marketing campaign has completed design phase and is moving to implementation
        • Budget analysis shows 15% under budget, providing flexibility for additional features
        • Technical development is on track with no major blockers
        • Team agreed to allocate extra budget funds to user testing
        • All systems are ready for the planned launch timeline
        """.strip()

    def _extract_demo_decisions(self, transcript: str) -> List[str]:
        """Demo decision extraction"""
        return [
            "Allocate extra budget funds to user testing",
            "Proceed with campaign launch by end of next week"
        ]

    def _extract_demo_action_items(self, transcript: str) -> List[Dict]:
        """Demo action items"""
        return [
            {
                "task": "Finalize campaign launch preparations",
                "assignee": "John",
                "due_date": "End of next week",
                "priority": "High"
            },
            {
                "task": "Prepare budget reallocation proposal",
                "assignee": "Jane",
                "due_date": "Next meeting",
                "priority": "Medium"
            }
        ]

    def _extract_demo_next_steps(self, transcript: str) -> List[str]:
        """Demo next steps"""
        return [
            "Review budget reallocation proposal in next meeting",
            "Monitor campaign launch progress",
            "Schedule user testing sessions"
        ]

    def _estimate_duration(self, transcript: str) -> str:
        """Estimate meeting duration from word count (150 words ≈ 1 minute)"""
        word_count = len(transcript.split())
        duration_minutes = max(1, word_count // 150)
        return f"{duration_minutes} minutes"
