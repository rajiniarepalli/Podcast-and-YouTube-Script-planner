
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.gemini_service import gemini_service

router = APIRouter(
    prefix="/api",
    tags=["Scripts"]
)


class ScriptRequest(BaseModel):
    content_type: str
    topic: str
    target_audience: str = "General Audience"
    language: str = "English"
    tone: str = "Conversational"
    duration: str = "5-7 minutes"
    keywords: str = ""
    additional_instructions: str = ""


class RefineRequest(BaseModel):
    script: str
    action: str
    target_tone: str | None = None
    custom_instruction: str | None = None


@router.post("/generate-script")
async def generate_script(request: ScriptRequest):

    if not request.topic.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a topic."
        )

    prompt = f"""
    Create a complete and engaging {request.content_type} script.

    Topic: {request.topic}
    Target Audience: {request.target_audience}
    Language: {request.language}
    Tone: {request.tone}
    Duration: {request.duration}
    Keywords: {request.keywords}
    Additional Instructions: {request.additional_instructions}

    Include:
    1. An attractive title
    2. An engaging introduction and hook
    3. Main content with clear sections
    4. Practical examples where appropriate
    5. A conclusion
    6. A call to action

    Write the complete script in the requested language.
    """

    try:
        result = await gemini_service.generate_text(prompt)

        return {
            "success": True,
            "script": result,
            "title": request.topic
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/refine-script")
async def refine_script(request: RefineRequest):

    if not request.script.strip():
        raise HTTPException(
            status_code=400,
            detail="Script cannot be empty."
        )

    instructions = {
        "improve_hook": "Make the hook and introduction more engaging.",
        "make_shorter": "Make the script shorter and remove unnecessary content.",
        "make_longer": "Expand the script with deeper talking points.",
        "add_examples": "Add practical real-world examples.",
        "simplify": "Simplify difficult words and technical explanations for beginners.",
        "change_tone": f"Change the overall tone to {request.target_tone}."
    }

    if request.action == "custom":
        instruction = request.custom_instruction or ""
        if not instruction.strip():
            raise HTTPException(
                status_code=400,
                detail="Please enter a custom instruction."
            )
    else:
        instruction = instructions.get(request.action)

        if not instruction:
            raise HTTPException(
                status_code=400,
                detail="Invalid refinement action."
            )

    prompt = f"""
    Improve the following script based on the instruction.

    Existing Script:
    {request.script}

    Refinement Instruction:
    {instruction}

    Return the complete improved script only.
    """

    try:
        result = await gemini_service.generate_text(prompt)

        return {
            "success": True,
            "refined_script": result
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
