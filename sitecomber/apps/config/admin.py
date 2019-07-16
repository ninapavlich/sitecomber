from django import forms
from django.contrib import admin
from django.conf import settings

from dal import forward

from sitecomber.apps.shared.forms import AdminAutocompleteFormMixin
from sitecomber.apps.shared.admin import AdminModelSelect2

from .models import Site, SiteDomain, IgnoreURL, IgnoreQueryParam


class SiteDomainForm(AdminAutocompleteFormMixin):

    class Meta:
        model = SiteDomain
        fields = ('__all__')

        widgets = {
            # 'alias_of': AdminModelSelect2(
            #     url='admin-autocomplete',
            #     attrs={'data-html': True},
            #     forward=(forward.Const(
            #         val="config.SiteDomain", dst="model"),)
            # ),
        }


class SiteDomainInline(admin.TabularInline):
    model = SiteDomain
    form = SiteDomainForm
    fields = ['title', 'url', 'should_crawl', 'alias_of', 'override_sitemap']  # , 'authentication_type', 'authentication_data']
    extra = 0


class IgnoreURLInline(admin.TabularInline):
    model = IgnoreURL
    fields = ['url', 'authentication_type', 'authentication_data']
    extra = 0


class IgnoreQueryParamInline(admin.TabularInline):
    model = IgnoreQueryParam
    fields = ['param']
    extra = 0


class SiteForm(AdminAutocompleteFormMixin):

    class Meta:
        model = Site
        fields = ('__all__')

        widgets = {
            'owner': AdminModelSelect2(
                url='admin-autocomplete',
                attrs={'data-html': True},
                forward=(forward.Const(
                    val=settings.AUTH_USER_MODEL, dst="model"),)
            ),
        }


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
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
