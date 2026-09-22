"""Request parameter validation helpers.

Views must never let malformed or missing request input escape as an unhandled
exception (``MultiValueDictKeyError``, ``KeyError``, ``ValueError``,
``TypeError``, ``IndexError``).  Django renders such exceptions as a technical
500 page which exposes the failing source, every frame's local variables
(including submitted credentials), the executed SQL and the settings table.
Django REST Framework does not help here either: its exception handler only
converts ``APIException``/``Http404``/``PermissionDenied``.

These helpers turn untrusted input into validated values (or an explicit
"invalid" signal) so that every view can answer with a controlled response.
"""


def coerce_int(value, default=None):
    """Return ``value`` as an ``int``, or ``default`` if it is not an integer.

    Accepts ``None``, empty strings and arbitrary text without raising.
    """
    if value is None:
        return default
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def coerce_float(value, default=None):
    """Return ``value`` as a ``float``, or ``default`` if it is not numeric."""
    if value is None:
        return default
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def get_int(params, name, default=None):
    """Read ``name`` from a mapping (QueryDict/dict) and coerce it to ``int``."""
    return coerce_int(params.get(name), default)


def get_text(params, name, default=''):
    """Read ``name`` from a mapping and return it as a stripped string."""
    value = params.get(name)
    if value is None:
        return default
    return str(value).strip()


def collect_ints(params, *names):
    """Coerce every named parameter to ``int``.

    Returns a ``(values, invalid)`` tuple where ``values`` maps the parameter
    names that parsed successfully and ``invalid`` lists the names that were
    missing or not integers.
    """
    values = {}
    invalid = []
    for name in names:
        parsed = coerce_int(params.get(name))
        if parsed is None:
            invalid.append(name)
        else:
            values[name] = parsed
    return values, invalid


def invalid_parameters_message(invalid):
    """Build a message naming the rejected parameters, without echoing values."""
    return 'Invalid or missing parameter(s): {}'.format(', '.join(invalid))
