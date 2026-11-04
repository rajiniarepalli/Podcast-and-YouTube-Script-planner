
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services.rag_service import (
    store_document,
    retrieve_relevant_documents
)
from app.services.gemini_service import gemini_service
import tempfile
from pathlib import Path

router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)


class QuestionRequest(BaseModel):
    question: str


# PDF Upload API
@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file"
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty"
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp:
            temp.write(content)
            temp_path = Path(temp.name)

        result = store_document(str(temp_path))

        return {
            "message": "PDF uploaded successfully",
            "result": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


# RAG Question Answering API
@router.post("/ask")
async def ask_question(request: QuestionRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        documents = retrieve_relevant_documents(
            request.question
        )

        if not documents:
            raise HTTPException(
                status_code=404,
                detail="No documents found. Please upload a PDF first."
            )

        context = "\n\n".join(documents)

        prompt = f"""
        Answer the user's question using the following
        information retrieved from uploaded PDF documents.

        If the answer is not available in the context,
        clearly mention that.

        Context:
        {context}

        Question:
        {request.question}

        Answer:
        """

        answer = await gemini_service.generate_text(prompt)

        return {
            "question": request.question,
            "answer": answer
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
