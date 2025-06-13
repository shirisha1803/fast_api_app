import httpx
import json
import os

# Ensure the parent directory is in the Python path for module imports
import sys
from pathlib import Path

# Add the 'PROJ' directory to sys.path to allow importing 'app.config'
# This assumes chat_with_website.py is in PROJ/app
current_dir = Path(__file__).resolve().parent
proj_dir = current_dir.parent
sys.path.insert(0, str(proj_dir)) 

from app.config import settings

FASTAPI_URL = "http://127.0.0.1:8000"
API_KEY = settings.API_SECRET_KEY # Make sure your .env has API_SECRET_KEY set

async def chat_with_website():
    print("--- Start Chat Session ---")
    print("Type 'exit' to end the session.")

    website_url = input("Enter the URL of the website you want to chat about (e.g., https://www.google.com): ").strip()
    if not website_url:
        print("URL cannot be empty. Exiting.")
        return

    # Optional: Initial analysis request (can be skipped if you know the site is already 'known' to the LLM)
    # For this simple script, we'll assume a prior analysis or that the LLM can handle it.
    # In a real app, you might have a mechanism to fetch/store analysis results.

    conversation_history = []

    while True:
        user_query = input("You: ").strip()
        if user_query.lower() == 'exit':
            break

        if not user_query:
            continue

        headers = {
            "Content-Type": "application/json",
            #"X-API-Key": API_KEY
            "Authorization": f"Bearer {API_KEY}"
        }

        request_body = {
            "url": website_url,
            "query": user_query,
            "conversation_history": conversation_history
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{FASTAPI_URL}/chat", headers=headers, json=request_body)
                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
                
                chat_response = response.json()
                agent_response = chat_response.get("agent_response", "No response from agent.")
                context_sources = chat_response.get("context_sources", [])

                print(f"Agent: {agent_response}")
                if context_sources:
                    print("Context Sources:")
                    for source in context_sources:
                        print(f"- {source}")
                
                # Add current turn to history for next iteration
                conversation_history.append({"role": "user", "content": user_query})
                conversation_history.append({"role": "agent", "content": agent_response})

        except httpx.RequestError as e:
            print(f"An error occurred while requesting URL('{e.request.url}'): {e}")
        except httpx.HTTPStatusError as e:
            print(f"Error response {e.response.status_code}: {e.response.json()}")
        except json.JSONDecodeError:
            print("Failed to decode JSON response from server.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    print("--- Chat Session Ended ---")

if __name__ == "__main__":
    import asyncio
    asyncio.run(chat_with_website())