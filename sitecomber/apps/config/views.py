from datetime import datetime
import io

from django.conf import settings
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

import xlsxwriter


from sitecomber.apps.config.models import Site


class SiteDetailView(DetailView):

    model = Site

    def get_context_data(self, **kwargs):
        context = super(SiteDetailView, self).get_context_data(**kwargs)
        context['SETTINGS'] = settings.TEMPLATE_SETTINGS
        return context


class SiteListView(ListView):

    model = Site


class SiteTestResultView(DetailView):

    model = Site
    template_name = 'config/site_detail_tests.html'

    def get_context_data(self, **kwargs):
        context = super(SiteTestResultView, self).get_context_data(**kwargs)
        context['SETTINGS'] = settings.TEMPLATE_SETTINGS
        return context


class SiteDetailReportView(DetailView):

    model = Site

    def render_to_response(self, context, **response_kwargs):
        site = self.get_object()
        report_data = site.get_report_data()


        if self.request.GET.get('debug'):
            # For debugging page performance:
            html = "<html><body><pre>%s.</pre></body></html>" % (report_data)
            response = HttpResponse(
                html,
                content_type='text/html'
            )
            return response

        else:
            # Write data into an Excel Workbook:
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            for report_sheet in report_data:
                worksheet = workbook.add_worksheet(report_sheet['title'])
                for row_num, columns in enumerate(report_sheet['data']):
                    for col_num, cell_data in enumerate(columns):
                        worksheet.write(row_num, col_num, cell_data)

            workbook.close()
            output.seek(0)
            filename = 'site_%s_report_%s.xlsx'%(site.pk, datetime.today().strftime('%Y-%m-%d'))
            response = HttpResponse(
                output,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response
