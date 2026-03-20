# Verification

Run from `integration/` after installing requirements.

## 1. Generate a sample package
```bash
python3 content_cli.py create-post-package   --topic "Why simple workflows outperform chaos"   --type educational   --audience "service businesses"   --angle "emphasize consistency over complexity"   --variant midnight-premium
```

## 2. Inspect pending drafts
```bash
python3 queue_cli.py list --state pending
python3 queue_cli.py dashboard
```

## 3. Approve + build publish-ready payload
```bash
python3 queue_cli.py approve --draft-id <draft-id> --note "verification run"
python3 publish_cli.py build-publish-ready --draft-id <draft-id>
```

## 4. Optional provider checks
```bash
python3 publish_cli.py credentials-needed
python3 publish_cli.py provider-status
UPLOAD_POST_API_KEY=... python3 publish_cli.py validate-upload-post
```
