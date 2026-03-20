# Publishing boundary

Publishing should happen through an adapter layer, not by mutating the core draft model into vendor-specific shapes.

## Current commands

```bash
python3 publish_cli.py provider-status
python3 publish_cli.py credentials-needed
python3 publish_cli.py build-publish-ready --draft-id <DRAFT_ID>
python3 queue_cli.py schedule --draft-id <DRAFT_ID> --at "2026-03-18T09:00:00Z"
python3 queue_cli.py unschedule --draft-id <DRAFT_ID>
python3 queue_cli.py dashboard
```

## Current provider target
- `upload_post` is the planned first publishing backend
- keep it optional and replaceable

## Rule
The draft JSON remains vendor-neutral.
Provider-specific payloads belong in the publish adapter layer.
