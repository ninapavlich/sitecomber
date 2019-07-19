from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from sitecomber.apps.config.models import Site


class SiteDetailView(DetailView):

    model = Site


class SiteListView(ListView):

    model = Site
