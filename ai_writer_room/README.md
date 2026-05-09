# AI Writer Room v0.1

AI Writer Room v0.1 是一個可擴充的 AI 敘事系統工程骨架。當前版本支援本地 mock storyboard JSON 輸出、本地 evaluator、prompt template 組裝，以及 mock / OpenAI / local 三種 model provider。

目前不實作 auto-fix。OpenAI 與 local provider 都只負責生成 raw text、解析成 `Storyboard` schema，並輸出 JSON。

## Current Scope

- Python 3.11+
- 3 分鐘規則怪談 storyboard JSON
- 本地 mock data 產生器
- Model Provider 抽象層：`mock` / `openai` / `local`
- 本地 RuleChecker / ForbiddenWordChecker / StoryboardEvaluator
- PromptBuilder 與 prompt templates
- OpenAI API 生成模式
- OpenAI-compatible local server 生成模式
- CLI/script 操作
- Pydantic schema
- pathlib output handling

## Folder Structure

```text
ai_writer_room/
├── cli.py
├── config.py
├── generate_storyboard.py
├── README.md
├── requirements.txt
├── evaluator/
│   ├── __init__.py
│   ├── evaluator.py
│   ├── forbidden_word_checker.py
│   ├── pacing_checker.py
│   └── rule_checker.py
├── generator/
│   ├── __init__.py
│   ├── api_client.py
│   ├── json_parser.py
│   ├── model_provider.py
│   ├── prompt_builder.py
│   ├── rule_engine.py
│   ├── scene_generator.py
│   └── story_planner.py
├── logs/
├── memory/
├── output/
├── prompts/
│   ├── auto_fix.tmpl
│   ├── evaluator.tmpl
│   └── rule_horror.tmpl
├── schemas/
│   ├── scene_schema.py
│   └── storyboard_schema.py
└── tests/
```

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## API Key

OpenAI API key 讀取順序：

1. 環境變數 `OPENAI_API_KEY`
2. 本機檔案：

```text
C:\Users\p0989\Desktop\claude floder\claude floder.openai_api_key
```

OpenAI provider 的預設模型：

```text
gpt-4o-mini
```

安全注意事項：

- 不要 commit API key。
- 不要把 `.env` commit。
- 不要把 `.openai_api_key` 或任何 `*.openai_api_key` 檔案 commit。
- `output/` 與 `logs/` 不應保存 API key。
- CLI 不會印出 API key。

## Providers

`--provider mock`

- 預設模式。
- 不呼叫任何模型。
- 使用 `generator/story_planner.py` 產生固定 12 scenes mock storyboard。
- 適合本地開發、schema 測試、evaluator 測試。

`--provider openai`

- 使用 `OpenAIModelProvider`。
- 包裝既有 `OpenAIClient`。
- 需要 OpenAI API key。
- 預設模型使用 `config.DEFAULT_MODEL`，目前是 `gpt-4o-mini`。

`--provider local`

- 使用 `LocalModelProvider`。
- 支援本地 OpenAI-compatible API。
- 預設 base URL：

```text
http://localhost:11434/v1
```

- 預設模型：

```text
qwen2.5:7b
```

- 預設 api_key 使用 placeholder：

```text
ollama
```

- 需要本機已啟動相容 OpenAI API 的服務，例如 Ollama OpenAI-compatible endpoint。

`--use-api`

- legacy alias。
- 等同於：

```bash
--provider openai
```

## Usage

Mock storyboard generation:

```bash
python generate_storyboard.py --provider mock --sub-genre 地鐵末班車 --duration 180 --output output/storyboard_mock.json
```

Mock generation with local evaluator:

```bash
python generate_storyboard.py --provider mock --sub-genre 地鐵末班車 --duration 180 --output output/storyboard_mock.json --eval
```

Print the assembled rule horror prompt only:

```bash
python generate_storyboard.py --sub-genre 地鐵末班車 --duration 180 --print-prompt
```

OpenAI provider:

```bash
python generate_storyboard.py --provider openai --sub-genre 地鐵末班車 --duration 180 --model gpt-4o-mini --output output/storyboard_openai.json --eval
```

Legacy OpenAI alias:

```bash
python generate_storyboard.py --use-api --sub-genre 地鐵末班車 --duration 180 --model gpt-4o-mini --output output/storyboard_openai.json --eval
```

Local provider:

```bash
python generate_storyboard.py --provider local --sub-genre 地鐵末班車 --duration 180 --model qwen2.5:7b --output output/storyboard_local.json --eval
```

## Outputs

Storyboard JSON:

```text
output/storyboard_mock.json
output/storyboard_openai.json
output/storyboard_local.json
```

Evaluator JSON:

```text
output/storyboard_mock.eval.json
output/storyboard_openai.eval.json
output/storyboard_local.eval.json
```

JSON output uses:

- `ensure_ascii=False`
- `indent=2`

## Logs

Each non-`--print-prompt` generation run creates a `run_id`.

Successful generation metadata is written to:

```text
logs/generations/{YYYY-MM-DD}/{run_id}.json
```

Failure metadata is appended to:

```text
logs/failures.jsonl
```

Generation logs currently include metadata such as:

- `run_id`
- `created_at`
- `provider`
- `model`
- `sub_genre`
- `duration_sec`
- `output_path`
- `eval_path`
- `success`
- `eval_passed`
- `scene_count`
- `rule_check_passed`
- `forbidden_word_check_passed`

Failure logs currently include:

- `run_id`
- `created_at`
- `provider`
- `model`
- `sub_genre`
- `duration_sec`
- `error_type`
- `error_message`
- `stage`

Log safety:

- Logs do not record API keys.
- Logs do not record the full prompt.
- Logs do not record raw model output.
- Real log files are ignored by Git.
- `logs/.gitkeep` is kept only so the directory exists in the repository.

## Module Responsibilities

- `generator/model_provider.py`: Base provider interface plus OpenAI and local providers.
- `generator/api_client.py`: OpenAI client wrapper. It returns raw text only and does not parse JSON.
- `generator/json_parser.py`: Extracts JSON from raw model output and validates it as `Storyboard`.
- `generator/prompt_builder.py`: Builds rule horror, evaluator, and auto-fix prompts from templates.
- `generator/run_logger.py`: Writes safe generation and failure metadata logs.
- `generator/story_planner.py`: Local mock storyboard generation.
- `generator/rule_engine.py`: Mock rules and rule reference checks.
- `evaluator/`: Local rule and forbidden-word evaluation.
- `schemas/`: Pydantic contracts for scene and storyboard JSON.
- `prompts/`: Prompt templates for generation, evaluator, and future auto-fix.
- `output/`: Local generated JSON files.
- `logs/`: Future runtime logs.

## Roadmap

1. Keep mock generation as the safe local fallback.
2. Improve prompt templates with stronger JSON constraints.
3. Harden API JSON parsing and add retry/fix strategy.
4. Add evaluator coverage for pacing, clarity, and payoff quality.
5. Add auto-fix loop.
6. Add Story Bible, Memory Summary, and Foreshadow Tracker.
7. Extend to 30-60 minute long-form story generation.
8. Add render/export adapters for video, narration, and script workflows.
