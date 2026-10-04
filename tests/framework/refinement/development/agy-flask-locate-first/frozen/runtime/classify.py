"""Native provider availability classification; source/tool text is never evidence."""
import json

AUTH_MARKERS = ('invalid_grant', 'resource_exhausted', 'rate_limit_exceeded',
                'quota exceeded', 'authentication failed', 'unauthorized',
                'sign in to', 'login required', 'invalid api key', 'insufficient_quota')

def auth_blocked(events):
    for event in events:
        error = None
        if event.get('event') == 'result':
            result = event.get('result', {})
            if isinstance(result, dict) and result.get('status') == 'ERROR':
                error = result.get('error')
        elif event.get('event') in ('error', 'provider_error', 'sdk_error'):
            error = event.get('error')
        if error is not None:
            text = json.dumps(error, ensure_ascii=False).lower()
            if any(marker in text for marker in AUTH_MARKERS):
                return True
    return False
