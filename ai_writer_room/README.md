# AI Writer Room v0.1

AI Writer Room v0.1 是一個可擴充的 AI 敘事系統工程骨架。當前版本支援本地 mock storyboard JSON、本地 evaluator、prompt template 組裝，以及 `mock` / `openai` / `local` / `manual` 四種 provider。

目前不實作 auto-fix。API 商業化路線保留在 `openai` provider；`manual` provider 是給開發者本人低成本測試用的人工中轉流程。

## Current Scope

- Python 3.11+
- 3 分鐘規則怪談 storyboard JSON
- Model Provider：`mock` / `openai` / `local` / `manual`
- 本地 RuleChecker / ForbiddenWordChecker / StoryboardEvaluator
- PromptBuilder 與 prompt templates
- OpenAI API 生成模式
- OpenAI-compatible local server 生成模式
- Manual copy/paste 生成流程
- Generation / failure metadata logging
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
├── generator/
│   ├── api_client.py
│   ├── json_parser.py
│   ├── model_provider.py
│   ├── prompt_builder.py
│   ├── rule_engine.py
│   ├── run_logger.py
│   ├── scene_generator.py
│   └── story_planner.py
├── logs/
├── memory/
├── output/
├── prompts/
├── schemas/
└── tests/
```

## Setup

```bash
pip install -r requirements.txt
```

## Providers

`--provider mock`

- 預設模式。
- 不呼叫任何模型。
- 使用本地假資料產生固定 12 scenes storyboard。

`--provider openai`

- 使用 `OpenAIModelProvider`。
- 包裝既有 `OpenAIClient`。
- 需要 OpenAI API key。
- 預設模型：`gpt-4o-mini`。

`--provider local`

- 使用 `LocalModelProvider`。
- 支援本地 OpenAI-compatible server。
- Ollama 預設 base URL：

```text
http://localhost:11434/v1
```

- 預設模型：`qwen2.5:7b`
- 預設 api_key placeholder：`ollama`

`--provider manual`

- 不讀 API key。
- 不呼叫 OpenAI API。
- 不需要 local server。
- 用於把 prompt 複製到 ChatGPT / Claude / Gemini，再把回覆 JSON 讀回本地驗證。
- 支援模型回覆被 ```json code fence 包住的 JSON。

`--use-api`

- legacy alias。
- 等同 `--provider openai`。

## API Key

OpenAI API key 讀取順序：

1. 環境變數 `OPENAI_API_KEY`
2. 本機檔案：

```text
C:\Users\p0989\Desktop\claude floder\claude floder.openai_api_key
```

安全注意事項：

- 不要 commit API key。
- 不要 commit `.env`。
- 不要 commit `.openai_api_key` 或任何 `*.openai_api_key` 檔案。
- `output/` 與 `logs/` 不應保存 API key。
- CLI 不會印出 API key。

## Usage

Mock generation:

```bash
python generate_storyboard.py --provider mock --sub-genre 地鐵末班車 --duration 180 --output output/storyboard_mock.json --eval
```

Print prompt only:

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

## Manual Provider Workflow

Step 1: 產生 prompt 檔案。

```bash
python generate_storyboard.py --provider manual --sub-genre 地鐵末班車 --duration 180 --output output/manual_prompt.txt
```

Step 2: 把 `output/manual_prompt.txt` 的內容貼到 ChatGPT / Claude / Gemini。

Step 3: 把模型回傳 JSON 存成：

```text
output/manual_response.json
```

Step 4: 讀回並驗證。

```bash
python generate_storyboard.py --provider manual --manual-response output/manual_response.json --output output/storyboard_manual.json --eval
```

Manual prompt 產生模式不寫 generation log。Manual response parse 模式會寫 provider=`manual` 的 generation metadata log，但不會把 prompt 或 response 內容寫進 log。

## Local Auto-Fix

v0.1 auto-fix 只做本地 deterministic 修正：

- 不呼叫 LLM。
- 不呼叫 OpenAI API。
- 不花 API 費。
- 可修禁忌詞。
- 可補缺失的 `rule_refs`。
- 可補基本 metadata fallback。

不能修：

- 故事邏輯。
- 反轉品質。
- 長篇節奏。
- 角色動機。
- 真實敘事張力。

Mock auto-fix example:

```bash
python generate_storyboard.py --provider mock --sub-genre 地鐵末班車 --duration 180 --output output/storyboard_mock.json --eval --auto-fix
```

Manual response auto-fix with custom forbidden words:

```bash
python generate_storyboard.py --provider manual --manual-response output/manual_response.json --output output/storyboard_manual.json --eval --auto-fix --forbidden-words-file config/forbidden_words.custom.json
```

Forbidden-word config:

- Default config: `config/forbidden_words.default.json`
- Optional custom config: `config/forbidden_words.custom.json`
- Custom config overrides default replacements.
- Future frontend input can be converted into a custom forbidden-word JSON file.

Custom config example:

```json
{
  "某詞": "替換詞",
  "另一個詞": ""
}
```

If the replacement is an empty string, the word is removed.

When `--auto-fix` is used with `--eval`, eval JSON contains:

- `before_fix`
- `after_fix`
- `auto_fix_applied`
- `final_passed`

## Cost Guard

Cost Guard 用來避免 OpenAI API 成本失控。

