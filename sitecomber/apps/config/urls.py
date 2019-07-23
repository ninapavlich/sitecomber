from django.urls import path

from .views import SiteListView, SiteDetailView, SiteTestResultView

urlpatterns = [
    path('', SiteListView.as_view(), name='site-list'),
    path('<slug:pk>/', SiteDetailView.as_view(), name='site-detail'),
    path('<slug:pk>/test/', SiteTestResultView.as_view(), name='site-test-results'),
]
