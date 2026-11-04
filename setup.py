import os

FILES = {
    "backend/requirements.txt": """fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.0
python-dotenv>=1.0.1
google-genai>=0.1.1
pytest>=8.0.0
httpx>=0.27.0
""",

    "backend/.env.example": """GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
FRONTEND_ORIGIN=http://localhost:5173
""",

    "backend/app/__init__.py": "",
    "backend/app/routes/__init__.py": "",
    "backend/app/services/__init__.py": "",
    "backend/tests/__init__.py": "",

    "backend/app/config.py": """import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

settings = Settings()
""",

    "backend/app/schemas.py": """from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class ContentType(str, Enum):
    YOUTUBE = "youtube"
    PODCAST = "podcast"

class ToneEnum(str, Enum):
    PROFESSIONAL = "Professional"
    FRIENDLY = "Friendly"
    EDUCATIONAL = "Educational"
    ENTERTAINING = "Entertaining"
    CONVERSATIONAL = "Conversational"

class ScriptGenerationRequest(BaseModel):
    content_type: ContentType
    topic: str = Field(..., min_length=3, max_length=300, description="Main topic or idea")
    target_audience: str = Field("General Audience", max_length=150)
    language: str = Field("English", max_length=50)
    tone: ToneEnum = ToneEnum.CONVERSATIONAL
    duration: str = Field("5-7 minutes", max_length=50)
    keywords: Optional[str] = Field("", max_length=300)
    additional_instructions: Optional[str] = Field("", max_length=500)

class ScriptGenerationResponse(BaseModel):
    title: str
    script: str
    content_type: str
    estimated_duration: str
    model_used: str

class RefinementAction(str, Enum):
    MAKE_SHORTER = "make_shorter"
    MAKE_LONGER = "make_longer"
    CHANGE_TONE = "change_tone"
    IMPROVE_HOOK = "improve_hook"
    ADD_EXAMPLES = "add_examples"
    SIMPLIFY = "simplify"
    CUSTOM = "custom"

class ScriptRefinementRequest(BaseModel):
    script: str = Field(..., min_length=20, description="Original script to refine")
    action: RefinementAction
    target_tone: Optional[ToneEnum] = None
    custom_instruction: Optional[str] = Field(None, max_length=300)

class ScriptRefinementResponse(BaseModel):
    refined_script: str
    action_applied: str
""",

    "backend/app/services/prompt_templates.py": '''from app.schemas import ScriptGenerationRequest, ScriptRefinementRequest, RefinementAction

def build_youtube_prompt(req: ScriptGenerationRequest) -> str:
    return f"""
You are an award-winning YouTube content strategist and scriptwriter.
Create a comprehensive, production-ready YouTube video script based on the following specifications:

- Topic: {req.topic}
- Target Audience: {req.target_audience}
- Language: {req.language}
- Tone: {req.tone.value}
- Desired Duration: {req.duration}
- Keywords to naturally include: {req.keywords or "None specified"}
- Special Instructions: {req.additional_instructions or "None"}

Please format your response clearly using Markdown with the following distinct sections:

# [Video Title Suggestions]
(Provide 3 punchy, high-CTR YouTube title options)

# [Thumbnail Concept]
(Provide 2 visual thumbnail ideas with brief text overlay suggestions)

# [Hook & Intro] (0:00 - 0:45)
- Attention-grabbing opening hook.
- Problem statement / payoff teaser.
- Quick introduction and video roadmap.

# [Main Body Segments]
(Break down the core content into 3-4 structured segments with speaking lines, on-screen text [OST] cues, and B-roll/visual directions in brackets. Ensure script length aligns closely with {req.duration}.)

# [Audience Engagement & Call to Action (CTA)]
- A natural question to spark comments in the comment section.
- Clear, non-spammy Like/Subscribe CTA.

# [Outro & Next Steps]
- Key takeaway summary and wrap-up.

# [Metadata: Description & Hashtags]
- SEO-friendly 2-paragraph video description.
- 5-8 relevant hashtags.

CRITICAL INSTRUCTIONS:
- Ground all facts. If an unverified claim, metric, or reference is introduced, explicitly flag it with [VERIFY: ...].
- Write naturally for the speaker in the specified tone ({req.tone.value}).
"""

def build_podcast_prompt(req: ScriptGenerationRequest) -> str:
    return f"""
You are a veteran podcast producer and scriptwriter.
Create a natural, conversational, and highly engaging podcast episode script based on these specifications:

- Episode Topic: {req.topic}
- Target Listeners: {req.target_audience}
- Language: {req.language}
- Tone: {req.tone.value}
- Target Duration: {req.duration}
- Key Topics/Keywords: {req.keywords or "None specified"}
- Special Instructions: {req.additional_instructions or "None"}

Please format your response clearly using Markdown with the following sections:

# [Episode Title Options]
(Provide 2-3 engaging episode titles)

# [Episode Summary]
(A concise, intriguing 2-sentence summary)

# [Intro & Host Welcome]
- Audio cue suggestions [e.g., Intro Music Fade Out].
- Warm welcome, episode theme announcement, and listener hook.

# [Segment 1: Setting the Stage]
- Natural host narration setting context and why this matters today.

# [Segment 2: Deep Dive Discussion]
- In-depth exploration with vocal pacing cues [e.g., Short pause, Emphasize this].
- 3 thought-provoking questions (useful for guest interviews or solo contemplation).
- Smooth verbal transition into the next segment.

# [Segment 3: Practical Takeaways & Real-World Application]
- Actionable steps, insights, or relatable story points.

# [Listener Engagement & Outro]
- Review/share call to action.
- Community question of the week.
- Warm closing remarks [Outro Music Fade In].

# [Show Notes & Description]
- Ready-to-publish show notes with key bullet points.
- Resource links / follow-up prompts.

CRITICAL INSTRUCTIONS:
- The script MUST sound natural when spoken aloud. Use conversational pacing, rhetorical pauses, and natural language.
- Flag any claims needing factual verification with [VERIFY: ...].
"""

def build_refinement_prompt(req: ScriptRefinementRequest) -> str:
    action_guidelines = {
        RefinementAction.MAKE_SHORTER: "Condense this script by approximately 30-40%, removing filler words while keeping the core value and flow intact.",
        RefinementAction.MAKE_LONGER: "Expand this script by adding richer explanations, practical analogies, and deeper talking points without adding fluff.",
        RefinementAction.CHANGE_TONE: f"Rewrite this script completely shifting the tone to {req.target_tone.value if req.target_tone else 'Conversational'}.",
        RefinementAction.IMPROVE_HOOK: "Revise the introduction and hook to be dramatically more compelling, high-stakes, and retention-focused.",
        RefinementAction.ADD_EXAMPLES: "Integrate 2-3 concrete, relatable examples and practical case scenarios into the main sections.",
        RefinementAction.SIMPLIFY: "Simplify complex technical jargon into clear, accessible language suitable for absolute beginners.",
        RefinementAction.CUSTOM: f"Apply this specific custom refinement: {req.custom_instruction}"
    }

    guideline = action_guidelines.get(req.action, "Improve clarity and flow.")

    return f"""
You are an expert script editor.
Your task is to refine the following script according to these instructions:

DIRECTIVE: {guideline}

ORIGINAL SCRIPT:
\"\"\"
{req.script}
\"\"\"

Output the complete, revised script in clean Markdown format maintaining clean headers and visual cues.
"""
''',

    "backend/app/services/gemini_service.py": """from google import genai
from google.genai import errors
from fastapi import HTTPException, status
from app.config import settings

class GeminiService:
    def __init__(self):
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_actual_gemini_api_key_here":
            self.client = None
        else:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL

    def _ensure_client(self):
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API Key is not configured on the backend. Please add GEMINI_API_KEY to your backend .env file."
            )

    async def generate_text(self, prompt: str) -> str:
        self._ensure_client()
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

            if not response or not response.text:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Gemini returned an empty response. Please try modifying your prompt."
                )

            return response.text

        except errors.APIError as e:
            error_msg = str(e)
            if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Gemini API quota exceeded or rate limit hit. Please wait a minute and retry."
                )
            elif "INVALID_ARGUMENT" in error_msg or "API_KEY_INVALID" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Gemini API key. Please check your credentials."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Google Gemini API error: {error_msg}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error communicating with AI service: {str(e)}"
            )

gemini_service = GeminiService()
""",

    "backend/app/routes/scripts.py": """from fastapi import APIRouter, HTTPException, status
from app.schemas import (
    ScriptGenerationRequest,
    ScriptGenerationResponse,
    ScriptRefinementRequest,
    ScriptRefinementResponse,
    ContentType
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
    if req.content_type == ContentType.YOUTUBE:
        prompt = build_youtube_prompt(req)
        default_title = f"YouTube: {req.topic}"
    else:
        prompt = build_podcast_prompt(req)
        default_title = f"Podcast: {req.topic}"

    generated_text = await gemini_service.generate_text(prompt)

    return ScriptGenerationResponse(
        title=default_title,
        script=generated_text,
        content_type=req.content_type.value,
        estimated_duration=req.duration,
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
        action_applied=req.action.value
    )
""",

    "backend/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes.scripts import router as scripts_router

app = FastAPI(
    title="AI-Powered Podcast & YouTube Script Planner API",
    description="Backend API powered by FastAPI and Google Gemini for generating and refining scripts.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_ORIGIN,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scripts_router)

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "AI Script Planner API",
        "model": settings.GEMINI_MODEL,
        "has_api_key": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_actual_gemini_api_key_here")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
""",

    "backend/tests/test_api.py": """from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model" in data

def test_generate_script_validation_failure():
    payload = {"content_type": "youtube", "topic": "ab"}
    response = client.post("/api/generate-script", json=payload)
    assert response.status_code == 422

@patch("app.routes.scripts.gemini_service.generate_text", new_callable=AsyncMock)
def test_generate_youtube_script_success(mock_generate):
    mock_generate.return_value = "# [Video Title Suggestions]\\n1. Top 5 AI Tools"
    payload = {
        "content_type": "youtube",
        "topic": "Top 5 AI productivity tools for developers",
        "duration": "8-10 minutes"
    }
    response = client.post("/api/generate-script", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Top 5 AI Tools" in data["script"]
""",

    "frontend/package.json": """{
  "name": "podcast-youtube-script-planner-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.6.8",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.2.0"
  }
}
""",

    "frontend/vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  }
})
""",

    "frontend/.env.example": """VITE_API_BASE_URL=http://localhost:8000
""",

    "frontend/index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ScriptCraft AI | Podcast & YouTube Script Planner</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""",

    "frontend/src/index.css": """:root {
  --bg-primary: #0a0e17;
  --bg-surface: #111827;
  --bg-card: #1f2937;
  --bg-card-hover: #283548;
  --border-color: #374151;
  --accent-primary: #6366f1;
  --accent-primary-hover: #4f46e5;
  --accent-secondary: #ec4899;
  --text-main: #f9fafb;
  --text-muted: #9ca3af;
  --text-dim: #6b7280;
  --success: #10b981;
  --error: #ef4444;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --font-sans: 'Plus Jakarta Sans', system-ui, sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body { background-color: var(--bg-primary); color: var(--text-main); font-family: var(--font-sans); line-height: 1.6; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }

.navbar { background-color: rgba(17, 24, 39, 0.85); backdrop-filter: blur(12px); border-bottom: 1px solid var(--border-color); position: sticky; top: 0; z-index: 100; padding: 1rem 0; }
.nav-container { display: flex; justify-content: space-between; align-items: center; }
.nav-brand { display: flex; align-items: center; gap: 0.75rem; font-weight: 800; font-size: 1.25rem; cursor: pointer; }
.brand-icon { background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)); width: 36px; height: 36px; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; }
.nav-links { display: flex; gap: 1rem; }
.nav-btn { background: transparent; border: 1px solid transparent; color: var(--text-muted); font-size: 0.95rem; font-weight: 600; padding: 0.5rem 1rem; border-radius: var(--radius-sm); cursor: pointer; }
.nav-btn.active { background-color: var(--bg-card); color: var(--text-main); border-color: var(--border-color); }

.hero { padding: 5rem 0 3.5rem; text-align: center; }
.hero-badge { display: inline-block; background-color: rgba(99, 102, 241, 0.15); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.3); padding: 0.35rem 0.85rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; margin-bottom: 1.25rem; }
.hero-title { font-size: 3rem; font-weight: 800; line-height: 1.15; margin-bottom: 1.25rem; background: linear-gradient(135deg, #ffffff 40%, #9ca3af 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-subtitle { font-size: 1.15rem; color: var(--text-muted); max-width: 650px; margin: 0 auto 2rem; }

.btn-primary { background-color: var(--accent-primary); color: #fff; border: none; font-weight: 700; font-size: 1rem; padding: 0.75rem 1.75rem; border-radius: var(--radius-md); cursor: pointer; }
.btn-primary:hover:not(:disabled) { background-color: var(--accent-primary-hover); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background-color: var(--bg-card); color: var(--text-main); border: 1px solid var(--border-color); font-weight: 600; padding: 0.5rem 1rem; border-radius: var(--radius-sm); cursor: pointer; }
.btn-secondary:hover:not(:disabled) { background-color: var(--bg-card-hover); }

.features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin: 3.5rem 0; }
.feature-card { background-color: var(--bg-surface); border: 1px solid var(--border-color); padding: 1.75rem; border-radius: var(--radius-lg); }
.feature-icon { font-size: 2rem; margin-bottom: 1rem; }
.feature-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 0.5rem; }
.feature-text { color: var(--text-muted); font-size: 0.95rem; }

.planner-grid { display: grid; grid-template-columns: 450px 1fr; gap: 2rem; margin: 2rem 0 4rem; }
@media (max-width: 950px) { .planner-grid { grid-template-columns: 1fr; } }
.card { background-color: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 1.75rem; }
.form-group { margin-bottom: 1.25rem; }
.form-label { display: block; font-weight: 600; font-size: 0.875rem; margin-bottom: 0.4rem; }
.form-input, .form-select, .form-textarea { width: 100%; background-color: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-main); padding: 0.7rem 0.9rem; border-radius: var(--radius-sm); font-size: 0.95rem; font-family: inherit; }
.form-textarea { resize: vertical; min-height: 85px; }

.pill-selector { display: flex; gap: 0.5rem; }
.pill-option { flex: 1; text-align: center; padding: 0.65rem 0.5rem; background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-sm); font-weight: 600; cursor: pointer; }
.pill-option.active { background-color: var(--accent-primary); border-color: var(--accent-primary); color: white; }

.alert { padding: 0.75rem 1rem; border-radius: var(--radius-sm); margin-bottom: 1.25rem; font-size: 0.9rem; }
.alert-error { background-color: rgba(239, 68, 68, 0.15); border: 1px solid var(--error); color: #fca5a5; }

.viewer-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1rem; }
.action-bar { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.script-content { background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1.5rem; white-space: pre-wrap; line-height: 1.7; max-height: 650px; overflow-y: auto; font-size: 0.95rem; }
.empty-state { text-align: center; padding: 4rem 2rem; color: var(--text-dim); }
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }

.metrics-bar { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1rem; }
.metric-pill { background-color: var(--bg-card); border: 1px solid var(--border-color); padding: 0.35rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.8rem; color: var(--text-muted); }
.metric-pill strong { color: var(--text-main); margin-left: 0.25rem; }

.modal-overlay { position: fixed; inset: 0; background-color: rgba(0, 0, 0, 0.75); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 200; padding: 1rem; }
.modal-content { background-color: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-lg); width: 100%; max-width: 520px; padding: 2rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.5rem; }

.teleprompter-overlay { position: fixed; inset: 0; background-color: #050508; z-index: 1000; display: flex; flex-direction: column; }
.teleprompter-controls { display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background-color: rgba(17, 24, 39, 0.95); border-bottom: 1px solid var(--border-color); gap: 1rem; }
.teleprompter-buttons { display: flex; align-items: center; gap: 1rem; }
.control-label { display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: var(--text-muted); }
.control-label input[type='range'] { width: 100px; }
.btn-active { background-color: var(--accent-primary) !important; color: #fff !important; }
.teleprompter-screen { flex: 1; overflow-y: scroll; padding: 4rem 15% 20rem; scroll-behavior: smooth; }
.teleprompter-screen.mirrored { transform: scaleX(-1); }
.teleprompter-text { color: #ffffff; line-height: 1.8; white-space: pre-wrap; font-weight: 600; }

.history-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.25rem; margin-top: 1.5rem; }
.history-card { background-color: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between; }
.history-meta { display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-dim); margin-bottom: 0.5rem; }
.badge { background-color: rgba(255, 255, 255, 0.1); padding: 0.2rem 0.5rem; border-radius: 4px; text-transform: uppercase; font-weight: 700; font-size: 0.7rem; }
.badge-youtube { background-color: rgba(239, 68, 68, 0.2); color: #fca5a5; }
.badge-podcast { background-color: rgba(99, 102, 241, 0.2); color: #c7d2fe; }
""",

    "frontend/src/services/api.js": """import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
});

export const scriptApi = {
  checkHealth: async () => {
    const response = await apiClient.get('/api/health');
    return response.data;
  },
  generateScript: async (payload) => {
    const response = await apiClient.post('/api/generate-script', payload);
    return response.data;
  },
  refineScript: async (payload) => {
    const response = await apiClient.post('/api/refine-script', payload);
    return response.data;
  },
};
""",

    "frontend/src/services/storage.js": """const STORAGE_KEY = 'scriptcraft_saved_scripts';

export const storageService = {
  getSavedScripts: () => {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (err) {
      return [];
    }
  },
  saveScript: (scriptItem) => {
    try {
      const existing = storageService.getSavedScripts();
      const newEntry = {
        id: Date.now().toString(),
        savedAt: new Date().toISOString(),
        ...scriptItem,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify([newEntry, ...existing]));
      return newEntry;
    } catch (err) {
      return null;
    }
  },
  deleteScript: (id) => {
    try {
      const existing = storageService.getSavedScripts();
      const filtered = existing.filter((item) => item.id !== id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
      return filtered;
    } catch (err) {
      return [];
    }
  },
};
""",

    "frontend/src/components/Navbar.jsx": """import React from 'react';

export default function Navbar({ activeTab, setActiveTab }) {
  return (
    <nav className="navbar">
      <div className="container nav-container">
        <div className="nav-brand" onClick={() => setActiveTab('home')}>
          <div className="brand-icon">⚡</div>
          <span>ScriptCraft AI</span>
        </div>
        <div className="nav-links">
          <button
            className={`nav-btn ${activeTab === 'home' ? 'active' : ''}`}
            onClick={() => setActiveTab('home')}
          >
            Overview
          </button>
          <button
            className={`nav-btn ${activeTab === 'planner' ? 'active' : ''}`}
            onClick={() => setActiveTab('planner')}
          >
            Script Studio
          </button>
          <button
            className={`nav-btn ${activeTab === 'saved' ? 'active' : ''}`}
            onClick={() => setActiveTab('saved')}
          >
            Saved Scripts
          </button>
        </div>
      </div>
    </nav>
  );
}
""",

    "frontend/src/components/ScriptForm.jsx": """import React, { useState } from 'react';

export default function ScriptForm({ onGenerate, isLoading }) {
  const [formData, setFormData] = useState({
    content_type: 'youtube',
    topic: '',
    target_audience: 'General Audience',
    language: 'English',
    tone: 'Conversational',
    duration: '5-7 minutes',
    keywords: '',
    additional_instructions: '',
  });

  const [validationError, setValidationError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleContentTypeChange = (type) => {
    setFormData((prev) => ({
      ...prev,
      content_type: type,
      duration: type === 'youtube' ? '5-7 minutes' : '15-20 minutes',
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setValidationError('');

    if (!formData.topic.trim()) {
      setValidationError('Please enter a content topic or idea.');
      return;
    }
    if (formData.topic.trim().length < 5) {
      setValidationError('Topic must be at least 5 characters long.');
      return;
    }

    onGenerate(formData);
  };

  return (
    <div className="card">
      <h2 style={{ marginBottom: '1.25rem', fontSize: '1.25rem', fontWeight: 700 }}>
        1. Content Specifications
      </h2>

      {validationError && <div className="alert alert-error">{validationError}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Format</label>
          <div className="pill-selector">
            <div
              className={`pill-option ${formData.content_type === 'youtube' ? 'active' : ''}`}
              onClick={() => handleContentTypeChange('youtube')}
            >
              📹 YouTube Video
            </div>
            <div
              className={`pill-option ${formData.content_type === 'podcast' ? 'active' : ''}`}
              onClick={() => handleContentTypeChange('podcast')}
            >
              🎙️ Podcast Episode
            </div>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Topic or Core Idea *</label>
          <input
            type="text"
            name="topic"
            className="form-input"
            placeholder="e.g., How to start freelance programming with zero experience"
            value={formData.topic}
            onChange={handleChange}
            maxLength={300}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Target Audience</label>
          <input
            type="text"
            name="target_audience"
            className="form-input"
            placeholder="e.g., Computer science students, beginners"
            value={formData.target_audience}
            onChange={handleChange}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
          <div className="form-group">
            <label className="form-label">Language</label>
            <input
              type="text"
              name="language"
              className="form-input"
              value={formData.language}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Tone</label>
            <select
              name="tone"
              className="form-select"
              value={formData.tone}
              onChange={handleChange}
            >
              <option value="Conversational">Conversational</option>
              <option value="Educational">Educational</option>
              <option value="Entertaining">Entertaining</option>
              <option value="Professional">Professional</option>
              <option value="Friendly">Friendly</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Target Duration</label>
          <input
            type="text"
            name="duration"
            className="form-input"
            placeholder="e.g., 8-10 minutes"
            value={formData.duration}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Keywords (Optional)</label>
          <input
            type="text"
            name="keywords"
            className="form-input"
            placeholder="e.g., portfolio, outreach, GitHub"
            value={formData.keywords}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Additional Instructions</label>
          <textarea
            name="additional_instructions"
            className="form-textarea"
            placeholder="e.g., Emphasize practical examples."
            value={formData.additional_instructions}
            onChange={handleChange}
          />
        </div>

        <button
          type="submit"
          className="btn-primary"
          style={{ width: '100%', marginTop: '0.5rem' }}
          disabled={isLoading}
        >
          {isLoading ? 'Crafting Your Script...' : '✨ Generate Full Script'}
        </button>
      </form>
    </div>
  );
}
""",

    "frontend/src/components/TeleprompterModal.jsx": """import React, { useState, useEffect, useRef } from 'react';

export default function TeleprompterModal({ isOpen, onClose, scriptText, title }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [scrollSpeed, setScrollSpeed] = useState(2);
  const [fontSize, setFontSize] = useState(28);
  const [isMirrored, setIsMirrored] = useState(false);
  const scrollContainerRef = useRef(null);

  useEffect(() => {
    let animationFrameId;
    const performScroll = () => {
      if (scrollContainerRef.current && isPlaying) {
        scrollContainerRef.current.scrollTop += scrollSpeed * 0.5;
        if (
          scrollContainerRef.current.scrollTop + scrollContainerRef.current.clientHeight >=
          scrollContainerRef.current.scrollHeight
        ) {
          setIsPlaying(false);
          return;
        }
      }
      if (isPlaying) {
        animationFrameId = requestAnimationFrame(performScroll);
      }
    };
    if (isPlaying) {
      animationFrameId = requestAnimationFrame(performScroll);
    }
    return () => cancelAnimationFrame(animationFrameId);
  }, [isPlaying, scrollSpeed]);

  if (!isOpen) return null;

  return (
    <div className="teleprompter-overlay">
      <div className="teleprompter-controls">
        <div className="teleprompter-info">
          <strong>Prompter:</strong> {title}
        </div>

        <div className="teleprompter-buttons">
          <button
            className={`btn-secondary ${isPlaying ? 'btn-active' : ''}`}
            onClick={() => setIsPlaying(!isPlaying)}
          >
            {isPlaying ? '⏸ Pause' : '▶ Start Scroll'}
          </button>

          <label className="control-label">
            Speed: {scrollSpeed}x
            <input
              type="range"
              min="1"
              max="8"
              value={scrollSpeed}
              onChange={(e) => setScrollSpeed(Number(e.target.value))}
            />
          </label>

          <label className="control-label">
            Font: {fontSize}px
            <input
              type="range"
              min="20"
              max="48"
              value={fontSize}
              onChange={(e) => setFontSize(Number(e.target.value))}
            />
          </label>

          <button
            className={`btn-secondary ${isMirrored ? 'btn-active' : ''}`}
            onClick={() => setIsMirrored(!isMirrored)}
          >
            🪞 Mirror
          </button>

          <button className="btn-secondary" onClick={onClose}>
            ✕ Exit
          </button>
        </div>
      </div>

      <div
        ref={scrollContainerRef}
        className={`teleprompter-screen ${isMirrored ? 'mirrored' : ''}`}
      >
        <div className="teleprompter-text" style={{ fontSize: `${fontSize}px` }}>
          {scriptText}
        </div>
      </div>
    </div>
  );
}
""",

    "frontend/src/components/ScriptViewer.jsx": """import React, { useState } from 'react';
import TeleprompterModal from './TeleprompterModal';

export default function ScriptViewer({ currentScript, onOpenRefine, onSaveScript }) {
  const [copied, setCopied] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [isPrompterOpen, setIsPrompterOpen] = useState(false);

  if (!currentScript) {
    return (
      <div className="card empty-state">
        <div className="empty-icon">📝</div>
        <h3>No Script Generated Yet</h3>
        <p style={{ marginTop: '0.5rem' }}>
          Fill in the content brief on the left and click Generate to produce a structured,
          teleprompter-ready script.
        </p>
      </div>
    );
  }

  const wordCount = currentScript.script
    .trim()
    .split(/\\s+/)
    .filter((w) => w.length > 0).length;
  const charCount = currentScript.script.length;
  const estimatedMins = Math.max(1, Math.round(wordCount / 140));

  const handleCopy = () => {
    navigator.clipboard.writeText(currentScript.script);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const filename = `${currentScript.title.replace(/[^a-zA-Z0-9_-]/g, '_')}.txt`;
    const blob = new Blob([currentScript.script], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleSave = () => {
    onSaveScript(currentScript);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2500);
  };

  return (
    <>
      <div className="card">
        <div className="viewer-header">
          <div>
            <span
              className={`badge ${
                currentScript.content_type === 'youtube' ? 'badge-youtube' : 'badge-podcast'
              }`}
            >
              {currentScript.content_type}
            </span>
            <h2 style={{ fontSize: '1.25rem', marginTop: '0.35rem', fontWeight: 700 }}>
              {currentScript.title}
            </h2>
          </div>

          <div className="action-bar">
            <button
              className="btn-secondary"
              onClick={() => setIsPrompterOpen(true)}
              title="Open full-screen teleprompter"
            >
              📺 Teleprompter
            </button>
            <button className="btn-secondary" onClick={handleCopy}>
              {copied ? '✓ Copied!' : '📋 Copy'}
            </button>
            <button className="btn-secondary" onClick={handleDownload}>
              💾 .txt
            </button>
            <button className="btn-secondary" onClick={handleSave}>
              {savedSuccess ? '✓ Saved!' : '⭐ Save'}
            </button>
            <button className="btn-primary" onClick={onOpenRefine} style={{ padding: '0.5rem 1rem' }}>
              🪄 AI Refine
            </button>
          </div>
        </div>

        <div className="metrics-bar">
          <div className="metric-pill">
            <span>Words:</span> <strong>{wordCount}</strong>
          </div>
          <div className="metric-pill">
            <span>Est. Time:</span> <strong>~{estimatedMins} min</strong>
          </div>
          <div className="metric-pill">
            <span>Chars:</span> <strong>{charCount}</strong>
          </div>
          <div className="metric-pill">
            <span>Engine:</span> <strong>{currentScript.model_used || 'Gemini'}</strong>
          </div>
        </div>

        <div className="script-content">{currentScript.script}</div>
      </div>

      <TeleprompterModal
        isOpen={isPrompterOpen}
        onClose={() => setIsPrompterOpen(false)}
        scriptText={currentScript.script}
        title={currentScript.title}
      />
    </>
  );
}
""",

    "frontend/src/components/RefineModal.jsx": """import React, { useState } from 'react';

export default function RefineModal({ isOpen, onClose, onApplyRefine, isRefining }) {
  const [action, setAction] = useState('improve_hook');
  const [targetTone, setTargetTone] = useState('Conversational');
  const [customInstruction, setCustomInstruction] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onApplyRefine({
      action,
      target_tone: action === 'change_tone' ? targetTone : null,
      custom_instruction: action === 'custom' ? customInstruction : null,
    });
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 style={{ marginBottom: '1rem', fontSize: '1.3rem' }}>🪄 Refine Script with Gemini</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
          Select how you want the AI to polish or reshape your existing script.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Select Refinement Goal</label>
            <select
              className="form-select"
              value={action}
              onChange={(e) => setAction(e.target.value)}
            >
              <option value="improve_hook">🎣 Make Hook & Intro punchier</option>
              <option value="make_shorter">✂️ Make it shorter (Remove filler)</option>
              <option value="make_longer">📖 Expand with deeper talking points</option>
              <option value="add_examples">💡 Add concrete real-world examples</option>
              <option value="simplify">🧩 Simplify jargon for beginners</option>
              <option value="change_tone">🎭 Shift overall tone</option>
              <option value="custom">✏️ Custom prompt instruction</option>
            </select>
          </div>

          {action === 'change_tone' && (
            <div className="form-group">
              <label className="form-label">New Tone</label>
              <select
                className="form-select"
                value={targetTone}
                onChange={(e) => setTargetTone(e.target.value)}
              >
                <option value="Conversational">Conversational</option>
                <option value="Educational">Educational</option>
                <option value="Entertaining">Entertaining</option>
                <option value="Professional">Professional</option>
                <option value="Friendly">Friendly</option>
              </select>
            </div>
          )}

          {action === 'custom' && (
            <div className="form-group">
              <label className="form-label">Custom Instruction</label>
              <textarea
                className="form-textarea"
                placeholder="e.g., Focus more on budget-friendly gear."
                value={customInstruction}
                onChange={(e) => setCustomInstruction(e.target.value)}
                required
              />
            </div>
          )}

          <div className="modal-footer">
            <button
              type="button"
              className="btn-secondary"
              onClick={onClose}
              disabled={isRefining}
            >
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={isRefining}>
              {isRefining ? 'Polishing Script...' : 'Apply Refinement'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
""",

    "frontend/src/components/SavedScripts.jsx": """import React from 'react';

export default function SavedScripts({ savedList, onSelectScript, onDeleteScript }) {
  if (savedList.length === 0) {
    return (
      <div className="card empty-state" style={{ marginTop: '2rem' }}>
        <div className="empty-icon">📂</div>
        <h3>No Saved Scripts Yet</h3>
        <p style={{ marginTop: '0.5rem' }}>
          Generate a script in the studio and click <strong>Save</strong> to store it in your browser.
        </p>
      </div>
    );
  }

  return (
    <div style={{ marginTop: '2rem' }}>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Saved Scripts ({savedList.length})</h2>
      <div className="history-grid">
        {savedList.map((item) => (
          <div key={item.id} className="history-card">
            <div>
              <div className="history-meta">
                <span
                  className={`badge ${
                    item.content_type === 'youtube' ? 'badge-youtube' : 'badge-podcast'
                  }`}
                >
                  {item.content_type}
                </span>
                <span>{new Date(item.savedAt).toLocaleDateString()}</span>
              </div>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>{item.title}</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                Duration: {item.estimated_duration}
              </p>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1.25rem' }}>
              <button
                className="btn-primary"
                style={{ flex: 1, padding: '0.45rem' }}
                onClick={() => onSelectScript(item)}
              >
                Open in Studio
              </button>
              <button
                className="btn-secondary"
                style={{ color: '#ef4444', borderColor: 'rgba(239, 68, 68, 0.3)' }}
                onClick={() => onDeleteScript(item.id)}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
""",

    "frontend/src/pages/HomePage.jsx": """import React from 'react';

export default function HomePage({ onStartClick }) {
  return (
    <div className="container">
      <section className="hero">
        <span className="hero-badge">AI-Powered Content Creation</span>
        <h1 className="hero-title">
          Plan, Script, and Produce <br />
          Hit Videos & Podcasts.
        </h1>
        <p className="hero-subtitle">
          Turn rough ideas into engaging, high-retention video outlines, host narrations,
          catchy hooks, and SEO descriptions in seconds with Google Gemini.
        </p>
        <button className="btn-primary" onClick={onStartClick} style={{ fontSize: '1.1rem', padding: '0.85rem 2.2rem' }}>
          🚀 Create a Script Now
        </button>
      </section>

      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">📹</div>
          <h3 className="feature-title">YouTube Script Architect</h3>
          <p className="feature-text">
            Generate 3 CTR-boosting titles, 45-second hooks, body breakdown with visual cues,
            descriptions, and hashtags.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🎙️</div>
          <h3 className="feature-title">Podcast Episode Engine</h3>
          <p className="feature-text">
            Create natural-sounding host scripts with pacing notes, guest interview questions,
            and show notes.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🪄</div>
          <h3 className="feature-title">One-Click AI Refinement</h3>
          <p className="feature-text">
            Easily tighten scripts, add real-world analogies, rewrite for different tones, or
            adjust lengths without restarting.
          </p>
        </div>
      </div>
    </div>
  );
}
""",

    "frontend/src/pages/PlannerPage.jsx": """import React, { useState } from 'react';
import ScriptForm from '../components/ScriptForm';
import ScriptViewer from '../components/ScriptViewer';
import RefineModal from '../components/RefineModal';
import { scriptApi } from '../services/api';

export default function PlannerPage({ currentScript, setCurrentScript, onSaveScript }) {
  const [isLoading, setIsLoading] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleGenerateScript = async (formData) => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      const result = await scriptApi.generateScript(formData);
      setCurrentScript(result);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to communicate with AI server. Is the backend running?';
      setErrorMessage(detail);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplyRefine = async (refinePayload) => {
    if (!currentScript) return;
    setIsRefining(true);
    setErrorMessage('');
    try {
      const result = await scriptApi.refineScript({
        script: currentScript.script,
        ...refinePayload,
      });

      setCurrentScript((prev) => ({
        ...prev,
        script: result.refined_script,
      }));
      setIsModalOpen(false);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to refine script.';
      setErrorMessage(detail);
    } finally {
      setIsRefining(false);
    }
  };

  return (
    <div className="container">
      {errorMessage && (
        <div className="alert alert-error" style={{ marginTop: '1.5rem' }}>
          <strong>Error:</strong> {errorMessage}
        </div>
      )}

      <div className="planner-grid">
        <ScriptForm onGenerate={handleGenerateScript} isLoading={isLoading} />
        <ScriptViewer
          currentScript={currentScript}
          onOpenRefine={() => setIsModalOpen(true)}
          onSaveScript={onSaveScript}
        />
      </div>

      <RefineModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onApplyRefine={handleApplyRefine}
        isRefining={isRefining}
      />
    </div>
  );
}
""",

    "frontend/src/App.jsx": """import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import PlannerPage from './pages/PlannerPage';
import SavedScripts from './components/SavedScripts';
import { storageService } from './services/storage';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [currentScript, setCurrentScript] = useState(null);
  const [savedList, setSavedList] = useState([]);

  useEffect(() => {
    setSavedList(storageService.getSavedScripts());
  }, []);

  const handleSaveCurrentScript = (scriptToSave) => {
    const saved = storageService.saveScript(scriptToSave);
    if (saved) {
      setSavedList(storageService.getSavedScripts());
    }
  };

  const handleDeleteSavedScript = (id) => {
    const updated = storageService.deleteScript(id);
    setSavedList(updated);
  };

  const handleSelectFromSaved = (item) => {
    setCurrentScript(item);
    setActiveTab('planner');
  };

  return (
    <div>
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main>
        {activeTab === 'home' && <HomePage onStartClick={() => setActiveTab('planner')} />}
        {activeTab === 'planner' && (
          <PlannerPage
            currentScript={currentScript}
            setCurrentScript={setCurrentScript}
            onSaveScript={handleSaveCurrentScript}
          />
        )}
        {activeTab === 'saved' && (
          <div className="container">
            <SavedScripts
              savedList={savedList}
              onSelectScript={handleSelectFromSaved}
              onDeleteScript={handleDeleteSavedScript}
            />
          </div>
        )}
      </main>
    </div>
  );
}
""",

    "frontend/src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
}

for path, content in FILES.items():
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ All folders and files generated successfully inside VS Code!")