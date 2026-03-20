#!/usr/bin/env python3
import argparse
import datetime as dt
import json
from pathlib import Path
from workspace import DRAFTS, STATE_DIRS, load_json, save_json
from workspace import CONFIG

SCHED_CFG = load_json(CONFIG / 'scheduling.json')

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
    draft['updated_at'] = dt.datetime.now(dt.timezone.utc).isoformat()
    save_json(path, draft)

def move_draft(draft_id: str, target_state: str):
    current_state, path, draft = load_draft(draft_id)
    draft['status'] = target_state
    draft['updated_at'] = dt.datetime.now(dt.timezone.utc).isoformat()
    if target_state == 'approved':
        draft['approval']['approved'] = True; draft['approval']['approved_at'] = draft['updated_at']; draft['approval']['approved_by'] = 'reviewer'
    elif target_state in {'pending', 'rejected'}:
        draft['approval']['approved'] = False
        if target_state == 'rejected': draft['approval']['approved_at'] = None; draft['approval']['approved_by'] = None
    new_path = DRAFTS / target_state / path.name
    save_json(new_path, draft)
    if path.exists(): path.unlink()
    print(json.dumps({'draft_id': draft_id, 'from': current_state, 'to': target_state, 'path': str(new_path)}, indent=2))

def add_note(draft_id: str, note: str):
    _state, path, draft = load_draft(draft_id)
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(); draft.setdefault('notes', []).append(f'{stamp} :: {note}'); save_draft(path, draft)
    print(json.dumps({'draft_id': draft_id, 'note_added': True, 'notes_count': len(draft['notes'])}, indent=2))

def summarize_draft(draft_id: str):
    state, path, draft = load_draft(draft_id)
    print(json.dumps({'id': draft['id'], 'topic': draft['topic'], 'state': state, 'post_type': draft.get('post_type'), 'platform': draft['platform'], 'target': draft['target'], 'version': draft.get('generation', {}).get('version'), 'full_post': draft['text']['full_post'], 'visual': {'variant': draft['visual'].get('variant'), 'headline': draft['visual']['headline'], 'subtext': draft['visual']['subtext'], 'asset_path': draft['visual']['asset_path']}, 'approval': draft['approval'], 'publishing': draft.get('publishing', {}), 'notes': draft.get('notes', []), 'path': str(path)}, indent=2))

def request_revision(draft_id: str, note: str):
    state, path, draft = load_draft(draft_id)
    if state != 'pending': raise SystemExit('Revision requests are only supported for pending drafts')
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(); draft.setdefault('notes', []).append(f'{stamp} :: revision-request :: {note}'); save_draft(path, draft)
    print(json.dumps({'draft_id': draft_id, 'revision_requested': True, 'path': str(path)}, indent=2))

def set_schedule(draft_id: str, when: str, timezone: str | None):
    state, path, draft = load_draft(draft_id)
    if state not in {'approved', 'scheduled'}: raise SystemExit('Only approved or scheduled drafts can be scheduled')
    tz = timezone or SCHED_CFG.get('timezone') or 'UTC'
    draft.setdefault('publishing', {})['schedule_at'] = when; draft['publishing']['timezone'] = tz; draft['publishing']['publish_action'] = 'schedule'
    draft.setdefault('notes', []).append(f"{dt.datetime.now(dt.timezone.utc).isoformat()} :: scheduled :: {when} [{tz}]")
    draft['status'] = 'scheduled'
    new_path = DRAFTS / 'scheduled' / path.name
    save_json(new_path, draft)
    if path != new_path and path.exists(): path.unlink()
    print(json.dumps({'draft_id': draft_id, 'scheduled_for': when, 'timezone': tz, 'path': str(new_path)}, indent=2))

