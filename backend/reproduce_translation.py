from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch

def test_translation():
    model_name = "facebook/nllb-200-distilled-600M"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading model {model_name} on {device}...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
    
    # Test cases
    cases = [
        ("Hello", "eng_Latn", "spa_Latn"),
        ("How are you?", "eng_Latn", "spa_Latn"),
        ("Good morning", "eng_Latn", "fra_Latn"),
    ]
    
    print("\n--- Testing Pipeline Method (Current Implementation) ---")
    for text, src, tgt in cases:
        try:
            translator = pipeline(
                "translation",
                model=model,
                tokenizer=tokenizer,
                src_lang=src,
                tgt_lang=tgt,
                device=0 if device == "cuda" else -1,
                max_length=512
            )
            result = translator(text)
            print(f"'{text}' ({src}) -> '{result[0]['translation_text']}' ({tgt})")
        except Exception as e:
            print(f"Error: {e}")

    print("\n--- Testing Generate Method (Proposed Fix) ---")
    for text, src, tgt in cases:
        try:
            inputs = tokenizer(text, return_tensors="pt").to(device)
            forced_bos_token_id = tokenizer.convert_tokens_to_ids(tgt)
            
            translated_tokens = model.generate(
                **inputs, 
                forced_bos_token_id=forced_bos_token_id, 
                max_length=100
            )
            result = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
            print(f"'{text}' ({src}) -> '{result}' ({tgt})")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_translation()
