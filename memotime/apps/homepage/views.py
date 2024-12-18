from datetime import datetime

import django.views.generic

__all__ = ()


class HomeView(django.views.generic.TemplateView):
    template_name = "homepage/index.html"


class BlockedView(django.views.generic.TemplateView):
    template_name = "homepage/blocked.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        timestamp = float(self.kwargs["expires_at"])
        context["expires_at"] = datetime.fromtimestamp(timestamp)
        return context