- 只限制 `--provider openai`。
- `mock` / `manual` / `local` 不受 Cost Guard 阻擋。
- 目前是估算型成本控制。
- 不呼叫 OpenAI usage API。
- 不需要 DB。
- 不實作 dashboard。
- 不實作付費系統。

Default config:

```text
config/cost_guard.default.json
```

目前支援：

- 單次成本限制：`single_run_max_usd`
- 月成本限制：`monthly_budget_usd`
- warning threshold：`warning_threshold_ratio`
- model rough pricing table

Token estimation:

```text
estimated_tokens = len(text) / 4
```

Pricing 是 rough estimate，未來可更新，不要求與 OpenAI 官方價格完全同步。

如果 OpenAI run 超過單次或月成本限制，生成會在 API 呼叫前中止，並寫入 failure log：

```text
stage = budget_guard
```

## Ignore Budget Guard

開發者可以強制略過 budget guard：

```bash
python generate_storyboard.py --provider openai --ignore-budget-guard --sub-genre 地鐵末班車 --duration 180 --output output/storyboard_openai.json
```

使用 `--ignore-budget-guard` 時：

- Cost Guard 仍會估算成本。
- 若超過限制，console 只顯示 warning。
- 不會因 budget guard 阻擋執行。
- 成功生成時 generation metadata 仍會寫入估算成本。

## Outputs

Storyboard JSON:

```text
output/storyboard_mock.json
output/storyboard_openai.json
output/storyboard_local.json
output/storyboard_manual.json
```

Evaluator JSON:

```text
output/storyboard_mock.eval.json
output/storyboard_openai.eval.json
output/storyboard_local.eval.json
output/storyboard_manual.eval.json
```

JSON output uses:

- `ensure_ascii=False`
- `indent=2`

## Logs

Successful generation metadata is written to:

```text
logs/generations/{YYYY-MM-DD}/{run_id}.json
```

Failure metadata is appended to:

```text
logs/failures.jsonl
```

Log safety:

- Logs do not record API keys.
- Logs do not record the full prompt.
- Logs do not record raw model output.
- Logs do not record manual prompt or manual response content.
- Real log files are ignored by Git.
- `logs/.gitkeep` is kept only so the directory exists in the repository.

Generation metadata includes estimated cost fields:

- `estimated_cost_usd`
- `estimated_input_tokens`
- `estimated_output_tokens`

For `mock` / `manual` / `local`, these values default to zero.

## Module Responsibilities

- `generator/model_provider.py`: Base provider interface plus OpenAI and local providers.
- `generator/api_client.py`: OpenAI client wrapper. It returns raw text only and does not parse JSON.
- `generator/json_parser.py`: Extracts JSON from raw model/manual output and validates it as `Storyboard`.
- `generator/prompt_builder.py`: Builds rule horror, evaluator, and auto-fix prompts from templates.
- `generator/run_logger.py`: Writes safe generation and failure metadata logs.
- `generator/story_planner.py`: Local mock storyboard generation.
- `generator/rule_engine.py`: Mock rules and rule reference checks.
- `evaluator/`: Local rule and forbidden-word evaluation.
- `schemas/`: Pydantic contracts for scene and storyboard JSON.
- `prompts/`: Prompt templates for generation, evaluator, and future auto-fix.

## Story Bible

Story Bible is the long-form continuity layer. In v0.1 it is initialized from the
current storyboard and stores:

- character profiles
- world rules
- major unanswered questions
- hidden truths
- tone and theme notes

Purpose:

- keep long-form characters consistent
- keep rule-horror world logic consistent
- prepare for future Arc Planner support

v0.1 only initializes this data. It does not run long-form generation yet.

## Memory Summary

Memory Summary is the compressed story-state layer for future 30-60 minute
generation. In v0.1 it stores:

- current arc summary
- protagonist goal and status
- known rules
- unresolved questions
- threat level
- emotional curve
- last major event

Purpose:

- support future long-form context compression
- prepare for future multi-pass generation

v0.1 does not implement automatic LLM memory summarization or memory compression.

## Foreshadow Tracker

Foreshadow Tracker manages setup/payoff state. In v0.1 it initializes
foreshadowing items from storyboard scene refs and tracks unresolved items with
`status=setup_only`.

Purpose:

- manage setup/payoff pairs
- avoid lost foreshadowing threads
- prepare for long-form twist and payoff planning

v0.1 does not implement automatic payoff generation.

## Arc Planner

Arc Planner is the long-form structure layer for future 30-60 minute stories.
In v0.1 it initializes a fixed six-arc plan and attaches it to each storyboard
as `arc_plan`.

Purpose:

- control long-form narrative pacing
- distribute setup/payoff targets
- plan layered twists
- manage the emotional curve

v0.1 uses a fixed 6 Arc template. It does not implement dynamic arcs, Arc
continuation, LLM arc generation, or automatic payoff.

## 6 Arc Structure

Arc 1: 世界建立
Arc 2: 異常擴大
Arc 3: 中段反轉
Arc 4: 世界真相擴張
Arc 5: 主反轉
Arc 6: 尾刀

## Roadmap

1. Keep mock generation as the safe local fallback.
2. Keep manual provider for low-cost prompt iteration.
3. Improve prompt templates with stronger JSON constraints.
4. Harden API JSON parsing and add retry/fix strategy.
5. Add evaluator coverage for pacing, clarity, and payoff quality.
6. Add auto-fix loop.
7. Add Story Bible, Memory Summary, and Foreshadow Tracker.
8. Extend to 30-60 minute long-form story generation.
