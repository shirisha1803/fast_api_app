FASTAPI AI for Website Intelligence

A robust and scalable FastAPI-based application designed as an AI-driven agent for extracting, interpreting, and summarizing critical business information from company websites. By integrating modern web scraping methodologies with powerful language models, this system intelligently analyzes homepage content and delivers organized, real-time insights, facilitating interactive, question-answering capabilities about businesses.

Architecture
![Architecture](https://github.com/user-attachments/assets/3b6ce968-d26c-41a1-bd24-72cd3160a6ff)



Technology Justification

| Technology            | Role in Project                     | Justification                                                                   |
| --------------------- | ----------------------------------- | ------------------------------------------------------------------------------- |
| **FastAPI**           | Web framework for building APIs     | Offers high performance, built-in validation, automatic docs, and async support |
| **httpx**             | HTTP client for making web requests | Provides async capabilities, robust for crawling and scraping web content       |
| **BeautifulSoup**     | HTML parsing and content extraction | Simple and efficient for navigating and scraping structured HTML                |
| **OpenAI API / LLMs** | NLP engine for response generation  | Delivers powerful language understanding and synthesis for web content          |
| **SlowAPI**           | Rate limiting middleware            | Prevents abuse by restricting API request rates per IP                          |
| **Render**            | Cloud deployment platform           | Easy CI/CD with GitHub integration, supports FastAPI natively                   |
| **dotenv**            | Environment variable management     | Keeps sensitive data like API keys secure and manageable                        |
| **Uvicorn**           | ASGI server for running FastAPI     | Fast, lightweight, and production-ready ASGI server                             |

API Usage Examples

Website Analysis

curl -X POST "http://localhost:8000/analyze" \
     -H "Authorization: Bearer YOUR_SECRET_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "url": "https://example.com",
           "questions": [
             "What is their primary business model?",
             "Who is their target market?"
           ]
         }'

Conversation with AI

curl -X POST "http://localhost:8000/chat" \
     -H "Authorization: Bearer YOUR_SECRET_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "url": "https://example.com",
           "query": "What are their key features?",
           "conversation_history": [
             {
               "user_query": "What industry are they in?",
               "agent_response": "They are in the SaaS industry."
             }
           ]
         }'


