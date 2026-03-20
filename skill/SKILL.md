---
name: social-workspace
description: Structured VPS-side social content workspace for OpenClaw users. Use when creating, organizing, reviewing, approving, or preparing social media drafts, brand notes, visual placeholders, queue states, and future publishing adapters for LinkedIn and later channels. Prefer this skill for social content workflow instead of ad hoc files or direct third-party posting logic.
---

# Social Workspace

Use the canonical integration root:

`<YOUR_OPENCLAW_WORKSPACE>/social-workspace-integration`

This workspace owns:
- brand structure
- draft objects
- approval states
- generated assets
- future publishing adapter boundaries

## Working directory

```bash
cd <YOUR_OPENCLAW_WORKSPACE>/social-workspace-integration
source .venv/bin/activate
```

## Current v1 commands

- `python3 content_cli.py create-draft --topic "..."`
- `python3 content_cli.py create-post-package --topic "..." --type authority --variant indigo-steel`
- `python3 queue_cli.py list --state pending`
- `python3 queue_cli.py show --draft-id <id>`
- `python3 queue_cli.py add-note --draft-id <id> --note "..."`
- `python3 queue_cli.py request-revision --draft-id <id> --note "..."`
- `python3 content_cli.py regenerate-post-package --draft-id <id> --note "..."`
- `python3 queue_cli.py approve --draft-id <id> [--note "..."]`
- `python3 queue_cli.py reject --draft-id <id> --note "..."`
- `python3 queue_cli.py schedule --draft-id <id> --at "2026-03-18T09:00:00Z"`
- `python3 queue_cli.py unschedule --draft-id <id>`
- `python3 queue_cli.py dashboard`
- `python3 assets_cli.py render-placeholder --headline "..." --subtext "..." --output outputs/images/example.png`
- `python3 publish_cli.py build-publish-ready --draft-id <id>`
- `python3 publish_cli.py credentials-needed`

## Design rules

- Keep the workspace as the source of truth.
- Do not couple draft storage to any publishing vendor.
- Treat future services like Upload-Post, LinkedIn APIs, or Canva as adapters, not the core workflow.
- Maintain explicit approval states.
- Keep strategy, drafts, outputs, config, and logs separated.

## References

Read as needed:
- `references/structure.md`
- `references/brand.md`
- `references/workflow.md`
- `references/future-publishing.md`
