import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_content(prompt):
    # Dynamicznie szukamy najlepszego modelu flash, żeby uniknąć błędu 404
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Próbujemy znaleźć najnowszy model flash
    model_name = "gemini-1.5-flash" # Domyślny
    for m in available_models:
        if "1.5-flash" in m:
            model_name = m
            break
            
    model = genai.GenerativeModel(model_name)
    
    full_prompt = f"""
    Jesteś profesjonalnym copywriterem i twórcą contentu wideo. 
    Na podstawie opisu dnia użytkownika: "{prompt}"
    
    Przygotuj:
    1. Post na LinkedIn (profesjonalny, angażujący, z emotikonami).
    2. Krótki scenariusz (60s) na wideo (TikTok/Reels) zaczynający się od mocnego haczyka.
    
    Użyj separatora 🎬 przed scenariuszem wideo.
    """
    
    response = model.generate_content(full_prompt)
    return response.text
