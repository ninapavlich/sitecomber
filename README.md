# SiteComber

This tool crawls an entire domain (or set of domains) to create a living snapshot of a website. A worker script is constantly crawling and re-crawing to provide the most up-to-date snapshot.

With this snapshot you are able to see problems that may arise from content entry or underlying code problems. For example, you can use this tool to identify problems like broken links, spelling errors, slow load times, or SEO issues.

A whole suite of tests are available out of the box, but you can also write your own custom tests to fit your own needs. Some examples: You could use natural language processing to make sure your language doesn't exceed a certain reading level. Or you could hook into the Google Analytics API to correlate search performance to load times. Or you could use Selenium to generate snapshots at different window sizes... really anything you can code.

[See a live demo of SiteComber](https://sitecomber-ninalp.herokuapp.com/1/)

## Featured Tests

**Built-In Tests** Built into the core code is "PageUpTest," which will tell you if an internal page isn't returning a 200 status code, and "BrokenOutgoingLinkTest," which will tell you if a page contains broken outgoing links.

**[Article Content Test](https://github.com/ninapavlich/sitecomber-article-tests)** These tests provide tools for ensuring that articles are optimized for Reader View, no misspellings or placeholder text is found, and estimating article read time.

## Heroku One-Click Deployment Quickstart

### Pre-reqs for deploying this project to Heroku:

- Create a free [Heroku account](https://signup.heroku.com/)
- Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/ninapavlich/sitecomber/blob/master)

When configuring the fields, be sure to take note of the App Name, as you will be using this in the next steps.

After your application has deployed, run the following commands through the command line Heroku CLI and follow the prompts:

    > heroku ps:scale web=1 worker=1 --app=<replace-with-app-name>

Once deployed, you can configure the crawling settings by going here: https://<replace-with-app-name>.herokuapp.com/admin/

The default admin username is 'admin' and the default admin password is 'sitecomber'. You can update the password by going here: https://<replace-with-app-name>.herokuapp.com/admin/auth/user/1/password/

Note that if you are parsing a large site, you will probably need to upgrade your database instance in the Heroku admin panel. The free database allows for up to 10000 rows.

## Local Development Quickstart

### Pre-Requisites:

- Python 3
- PIP
- Virtualenv
- Postgres (To use a different database backend, you can comment 'psycopg2' out in the requirements.txt)

Run the following commands in your terminal:

```bash
  git clone git@bitbucket.org:ninapavlich/sitecomber.git
  cd sitecomber
```

Copy the contents of env.example into a file called .env at the root of the
project directory. Update the SECRET_KEY value with some other random string.'

Then run the following commands:

```bash
    virtualenv venv -p python3
    source venv/bin/activate
    pip install -r requirements.txt
    python download_nltk_libs.py
    python manage.py migrate
    python manage.py loaddata sitecomber/apps/config/fixtures/example_data.json
    python manage.py setpassword admin
    # Follow interactive commands to reset admin password
    python manage.py runserver
```

With the local server running, you may browse the admin CMS at:

http://localhost:8000/admin/

Log in with the credentials you provided when you ran the 'createsuperuser' command.

To bootstrap the frontend for development:

```bash
    cd frontend
    npm install
    npm run watch
```

You can see a local server running at:

http://localhost:8000/

## SiteComber Worker

A background worker can run along side the web server to execute the crawling.

To run the worker locally, follow the "Local Development Quickstart" instructions above, and then run:

```bash
    python site_comber_worker.py
```

To adjust how fast the worker crawls, adjust the WORKER_LOOP_DELAY_SECONDS value in the .env

## Development Tools

#### Manually re-run tests after a configuration change:

```
    # Re-run tests on site with primary key = 1
    python manage.py rerun_tests 1
```

#### Manually crawl a single page result:

```
    # Crawl page result with primary key = 1
    python manage.py crawl_page 1
```

#### Manually crawl a batch of URLs within a site:

```
    # Crawl 5 URLs on the Site with primary key = 1
    python manage.py crawl_site 1 5
```

#### Update Example Data Fixture

```
    python manage.py dumpdata auth.user config --natural-foreign --indent=4 > sitecomber/apps/config/fixtures/example_data.json
```

## Create a Custom Test

1. Create the Test

```python
    # example_test.py 
    
    from sitecomber.apps.shared.interfaces import BaseSiteTest

    class ExamplePageTest(BaseSiteTest):

        def on_sitemap_parsed(self, sitemap_item):
            """
            sitemap_item is an instance of an AbstractIndexSitemap,
            see https://ultimate-sitemap-parser.readthedocs.io/en/latest/usp.objects.html#module-usp.objects.sitemap
            for source
            """
            print(u"Parsed sitemap %s"%(sitemap_item.url))
            
          
        def on_page_parsed(self, page):
            from sitecomber.apps.results.models import PageTestResult

            if page.latest_request and page.latest_request.response:

                status_code = page.latest_request.response.status_code
                status = PageTestResult.STATUS_SUCCESS if status_code == 200 else PageTestResult.STATUS_ERROR
                message = '%s status code: %s' % (page.url, status_code)

                r, created = PageTestResult.objects.get_or_create(
                    page=page,
                    test=self.class_path
                )
                r.data = status_code
                r.message = message
                r.status = status
                r.save()
            
```

2. Save Test File

Either place this in the sitecomber source code, in sitecomber/apps/tests/example_test.py or save this in an external repository and make it an installable application with PyPi. 

See [sitecomber-article-tests](https://github.com/ninapavlich/sitecomber-article-tests) to see an example set of custom installable tests.

3. Restart the Server

When the server restarts, it will re-register any classes that are subclasses of sitecomber.apps.shared.interfaces.BaseSiteTest

You can verify that your new test was found by running:
```
  python manage.py list_available_tests
```

4. Add Test to Site

Go into the site admin at /admin/config/site/, select your site, scroll down to the "Site test settings" section and add a row for this new test.

5. Re-run Tests

In order to re-apply the new tests to your existing site, run the following command, passing in the primary key of your site:

```
  # Re-run tests on site with primary key = 1
  python manage.py rerun_tests 1
```

