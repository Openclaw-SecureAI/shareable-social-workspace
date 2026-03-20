#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import re
import subprocess
from pathlib import Path
from workspace import ROOT, DRAFTS, STATE_DIRS, load_defaults, save_json

DEFAULTS = load_defaults()
ASSETS_CLI = ROOT / 'assets_cli.py'
DRAFTS_PENDING = DRAFTS / 'pending'
POST_TYPES = {
    'authority': {'body': 'Most people know this matters, but very few turn it into a system they can rely on consistently.', 'cta': 'What part of this would you improve first?', 'visual_concept': 'clean authority card with direct statement', 'subtext': 'Small systems create big leverage over time.'},
    'educational': {'body': 'The real value is not in doing more tasks manually. It is in designing a process that reduces repetition, protects focus, and scales cleanly.', 'cta': 'What would you automate first?', 'visual_concept': 'educational insight card with clear takeaway', 'subtext': 'Clarity and consistency beat complexity.'},
    'opinion': {'body': 'Too many teams confuse effort with leverage. Real leverage comes from systems, not repeated manual friction.', 'cta': 'Do you agree or disagree?', 'visual_concept': 'bold opinion card', 'subtext': 'Systems beat hustle when scale matters.'},
}

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-') or 'draft'

def build_post_text(topic: str, post_type: str, audience=None, angle=None):
    profile = POST_TYPES[post_type]
    angle_line = f"\n\nAngle: {angle}." if angle else ''
    audience_line = f"\n\nThis matters especially for {audience}." if audience else ''
    full_post = (
        f"{topic}\n\n{profile['body']}{angle_line}{audience_line}\n\n"
        "Leverage comes from creating a repeatable way to get the result, not from manually forcing the same action every time.\n\n"
        "When you reduce friction, protect attention, and make execution more consistent, you create room for better decisions and better growth.\n\n"
        f"{profile['cta']}"
    )
    return {'hook': topic, 'body': profile['body'], 'cta': profile['cta'], 'full_post': full_post}

def build_draft(topic: str, post_type='authority', audience=None, angle=None, variant='indigo-steel'):
    now = dt.datetime.now(dt.timezone.utc)
    draft_id = f"{now.strftime('%Y-%m-%d')}-{DEFAULTS['platform']}-{slugify(topic)[:40]}"
    profile = POST_TYPES[post_type]
    text = build_post_text(topic, post_type, audience, angle)
    return {
        'id': draft_id,
        'platform': DEFAULTS['platform'],
        'target': DEFAULTS['target'],
        'status': 'pending',
        'created_at': now.isoformat(),
        'updated_at': now.isoformat(),
        'topic': topic,
        'content_type': 'text-image',
        'post_type': post_type,
        'brand_profile': DEFAULTS['brand_profile'],
        'generation': {'audience': audience, 'angle': angle, 'version': 1, 'last_action': 'create-post-package'},
        'text': text,
        'visual': {
            'concept': profile['visual_concept'],
            'headline': topic,
            'subtext': profile['subtext'],
            'variant': variant,
            'asset_path': str(ROOT / 'outputs' / 'images' / f'{draft_id}.png'),
            'preview_path': str(ROOT / 'outputs' / 'previews' / f'{draft_id}-preview.png'),
        },
        'approval': {'required': DEFAULTS['approval_required'], 'approved': False, 'approved_by': None, 'approved_at': None},
        'publishing': {'schedule_at': None, 'timezone': DEFAULTS.get('timezone', 'UTC'), 'publish_action': 'publish-now', 'provider': None, 'external_job_id': None, 'published_url': None},
        'notes': [],
    }

def find_draft(draft_id: str):
    matches = []
    for state in STATE_DIRS:
        path = DRAFTS / state / f'{draft_id}.json'
        if path.exists():
            matches.append((state, path))
    if not matches:
        raise SystemExit(f'Draft not found: {draft_id}')
    if len(matches) > 1:
        raise SystemExit(f'Duplicate draft IDs detected for {draft_id}: {matches}')
    return matches[0]

def load_draft(draft_id: str):
    state, path = find_draft(draft_id)
    return state, path, json.loads(path.read_text())

def save_draft(path: Path, draft: dict):
    draft['updated_at'] = dt.datetime.now(dt.timezone.utc).isoformat()
    save_json(path, draft)
    return path

