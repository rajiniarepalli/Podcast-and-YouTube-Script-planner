from fastapi import APIRouter, HTTPException, status
from app.schemas import (
    ScriptGenerationRequest,
    ScriptGenerationResponse,
    ScriptRefinementRequest,
    ScriptRefinementResponse
)
from app.services.gemini_service import gemini_service
from app.services.prompt_templates import (
    build_youtube_prompt,
    build_podcast_prompt,
    build_refinement_prompt
)
from app.config import settings

router = APIRouter(prefix="/api", tags=["Scripts"])

@router.post("/generate-script", response_model=ScriptGenerationResponse)
async def generate_script(req: ScriptGenerationRequest):
    content_type_str = str(req.content_type).lower()
    
    if "youtube" in content_type_str:
        prompt = build_youtube_prompt(req)
        default_title = f"YouTube: {req.topic}"
    else:
        prompt = build_podcast_prompt(req)
        default_title = f"Podcast: {req.topic}"

    generated_text = await gemini_service.generate_text(prompt)

    return ScriptGenerationResponse(
        title=default_title,
        script=generated_text,
        content_type=req.content_type,
        estimated_duration=req.duration or "5-7 minutes",
        model_used=settings.GEMINI_MODEL
    )

@router.post("/refine-script", response_model=ScriptRefinementResponse)
async def refine_script(req: ScriptRefinementRequest):
    if req.action == "custom" and not req.custom_instruction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A custom instruction is required when 'custom' refinement action is chosen."
        )

    prompt = build_refinement_prompt(req)
    refined_text = await gemini_service.generate_text(prompt)

    return ScriptRefinementResponse(
        refined_script=refined_text,
        action_applied=req.action
    )
    