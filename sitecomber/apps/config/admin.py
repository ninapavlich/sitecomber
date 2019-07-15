from django import forms
from django.contrib import admin

from dal import autocomplete

from django_list_wrestler.admin import AdminListOrderable, AdminListCollapsible

from .models import Site, SiteDomain, IgnoreURL, IgnoreQueryParam


class SiteDomainInline(admin.TabularInline):
    model = SiteDomain
    fields = ['title', 'url', 'canonical', 'authentication_type', 'authentication_data']
    extra = 0


class IgnoreURLInline(admin.TabularInline):
    model = IgnoreURL
    fields = ['url', 'authentication_type', 'authentication_data']
    extra = 0


class IgnoreQueryParamInline(admin.TabularInline):
    model = IgnoreQueryParam
    fields = ['param']
    extra = 0


class SiteForm(forms.ModelForm):

    class Meta:
        model = Site
        fields = ('__all__')
        widgets = {
            'owner': autocomplete.ModelSelect2(
                url='user-autocomplete',
                attrs={'data-html': True}
            )
        }


@admin.register(Site)
class SiteAdmin(AdminListCollapsible):
    form = SiteForm

    list_display_links = list_display = ['owner', 'title', 'created']
    list_filter = ['owner']
    readonly_fields = ['created', 'modified']

    fieldsets = (
        (None, {
            'fields': (
                'owner',
                'title',
                'recursive',
                'override_user_agent',
                'override_max_redirects', 'override_max_timeout_seconds'
            )
        }),
        ('Metadata', {
            'fields': (
                'created',
                'modified'
            ),
        }),
    )

    inlines = [SiteDomainInline, IgnoreURLInline, IgnoreQueryParamInline]
    custom_list_order_by = 'title'
