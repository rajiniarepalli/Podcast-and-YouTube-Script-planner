
import asyncio
import os

from google import genai
from google.genai import errors
from fastapi import HTTPException, status

from app.config import settings


class GeminiService:

    def __init__(self):
        self.model_name = settings.GEMINI_MODEL

        # Configure backup model through environment variable
        self.fallback_model = os.getenv(
            "GEMINI_FALLBACK_MODEL", ""
        ).strip()

        if (
            not settings.GEMINI_API_KEY
            or settings.GEMINI_API_KEY == "your_actual_gemini_api_key_here"
        ):
            self.client = None
        else:
            self.client = genai.Client(
                api_key=settings.GEMINI_API_KEY
            )

        print("Gemini Service Initialized", flush=True)
        print("Primary Model:", self.model_name, flush=True)
        print(
            "Backup Model:",
            self.fallback_model or "Not configured",
            flush=True
        )

    def _ensure_client(self):
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API Key is not configured."
            )

    async def _generate_with_model(self, model, prompt):
        return await asyncio.to_thread(
            self.client.models.generate_content,
            model=model,
            contents=prompt
        )

    async def generate_text(self, prompt: str) -> str:

        self._ensure_client()

        models = [self.model_name]

        if (
            self.fallback_model
            and self.fallback_model != self.model_name
        ):
            models.append(self.fallback_model)

        errors_found = []

        for index, model in enumerate(models):

            print("Trying Gemini model:", model, flush=True)

            try:
                response = await self._generate_with_model(
                    model, prompt
                )

                if response and response.text:
                    print(
                        "Gemini generation successful using:",
                        model,
                        flush=True
                    )
                    return response.text

                raise HTTPException(
                    status_code=502,
                    detail=f"Gemini returned an empty response from {model}."
                )

            except errors.APIError as e:

                error_msg = str(e)
                print(
                    "GEMINI API ERROR:",
                    model,
                    error_msg,
                    flush=True
                )

                errors_found.append(
                    f"{model}: {error_msg}"
                )

                upper_error = error_msg.upper()

                retryable = (
                    "429" in upper_error
                    or "RESOURCE_EXHAUSTED" in upper_error
                    or "503" in upper_error
                    or "UNAVAILABLE" in upper_error
                )

                if retryable and index < len(models) - 1:
                    print(
                        "Primary model failed. Trying backup model.",
                        flush=True
                    )
                    continue

                if "429" in upper_error or "RESOURCE_EXHAUSTED" in upper_error:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Gemini quota/rate limit error: {error_msg}"
                    )

                if "503" in upper_error or "UNAVAILABLE" in upper_error:
                    raise HTTPException(
                        status_code=503,
                        detail=f"Gemini temporarily unavailable: {error_msg}"
                    )

                if (
                    "INVALID_ARGUMENT" in upper_error
                    or "API_KEY_INVALID" in upper_error
                ):
                    raise HTTPException(
                        status_code=401,
                        detail=f"Gemini configuration error: {error_msg}"
                    )

                raise HTTPException(
                    status_code=502,
                    detail=f"Gemini API error: {error_msg}"
                )

            except HTTPException:
                raise

            except Exception as e:
                print(
                    "UNEXPECTED GEMINI ERROR:",
                    str(e),
                    flush=True
                )
                raise HTTPException(
                    status_code=500,
                    detail=f"Unexpected error: {str(e)}"
                )

        raise HTTPException(
            status_code=503,
            detail="All configured Gemini models are unavailable. "
                   + " | ".join(errors_found)
        )


gemini_service = GeminiService()
