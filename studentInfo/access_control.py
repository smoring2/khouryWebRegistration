"""Session based authentication / authorization helpers.

The application manages its own principals (``Student``, ``Advisor`` and
``Admin`` rows) instead of ``django.contrib.auth`` users, so the standard
``login_required`` / ``permission_required`` decorators cannot be used.

This module centralises everything related to the signed in principal:

* establishing a session for a principal (with session fixation protection),
* reading the role / identifier of the current principal,
* view decorators and class based view mixins that deny anonymous callers,
* object level checks so a principal can only reach its own records,
* a DRF permission class used as the project wide default so that API
  endpoints fail closed.
"""

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect
from rest_framework.permissions import BasePermission

# Roles.
ROLE_STUDENT = 'student'
ROLE_ADVISOR = 'advisor'
ROLE_ADMIN = 'admin'

# Session keys. The role marker is mandatory: without it an advisor session and
# an admin session would be indistinguishable.
SESSION_ROLE_KEY = 'role'
SESSION_STUDENT_ID_KEY = 'nuid'
SESSION_ADVISOR_ID_KEY = 'advisor_employee_id'
SESSION_ADMIN_ID_KEY = 'admin_employee_id'

_ID_KEY_BY_ROLE = {
    ROLE_STUDENT: SESSION_STUDENT_ID_KEY,
    ROLE_ADVISOR: SESSION_ADVISOR_ID_KEY,
    ROLE_ADMIN: SESSION_ADMIN_ID_KEY,
}

_LOGIN_PAGE_BY_ROLE = {
    ROLE_STUDENT: 'student_login_page',
    ROLE_ADVISOR: 'advisor_login_page',
    ROLE_ADMIN: 'admin_login_page',
}

SIGN_IN_REQUIRED_MESSAGE = 'Please sign in to continue.'
FORBIDDEN_MESSAGE = 'You are not allowed to access that record.'


def start_session(request, role, principal_id):
    """Bind ``principal_id`` to the session under an explicit role marker.

    The existing session is flushed first so that a session identifier chosen
    by an attacker before the login cannot be reused afterwards (session
    fixation).
    """
    if role not in _ID_KEY_BY_ROLE:
        raise ValueError('Unknown role: {}'.format(role))
    request.session.flush()
    request.session[SESSION_ROLE_KEY] = role
    request.session[_ID_KEY_BY_ROLE[role]] = principal_id


def end_session(request):
    """Drop every trace of the signed in principal."""
    request.session.flush()


def current_role(request):
    """Return the role of the signed in principal, or ``None``."""
    role = request.session.get(SESSION_ROLE_KEY)
    return role if role in _ID_KEY_BY_ROLE else None


def current_principal_id(request, role=None):
    """Return the identifier of the signed in principal, or ``None``.

    When ``role`` is given the identifier is only returned if the session
    actually belongs to that role.
    """
    session_role = current_role(request)
    if session_role is None or (role is not None and session_role != role):
        return None
    return request.session.get(_ID_KEY_BY_ROLE[session_role])


def _same_id(session_id, requested_id):
    if session_id is None or requested_id is None:
        return False
    try:
        return int(session_id) == int(requested_id)
    except (TypeError, ValueError):
        return False


def _deny(request, role):
    """Send an unauthenticated / unauthorized caller back to a login page."""
    messages.warning(request, SIGN_IN_REQUIRED_MESSAGE)
    return redirect(_LOGIN_PAGE_BY_ROLE[role])


def role_required(role):
    """Deny any caller that is not signed in with exactly ``role``."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if current_role(request) != role:
                return _deny(request, role)
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


student_required = role_required(ROLE_STUDENT)
advisor_required = role_required(ROLE_ADVISOR)
admin_required = role_required(ROLE_ADMIN)


def student_self_required(id_kwarg):
    """Require a student session whose ``nuid`` matches ``id_kwarg``.

    Prevents one student from reading or modifying another student's record.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if current_role(request) != ROLE_STUDENT:
                return _deny(request, ROLE_STUDENT)
            requested_id = kwargs.get(id_kwarg, args[0] if args else None)
            if not _same_id(current_principal_id(request, ROLE_STUDENT), requested_id):
                messages.warning(request, FORBIDDEN_MESSAGE)
                return redirect(_LOGIN_PAGE_BY_ROLE[ROLE_STUDENT])
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


def advisor_self_required(id_kwarg=None, id_query_param=None):
    """Require an advisor session that owns the requested advisor identity.

    The advisor identifier is taken from the URL keyword ``id_kwarg`` when
    given, otherwise from the ``id_query_param`` query string parameter.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if current_role(request) != ROLE_ADVISOR:
                return _deny(request, ROLE_ADVISOR)
            if id_kwarg is not None:
                requested_id = kwargs.get(id_kwarg, args[0] if args else None)
            else:
                requested_id = request.GET.get(id_query_param)
            if not _same_id(current_principal_id(request, ROLE_ADVISOR), requested_id):
                messages.warning(request, FORBIDDEN_MESSAGE)
                return redirect(_LOGIN_PAGE_BY_ROLE[ROLE_ADVISOR])
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


class RoleRequiredMixin:
    """Class based view guard mirroring :func:`role_required`."""

    required_role = None

    def dispatch(self, request, *args, **kwargs):
        if current_role(request) != self.required_role:
            return _deny(request, self.required_role)
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    required_role = ROLE_ADMIN


class StudentSelfRequiredMixin:
    """Requires a student session that owns the record being rendered."""

    owner_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        if current_role(request) != ROLE_STUDENT:
            return _deny(request, ROLE_STUDENT)
        if not _same_id(current_principal_id(request, ROLE_STUDENT),
                        kwargs.get(self.owner_url_kwarg)):
            messages.warning(request, FORBIDDEN_MESSAGE)
            return redirect(_LOGIN_PAGE_BY_ROLE[ROLE_STUDENT])
        return super().dispatch(request, *args, **kwargs)


class IsSignedInAdvisor(BasePermission):
    """DRF default permission: only the advisor that owns the data may call.

    Every REST endpoint in this project is part of the advisor portal, so this
    is used as ``DEFAULT_PERMISSION_CLASSES``; any endpoint added later is
    therefore denied to anonymous callers unless it opts out explicitly.
    """

    message = 'Advisor sign in required.'

    def has_permission(self, request, view):
        session_advisor_id = current_principal_id(request, ROLE_ADVISOR)
        if session_advisor_id is None:
            return False
        requested_advisor_id = request.query_params.get('advisor_id')
        if requested_advisor_id is not None:
            return _same_id(session_advisor_id, requested_advisor_id)
        return True
