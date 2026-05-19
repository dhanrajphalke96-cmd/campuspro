"""
core/middleware.py
──────────────────
AuditLogMiddleware: records mutating HTTP requests to AuditLog.

Security hardening applied:
  - Sensitive keys (password, token, csrfmiddlewaretoken) are stripped from payload.
  - X-Forwarded-For header is validated: only the first IP segment is trusted.
  - Static files, admin media, and favicon paths are excluded to avoid log flooding.
  - Catches all exceptions so a logging failure never breaks a user request.
"""

import json
from django.utils.deprecation import MiddlewareMixin

# Paths that should never be logged (static / noisy / irrelevant)
_EXCLUDED_PREFIXES = (
    '/static/',
    '/media/',
    '/favicon.ico',
    '/admin/jsi18n/',
)

# POST keys whose values must never appear in logs
_SENSITIVE_KEYS = {'password', 'token', 'csrfmiddlewaretoken', 'new_password', 'old_password'}


def _get_client_ip(request):
    """Return a safe client IP, taking only the first segment of X-Forwarded-For."""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        # Strip whitespace and take the leftmost (original client) address
        ip = forwarded.split(',')[0].strip()
        # Basic sanity: if it doesn't look like an IP, fall back
        if ip and len(ip) <= 45:
            return ip
    return request.META.get('REMOTE_ADDR', None)


class AuditLogMiddleware(MiddlewareMixin):
    """Log mutating requests (POST/PUT/PATCH/DELETE) to AuditLog."""

    def process_request(self, request):
        if request.method not in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return
        if not request.user.is_authenticated:
            return
        if any(request.path.startswith(p) for p in _EXCLUDED_PREFIXES):
            return

        action_map = {
            'POST':   'create',
            'PUT':    'update',
            'PATCH':  'update',
            'DELETE': 'delete',
        }
        action = action_map.get(request.method, 'other')

        # Build a sanitised payload dict
        payload = {}
        if request.method in ('POST', 'PUT', 'PATCH'):
            for key, value in request.POST.items():
                if key.lower() not in _SENSITIVE_KEYS:
                    payload[key] = value

        try:
            from core.models import AuditLog
            AuditLog.objects.create(
                user=request.user,
                action=action,
                model_name=request.path,
                details=json.dumps(payload) if payload else '',
                ip_address=_get_client_ip(request),
            )
        except Exception:
            # Never let audit logging break a user-facing request
            pass
