from django.views.generic.detail import DetailView

from sitecomber.apps.results.models import PageResult


class PageResultDetailView(DetailView):

    model = PageResult

    def get_queryset(self):
        print("GETTING QUERYSET!")
        # super(PageResultDetailView, self).get_queryset()
        return PageResult.objects.all().select_related('site_domain').prefetch_related('pagetestresult_set').prefetch_related('pagerequest_set').prefetch_related('pagerequest_set__response')
