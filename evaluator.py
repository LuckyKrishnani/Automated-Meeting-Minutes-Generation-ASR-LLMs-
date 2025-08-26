import streamlit as st
from typing import Dict, List, Tuple
import re

class Evaluator:
    """Evaluates the quality of transcription and summarization"""
    
    def __init__(self):
        # Constructor (currently unused, but may be extended later)
        pass
    
    def evaluate_transcription(self, reference: str, hypothesis: str) -> Dict[str, float]:
        """
        Evaluate transcription quality using WER, CER, BLEU, and accuracy.
        
        Args:
            reference (str): Ground truth transcription (expected text)
            hypothesis (str): Generated transcription (predicted text)
            
        Returns:
            Dict[str, float]: Dictionary containing evaluation metrics
        """
        try:
            # Calculate metrics (simplified versions)
            metrics = {
                'word_error_rate': self._calculate_wer(reference, hypothesis),
                'character_error_rate': self._calculate_cer(reference, hypothesis),
                'bleu_score': self._calculate_bleu(reference, hypothesis),
                'accuracy': 1 - self._calculate_wer(reference, hypothesis)  # Accuracy = 1 - WER
            }
            
            return metrics
            
        except Exception as e:
            st.error(f"Error evaluating transcription: {str(e)}")
            return {}
    
    def evaluate_summarization(self, reference: str, hypothesis: str) -> Dict[str, float]:
        """
        Evaluate summarization quality using ROUGE and semantic similarity.
        
        Args:
            reference (str): Ground truth summary
            hypothesis (str): Generated summary
            
        Returns:
            Dict[str, float]: Dictionary containing evaluation metrics
        """
        try:
            # Compute summarization evaluation metrics
            metrics = {
                'rouge_1': self._calculate_rouge_1(reference, hypothesis),
                'rouge_2': self._calculate_rouge_2(reference, hypothesis),
                'rouge_l': self._calculate_rouge_l(reference, hypothesis),
                'semantic_similarity': self._calculate_semantic_similarity(reference, hypothesis)
            }
            
            return metrics
            
        except Exception as e:
            st.error(f"Error evaluating summarization: {str(e)}")
            return {}
    
    # -------------------
    # Metric Calculations
    # -------------------
    
    def _calculate_wer(self, reference: str, hypothesis: str) -> float:
        """Calculate Word Error Rate (simplified: overlap-based, not true edit distance)."""
        ref_words = reference.lower().split()
        hyp_words = hypothesis.lower().split()
        
        if len(ref_words) == 0:
            return 1.0 if len(hyp_words) > 0 else 0.0
        
        # Simplified WER: 1 - (# common words / # reference words)
        common_words = set(ref_words) & set(hyp_words)
        wer = 1 - (len(common_words) / len(ref_words))
        return max(0.0, min(1.0, wer))  # Clamp between 0 and 1
    
    def _calculate_cer(self, reference: str, hypothesis: str) -> float:
        """Calculate Character Error Rate (simplified)."""
        if len(reference) == 0:
            return 1.0 if len(hypothesis) > 0 else 0.0
        
        # Compare characters at the same position
        common_chars = sum(1 for a, b in zip(reference.lower(), hypothesis.lower()) if a == b)
        cer = 1 - (common_chars / len(reference))
        return max(0.0, min(1.0, cer))
    
    def _calculate_bleu(self, reference: str, hypothesis: str) -> float:
        """Calculate BLEU score (simplified unigram precision)."""
        ref_words = set(reference.lower().split())
        hyp_words = set(hypothesis.lower().split())
        
        if len(hyp_words) == 0:
            return 0.0
        
        precision = len(ref_words & hyp_words) / len(hyp_words)
        return precision
    
    def _calculate_rouge_1(self, reference: str, hypothesis: str) -> float:
        """Calculate ROUGE-1 score (unigram overlap ratio)."""
        ref_words = set(reference.lower().split())
        hyp_words = set(hypothesis.lower().split())
        
        if len(ref_words) == 0:
            return 0.0
        
        overlap = len(ref_words & hyp_words)
        return overlap / len(ref_words)
    
    def _calculate_rouge_2(self, reference: str, hypothesis: str) -> float:
        """Calculate ROUGE-2 score (bigram overlap ratio)."""
        ref_bigrams = self._get_bigrams(reference.lower())
        hyp_bigrams = self._get_bigrams(hypothesis.lower())
        
        if len(ref_bigrams) == 0:
            return 0.0
        
        overlap = len(set(ref_bigrams) & set(hyp_bigrams))
        return overlap / len(ref_bigrams)
    
    def _calculate_rouge_l(self, reference: str, hypothesis: str) -> float:
        """Calculate ROUGE-L score (simplified: reuse ROUGE-1 as placeholder)."""
        # Normally this is based on Longest Common Subsequence (LCS)
        return self._calculate_rouge_1(reference, hypothesis)
    
    def _calculate_semantic_similarity(self, reference: str, hypothesis: str) -> float:
        """Calculate semantic similarity (simplified: word overlap proxy)."""
        # Real implementation would use embeddings (e.g., cosine similarity of sentence vectors)
        return self._calculate_rouge_1(reference, hypothesis)
    
    def _get_bigrams(self, text: str) -> List[Tuple[str, str]]:
        """Extract bigrams from text."""
        words = text.split()
        return [(words[i], words[i+1]) for i in range(len(words)-1)]
    
    # -------------------
    # Reporting
    # -------------------
    
    def generate_evaluation_report(self, transcription_metrics: Dict, 
                                 summarization_metrics: Dict) -> str:
        """Generate a formatted evaluation report from metrics."""
        
        report = f"""
        📊 EVALUATION REPORT
        ==================
        
        🎤 Transcription Quality:
        • Word Error Rate: {transcription_metrics.get('word_error_rate', 0):.3f}
        • Character Error Rate: {transcription_metrics.get('character_error_rate', 0):.3f}
        • BLEU Score: {transcription_metrics.get('bleu_score', 0):.3f}
        • Accuracy: {transcription_metrics.get('accuracy', 0):.1%}
        
        📝 Summarization Quality:
        • ROUGE-1: {summarization_metrics.get('rouge_1', 0):.3f}
        • ROUGE-2: {summarization_metrics.get('rouge_2', 0):.3f}
        • ROUGE-L: {summarization_metrics.get('rouge_l', 0):.3f}
        • Semantic Similarity: {summarization_metrics.get('semantic_similarity', 0):.3f}
        
        💡 Recommendations:
        • Transcription quality is {'excellent' if transcription_metrics.get('accuracy', 0) > 0.9 else 'good' if transcription_metrics.get('accuracy', 0) > 0.8 else 'needs improvement'}
        • Summary captures {'high' if summarization_metrics.get('rouge_1', 0) > 0.7 else 'moderate' if summarization_metrics.get('rouge_1', 0) > 0.5 else 'low'} content overlap
        """
        
        return report.strip()
