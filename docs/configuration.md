# Configuration

## `integration/config/defaults.json`
Core defaults used by the draft generator and asset renderer.

Key fields:
- `brand_profile` — internal brand slug
- `brand_display_name` — visible brand name on rendered cards
- `platform` — default target platform
- `target` — default publishing target
- `approval_required` — enforce review flow
- `timezone` — scheduling default
- `visual_footer_text` — footer line on generated cards

## `integration/config/publishing.json`
Provider adapter configuration.

Important:
- keep real API keys out of this file
- reference keys via environment variables
- use placeholders until deployment time

## Environment variables
- `UPLOAD_POST_API_KEY` — required only for Upload-Post validation/publishing
- `SOCIAL_WORKSPACE_ROOT` — optional override if you want the CLIs to operate on a different workspace root
