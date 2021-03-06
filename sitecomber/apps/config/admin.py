from django.contrib import admin
from django import forms

# from dal import forward
from django_ace import AceWidget

from sitecomber.apps.shared.forms import AdminAutocompleteFormMixin
# from sitecomber.apps.shared.admin import AdminModelSelect2

from .models import Site, SiteDomain, IncludeSeed, IgnoreResult, \
    IgnoreQueryParam, SiteTestSetting


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
    fields = ['title', 'url', 'should_crawl', 'alias_of', ]
    extra = 0


class IncludeSeedInline(admin.TabularInline):
    model = IncludeSeed
    fields = ['url']
    extra = 0


class IgnoreResultInline(admin.TabularInline):
    model = IgnoreResult
    fields = ['path']
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
            # 'owner': AdminModelSelect2(
            #     url='admin-autocomplete',
            #     attrs={'data-html': True},
            #     forward=(forward.Const(
            #         val=settings.AUTH_USER_MODEL, dst="model"),)
            # ),
        }


class SiteTestSettingAdminForm(forms.ModelForm):
    settings = forms.CharField(
        widget=AceWidget(mode='json', width="600px", height="200px", showprintmargin=True, wordwrap=True), required=False)

    class Meta:
        model = SiteTestSetting
        fields = '__all__'


class SiteTestSettingInline(admin.TabularInline):
    model = SiteTestSetting
    form = SiteTestSettingAdminForm
    fields = ['test', 'settings', 'active']
    extra = 0


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    form = SiteForm
    change_form_template = 'admin/site_change_form.html'

    list_display = ['title', 'owner', 'created', 'active']
    list_display_links = ['title']
    list_editable = ['active']
    list_filter = ['owner', 'active']
    readonly_fields = ['created', 'modified']

    fieldsets = (
        (None, {
            'fields': (
                'owner',
                'title',
                'active',
                'recursive',
                'override_user_agent',
                'override_max_timeout_seconds',
                'max_page_results'
            )
        }),
        ('Metadata', {
            'fields': (
                'created',
                'modified'
            ),
        }),
    )

    inlines = [SiteDomainInline, IncludeSeedInline, IgnoreResultInline, IgnoreQueryParamInline, SiteTestSettingInline]
    custom_list_order_by = 'title'
