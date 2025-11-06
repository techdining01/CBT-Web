from .models import ActionLog
from django.utils import timezone
import json

def log_action(user, action, model_name=None, object_id=None, details=None):
    ActionLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id else None,
        details=details or {}
    )
