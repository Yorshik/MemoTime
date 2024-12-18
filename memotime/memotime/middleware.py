from datetime import datetime, timedelta

from django.core.cache import cache
from django.shortcuts import redirect
from django.urls import reverse
from django_ratelimit.core import is_ratelimited
from ipware.ip import IpWare

__all__ = ()


class RedirectBlockedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.resolver_match
            and request.resolver_match.view_name != "homepage:blocked"
        ):
            ip, _ = IpWare().get_client_ip(request.META)
            if ip:
                ip_str = str(ip)
                blocked_ip = cache.get(f"blocked_{ip_str}")
                if blocked_ip:
                    expires_at_str = blocked_ip.get("expires_at")
                    expires_at = datetime.fromisoformat(expires_at_str).timestamp()
                    return redirect(
                        reverse(
                            "homepage:blocked",
                            kwargs={"expires_at": expires_at},
                        ),
                    )

        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if (
            request.resolver_match
            and request.resolver_match.view_name == "homepage:blocked"
        ):
            return None

        ip, _ = IpWare().get_client_ip(request.META)
        if not ip:
            return None

        ip_str = str(ip)
        if blocked_ip := cache.get(f"blocked_{ip_str}"):
            expires_at_str = blocked_ip.get("expires_at")
            expires_at = datetime.fromisoformat(expires_at_str).timestamp()
            return redirect(
                reverse(
                    "homepage:blocked",
                    kwargs={"expires_at": expires_at},
                ),
            )

        def get_ip_key(group, request):
            return ip_str

        is_limited = is_ratelimited(
            request=request,
            group="daily_ip_limit",
            key=get_ip_key,
            rate="100/d",
            method=["POST"],
            increment=True,
        )
        if not is_limited:
            return None

        expires_at = datetime.now() + timedelta(weeks=1)
        expires_at_iso = expires_at.isoformat()
        cache.set(
            f"blocked_{ip_str}",
            {"expires_at": expires_at_iso},
            timeout=60 * 60 * 24 * 7,
        )
        return redirect(
            reverse("homepage:blocked", kwargs={"expires_at": expires_at.timestamp()}),
        )
