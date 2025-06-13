import httpx
import os
from dotenv import load_dotenv

# Load environment variables (assuming .env is in the same directory as this script, or parent)
load_dotenv()

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000"
API_SECRET_KEY = os.getenv("API_SECRET_KEY") # Ensure this is set in your .env file
if not API_SECRET_KEY:
    raise ValueError("API_SECRET_KEY environment variable not set. Please check your .env file.")

# --- Request Parameters ---
target_url = " https://www.google.com" # Replace with the website you want to analyze
questions_to_ask = [
    "What is their primary business model?",
    "What are their main products or services?",
    "Where is the company located?"
]

headers = {
    "Content-Type": "application/json",
    #"X-API-Key": API_SECRET_KEY
    "Authorization": f"Bearer {API_SECRET_KEY}"
}

payload = {
    "url": target_url,
    "questions": questions_to_ask
}

async def analyze_website():
    async with httpx.AsyncClient() as client:
        try:
            print(f"Sending request to {BASE_URL}/analyze for URL: {target_url}")
            response = await client.post(f"{BASE_URL}/analyze", headers=headers, json=payload)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

            analysis_data = response.json()
            #print(response.json())
            print("\n--- Website Analysis Result ---")
            print(f"URL: {analysis_data.get('url')}")
            print(f"Analysis Timestamp: {analysis_data.get('analysis_timestamp')}")

            company_info = analysis_data.get('company_info', {})
            print("\nCompany Info:")
            for key, value in company_info.items():
                if isinstance(value, dict):
                    print(f"  {key.replace('_', ' ').title()}:")
                    for sub_key, sub_value in value.items():
                        print(f"    {sub_key.replace('_', ' ').title()}: {sub_value}")
                else:
                    print(f"  {key.replace('_', ' ').title()}: {value}")

            extracted_answers = analysis_data.get('extracted_answers', [])
            if extracted_answers:
                print("\nExtracted Answers:")
                for qa in extracted_answers:
                    print(f"  Question: {qa.get('question')}")
                    print(f"  Answer: {qa.get('answer')}")
            else:
                print("\nNo specific answers extracted for the questions provided.")

        except httpx.HTTPStatusError as e:
            print(f"Error response {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}: {e}")
        except ValueError as e:
            print(f"Configuration Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(analyze_website())