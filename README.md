# Shareable Social Workspace for OpenClaw

Portable, GitHub-ready packaging of a social content workspace for OpenClaw.

It includes two layers:
- `skill/` — the instruction layer for OpenClaw agents
- `integration/` — the local source-of-truth workspace and Python CLIs

This repo is designed to be reusable by another OpenClaw user without shipping live credentials, private profile names, or environment-specific absolute paths.

## What it does
- creates structured social drafts from topics
- generates a paired text + placeholder image package
- keeps explicit queue states: pending, approved, scheduled, published, rejected
- preserves a vendor-neutral draft schema
- keeps publishing behind an adapter boundary

## Quick start
1. Clone the repo into your OpenClaw workspace.
2. Create a virtual environment in `integration/`.
3. Install `requirements.txt`.
4. Copy the example config values and replace placeholders.
5. Run the verification commands in `docs/verification.md`.
6. Optionally copy `skill/` into your own OpenClaw skills directory and update paths.

## Repo map
- `skill/` — reusable skill instructions and references
- `integration/` — CLI implementation, config, schemas, brand docs, examples
- `docs/` — onboarding, configuration, workflow, outputs, verification, troubleshooting

## Safety / sanitization
Excluded from this repo:
- live API keys and tokens
- private local virtualenv files
- local `__pycache__`
- real published job IDs / published URLs
- user-specific absolute paths
- private profile names replaced with placeholders where appropriate
