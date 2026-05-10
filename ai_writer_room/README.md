# AI Writer Room v0.1

AI Writer Room is a Python 3.11+ foundation for an extensible AI narrative
system. v0.1 focuses on 3-minute rule-horror storyboard JSON generation, local
evaluation, deterministic local auto-fix, cost guard metadata, long-form memory
scaffolding, Arc planning, and render-input export.

v0.1 does not generate video, run TTS, generate images, perform RAG, use a
vector database, or run multi-pass long-form generation.

## Setup

```bash
pip install -r requirements.txt
```

## API Key

OpenAI API key lookup order:

1. Environment variable: `OPENAI_API_KEY`
2. Optional key file path from environment variable: `OPENAI_API_KEY_FILE`
3. Default local key file:

```text
~/.config/ai_writer_room/openai_api_key
```

Safety notes:

- Do not commit API keys.
- Do not commit `.env`.
- Do not commit `.openai_api_key`, `*.openai_api_key`, or `*api_key*` files.
- `output/` and `logs/` are generated artifacts and should not be committed.
- The CLI does not print API keys.

## Providers

- `mock`: local deterministic mock storyboard generation.
- `manual`: writes a prompt file or parses a manually pasted model response.
- `openai`: calls OpenAI through the official SDK.
- `local`: calls an OpenAI-compatible local server such as Ollama.

`--use-api` remains as a legacy alias for `--provider openai`.

## Generation Modes

List UI-ready generation modes:

```bash
python generate_storyboard.py --list-generation-modes
```

## 省錢模式（Manual）

Flow:

```text
prompt.txt
↓
貼到 ChatGPT / Claude / Gemini
↓
匯回 JSON
↓
parse/eval/render export
```

Best for:

- 個人創作
- 開發測試
- 節省 API 成本

## API 自動模式（OpenAI）

Flow:

```text
prompt
↓
OpenAI API
↓
JSON parse
↓
eval
↓
render export
```

Best for:

- 商業化
- 大量生成
- 自動化 pipeline

## Usage

Mock generation with evaluation:

```bash
python generate_storyboard.py --provider mock --sub-genre 地鐵末班車 --duration 180 --output output/storyboard_mock.json --eval
```

Print the assembled prompt without calling any model:

```bash
python generate_storyboard.py --sub-genre 地鐵末班車 --duration 180 --print-prompt
```

OpenAI provider:

```bash
python generate_storyboard.py --provider openai --sub-genre 地鐵末班車 --duration 180 --model gpt-4o-mini --output output/storyboard_openai.json --eval
```

Local provider:

```bash
python generate_storyboard.py --provider local --sub-genre 地鐵末班車 --duration 180 --model qwen2.5:7b --output output/storyboard_local.json --eval
```

## Manual Provider

Step 1: write a prompt file.

```bash
python generate_storyboard.py --provider manual --sub-genre 地鐵末班車 --duration 180 --output output/manual_prompt.txt
```

Step 2: paste `output/manual_prompt.txt` into ChatGPT, Claude, or Gemini.

Step 3: save the model JSON response as:

```text
output/manual_response.json
```

Step 4: parse and validate it.

```bash
python generate_storyboard.py --provider manual --manual-response output/manual_response.json --output output/storyboard_manual.json --eval
```

## Local Auto-Fix

v0.1 auto-fix is deterministic and local. It does not call an LLM and does not
spend API budget.

It can currently fix:

- configured forbidden words
- known missing v0.1 rule refs
- basic metadata defaults

It cannot fix story logic, twist quality, pacing quality, or long-form payoff.

```bash
python generate_storyboard.py --provider mock --sub-genre 地鐵末班車 --duration 180 --output output/storyboard_mock.json --eval --auto-fix
```

Custom forbidden words:

```bash
python generate_storyboard.py --provider manual --manual-response output/manual_response.json --output output/storyboard_manual.json --eval --auto-fix --forbidden-words-file config/forbidden_words.custom.json
```

## Cost Guard

Cost Guard is estimate-based and applies only to `provider=openai`.
`mock`, `manual`, and `local` are not blocked by cost guard.

It checks:

- single-run estimated cost
- current-month estimated OpenAI usage from local generation logs
- warning threshold

Override for developer use:

```bash
python generate_storyboard.py --provider openai --ignore-budget-guard --sub-genre 地鐵末班車 --duration 180 --output output/storyboard_openai.json
```

## Story Memory

v0.1 initializes long-form state but does not perform long-form generation.

Story Bible tracks:

- characters
- world rules
- major questions
- hidden truths
- current Arc metadata

Memory Summary tracks:

- current arc state
- protagonist goal/status
- known rules
- unresolved questions
- active foreshadow ids

