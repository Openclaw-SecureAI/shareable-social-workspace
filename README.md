# Shareable Social Workspace for OpenClaw

A portable, GitHub-ready social content workspace for OpenClaw.

It includes two layers:
- `skill/` — the instruction layer for OpenClaw agents
- `integration/` — the local source-of-truth workspace and Python CLIs

This repository is designed to be reusable by another OpenClaw user without shipping live credentials, private profile names, or environment-specific absolute paths.

## What it does

- creates structured social drafts from topics
- generates paired text and placeholder image packages
- keeps explicit queue states: pending, approved, scheduled, published, rejected
- preserves a vendor-neutral draft schema
- keeps publishing behind an adapter boundary

## Quick start

1. Clone the repository into your OpenClaw workspace.
2. Create a virtual environment in `integration/`.
3. Install `requirements.txt`.
4. Copy the example configuration values and replace placeholders.
5. Run the verification commands in [`docs/verification.md`](./docs/verification.md).
6. Optionally copy `skill/` into your own OpenClaw skills directory and update paths.

## Repository map

- `skill/` — reusable skill instructions and references
- `integration/` — CLI implementation, config, schemas, brand docs, and examples
- `docs/` — onboarding, configuration, workflow, outputs, verification, and troubleshooting

## Recommended onboarding path

If you are evaluating the repo for the first time, read the docs in this order:
1. [`docs/setup.md`](./docs/setup.md)
2. [`docs/configuration.md`](./docs/configuration.md)
3. [`docs/workflow.md`](./docs/workflow.md)
4. [`docs/verification.md`](./docs/verification.md)
5. [`docs/troubleshooting.md`](./docs/troubleshooting.md)

## Safety and sanitization

This repository intentionally excludes:
- live API keys and tokens
- private local virtual environment files
- local `__pycache__`
- real published job IDs or published URLs
- user-specific absolute paths
- private profile names, replaced with placeholders where appropriate

## Notes

This is a workspace-oriented integration, not a polished SaaS product or package. The goal is clarity, portability, and a clean starting point for adaptation.
