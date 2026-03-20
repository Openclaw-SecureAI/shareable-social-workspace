#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import mimetypes
import os
from pathlib import Path
from urllib import request, error
from uuid import uuid4
from workspace import DRAFTS, STATE_DIRS, CONFIG, load_json, save_json

PUBLISHING_CFG = load_json(CONFIG / 'publishing.json')

def find_draft(draft_id: str):
    matches = []
    for state in STATE_DIRS:
        path = DRAFTS / state / f'{draft_id}.json'
        if path.exists(): matches.append((state, path))
    if not matches: raise SystemExit(f'Draft not found: {draft_id}')
    if len(matches) > 1: raise SystemExit(f'Duplicate draft IDs detected for {draft_id}: {matches}')
    return matches[0]

def load_draft(draft_id: str):
    state, path = find_draft(draft_id)
    return state, path, json.loads(path.read_text())

def save_draft(path: Path, draft: dict):
    draft['updated_at'] = dt.datetime.now(dt.timezone.utc).isoformat(); save_json(path, draft)

def move_to_published(path: Path, draft: dict):
    new_path = DRAFTS / 'published' / path.name; draft['status'] = 'published'; save_draft(new_path, draft)
    if path != new_path and path.exists(): path.unlink()
    return new_path

def upload_post_cfg(): return PUBLISHING_CFG['providers']['upload_post']

def build_publish_ready_object(draft: dict, provider=None):
    provider_name = provider or draft.get('publishing', {}).get('provider') or PUBLISHING_CFG.get('default_provider')
    scheduled_for = draft.get('publishing', {}).get('schedule_at')
    publish_action = 'schedule' if scheduled_for else 'publish-now'
    payload = {'draft_id': draft['id'], 'platform': draft['platform'], 'target': draft['target'], 'content_type': draft['content_type'], 'text': draft['text']['full_post'], 'asset_path': draft.get('visual', {}).get('asset_path'), 'publish_action': publish_action, 'scheduled_for': scheduled_for, 'timezone': draft.get('publishing', {}).get('timezone'), 'approval_required': draft['approval']['required'], 'approved': draft['approval']['approved'], 'provider': provider_name, 'provider_payload': None}
    if provider_name == 'upload_post':
        cfg = upload_post_cfg()
        payload['provider_payload'] = {'base_url': cfg['base_url'], 'user': cfg['profile_name'], 'platform': [draft['platform']], 'title': draft['text']['full_post'], 'scheduled_date': scheduled_for, 'timezone': draft.get('publishing', {}).get('timezone'), 'asset_path': draft.get('visual', {}).get('asset_path')}
    return payload

def build_publish_ready(draft_id: str, provider=None):
    state, _path, draft = load_draft(draft_id)
    if state not in {'approved', 'scheduled'}: raise SystemExit('Only approved or scheduled drafts can become publish-ready')
    print(json.dumps(build_publish_ready_object(draft, provider), indent=2))

def provider_status(): print(json.dumps(PUBLISHING_CFG, indent=2))

def credentials_needed():
    print(json.dumps({'upload_post': {'required': ['Upload-Post account', 'connected social accounts in Upload-Post', 'profile name', 'API key stored in environment variable UPLOAD_POST_API_KEY'], 'optional_later': ['LinkedIn page ID if posting to pages instead of personal profile', 'additional platform-specific IDs for other networks']}}, indent=2))

def validate_upload_post():
    cfg = upload_post_cfg(); api_key = os.environ.get(cfg['api_key_env'])
    if not api_key: raise SystemExit(f"Missing environment variable: {cfg['api_key_env']}")
    checks = ['/uploadposts/history?page=1&limit=1', '/uploadposts/schedule']; results = []
    for suffix in checks:
        req = request.Request(cfg['base_url'].rstrip('/') + suffix, headers={'Authorization': f'Apikey {api_key}'})
        try:
            with request.urlopen(req, timeout=20) as resp:
                body = resp.read().decode('utf-8', errors='replace')
                try: parsed = json.loads(body)
                except Exception: parsed = {'raw': body}
                results.append({'endpoint': suffix, 'status': resp.status, 'response': parsed})
        except error.HTTPError as e:
            results.append({'endpoint': suffix, 'status': e.code, 'error': e.read().decode('utf-8', errors='replace')})
    print(json.dumps({'ok': True, 'provider': 'upload_post', 'checks': results}, indent=2))

