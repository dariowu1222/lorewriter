# AI Writer Room v0.1

AI Writer Room v0.1 是一個可擴充的 AI 敘事系統工程骨架。當前版本先支援「本地假資料 storyboard JSON 輸出」，暫不呼叫 OpenAI API，也暫不實作 evaluator。

本專案目標是先把長篇 AI Writer Room 的乾淨架構打好，後續可逐步接上 Story Bible、Arc Planner、Foreshadow System、Memory Summary、Evaluator、Auto Fix，以及 30-60 分鐘長篇故事生成。

## Current Scope

- Python 3.11+
- 3 分鐘規則怪談 storyboard JSON
- 本地 mock data 產生器
- CLI/script 操作
- Pydantic schema
- pathlib output handling
- 不呼叫 OpenAI API

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

## Usage

先安裝依賴：

```bash
pip install -r requirements.txt
```

在 `ai_writer_room/` 目錄內執行 mock storyboard 生成：

```bash
python generate_storyboard.py --sub-genre 地鐵末班車 --duration 180 --output output/storyboard_mock.json
```

輸出檔會建立在：

```text
output/storyboard_mock.json
```

輸出的 JSON 使用：

- `ensure_ascii=False`
- `indent=2`
- 固定 12 個 scenes
- `model = local-mock-v0.1`
- `cost_usd = 0.0`

## Module Responsibilities

- `generator/`: story planning、prompt 組裝、rule engine、scene generation、model provider 邊界。
- `schemas/`: storyboard 與 scene 的 Pydantic JSON contract。
- `evaluator/`: 未來接 pacing、rule、forbidden word 與品質檢查。
- `memory/`: 未來接 Story Bible、memory summary、foreshadow tracking。
- `prompts/`: generation、evaluator、auto-fix prompt templates。
- `output/`: storyboard JSON 輸出。
- `logs/`: 未來 runtime logs。
- `tests/`: 未來測試。

## Roadmap

1. 完成本地 mock storyboard JSON 輸出。
2. 加入 template loading 與 prompt rendering。
3. 在 `APIClient` 後方接入 OpenAI API。
4. 產生 schema-valid 的規則怪談 storyboard。
5. 加入 evaluator：pacing、rules、forbidden words、clarity。
6. 加入 auto-fix loop。
7. 加入 Story Bible、Memory Summary、Foreshadow Tracker。
8. 擴展到 30-60 分鐘 long-form story generation。
9. 加入 render/export adapter，支援影片、旁白、腳本等下游流程。