def render_visual(draft: dict):
    cmd = ['python3', str(ASSETS_CLI), 'render-placeholder', '--headline', draft['visual']['headline'], '--subtext', draft['visual']['subtext'], '--variant', draft['visual'].get('variant', 'indigo-steel'), '--output', draft['visual']['asset_path']]
    subprocess.run(cmd, check=True, cwd=str(ROOT))

def create_draft(topic: str):
    draft = build_draft(topic)
    path = save_draft(DRAFTS_PENDING / f"{draft['id']}.json", draft)
    print(json.dumps({'draft_id': draft['id'], 'path': str(path), 'status': draft['status']}, indent=2))

def create_post_package(topic: str, post_type: str, audience, angle, variant: str):
    draft = build_draft(topic, post_type=post_type, audience=audience, angle=angle, variant=variant)
    render_visual(draft)
    path = save_draft(DRAFTS_PENDING / f"{draft['id']}.json", draft)
    print(json.dumps({'draft_id': draft['id'], 'path': str(path), 'status': draft['status'], 'post_type': post_type, 'asset_path': draft['visual']['asset_path'], 'full_post': draft['text']['full_post']}, indent=2))

def regenerate_post_package(draft_id: str, post_type=None, audience=None, angle=None, variant=None, note=None):
    state, path, draft = load_draft(draft_id)
    if state != 'pending':
        raise SystemExit('Only pending drafts can be regenerated')
    effective_type = post_type or draft.get('post_type', 'authority')
    effective_audience = audience if audience is not None else draft.get('generation', {}).get('audience')
    effective_angle = angle if angle is not None else draft.get('generation', {}).get('angle')
    effective_variant = variant or draft.get('visual', {}).get('variant', 'indigo-steel')
    profile = POST_TYPES[effective_type]
    draft['post_type'] = effective_type
    draft['generation'] = {'audience': effective_audience, 'angle': effective_angle, 'version': int(draft.get('generation', {}).get('version', 1)) + 1, 'last_action': 'regenerate-post-package'}
    draft['text'] = build_post_text(draft['topic'], effective_type, effective_audience, effective_angle)
    draft['visual']['concept'] = profile['visual_concept']
    draft['visual']['subtext'] = profile['subtext']
    draft['visual']['variant'] = effective_variant
    draft['approval'] = {'required': DEFAULTS['approval_required'], 'approved': False, 'approved_by': None, 'approved_at': None}
    stamp = dt.datetime.now(dt.timezone.utc).isoformat()
    draft.setdefault('notes', []).append(f'{stamp} :: regeneration :: {note or "package regenerated"}')
    render_visual(draft)
    save_draft(path, draft)
    print(json.dumps({'draft_id': draft['id'], 'state': state, 'post_type': draft['post_type'], 'variant': draft['visual']['variant'], 'version': draft['generation']['version'], 'asset_path': draft['visual']['asset_path']}, indent=2))

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd', required=True)
    p_create = sub.add_parser('create-draft'); p_create.add_argument('--topic', required=True)
    p_pkg = sub.add_parser('create-post-package'); p_pkg.add_argument('--topic', required=True); p_pkg.add_argument('--type', dest='post_type', choices=sorted(POST_TYPES.keys()), default='authority'); p_pkg.add_argument('--audience'); p_pkg.add_argument('--angle'); p_pkg.add_argument('--variant', choices=['midnight-premium', 'slate-cobalt', 'indigo-steel'], default='indigo-steel')
    p_regen = sub.add_parser('regenerate-post-package'); p_regen.add_argument('--draft-id', required=True); p_regen.add_argument('--type', dest='post_type', choices=sorted(POST_TYPES.keys())); p_regen.add_argument('--audience'); p_regen.add_argument('--angle'); p_regen.add_argument('--variant', choices=['midnight-premium', 'slate-cobalt', 'indigo-steel']); p_regen.add_argument('--note')
    args = parser.parse_args()
    if args.cmd == 'create-draft': create_draft(args.topic)
    elif args.cmd == 'create-post-package': create_post_package(args.topic, args.post_type, args.audience, args.angle, args.variant)
    elif args.cmd == 'regenerate-post-package': regenerate_post_package(args.draft_id, args.post_type, args.audience, args.angle, args.variant, args.note)

if __name__ == '__main__':
    main()
