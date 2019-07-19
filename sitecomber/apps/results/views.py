from django.views.generic.detail import DetailView

from sitecomber.apps.results.models import PageResult


class PageResultDetailView(DetailView):

    model = PageResult
