from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings

# from rest_framework import routers

# from sitecomber.post.api import PostViewSet, APIHealthView
from sitecomber.apps.shared.admin import UserAdminAutocomplete

# router = routers.DefaultRouter()
# router.register(r'posts', PostViewSet)
# router.register(r'health', APIHealthView, basename='health')


urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        r'admin/user-autocomplete/',
        UserAdminAutocomplete.as_view(),
        name='user-autocomplete',
    ),

    # re_path(r'^', include(router.urls)),
    # re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

]


if settings.DEBUG:

    # Serve media for testing
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Enable Debug toolbar in debug mode
    import debug_toolbar
    urlpatterns = [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
