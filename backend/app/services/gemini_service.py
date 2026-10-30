from google import genai
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
        
        # If the primary model experiences a 503 demand spike, automatically try these fallbacks
        models_to_try = [
            self.model_name,
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite"
        ]

        last_error_msg = ""

        for model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response and response.text:
                    return response.text

            except errors.APIError as e:
                error_msg = str(e)
                last_error_msg = error_msg
                # If Google has high demand (503) or rate limit (429), try the next model
                if "503" in error_msg or "UNAVAILABLE" in error_msg or "429" in error_msg:
                    continue
                elif "INVALID_ARGUMENT" in error_msg or "API_KEY_INVALID" in error_msg:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid Gemini API key. Please check your credentials."
                    )
                else:
                    break
            except Exception as e:
                last_error_msg = str(e)
                break

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Google Gemini servers are busy right now. Last message: {last_error_msg}"
        )

gemini_service = GeminiService()
