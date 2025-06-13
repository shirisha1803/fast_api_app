from pydantic import BaseModel, HttpUrl, Field, RootModel
from typing import List, Optional, Literal

# Nested models for CompanyInfo
class SocialMedia(BaseModel):
    linkedin: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    social_media: SocialMedia = Field(default_factory=SocialMedia)

class CompanyInfo(BaseModel):
    industry: str
    company_size: Optional[str] = None
    location: Optional[str] = None
    core_products_services: List[str]
    unique_selling_proposition: str
    target_audience: str
    contact_info: ContactInfo = Field(default_factory=ContactInfo)

# Model for extracted answers within analysis
class ExtractedAnswer(BaseModel):
    question: str
    answer: str

# Response model for the /analyze endpoint
class AnalysisResponse(BaseModel):
    company_info: CompanyInfo
    extracted_answers: List[ExtractedAnswer]

# Request/Response models for the /chat endpoint
class Message(BaseModel):
    role: Literal["user", "agent"]
    content: str

# Changed to use RootModel for Pydantic V2 compatibility
class ConversationHistory(RootModel[List[Message]]):
    pass

class ChatRequest(BaseModel):
    url: HttpUrl
    query: str
    conversation_history: List[Message] = []

class ChatResponse(BaseModel):
    agent_response: str
    context_sources: List[str]

# Added for the /analyze endpoint's request body
class AnalysisRequest(BaseModel):
    url: HttpUrl
    questions: List[str] = Field(default_factory=list)