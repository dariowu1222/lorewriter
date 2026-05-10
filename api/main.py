"""FastAPI application for the AI Writer Room web prototype."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import service
from api.schemas import (
    ApiResponse,
    GeneratePromptRequest,
    ManualParseRequest,
    OpenAIGenerateRequest,
)


app = FastAPI(title="AI Writer Room API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=ApiResponse)
def health() -> ApiResponse:
    """Return a basic health check response."""
    return ApiResponse(success=True, message="ok")


@app.get("/api/ui-contract", response_model=ApiResponse)
def ui_contract() -> ApiResponse:
    """Return the UI contract JSON."""
    return ApiResponse(
        success=True,
        message="UI contract loaded.",
        data=service.get_ui_contract(),
    )


@app.get("/api/generation-modes", response_model=ApiResponse)
def generation_modes() -> ApiResponse:
    """Return generation mode metadata."""
    return ApiResponse(
        success=True,
        message="Generation modes loaded.",
        data={"modes": service.list_generation_modes()},
    )


@app.post("/api/manual/generate-prompt", response_model=ApiResponse)
def manual_generate_prompt(req: GeneratePromptRequest) -> ApiResponse:
    """Generate a prompt for manual copy/paste workflows."""
    return service.generate_manual_prompt(req)


@app.post("/api/manual/parse-response", response_model=ApiResponse)
def manual_parse_response(req: ManualParseRequest) -> ApiResponse:
    """Parse a manually pasted response."""
    return service.parse_manual_response(req)


@app.post("/api/openai/generate", response_model=ApiResponse)
def openai_generate(req: OpenAIGenerateRequest) -> ApiResponse:
    """Generate a storyboard through OpenAI."""
    return service.generate_with_openai(req)
