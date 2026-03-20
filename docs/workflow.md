# Brand + Content Workflow

## Operating model
1. Capture/update brand notes in `integration/brand/`
2. Generate a draft package from a topic
3. Review the draft JSON and placeholder asset
4. Add notes or request revision
5. Approve or reject explicitly
6. Schedule if needed
7. Build a publish-ready payload or publish through an adapter

## Core commands
```bash
python3 content_cli.py create-draft --topic "..."
python3 content_cli.py create-post-package --topic "..." --type authority --variant indigo-steel
python3 queue_cli.py list --state pending
python3 queue_cli.py show --draft-id <id>
python3 queue_cli.py add-note --draft-id <id> --note "..."
python3 queue_cli.py request-revision --draft-id <id> --note "..."
python3 content_cli.py regenerate-post-package --draft-id <id> --note "..."
python3 queue_cli.py approve --draft-id <id> --note "approved"
python3 queue_cli.py schedule --draft-id <id> --at "2026-03-21T09:00:00Z"
python3 publish_cli.py build-publish-ready --draft-id <id>
```

## Design rule
The draft JSON is the source of truth.
Publishing vendors are adapters, not the core workflow.
