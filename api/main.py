"""FastAPI application for the AI Writer Room web prototype."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import service
from api.schemas import (
    ApiResponse,
    GeneratePromptRequest,
    GenerateRulesRequest,
    ManualParseRequest,
    OpenAIGenerateRequest,
    ProductionRequest,
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


@app.post("/api/rules/generate", response_model=ApiResponse)
def rules_generate(req: GenerateRulesRequest) -> ApiResponse:
    """Generate editable rules for the creator workflow."""
    return service.generate_rules(req)


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


@app.post("/api/production/voice", response_model=ApiResponse)
def production_voice(req: ProductionRequest) -> ApiResponse:
    """Build a local voice script package."""
    return service.generate_voice_project(req)


@app.post("/api/production/images", response_model=ApiResponse)
def production_images(req: ProductionRequest) -> ApiResponse:
    """Build a local image prompt package."""
    return service.generate_image_prompt_project(req)


@app.post("/api/production/storyboard", response_model=ApiResponse)
def production_storyboard(req: ProductionRequest) -> ApiResponse:
    """Build a local shot storyboard package."""
    return service.generate_shot_storyboard(req)


@app.post("/api/production/video", response_model=ApiResponse)
def production_video(req: ProductionRequest) -> ApiResponse:
    """Build a local video manifest package."""
    return service.generate_video_manifest(req)
