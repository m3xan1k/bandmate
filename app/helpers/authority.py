from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied


def check_user(model, attribute):
    def _check_user(func):
        def wrapper(*args, **kwargs):
            _id = kwargs.get('id')
            if _id is not None:
                instance = get_object_or_404(model, id=_id)
                user = getattr(instance, attribute)
                if not user == args[1].user:
                    raise PermissionDenied
            return func(*args, **kwargs)
        return wrapper
    return _check_user
