# Setup

## 1. Clone into your OpenClaw workspace

Suggested location:
`~/.openclaw/workspace/shareable-social-workspace`

## 2. Create a Python environment

```bash
cd integration
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Update config placeholders

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
python3 content_cli.py create-post-package   --topic "How small systems reduce admin friction"   --type educational   --audience "small business owners"   --angle "show business value without hype"   --variant indigo-steel
```
