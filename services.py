import httpx
import google.generativeai as genai
import json
from bs4 import BeautifulSoup
from fastapi import HTTPException
from typing import Optional, List
from .config import settings
from . import models
# from .models import CompanyInfo # <-- THIS LINE HAS BEEN REMOVED

# Configure the Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

# --- PROMPT ENGINEERING ---
# This section contains the carefully crafted prompts for the LLM.

ANALYSIS_PROMPT_TEMPLATE = """
Analyze the text content from the homepage of the website: {url}.
Based *only* on the text provided below, extract the following business information.
Your response MUST be a valid JSON object matching the specified structure. Do not include any text or markdown formatting before or after the JSON.

**JSON Output Structure:**
{{
  "company_info": {{
    "industry": "Infer the primary industry (e.g., 'SaaS', 'E-commerce', 'FinTech').",
    "company_size": "State the employee count or size (e.g., '1-10 employees', 'Large Enterprise') if mentioned, otherwise null.",
    "location": "Extract the headquarters or primary location if mentioned, otherwise null.",
    "core_products_services": ["List the main products or services offered."],
    "unique_selling_proposition": "Summarize what makes the company stand out in one sentence.",
    "target_audience": "Describe the primary customer demographic (e.g., 'B2B SaaS companies', 'Individual Consumers').",
    "contact_info": {{
      "email": "Extract email if mentioned, otherwise null.",
      "phone": "Extract phone number if mentioned, otherwise null.",
      "social_media": {{
        "linkedin": "Extract LinkedIn URL if present, otherwise null.",
        "twitter": "Extract Twitter URL if present, otherwise null."
      }}
    }}
  }},
  "extracted_answers": [
    {{
      "question": "Original question asked (if questions input was provided).",
      "answer": "Concise answer based on website content, otherwise 'Not available'."
    }}
  ]
}}

**Website Text Content:**
{text_content}

**Questions to Answer (if any, otherwise provide default insights):**
{questions_json}
"""


CONVERSATIONAL_PROMPT_TEMPLATE = """
You are an AI assistant tasked with answering questions about a website, using ONLY the provided text content and conversation history.
Do not invent information. If the information is not present in the text, state that.
Your response MUST be a valid JSON object matching the specified structure. Do not include any text or markdown formatting before or after the JSON.

**JSON Output Structure:**
{{
  "agent_response": "Your concise answer to the user's query.",
  "context_sources": ["List brief phrases or sections from the website text that directly support your answer."]
}}

**Website Text Content:**
{text_content}

**Conversation History:**
{formatted_history}

**User's Current Query:**
{query}
"""


async def scrape_website_text(url: str) -> Optional[str]:
    """Scrapes the text content from a given URL's homepage."""
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

            soup = BeautifulSoup(response.text, 'html.parser')

            # Prioritize visible text content from common elements
            paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
            headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']) if h.get_text(strip=True)]
            
            # Combine content, removing duplicates and ensuring readability
            content_list = list(set(paragraphs + headings))
            text_content = "\n".join(content_list)
            
            # Fallback to body text if specific elements are scarce
            if len(text_content) < 200: # Arbitrary threshold for minimal content
                body_text = soup.body.get_text(separator=' ', strip=True) if soup.body else ''
                text_content = body_text

            return text_content[:4000] # Limit content to avoid overly long prompts
    except httpx.RequestError as e:
        print(f"DEBUG: HTTPX Request Error for {url}: {e}")
        raise HTTPException(status_code=400, detail=f"Could not connect to URL: {url}. Error: {e}")
    except httpx.HTTPStatusError as e:
        print(f"DEBUG: HTTPX Status Error for {url}: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP Error for {url}: {e.response.status_code}")
    except Exception as e:
        print(f"DEBUG: Unexpected error during scraping {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to scrape website: {url}. Error: {e}")


def generate_llm_response(prompt: str) -> str:
    """Sends a prompt to the Gemini LLM and returns the text response."""
    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME) # Using model name from config
        response = model.generate_content(prompt)
        # Access content directly from the response object
        return response.text
    except Exception as e:
        print(f"DEBUG: LLM API Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get response from AI model: {e}")


async def get_website_analysis(url: str, questions: List[str]) -> dict:
    """Orchestrates scraping and AI analysis for the /analyze endpoint."""
    text_content = await scrape_website_text(url)
    if not text_content:
        raise HTTPException(status_code=404, detail="Could not extract content from the website.")

    questions_json = json.dumps([{"question": q} for q in questions]) if questions else "[]"
    
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        url=url,
        text_content=text_content,
        questions_json=questions_json
    )

    llm_output = generate_llm_response(prompt)

    # Clean the LLM output by removing markdown fences and stripping whitespace
    llm_output = llm_output.strip().removeprefix("```json").removesuffix("```")
    llm_output = llm_output.strip()

    try:
        analysis_data = json.loads(llm_output)

        # --- NEW: Clean 'null' strings from HttpUrl fields before Pydantic validation ---
        company_info = analysis_data.get("company_info", {})
        contact_info = company_info.get("contact_info", {})
        social_media = contact_info.get("social_media", {})

        if social_media:
            for key in ["linkedin", "twitter"]:
                # Ensure the value is a string and it's 'null' (case-insensitive)
                if isinstance(social_media.get(key), str) and social_media[key].lower() == 'null':
                    social_media[key] = None # Convert to Python None
        # --- END NEW ---

        return models.AnalysisResponse(
            company_info=models.CompanyInfo(**company_info),
            extracted_answers=[models.ExtractedAnswer(**qa) for qa in analysis_data.get("extracted_answers", [])]
        )
    except json.JSONDecodeError:
        print(f"DEBUG: Failed to decode JSON from LLM. Raw output was: '{llm_output}'")
        raise HTTPException(status_code=500, detail="Failed to parse AI model's JSON response.")


async def get_conversational_answer(url: str, query: str, history: list):
    """Orchestrates scraping and AI conversation for the /chat endpoint."""
    text_content = await scrape_website_text(url)
    if not text_content:
        raise HTTPException(status_code=404, detail="Could not extract content from the website.")

    formatted_history = "\n".join([f"{item.role.capitalize()}: {item.content}" for item in history])

    prompt = CONVERSATIONAL_PROMPT_TEMPLATE.format(
        text_content=text_content,
        formatted_history=formatted_history,
        query=query
    )

    llm_output = generate_llm_response(prompt)

    # --- Clean the LLM output by removing markdown fences ---
    llm_output = llm_output.strip().removeprefix("```json").removesuffix("```")
    llm_output = llm_output.strip() # Strip any remaining whitespace
    # ---------------------------------------------------------------------------------

    try:
        chat_data = json.loads(llm_output)
        return chat_data
    except json.JSONDecodeError:
        # It's helpful to print the problematic output for debugging if it still fails
        print(f"DEBUG: Failed to decode JSON. Raw output was: '{llm_output}'")
        raise HTTPException(status_code=500, detail="Failed to parse AI model's JSON response.")