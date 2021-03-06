from django.contrib import admin
from django.template import Template, Context
from django.utils.html import format_html
from django.utils.text import Truncator

from .models import PageResult, PageRequest, PageResponse, PageTestResult


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
                'response_headers',
                'preview_response_text'
            )
        }),

    )
    readonly_fields = ['view_request',
                       'view_redirected_from',
                       'response_url',
                       'status_code',
                       'load_start_time', 'load_end_time',
                       'content_type', 'content_length', 'response_headers',
                       'preview_response_text', 'view_url', 'request_method']

    list_display = list_display_links = ['view_url', 'request_method', 'status_code']
    list_filter = ['request__method', 'status_code', 'content_type']
    search_fields = ['response_url']
    change_form_template = 'admin/pageresponse_change_form.html'

    def view_url(self, obj):
        return Truncator(obj.response_url).chars(80)

    def preview_response_text(self, obj):
        if self.showFull:
            return obj.text_content
        else:
            return Truncator(obj.text_content).chars(1000)

    def request_method(self, obj):
        if obj.request:
            return obj.request.method

    def view_request(self, obj):
        return format_html(u'<a href="%s">< Back to Request</a>' % (obj.request.get_edit_url()))

    def view_redirected_from(self, obj):
        if self.reqdirected_from:
            return format_html(u'<a href="%s">View %s</a>' % (obj.redirected_from.get_edit_url(), obj.redirected_from))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.showFull = ("full" in request.GET)
        return super().change_view(request, object_id, form_url, extra_context)

class PageResponseInline(admin.TabularInline):
    model = PageResponse
    readonly_fields = fields = ['load_start_time', 'response_url', 'status_code', 'content_type', 'view_item']
    extra = 0

    def view_item(self, obj):
        return format_html(u'<a href="%s">View Response Details +</a>' % (obj.get_edit_url()))


@admin.register(PageRequest)
class PageRequestAdmin(admin.ModelAdmin):

    inlines = [PageResponseInline]

    fieldsets = (
        (None, {
            'fields': (
                'view_page',
                'retain',
                'request_url',
                ('method', 'status_code'),
                ('content_type', 'content_length'),
                'view_response',
                ('load_start_time', 'load_end_time',),
                'request_headers'
            )
        }),

    )
    readonly_fields = ['view_page',
                       'request_url',
                       'method', 'status_code',
                       'content_type', 'content_length',
                       'view_response', 'request_headers',
                       'load_start_time', 'load_end_time', 'view_url']

    list_display = list_display_links = ['view_url', 'method', 'status_code']
    list_filter = ['method', 'response__status_code', 'response__content_type']
    search_fields = ['request_url']

    def view_url(self, obj):
        return Truncator(obj.request_url).chars(80)

    def view_page(self, obj):
        return format_html(u'<a href="%s">< Back to %s</a>' % (obj.page.get_edit_url(), obj.page))

    def status_code(self, obj):
        if obj.response:
            return obj.response.status_code

    def content_type(self, obj):
        if obj.response:
            return obj.response.content_type

    def content_length(self, obj):
        if obj.response:
            return obj.response.content_length

    def view_response(self, obj):
        return format_html(u'<a href="%s">View Response</a>' % (obj.response.get_edit_url()))


class PageRequestInline(admin.TabularInline):
    model = PageRequest
    fields = ['request_url', 'method', 'status_code', 'content_type', 'content_length', 'load_start_time', 'retain', 'view_item']
    readonly_fields = ['request_url', 'method', 'status_code', 'content_type', 'content_length', 'load_start_time', 'view_item']
    extra = 0

    def status_code(self, obj):
        if obj.response:
            return obj.response.status_code

    def content_type(self, obj):
        if obj.response:
            return obj.response.content_type

    def content_length(self, obj):
        if obj.response:
            return obj.response.content_length

    def view_item(self, obj):
        return format_html(u'<a href="%s">View Request Details +</a>' % (obj.get_edit_url()))


class PageTestResultInline(admin.TabularInline):
    model = PageTestResult
    extra = 0
    max_num = 0
    fields = readonly_fields = ['test', 'status', 'message', 'modified', 'view_test']

    def view_test(self, obj):
        return format_html(u'<a href="%s">View Test Data ></a>' % (obj.get_edit_url()))


