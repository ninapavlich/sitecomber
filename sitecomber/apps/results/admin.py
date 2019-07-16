from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator

from .models import PageResult, PageRequest, PageResponse, ResponseHeader, RequestHeader


class ResponseHeaderInline(admin.TabularInline):
    model = ResponseHeader
    readonly_fields = fields = ['key', 'value']
    extra = 0


class RequestHeaderInline(admin.TabularInline):
    model = RequestHeader
    readonly_fields = fields = ['key', 'value']
    extra = 0


@admin.register(PageResponse)
class PageResponseAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': (
                'view_request',
                'view_redirected_from',
                'response_url',
                'status_code',
                ('load_start_time', 'load_end_time',),
                ('content_type', 'content_length'),
                'view_text'
            )
        }),

    )
    readonly_fields = ['view_request',
                       'view_redirected_from',
                       'response_url',
                       'status_code',
                       'load_start_time', 'load_end_time',
                       'content_type', 'content_length',
                       'view_text']

    def view_text(self, obj):
        return Truncator(obj.text_content).chars(1000)

    def view_request(self, obj):
        return format_html(u'<a href="%s">< Back to Request</a>' % (obj.request.get_edit_url()))

    def view_redirected_from(self, obj):
        if self.reqdirected_from:
            return format_html(u'<a href="%s">View %s</a>' % (obj.redirected_from.get_edit_url(), obj.redirected_from))

    inlines = [ResponseHeaderInline]


class PageResponseInline(admin.TabularInline):
    model = PageResponse
    readonly_fields = fields = ['load_start_time', 'response_url', 'status_code', 'content_type', 'view_item']
    extra = 0

    def view_item(self, obj):
        return format_html(u'<a href="%s">View Response Details +</a>' % (obj.get_edit_url()))

    inlines = [RequestHeaderInline]


@admin.register(PageRequest)
class PageRequestAdmin(admin.ModelAdmin):

    inlines = [PageResponseInline]

    fieldsets = (
        (None, {
            'fields': (
                'view_page',
                'request_url',
                'method',
                ('status_code', 'content_type'),
                'view_response',
                ('load_start_time', 'load_end_time',),
            )
        }),

    )
    readonly_fields = ['view_page',
                       'request_url',
                       'method',
                       'status_code', 'content_type',
                       'view_response',
                       'load_start_time', 'load_end_time', ]

    def view_page(self, obj):
        return format_html(u'<a href="%s">< Back to %s</a>' % (obj.page.get_edit_url(), obj.page))

    def status_code(self, obj):
        if obj.response:
            return obj.response.status_code

    def content_type(self, obj):
        if obj.response:
            return obj.response.content_type

    def view_response(self, obj):
        return format_html(u'<a href="%s">View Response</a>' % (obj.response.get_edit_url()))


class PageRequestInline(admin.TabularInline):
    model = PageRequest
    readonly_fields = fields = ['request_url', 'method', 'status_code', 'content_type', 'load_start_time', 'view_item']
    extra = 0

    def status_code(self, obj):
        if obj.response:
            return obj.response.status_code

    def content_type(self, obj):
        if obj.response:
            return obj.response.content_type

    def view_item(self, obj):
        return format_html(u'<a href="%s">View Request Details +</a>' % (obj.get_edit_url()))


@admin.register(PageResult)
class PageResultAdmin(admin.ModelAdmin):

    list_display_links = list_display = ['site_domain', 'url', 'last_load_time']
    list_filter = ['site_domain']
    readonly_fields = ['site_domain', 'url', 'created', 'modified',
                       'last_load_time', 'view_site_settings']

    fieldsets = (
        (None, {
            'fields': (
                'view_site_settings',
                'site_domain',
                'url',
            )
        }),
        ('Metadata', {
            'fields': (
                'created',
                'modified'
            ),
        }),
    )

    inlines = [PageRequestInline]
    custom_list_order_by = 'title'

    def view_site_settings(self, obj):
        return format_html(u'<a href="%s">< View Settings for %s</a>' % (obj.site_domain.site.get_edit_url(), obj.site_domain.site))
