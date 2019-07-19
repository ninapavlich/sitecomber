from django.urls import path

from .views import PageResultDetailView

urlpatterns = [
    path('<slug:site_domain__site__pk>/<slug:pk>/', PageResultDetailView.as_view(), name='page-result-detail'),
]