def clear_schedule(draft_id: str):
    state, path, draft = load_draft(draft_id)
    if state != 'scheduled': raise SystemExit('Only scheduled drafts can clear schedule')
    draft['publishing']['schedule_at'] = None; draft['publishing']['timezone'] = SCHED_CFG.get('timezone') or 'UTC'; draft['publishing']['publish_action'] = 'publish-now'; draft['status'] = 'approved'
    draft.setdefault('notes', []).append(f"{dt.datetime.now(dt.timezone.utc).isoformat()} :: unscheduled")
    new_path = DRAFTS / 'approved' / path.name
    save_json(new_path, draft); path.unlink(); print(json.dumps({'draft_id': draft_id, 'unscheduled': True, 'path': str(new_path)}, indent=2))

def dashboard():
    summary = {}
    for state in STATE_DIRS:
        rows = []
        for path in sorted((DRAFTS / state).glob('*.json')):
            draft = json.loads(path.read_text())
            rows.append({'id': draft['id'], 'topic': draft['topic'], 'post_type': draft.get('post_type'), 'version': draft.get('generation', {}).get('version'), 'schedule_at': draft.get('publishing', {}).get('schedule_at')})
        summary[state] = rows
    print(json.dumps(summary, indent=2))

def list_drafts(state: str):
    rows = []
    for path in sorted((DRAFTS / state).glob('*.json')):
        draft = json.loads(path.read_text())
        rows.append({'id': draft['id'], 'topic': draft['topic'], 'status': draft['status'], 'post_type': draft.get('post_type'), 'version': draft.get('generation', {}).get('version'), 'schedule_at': draft.get('publishing', {}).get('schedule_at'), 'asset_path': draft.get('visual', {}).get('asset_path'), 'path': str(path)})
    print(json.dumps(rows, indent=2))

def main():
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest='cmd', required=True)
    p_list = sub.add_parser('list'); p_list.add_argument('--state', default='pending', choices=STATE_DIRS)
    sub.add_parser('dashboard')
    p_move = sub.add_parser('move'); p_move.add_argument('--draft-id', required=True); p_move.add_argument('--to', required=True, choices=STATE_DIRS)
    p_show = sub.add_parser('show'); p_show.add_argument('--draft-id', required=True)
    p_note = sub.add_parser('add-note'); p_note.add_argument('--draft-id', required=True); p_note.add_argument('--note', required=True)
    p_revision = sub.add_parser('request-revision'); p_revision.add_argument('--draft-id', required=True); p_revision.add_argument('--note', required=True)
    p_approve = sub.add_parser('approve'); p_approve.add_argument('--draft-id', required=True); p_approve.add_argument('--note')
    p_reject = sub.add_parser('reject'); p_reject.add_argument('--draft-id', required=True); p_reject.add_argument('--note', required=True)
    p_sched = sub.add_parser('schedule'); p_sched.add_argument('--draft-id', required=True); p_sched.add_argument('--at', required=True); p_sched.add_argument('--timezone')
    p_uns = sub.add_parser('unschedule'); p_uns.add_argument('--draft-id', required=True)
    args = parser.parse_args()
    if args.cmd == 'list': list_drafts(args.state)
    elif args.cmd == 'dashboard': dashboard()
    elif args.cmd == 'move': move_draft(args.draft_id, args.to)
    elif args.cmd == 'show': summarize_draft(args.draft_id)
    elif args.cmd == 'add-note': add_note(args.draft_id, args.note)
    elif args.cmd == 'request-revision': request_revision(args.draft_id, args.note)
    elif args.cmd == 'approve':
        if args.note: add_note(args.draft_id, f'approval-note :: {args.note}')
        move_draft(args.draft_id, 'approved')
    elif args.cmd == 'reject': add_note(args.draft_id, f'rejection :: {args.note}'); move_draft(args.draft_id, 'rejected')
    elif args.cmd == 'schedule': set_schedule(args.draft_id, args.at, args.timezone)
    elif args.cmd == 'unschedule': clear_schedule(args.draft_id)

if __name__ == '__main__':
    main()
