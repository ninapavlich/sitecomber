from django.conf import settings
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from sitecomber.apps.config.models import Site


class SiteDetailView(DetailView):

    model = Site

    def get_context_data(self, **kwargs):
        context = super(SiteDetailView, self).get_context_data(**kwargs)
        context['SETTINGS'] = settings.TEMPLATE_SETTINGS
        return context


class SiteListView(ListView):

    model = Site


class SiteTestResultView(DetailView):

    model = Site
    template_name = 'config/site_detail_tests.html'

    def get_context_data(self, **kwargs):
        context = super(SiteTestResultView, self).get_context_data(**kwargs)
        context['SETTINGS'] = settings.TEMPLATE_SETTINGS
        return context
