import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Cache dla nazwy modelu, aby nie odpytywać API o listę modeli przy każdym poście
CACHED_MODEL_NAME = None

def get_best_model():
    global CACHED_MODEL_NAME
    if CACHED_MODEL_NAME:
        return CACHED_MODEL_NAME
        
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash_models = [m for m in models if 'flash' in m.lower()]
        if flash_models:
            CACHED_MODEL_NAME = flash_models[0]
        else:
            CACHED_MODEL_NAME = models[0] if models else 'gemini-1.5-flash'
        return CACHED_MODEL_NAME
    except Exception as e:
        print(f"Błąd podczas listowania modeli: {e}")
        return 'gemini-1.5-flash' # Fallback

def generate_content(user_input):
    model_name = get_best_model()
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    Na podstawie poniższego opisu dnia:
    "{user_input}"
    
    Wygeneruj RÓWNOCZEŚNIE dwie oddzielne sekcje.
    WAŻNE: Użyj symbolu 🎬 jako JEDYNEGO separatora między sekcją LinkedIn a Scenariuszem.
    
    Sekcja 1: Profesjonalny post na LinkedIn (tekst + hashtagi).
    Sekcja 2 (zacznij od 🎬): Scenariusz wideo 60s (TikTok/Shorts) z sekcjami: HOOK, ŚRODEK, CTA.
    
    Język: Polski.
    """
    
    response = model.generate_content(prompt)
    return response.text
