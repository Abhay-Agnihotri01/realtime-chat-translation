from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
from functools import lru_cache

class TranslationService:
    def __init__(self):
        self.model_name = "facebook/nllb-200-distilled-600M"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading model {self.model_name} on {self.device}...")
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name).to(self.device)
        print("Model loaded successfully.")
        
        # Common greeting mappings to ensure proper literal translations
        self.greeting_mappings = {
            "eng_Latn": {
                "hello": {"spa_Latn": "hola", "fra_Latn": "bonjour", "deu_Latn": "hallo", "ita_Latn": "ciao"},
                "hi": {"spa_Latn": "hola", "fra_Latn": "salut", "deu_Latn": "hallo", "ita_Latn": "ciao"},
                "bye": {"spa_Latn": "adiós", "fra_Latn": "au revoir", "deu_Latn": "auf wiedersehen", "ita_Latn": "ciao"},
                "goodbye": {"spa_Latn": "adiós", "fra_Latn": "au revoir", "deu_Latn": "auf wiedersehen", "ita_Latn": "arrivederci"},
                "thanks": {"spa_Latn": "gracias", "fra_Latn": "merci", "deu_Latn": "danke", "ita_Latn": "grazie"},
                "thank you": {"spa_Latn": "gracias", "fra_Latn": "merci", "deu_Latn": "danke", "ita_Latn": "grazie"},
            }
        }

    def is_proper_name(self, text: str) -> bool:
        """Check if text appears to be a proper name"""
        text = text.strip()
        if len(text.split()) == 1 and text[0].isupper() and text.isalpha():
            common_words = {"Hello", "Hi", "Bye", "Thanks", "Yes", "No"}
            return text not in common_words
        return False

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        try:
            # Handle proper names - don't translate them
            if self.is_proper_name(text):
                print(f"Translation (proper name): '{text}' -> '{text}' (unchanged)")
                return text
            
            # Check for common greeting mappings first
            text_lower = text.lower().strip()
            if (source_lang in self.greeting_mappings and 
                text_lower in self.greeting_mappings[source_lang] and 
                target_lang in self.greeting_mappings[source_lang][text_lower]):
                
                translated_text = self.greeting_mappings[source_lang][text_lower][target_lang]
                print(f"Translation (mapped): {ascii(text)} ({source_lang}) -> {ascii(translated_text)} ({target_lang})")
                return translated_text
            
            # Use model for other translations
            translator = pipeline(
                "translation",
                model=self.model,
                tokenizer=self.tokenizer,
                src_lang=source_lang,
                tgt_lang=target_lang,
                device=0 if self.device == "cuda" else -1,
                max_length=512
            )
            
            result = translator(text)
            translated_text = result[0]['translation_text'] if result else text
            
            print(f"Translation (model): {ascii(text)} ({source_lang}) -> {ascii(translated_text)} ({target_lang})")
            return translated_text
            
        except Exception as e:
            print(f"Translation error for {ascii(text)}: {e}")
            # For proper names or single words, return original text
            if self.is_proper_name(text) or len(text.split()) == 1:
                return text
            return f"[Translation Error] {text}"