from translation_service import TranslationService
import sys

def test_issue():
    print("Initializing service...")
    ts = TranslationService()
    
    text = "priyanshi"
    source_lang = "eng_Latn"
    target_lang = "hin_Deva"
    
    print(f"Testing translation for '{text}' from {source_lang} to {target_lang}")
    
    result = ts.translate(text, source_lang, target_lang)
    print(f"Result: '{result}'")
    
    # Debugging the logic in exception block if it were to happen
    print(f"is_proper_name('{text}'): {ts.is_proper_name(text)}")
    print(f"len('{text}'.split()): {len(text.split())}")

if __name__ == "__main__":
    test_issue()
