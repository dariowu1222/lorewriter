# AI Writer Room v0.1

AI Writer Room v0.1 是一個可擴充的 AI 敘事系統工程骨架。當前版本支援本地 mock storyboard JSON 輸出、本地 evaluator、prompt template 組裝，以及可選的 OpenAI API 生成模式。

目前不實作 auto-fix，OpenAI API 模式只負責生成 raw text、解析成 `Storyboard` schema，並輸出 JSON。

## Current Scope

- Python 3.11+
- 3 分鐘規則怪談 storyboard JSON
- 本地 mock data 產生器
- 本地 RuleChecker / ForbiddenWordChecker / StoryboardEvaluator
- PromptBuilder 與 prompt templates
- 可選 OpenAI API 生成模式
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
│   ├── prompt_builder.py
│   ├── rule_engine.py
│   ├── scene_generator.py
│   └── story_planner.py
├── logs/
├── memory/
│   ├── __init__.py
│   ├── foreshadow_tracker.py
│   ├── memory_summary.py
│   └── story_bible.py
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

模型預設值：

```text
gpt-4o-mini
```

也可以用環境變數覆蓋：

```bash
set OPENAI_API_KEY=your_api_key_here
set DEFAULT_MODEL=gpt-4o-mini
```

安全注意事項：

- 不要 commit API key。
- 不要把 `.env` commit。
- 不要把 `.openai_api_key` 或任何 `*.openai_api_key` 檔案 commit。
- `output/` 與 `logs/` 不應保存 API key。
- CLI 不會印出 API key。

## Usage

Mock storyboard generation:

```bash
python generate_storyboard.py --sub-genre 地鐵末班車 --duration 180 --output output/storyboard_mock.json
```

Mock generation with local evaluator:

```bash
python generate_storyboard.py --sub-genre 地鐵末班車 --duration 180 --output output/storyboard_mock.json --eval
```

Print the assembled rule horror prompt only:

```bash
python generate_storyboard.py --sub-genre 地鐵末班車 --duration 180 --print-prompt
```

OpenAI API generation:

```bash
python generate_storyboard.py --sub-genre 地鐵末班車 --duration 180 --use-api --model gpt-4o-mini --output output/storyboard_api.json
```

OpenAI API generation with local evaluator:

```bash
python generate_storyboard.py --sub-genre 地鐵末班車 --duration 180 --use-api --model gpt-4o-mini --output output/storyboard_api.json --eval
```

## Outputs

Storyboard JSON:

```text
output/storyboard_mock.json
output/storyboard_api.json
```

Evaluator JSON:

```text
output/storyboard_mock.eval.json
output/storyboard_api.eval.json
```

JSON output uses:

- `ensure_ascii=False`
- `indent=2`

## Module Responsibilities

- `generator/api_client.py`: OpenAI client wrapper. It returns raw text only and does not parse JSON.
- `generator/json_parser.py`: Extracts JSON from raw model output and validates it as `Storyboard`.
- `generator/prompt_builder.py`: Builds rule horror, evaluator, and auto-fix prompts from templates.
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

