from django.conf import settings
from django.views.generic.detail import DetailView

from sitecomber.apps.results.models import PageResult


class PageResultDetailView(DetailView):

    model = PageResult

    def get_queryset(self):
        return PageResult.objects.all().select_related('site_domain').prefetch_related('pagetestresult_set').prefetch_related('pagerequest_set').prefetch_related('pagerequest_set__response')

    def get_context_data(self, **kwargs):
        context = super(PageResultDetailView, self).get_context_data(**kwargs)
        context['SETTINGS'] = settings.TEMPLATE_SETTINGS
        return context
