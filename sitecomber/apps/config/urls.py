from django.urls import path

from .views import SiteListView, SiteDetailView, SiteDetailReportView, SiteTestResultView

urlpatterns = [
    path('', SiteListView.as_view(), name='site-list'),
    path('<slug:pk>/', SiteDetailView.as_view(), name='site-detail'),
    path('<slug:pk>/report/', SiteDetailReportView.as_view(), name='site-detail-report'),
    path('<slug:pk>/test/', SiteTestResultView.as_view(), name='site-test-results'),
]
