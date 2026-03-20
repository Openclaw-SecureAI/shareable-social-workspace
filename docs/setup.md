# Setup

## 1. Clone into your OpenClaw workspace

Suggested location:

```bash
~/.openclaw/workspace/shareable-social-workspace
```

## 2. Create a Python environment

```bash
cd integration
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Update configuration placeholders

Edit:
- `config/defaults.json`
- `config/publishing.json`
- brand files under `brand/`

Minimum changes:
- set your `brand_profile`
- set your `brand_display_name`
- set your Upload-Post profile name if you plan to publish

## 4. Create your first post package

```bash
python3 content_cli.py create-post-package \
  --topic "How small systems reduce admin friction" \
  --type educational \
  --audience "small business owners" \
  --angle "show business value without hype" \
  --variant indigo-steel
```

## 5. Review queue state

```bash
python3 queue_cli.py list --state pending
python3 queue_cli.py dashboard
```

## 6. Continue with the rest of the docs

Recommended next reads:
- `docs/configuration.md`
- `docs/workflow.md`
- `docs/verification.md`
- `docs/troubleshooting.md`
