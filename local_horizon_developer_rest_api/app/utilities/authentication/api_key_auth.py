"""Provides function wrapper to verify Horizon API key provided by user."""

from app.models.component import User
from flask import request, g
from functools import wraps
import hashlib
from typing import Callable
from app.utilities.context import RequestContext


def api_key_required(f: Callable) -> Callable:
    """Provides function wrapper to verify Horizon API key provided by user.

    Args:
        f (Callable): function to wrap.

    Returns:
        Callable: wrapped function.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-Api-Key")
        if not api_key:
            return {"error": "API key required"}, 401

        # Hash API key and look up user
        api_key_hash = hashlib.sha256(api_key.encode("UTF-8")).hexdigest()
        user = User.query.filter_by(api_key_hash=api_key_hash).first()
        if not user:
            return {"error": "Invalid API key"}, 401

        # Attach user object to app context for function to reference
        g.user = user

        # # Create RequestContext object and store user
        # ctx = RequestContext(user=user)
        # kwargs["ctx"] = ctx  # pass the 'ctx' object

        kwargs["g"] = g

        return f(*args, **kwargs)

    return decorated_function
