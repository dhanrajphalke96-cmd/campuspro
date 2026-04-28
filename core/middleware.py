import json
from django.utils.deprecation import MiddlewareMixin
from core.models import AuditLog

class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware to log all mutating requests (POST, PUT, PATCH, DELETE) to the generic AuditLog.
    """
    def process_request(self, request):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and request.user.is_authenticated:
            # We determine the action
            action = 'other'
            if request.method == 'POST':
                action = 'create'
            elif request.method in ['PUT', 'PATCH']:
                action = 'update'
            elif request.method == 'DELETE':
                action = 'delete'
                
            # Filter out sensitive data from POST payload
            details_dict = {}
            if request.method in ['POST', 'PUT', 'PATCH']:
                for k, v in request.POST.items():
                    if 'password' not in k.lower() and 'token' not in k.lower():
                        details_dict[k] = v
                        
            details = json.dumps(details_dict) if details_dict else "No payload or binary data"
            
            # Simple IP retrieval
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
                
            model_name = request.path
            
            AuditLog.objects.create(
                user=request.user,
                action=action,
                model_name=model_name,
                details=details,
                ip_address=ip_address
            )
