import re
from django.core.exceptions import ValidationError

def validate_username(value):
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise ValidationError('Username can only contain letters, numbers, and underscores.')