Foreshadow Tracker tracks:

- setup scene
- expected payoff scene
- planned payoff Arc
- payoff status

## Arc Planner

v0.1 uses a fixed 6 Arc template:

- Arc 1: 世界建立
- Arc 2: 異常擴大
- Arc 3: 中段反轉
- Arc 4: 世界真相擴張
- Arc 5: 主反轉
- Arc 6: 尾刀

Arc Planner currently creates structure only. It does not generate dynamic arcs,
Arc continuation, or automatic payoff.

## Render Adapter

Render Adapter converts storyboard JSON into render-friendly JSON for future
media pipelines.

It prepares:

- narration
- TTS text
- subtitle text
- image prompt
- duration
- camera style
- visual style
- transition type

It does not generate mp4, call ffmpeg, run TTS, generate images, compose video,
burn subtitles, or mix BGM.

```bash
python generate_storyboard.py --provider mock --sub-genre 地鐵末班車 --duration 180 --output output/storyboard_render.json --eval --export-render-input
```

This writes:

```text
output/storyboard_render.render.json
```

## Logs

Successful generation metadata:

```text
logs/generations/{YYYY-MM-DD}/{run_id}.json
```

Failure metadata:

```text
logs/failures.jsonl
```

Logs do not include API keys, full prompts, raw model output, manual response
content, full Story Bible content, full Arc Plan content, or full render JSON.

## UI Contract

The minimal UI contract is a JSON/Pydantic contract for a future Web UI. It lets
the frontend build tabs, fields, and actions from the same concepts used by the
CLI.

It defines:

- Manual and OpenAI tabs
- shared fields such as sub-genre, duration, evaluator, auto-fix, render export,
  and forbidden words input
- mode-specific fields
- shared and mode-specific actions

Print the contract:

```bash
python generate_storyboard.py --print-ui-contract
```

## Web Prototype

The prototype includes a FastAPI backend and a Vite React frontend. It does not
implement login, database storage, WebSocket collaboration, deployment, video
generation, image generation, TTS, ffmpeg, or `render_v5_local.py` integration.

Start the backend:

```bash
uvicorn api.main:app --reload --port 8000
```

Start the frontend:

```bash
cd web
npm install
npm run dev
```

Manual tab flow:

```text
產 prompt → 貼到 ChatGPT / Claude / Gemini → 貼回 JSON → parse/eval/render
```

OpenAI tab flow:

```text
設定後端 API key → 一鍵生成
```

OpenAI keys are read only by the backend. The frontend does not store API keys.

## Future Web UI Tabs

Tab 1:

- 省錢模式 Manual

Tab 2:

- API 自動模式 OpenAI

Shared capabilities:

- evaluator
- auto-fix
- render export
- forbidden words input

## Smoke Tests

Smoke tests validate the core local pipelines so later refactors do not quietly
break working behavior.

Current smoke coverage includes:

- mock generation
- manual parse
- local auto-fix
- render export
- story memory initialization
- cost guard blocking
- provider error handling
- CLI wrapper behavior

These tests are CI-friendly: they do not require an API key, do not require a
local model server, and write generated files into temporary directories instead
of the real `output/` and `logs/` folders.

## Run Smoke Tests

```bash
python -m unittest discover -s ai_writer_room/tests
```

## Future UI Plan

The future frontend can expose two primary tabs:

- Tab 1: 省錢模式（Manual）
- Tab 2: API 自動模式（OpenAI）

Both modes will share:

- evaluator
- auto-fix
- render export
- story memory
- arc planner

## Module Responsibilities

- `generate_storyboard.py`: main CLI entry point.
- `cli.py`: compatibility wrapper around `generate_storyboard.main`.
- `generator/prompt_builder.py`: prompt templates with safe substitution.
- `generator/api_client.py`: OpenAI SDK wrapper.
- `generator/model_provider.py`: provider abstraction for OpenAI/local models.
- `generator/json_parser.py`: robust JSON extraction and schema validation.
- `generator/story_planner.py`: mock storyboard and long-form scaffolding builders.
- `evaluator/`: rule, forbidden-word, Arc, memory, and render checks.
- `memory/`: Story Bible, Memory Summary, Foreshadow Tracker, Arc Plan models.
- `render/`: storyboard-to-render input adapter.
- `schemas/`: Pydantic storyboard and scene contracts.

## Roadmap

1. Harden OpenAI JSON generation and retry strategy.
2. Add more evaluator checks for pacing and payoff quality.
3. Add structured auto-fix reporting.
4. Add dynamic Arc planning.
5. Add long-form continuation and memory compression.
6. Integrate render, TTS, image, subtitle, and video pipelines.