def upload_post_publish(draft_id: str):
    state, path, draft = load_draft(draft_id)
    if state not in {'approved', 'scheduled'}: raise SystemExit('Only approved or scheduled drafts can be published')
    payload = build_publish_ready_object(draft, 'upload_post'); cfg = upload_post_cfg(); api_key = os.environ.get(cfg['api_key_env'])
    if not api_key: raise SystemExit(f"Missing environment variable: {cfg['api_key_env']}")
    endpoint = '/upload_photos' if payload['asset_path'] else '/upload_text'; url = cfg['base_url'].rstrip('/') + endpoint
    if payload['asset_path']:
        img_path = Path(payload['asset_path']); img_bytes = img_path.read_bytes(); boundary = '----WebKitFormBoundary' + uuid4().hex; parts = []
        def add_field(name, value): parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
        def add_file(name, filename, data, ctype): parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\nContent-Type: {ctype}\r\n\r\n').encode() + data + b'\r\n')
        add_field('user', cfg['profile_name']); add_field('platform[]', draft['platform']); add_field('title', payload['text'])
        if payload['scheduled_for']:
            add_field('scheduled_date', payload['scheduled_for'])
            if payload['timezone']: add_field('timezone', payload['timezone'])
        add_file('photos[]', img_path.name, img_bytes, mimetypes.guess_type(str(img_path))[0] or 'application/octet-stream'); parts.append(f'--{boundary}--\r\n'.encode()); body = b''.join(parts)
        req = request.Request(url, data=body, method='POST', headers={'Authorization': f'Apikey {api_key}', 'Content-Type': f'multipart/form-data; boundary={boundary}', 'Content-Length': str(len(body))})
    else:
        body = json.dumps({'user': cfg['profile_name'], 'platform': [draft['platform']], 'title': payload['text'], 'scheduled_date': payload['scheduled_for'], 'timezone': payload['timezone']}).encode()
        req = request.Request(url, data=body, method='POST', headers={'Authorization': f'Apikey {api_key}', 'Content-Type': 'application/json', 'Content-Length': str(len(body))})
    try:
        with request.urlopen(req, timeout=120) as resp: parsed = json.loads(resp.read().decode('utf-8', errors='replace'))
    except error.HTTPError as e:
        print(json.dumps({'ok': False, 'status': e.code, 'error': e.read().decode('utf-8', errors='replace')}, indent=2)); raise SystemExit(1)
    draft['publishing']['provider'] = 'upload_post'; draft['publishing']['external_job_id'] = parsed.get('job_id'); platform_result = (parsed.get('results') or {}).get(draft['platform']) or {}; draft['publishing']['published_url'] = platform_result.get('url')
    draft.setdefault('notes', []).append(f"{dt.datetime.now(dt.timezone.utc).isoformat()} :: publish :: upload_post :: job_id={parsed.get('job_id')}")
    new_path = move_to_published(path, draft)
    print(json.dumps({'ok': True, 'draft_id': draft_id, 'provider': 'upload_post', 'job_id': parsed.get('job_id'), 'request_id': parsed.get('request_id'), 'published_url': draft['publishing']['published_url'], 'path': str(new_path), 'response': parsed}, indent=2))

def main():
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest='cmd', required=True)
    p_status = sub.add_parser('status'); p_status.add_argument('--draft-id', required=True)
    p_ready = sub.add_parser('build-publish-ready'); p_ready.add_argument('--draft-id', required=True); p_ready.add_argument('--provider')
    p_publish = sub.add_parser('publish-upload-post'); p_publish.add_argument('--draft-id', required=True)
    sub.add_parser('provider-status'); sub.add_parser('credentials-needed'); sub.add_parser('validate-upload-post')
    args = parser.parse_args()
    if args.cmd == 'status': build_publish_ready(args.draft_id)
    elif args.cmd == 'build-publish-ready': build_publish_ready(args.draft_id, args.provider)
    elif args.cmd == 'provider-status': provider_status()
    elif args.cmd == 'credentials-needed': credentials_needed()
    elif args.cmd == 'validate-upload-post': validate_upload_post()
    elif args.cmd == 'publish-upload-post': upload_post_publish(args.draft_id)

if __name__ == '__main__':
    main()
