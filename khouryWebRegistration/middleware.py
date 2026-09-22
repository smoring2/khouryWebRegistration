"""Project middleware.

``SuppressTracebackMiddleware`` is a defense-in-depth control: even with the
per-view input validation in place, any unexpected exception raised by a view
would otherwise be rendered by Django as a technical 500 page whenever
``DEBUG`` is on, disclosing the failing source, frame locals (which can contain
submitted credentials), the executed SQL and the settings table.

The traceback is still recorded server-side through the logging framework, so
debugging information is preserved for operators without being returned to the
caller.
"""

import logging

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404, HttpResponseServerError

logger = logging.getLogger(__name__)

GENERIC_ERROR_BODY = (
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<title>Server Error (500)</title></head><body>'
    '<h1>Server Error (500)</h1>'
    '<p>The request could not be completed. Please try again later.</p>'
    '</body></html>'
)


class SuppressTracebackMiddleware:
    """Return a generic 500 instead of a debug traceback for view exceptions."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # These are part of Django's normal control flow (404 pages, permission
        # checks, request validation) and must keep their own handling.
        if isinstance(exception, (Http404, PermissionDenied, SuspiciousOperation)):
            return None
        logger.exception('Unhandled exception while processing %s', request.path)
        return HttpResponseServerError(GENERIC_ERROR_BODY, content_type='text/html')
