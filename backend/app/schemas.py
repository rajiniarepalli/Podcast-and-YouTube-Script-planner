from pydantic import BaseModel, Field
from typing import Optional

class ScriptGenerationRequest(BaseModel):
    content_type: str = "youtube"
    topic: str = Field(..., min_length=1, description="Main topic or idea")
    target_audience: Optional[str] = "General Audience"
    language: Optional[str] = "English"
    tone: Optional[str] = "Conversational"
    duration: Optional[str] = "5-7 minutes"
    keywords: Optional[str] = ""
    additional_instructions: Optional[str] = ""

class ScriptGenerationResponse(BaseModel):
    title: str
    script: str
    content_type: str
    estimated_duration: str
    model_used: str

class ScriptRefinementRequest(BaseModel):
    script: str
    action: str
    target_tone: Optional[str] = None
    custom_instruction: Optional[str] = None

class ScriptRefinementResponse(BaseModel):
    refined_script: str
    action_applied: str
    