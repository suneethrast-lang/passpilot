import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.services.validators import validate_documents


app = FastAPI(
    title="PassPilot Validation API",
    description="Checks consistency in supplied passport-document fields.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Document(BaseModel):
    type: str
    fields: dict = Field(default_factory=dict)


class ValidationRequest(BaseModel):
    case_id: str = "DEMO-001"
    documents: list[Document]


@app.get("/health")
def health():
    return {"status": "ok", "service": "PassPilot Validation API"}

@app.get("/api/rules")
def get_rules():
    rules_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "passport_rules.json"
    )

    try:
        with rules_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Passport rules dataset not found."
        )

@app.post("/api/documents/validate")
def validate(request: ValidationRequest):
    try:
        payload = {
            "case_id": request.case_id,
            "documents": [
                document.model_dump()
                for document in request.documents
            ],
        }
        return validate_documents(payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
