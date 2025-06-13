import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please check your .env file.")

genai.configure(api_key=GEMINI_API_KEY)

def list_models_and_check():
    try:
        print("Attempting to list models supporting 'generateContent':")
        found_models = []
        # Corrected: Use genai.list_models() directly (synchronous iterator)
        for m in genai.list_models(): 
            # The 'supported_generation_methods' attribute exists on the model object
            if "generateContent" in m.supported_generation_methods:
                found_models.append(m.name)
                # Print all relevant details
                print(f"  - {m.name} (Base: {m.base_model_id}, Display: {m.display_name}, Supported Methods: {m.supported_generation_methods})")
        
        if not found_models:
            print("No models found that support 'generateContent' with your API key.")
            print("Please ensure your API key is correct and has access to Generative Language models.")
            print("You might need to check Google AI Studio or Google Cloud Console for API key permissions.")
        else:
            print("\nIf 'gemini-pro-001' didn't work, try one of the above 'models/...' names in your services.py.")

    except Exception as e:
        print(f"An error occurred: {e}")
        if "403 Forbidden" in str(e) or "authentication" in str(e).lower():
            print("This usually means your GEMINI_API_KEY is incorrect, expired, or doesn't have the necessary permissions.")
            print("Please verify your API key in Google AI Studio or Google Cloud Console.")
        elif "Invalid API key" in str(e):
            print("Your API key is invalid. Please get a new one from Google AI Studio.")

if __name__ == "__main__":
    list_models_and_check()