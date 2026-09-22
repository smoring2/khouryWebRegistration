"""Shared helpers for validating untrusted request parameters.

Every view in this project reads values straight out of ``request.POST`` /
``request.GET`` / ``request.query_params``.  Without a key check and a
type-coercion guard, a missing or non-numeric parameter raises
``MultiValueDictKeyError`` / ``ValueError`` / ``TypeError`` inside the view.
Such unhandled exceptions are rendered by Django as a technical 500 page which
discloses the failing source, every frame's local variables (including any
submitted credentials), the executed SQL and the settings table.

These helpers turn malformed input into a controlled ``400 Bad Request`` with a
short, non-revealing message instead.
"""

from functools import wraps

from django.http import HttpResponseBadRequest
from django.http.response import JsonResponse


class InvalidParameter(Exception):
    """Raised when a request parameter is missing or cannot be coerced."""


def get_str(data, name, required=True, default=None, max_length=None):
    """Return ``data[name]`` as a stripped string.

    Raises ``InvalidParameter`` when the key is absent/blank and ``required``,
    or when the value is longer than ``max_length``.
    """
    value = data.get(name) if data is not None else None
    if value is None or str(value).strip() == '':
        if required:
            raise InvalidParameter("Missing required parameter '{}'.".format(name))
        return default
    value = str(value).strip()
    if max_length is not None and len(value) > max_length:
        raise InvalidParameter("Parameter '{}' is too long.".format(name))
    return value


def to_int(value, name, min_value=None, max_value=None):
    """Coerce an already-extracted value to ``int`` without leaking tracebacks."""
    if value is None or str(value).strip() == '':
        raise InvalidParameter("Missing required parameter '{}'.".format(name))
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError):
        raise InvalidParameter("Parameter '{}' must be an integer.".format(name))
    if min_value is not None and parsed < min_value:
        raise InvalidParameter("Parameter '{}' is out of range.".format(name))
    if max_value is not None and parsed > max_value:
        raise InvalidParameter("Parameter '{}' is out of range.".format(name))
    return parsed


def get_int(data, name, required=True, default=None, min_value=None, max_value=None):
    """Return ``data[name]`` coerced to ``int``, or ``default`` when optional."""
    raw = get_str(data, name, required=required, default=None)
    if raw is None:
        return default
    return to_int(raw, name, min_value=min_value, max_value=max_value)


def get_float(data, name, required=True, default=None, min_value=None, max_value=None):
    """Return ``data[name]`` coerced to ``float``, or ``default`` when optional."""
    raw = get_str(data, name, required=required, default=None)
    if raw is None:
        return default
    try:
        parsed = float(raw)
    except (TypeError, ValueError):
        raise InvalidParameter("Parameter '{}' must be a number.".format(name))
    if min_value is not None and parsed < min_value:
        raise InvalidParameter("Parameter '{}' is out of range.".format(name))
    if max_value is not None and parsed > max_value:
        raise InvalidParameter("Parameter '{}' is out of range.".format(name))
    return parsed


def first_row(rows):
    """Return the first row of a cursor result set, or ``None`` when empty."""
    if rows:
        return rows[0]
    return None


def api_bad_request_guard(view):
    """Convert ``InvalidParameter`` into a JSON ``400`` response.

    DRF's exception handler only translates ``APIException``, ``Http404`` and
    ``PermissionDenied``; plain ``TypeError``/``ValueError`` would propagate to
    Django and render the debug page, so validation errors are converted here.
    """

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except InvalidParameter as exc:
            return JsonResponse({'message': str(exc)}, status=400)

    return wrapper


def html_bad_request_guard(view):
    """Convert ``InvalidParameter`` into a plain ``400`` response for page views."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except InvalidParameter as exc:
            return HttpResponseBadRequest(str(exc))

    return wrapper
