from sitecomber.apps.shared.interfaces import BaseSiteTest


class BrokenLinkTest(BaseSiteTest):

    def on_page_parsed(self, page):

        from sitecomber.apps.results.models import PageTestResult

        if page.latest_request and page.latest_request.response:
            status_code = page.latest_request.response.status_code

            print(self.class_path)
            status = PageTestResult.STATUS_SUCCESS if status_code == 200 else PageTestResult.STATUS_ERROR
            message = 'Okay'

            r, created = PageTestResult.objects.get_or_create(
                page=page,
                test=self,
                defaults={
                    'data': status_code,
                    'message': message,
                    'status': status,
                }
            )

            print(r)
        pass
