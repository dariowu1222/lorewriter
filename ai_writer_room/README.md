# AI Writer Room v0.1

AI Writer Room v0.1 is the first engineering skeleton for an extensible AI narrative system. This version is scoped to 3-minute rule horror storyboard JSON generation through a CLI, while leaving clear extension points for evaluator, auto-fix, memory, and rendering workflows.

The codebase targets Python 3.11+ and uses `pathlib`, dataclasses, and Pydantic models. The current files are intentionally skeleton-only: class definitions, function signatures, docstrings, and TODO markers.

## Project Goals

- Generate 3-minute rule horror storyboard JSON.
- Provide a CLI-first workflow.
- Keep generation, evaluation, memory, schemas, prompts, and configuration separated.
- Prepare the architecture for long-form story generation without adding heavy abstractions in v0.1.

## Folder Structure

```text
ai_writer_room/
|
├─ generator/
│  ├─ __init__.py
│  ├─ api_client.py
│  ├─ prompt_builder.py
│  ├─ scene_generator.py
│  ├─ story_planner.py
│  └─ rule_engine.py
|
├─ evaluator/
│  ├─ __init__.py
│  ├─ evaluator.py
│  ├─ pacing_checker.py
│  ├─ rule_checker.py
│  └─ forbidden_word_checker.py
|
├─ memory/
│  ├─ __init__.py
│  ├─ story_bible.py
│  ├─ memory_summary.py
│  └─ foreshadow_tracker.py
|
├─ schemas/
│  ├─ storyboard_schema.py
│  └─ scene_schema.py
|
├─ prompts/
│  ├─ rule_horror.tmpl
│  ├─ evaluator.tmpl
│  └─ auto_fix.tmpl
|
├─ logs/
├─ output/
├─ tests/
├─ config.py
├─ cli.py
├─ generate_storyboard.py
├─ requirements.txt
└─ README.md
```

## Module Responsibilities

- `generator/`: Prompt construction, story planning, rule handling, scene generation, and model-provider boundary.
- `evaluator/`: Future storyboard quality checks, pacing checks, rule checks, and forbidden word scanning.
- `memory/`: Future Story Bible, memory summaries, and foreshadow tracking for long-form continuity.
- `schemas/`: Pydantic models for storyboard and scene JSON contracts.
- `prompts/`: Prompt templates for generation, evaluation, and auto-fix.
- `logs/`: Runtime logs.
- `output/`: Generated storyboard JSON files.
- `tests/`: Future unit and integration tests.
- `config.py`: Application settings and path configuration.
- `cli.py`: Typer-based command line interface.
- `generate_storyboard.py`: Programmatic storyboard generation entry point.

## Roadmap

1. Implement template loading and prompt rendering.
2. Add OpenAI API integration behind `APIClient`.
3. Generate schema-valid 3-minute storyboard JSON.
4. Add evaluator checks for pacing, rules, forbidden words, and story clarity.
5. Add auto-fix loop using evaluator feedback.
6. Add Story Bible, memory summary, and foreshadow continuity state.
7. Extend from 3-minute storyboard generation to 30-60 minute long-form story generation.
8. Add render/export adapters for downstream video, script, or narration workflows.

