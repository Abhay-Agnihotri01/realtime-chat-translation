import time
import json
import statistics
from sacrebleu.metrics import BLEU
from typing import List, Dict, Tuple
from translation_service import TranslationService

class ModelEvaluator:
    def __init__(self):
        self.translation_service = None
        self.latency_history = []
        self.bleu_scores = []
    
    def get_translation_service(self):
        if self.translation_service is None:
            self.translation_service = TranslationService()
        return self.translation_service
    
    def calculate_bleu(self, references: List[List[str]], hypotheses: List[str]) -> float:
        """Calculate BLEU score"""
        bleu = BLEU()
        score = bleu.corpus_score(hypotheses, references)
        return score.score
    
    def measure_translation_latency(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, float]:
        """Measure translation latency"""
        start_time = time.time()
        ts = self.get_translation_service()
        result = ts.translate(text, source_lang, target_lang)
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        self.latency_history.append(latency_ms)
        return result, latency_ms
    
    def evaluate_model_performance(self, test_data: List[Dict]) -> Dict:
        """Comprehensive model evaluation"""
        results = {
            "bleu_scores": [],
            "latencies": [],
            "avg_latency": 0,
            "avg_bleu": 0,
            "p95_latency": 0
        }
        
        for item in test_data:
            # Measure translation
            translation, latency = self.measure_translation_latency(
                item["source_text"], 
                item["source_lang"], 
                item["target_lang"]
            )
            
            # Calculate BLEU if reference available
            if "reference" in item:
                bleu_score = self.calculate_bleu([[item["reference"]]], [translation])
                results["bleu_scores"].append(bleu_score)
            
            results["latencies"].append(latency)
        
        # Calculate statistics
        if results["latencies"]:
            results["avg_latency"] = statistics.mean(results["latencies"])
            results["p95_latency"] = statistics.quantiles(results["latencies"], n=20)[18]  # 95th percentile
        
        if results["bleu_scores"]:
            results["avg_bleu"] = statistics.mean(results["bleu_scores"])
        
        return results
    
    def generate_performance_report(self) -> str:
        """Generate performance analysis report"""
        if not self.latency_history:
            return "No performance data available"
        
        avg_latency = statistics.mean(self.latency_history)
        p95_latency = statistics.quantiles(self.latency_history, n=20)[18] if len(self.latency_history) > 20 else max(self.latency_history)
        
        report = f"""
=== Model Performance Report ===
Total Translations: {len(self.latency_history)}
Average Latency: {avg_latency:.2f}ms
P95 Latency: {p95_latency:.2f}ms
Target Latency: <500ms (Real-time requirement)
Status: {'✓ PASS' if avg_latency < 500 else '✗ FAIL'}
        """
        return report

evaluator = ModelEvaluator()

if __name__ == "__main__":
    # Test data example
    test_data = [
        {
            "source_text": "Hello, how are you?",
            "source_lang": "eng_Latn",
            "target_lang": "spa_Latn",
            "reference": "Hola, ¿cómo estás?"
        }
    ]
    
    results = evaluator.evaluate_model_performance(test_data)
    print(json.dumps(results, indent=2))
    print(evaluator.generate_performance_report())
