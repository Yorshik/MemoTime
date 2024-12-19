import datetime

import django.conf
import django.core.cache
import django.shortcuts
import django.urls
import django_ratelimit.core
import ipware.ip

__all__ = ()


class RedirectBlockedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = django.conf.settings.RATE_LIMIT
        self.rate_limit_timeout = django.conf.settings.RATE_LIMIT_TIMEOUT

    def __call__(self, request):
        if self.rate_limit is False:
            return self.get_response(request)

        response = self.process_request(request)
        if response:
            return response

        return self.get_response(request)

    def process_request(self, request):
        if self.rate_limit is False:
            return None

        if (
            request.resolver_match
            and request.resolver_match.view_name == "homepage:blocked"
        ):
            return None

        ip, is_routable = ipware.ip.IpWare().get_client_ip(request.META)
        if ip is None:
            return None

        ip_str = str(ip)
        blocked_ip_data = django.core.cache.cache.get(f"blocked_{ip_str}")

        if blocked_ip_data:
            expires_at_str = blocked_ip_data.get("expires_at")
            return django.shortcuts.redirect(
                django.urls.reverse(
                    "homepage:blocked",
                    kwargs={"expires_at": expires_at_str},
                ),
            )

        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        if self.rate_limit is False:
            return None

        response = self.process_request(request)
        if response:
            return response

        ip, is_routable = ipware.ip.IpWare().get_client_ip(request.META)
        if ip is None:
            return None

        ip_str = str(ip)

        def get_ip_key(group, request):
            return ip_str

        is_limited = django_ratelimit.core.is_ratelimited(
            request=request,
            group="daily_ip_limit",
            key=get_ip_key,
            rate=self.rate_limit,
            method=["POST"],
            increment=True,
        )

        if is_limited:
            expires_at = datetime.datetime.now() + datetime.timedelta(
                seconds=self.rate_limit_timeout,
            )
            expires_at_iso = expires_at.isoformat()

            if not django.core.cache.cache.get(f"blocked_{ip_str}"):
                django.core.cache.cache.set(
                    f"blocked_{ip_str}",
                    {"expires_at": expires_at_iso},
                    timeout=self.rate_limit_timeout,
                )

            return django.shortcuts.redirect(
                django.urls.reverse(
                    "homepage:blocked",
                    kwargs={"expires_at": expires_at_iso},
                ),
            )

        return None
