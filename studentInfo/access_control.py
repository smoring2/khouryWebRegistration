"""Session based authentication / authorization for the registration app.

The application authenticates three distinct principal types (student, advisor
and admin) against its own tables instead of ``django.contrib.auth``.  This
module centralises

* establishing an authenticated session (``login_student`` / ``login_advisor``
  / ``login_admin`` / ``logout``),
* the view decorators that every non public route must be guarded with
  (``student_required`` / ``advisor_required`` / ``admin_required``),
* the DRF permission class used as ``DEFAULT_PERMISSION_CLASSES``.

The session stores an explicit role marker next to the principal identifier so
the three privilege levels can never be confused with one another, and the
decorators additionally verify that the identifier addressed by the request
belongs to the caller (horizontal privilege check).
"""

from functools import wraps

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from rest_framework.permissions import BasePermission

ROLE_STUDENT = 'student'
ROLE_ADVISOR = 'advisor'
ROLE_ADMIN = 'admin'

# Session keys.  The role marker is mandatory: ``advisor`` and ``admin`` used to
# share the ``employee_id`` key, which made the two privilege levels
# indistinguishable.
SESSION_ROLE_KEY = 'role'
SESSION_ID_KEYS = {
    ROLE_STUDENT: 'nuid',
    ROLE_ADVISOR: 'advisor_employee_id',
    ROLE_ADMIN: 'admin_employee_id',
}

LOGIN_PAGE_BY_ROLE = {
    ROLE_STUDENT: 'student_login_page',
    ROLE_ADVISOR: 'advisor_login_page',
    ROLE_ADMIN: 'admin_login_page',
}


def _login(request, role, principal_id):
    """Start a fresh authenticated session for ``role``.

    ``flush()`` drops any pre-existing session and issues a new session key,
    which prevents session fixation and stops privileges from an earlier login
    (e.g. a student session) leaking into the new one.
    """
    request.session.flush()
    request.session[SESSION_ROLE_KEY] = role
    request.session[SESSION_ID_KEYS[role]] = principal_id


def login_student(request, student):
    _login(request, ROLE_STUDENT, student.nuid)


def login_advisor(request, advisor):
    _login(request, ROLE_ADVISOR, advisor.employee_id)


def login_admin(request, admin):
    _login(request, ROLE_ADMIN, admin.employee_id)


def logout(request):
    request.session.flush()


def current_role(request):
    """Role of the caller, or ``None`` for an anonymous caller."""
    return request.session.get(SESSION_ROLE_KEY)


def current_principal_id(request, role=None):
    """Identifier of the caller for ``role`` (defaults to the session role)."""
    role = role or current_role(request)
    if role not in SESSION_ID_KEYS:
        return None
    return request.session.get(SESSION_ID_KEYS[role])


def is_authenticated_as(request, role):
    return current_role(request) == role and current_principal_id(request, role) is not None


def _same_principal(value, principal_id):
    """Compare a value coming from the URL/query string with the session id."""
    if value is None or value == '':
        return True  # nothing addressed, nothing to scope
    try:
        return int(value) == int(principal_id)
    except (TypeError, ValueError):
        return False


def _require_role(role, url_kwargs=(), query_params=()):
    """Build a decorator enforcing ``role`` plus an ownership check.

    ``url_kwargs`` / ``query_params`` name the request parameters that carry the
    identifier of the principal the request acts on.  When present they must
    match the identifier stored in the session, so an authenticated caller
    cannot operate on somebody else's records.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not is_authenticated_as(request, role):
                messages.warning(request, 'Please sign in to continue.')
                return redirect(LOGIN_PAGE_BY_ROLE[role])

            principal_id = current_principal_id(request, role)
            for name in url_kwargs:
                if name in kwargs and not _same_principal(kwargs[name], principal_id):
                    raise PermissionDenied('Not allowed to access this record.')
            for name in query_params:
                if not _same_principal(request.GET.get(name), principal_id):
                    raise PermissionDenied('Not allowed to access this record.')

            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


# A student may only ever address its own records.
student_required = _require_role(
    ROLE_STUDENT,
    url_kwargs=('pk', 'nuid', 'student_id'),
    query_params=('nuid', 'student_id'),
)

# An advisor may only ever act as itself.
advisor_required = _require_role(
    ROLE_ADVISOR,
    url_kwargs=('employee_id', 'advisor_id'),
    query_params=('advisor', 'advisor_id'),
)

# Admin routes are back office wide, so there is no per-object scoping.
admin_required = _require_role(ROLE_ADMIN)


class IsAdvisorSession(BasePermission):
    """Default permission for the REST API.

    Every endpoint under ``/api/advisor/`` is an advisor operation, so an
    authenticated advisor session is required and, when the request names an
    ``advisor_id``, it must be the advisor that is signed in.
    """

    message = 'Advisor authentication required.'

    scoped_params = ('advisor_id', 'advisor')

    def has_permission(self, request, view):
        if not is_authenticated_as(request, ROLE_ADVISOR):
            return False
        principal_id = current_principal_id(request, ROLE_ADVISOR)
        for name in self.scoped_params:
            if not _same_principal(request.query_params.get(name), principal_id):
                return False
        return True
