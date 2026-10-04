"""Native Codex availability interpretation, separate from patch grading.

Use structured terminal events only. No source/tool text, HTTP assumptions,
model calls, automatic retries, or replacement of original grades.
"""
import json

AUTH_TERMS = ('invalid_grant', 'authentication failed', 'failed to refresh oauth',
              'login required', 'unauthorized')
QUOTA_TERMS = ('insufficient_quota', 'quota exceeded', 'usage limit')


def interpret_codex_terminal(events):
    events = [e for e in events if isinstance(e, dict)]
    terminal = [e for e in events if e.get('type') in ('turn.completed', 'turn.failed')]
    if terminal and terminal[-1]['type'] == 'turn.completed':
        return {'actor_available': True, 'stage_stop_reason': None,
                'provider_failure': None, 'recovered_errors': sum(e.get('type') == 'error' for e in events)}
    failures = [e for e in events if e.get('type') in ('error', 'turn.failed')]
    messages = [json.dumps(e.get('error', e.get('message', ''))).lower() for e in failures]
    reason = None
    if any(any(term in message for term in AUTH_TERMS) for message in messages):
        reason = 'authentication_unavailable'
    elif any(any(term in message for term in QUOTA_TERMS) for message in messages):
        reason = 'quota_unavailable'
    elif any('workspace routing discovery failed' in message for message in messages):
        reason = 'workspace_routing_unavailable'
    elif terminal and terminal[-1]['type'] == 'turn.failed':
        reason = 'native_turn_failed'
    return {'actor_available': False if reason else None,
            'stage_stop_reason': reason, 'provider_failure': reason,
            'recovered_errors': 0}