@admin.register(PageTestResult)
class PageTestResultAdmin(admin.ModelAdmin):

    def view_page(self, obj):
        return format_html('<div title="%s">%s</div> <a href="%s" target="_blank">View Page Results ></a>' % (
            obj.page.url,
            Truncator(obj.page.url).chars(80),
            obj.page.get_edit_url()
        ))

    list_display = ['test', 'view_page', 'status', 'message', 'modified']
    fields = readonly_fields = ['test', 'view_page', 'status', 'message', 'data', 'modified']
    list_filter = ['page__site_domain__site', 'status', 'test']
    search_fields = ['page__url']


@admin.register(PageResult)
class PageResultAdmin(admin.ModelAdmin):

    list_display_links = ['view_title', 'view_url', 'last_load_start_time', 'last_time_elapsed_ms', 'last_status_code']
    list_display = ['view_site_domain_title', 'url_root', 'view_title', 'view_url', 'last_load_start_time', 'last_time_elapsed_ms', 'last_status_code', 'visit_url']
    list_filter = ['site_domain__site', 'site_domain', 'is_sitemap', 'is_root',
                   'is_internal', 'last_status_code', 'last_content_type', 'url_root',]
    readonly_fields = ['site_domain', 'view_site_domain_title', 'url', 'url_root','view_url', 'created', 'modified',
                       'title', 'last_load_start_time', 'last_load_end_time', 'last_time_elapsed_ms',
                       'last_status_code', 'last_content_type',
                       'last_content_length', 'view_site_settings',
                       'incoming_links', 'outgoing_links',
                       'view_incoming_links', 'view_outgoing_links',
                       'is_sitemap', 'is_root', 'is_internal', 'view_title',
                       'error_synopsis', 'warning_synoposis', ]
    change_form_template = 'admin/pageresult_change_form.html'
    # filter_horizontal = ['incoming_links', 'outgoing_links']
    search_fields = ['url']

    fieldsets = (
        (None, {
            'fields': (
                'view_site_settings',
                'site_domain',
                'title',
                'url',
                'url_root',
                'is_sitemap',
                'is_root',
                'is_internal',
                ('last_load_start_time', 'last_load_end_time', 'last_time_elapsed_ms'),
                ('last_status_code', 'last_content_type', 'last_content_length'),
                'error_synopsis',
                'warning_synoposis',
                'view_incoming_links',
                'view_outgoing_links',
            )
        }),
        ('Metadata', {
            'fields': (
                ('created', 'modified'),
            ),
        }),
    )

    inlines = [PageRequestInline, PageTestResultInline]
    custom_list_order_by = 'title'

    def view_site_domain_title(self, obj):
        return obj.site_domain.title

    def view_title(self, obj):
        return Truncator(obj.title).chars(80)

    def view_url(self, obj):
        return Truncator(obj.url).chars(80)

    def view_incoming_links(self, obj):
        template = Template("""<table>
        {% for link in links %}
        <td><td>{{forloop.counter}}. <a href="{{link.get_edit_url}}">{{link.url|truncatechars:80}}</td><td><a href="{{link.url}}" target="_blank">Visit ></a></td></tr>
        {% endfor %}
        </table>""")
        context = Context({"links": obj.incoming_links.all()})

        return format_html(template.render(context))

    def view_outgoing_links(self, obj):
        template = Template("""<table>
        {% for link in links %}
        <td><td>{{forloop.counter}}. <a href="{{link.get_edit_url}}">{{link.url|truncatechars:80}}</td><td><a href="{{link.url}}" target="_blank">Visit ></a></td></tr>
        {% endfor %}
        </table>""")
        context = Context({"links": obj.outgoing_links.all()})

        return format_html(template.render(context))

    def view_site_settings(self, obj):
        return format_html(u'<a href="%s">< View Settings for %s</a>' % (obj.site_domain.site.get_edit_url(), obj.site_domain.site))

    def visit_url(self, obj):
        return format_html(u'<a href="%s" target="_blank">Visit ></a>' % (obj.url))
