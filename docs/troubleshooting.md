# Troubleshooting

## `ModuleNotFoundError: PIL`
Install dependencies in the active virtual environment:
```bash
pip install -r requirements.txt
```

## Draft paths point to the wrong workspace
Use the repo-local `integration/` directory or set:
```bash
export SOCIAL_WORKSPACE_ROOT=/path/to/your/integration
```

## Publishing fails with missing environment variable
You have not exported `UPLOAD_POST_API_KEY` yet.

## Publish-ready works but live publish fails
Check:
- provider `profile_name`
- connected social accounts in Upload-Post
- API key scope / validity
- scheduling format and timezone

## Images render with unexpected fonts
The renderer falls back to common system fonts. Install DejaVu or Liberation fonts if needed.
