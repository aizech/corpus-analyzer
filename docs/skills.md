# Corpus Analyzer Skills

Corpus Analyzer uses a lightweight skill-routing system. Skills are Markdown files that provide task-specific instructions to the agent. The router selects relevant skills for each prompt and prepends them to the user request.

## Skill Layout

Skills live under `skills/core/`:

```text
skills/core/
├── medical-image-analysis/
│   └── SKILL.md
└── web-fetcher/
    ├── SKILL.md
    └── tools/
        ├── web_fetch.py
        └── web_fetch_lib/
```

Every skill folder must contain a `SKILL.md` file. Optional `tools/` subdirectories contain Python modules with Agno `@tool` functions that are discovered automatically.

## SKILL.md Format

```markdown
---
name: medical-image-analysis
description: >
  Analyze medical images (X-ray, MRI, CT, ultrasound) for educational purposes.
---

# Medical Image Analysis Skill

Instructions for the agent go here...
```

- `name` — Unique skill identifier.
- `description` — Used for routing; should explain when the skill applies.

## How Routing Works

1. `agent_config.skill_router.discover_catalog()` scans `skills/core/` for `SKILL.md` files.
2. `select_candidates()` scores each skill against the prompt using the `name` and `description`.
3. `route_prompt()` picks the top skills (with model-based ranking as a fallback).
4. `compose_routed_prompt()` prepends the selected skill instructions to the user prompt.

## Adding a New Skill

1. Create a new folder under `skills/core/<skill-name>/`.
2. Add `SKILL.md` with frontmatter (`name`, `description`) and instructions.
3. Optionally add `tools/` with `@tool` functions.
4. The router will discover the skill automatically on the next run.

## Web Fetcher

The `web-fetcher` skill is enabled by default. It provides a `web_fetch` tool that fetches and extracts web content for literature and guideline lookups.

- Set `ENABLE_WEB_FETCHER=false` to disable it.
- It requires `httpx`, `trafilatura`, and `nest_asyncio`.
