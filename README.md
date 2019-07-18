# SiteComber
This tool crawls an entire domain (or set of domains) to create a living snapshot of a website. A worker script is constantly crawling and re-crawing to provide the most up-to-date snapshot.

With this snapshot you are able to see problems that may arise from content entry or underlying code problems. For example, you can use this tool to identify problems like broken links, spelling errors, slow load times, or SEO issues. 

A whole suite of tests are available out of the box, but you can also write your own custom tests to fit your own needs. Some examples: You could use natural language processing to make sure your language doesn't exceed a certain reading level. Or you could hook into the Google Analytics API to correlate search performance to load times. Or you could use Selenium to generate snapshots at different window sizes.

## Featured Tests

**Built-In Tests** Built into the core code is "PageUpTest," which will tell you if an internal page isn't returning a 200 status code, and "BrokenOutgoingLinkTest," which will tell you if a page contains broken outgoing links.

**[Article Content Test](https://github.com/ninapavlich/sitecomber-article-tests)** These tests provide tools for ensuring that articles are optimized for Reader View, no misspellings or placeholder text is found, and estimating article read time.

## Heroku One-Click Deployment Quickstart

### Pre-reqs for deploying this project to Heroku:
 * Create a free [Heroku account](https://signup.heroku.com/) 
 * Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/ninapavlich/sitecomber/blob/master)

When configuring the fields, be sure to take note of the App Name, as you will be using this in the next steps. 

After your application has deployed, run the following commands through the command line Heroku CLI and follow the prompts:

    > heroku run python manage.py drf_create_token <replace-with-username> --app=<replace-with-app-name>
    > heroku run python manage.py generate_encryption_key
    > heroku config:set FIELD_ENCRYPTION_KEY='<replace-with-value-from-previous-command>'
    > heroku run python manage.py migrate
    > heroku run python manage.py loaddata sitecomber/apps/config/fixtures/example_data.json --app=<replace-with-app-name>
    > heroku run python manage.py setpassword admin --app=<replace-with-app-name>
    > heroku ps:scale web=1 worker=1 --app=<replace-with-app-name>

    You may now log in and configure your sites at https://<replace-with-app-name>.herokuapp.com/admin/config/site/

## Local Development Quickstart

### Pre-Requisites:

* Python 3
* PIP
* Virtualenv

Run the following commands in your terminal:

```bash
	git clone git@bitbucket.org:ninapavlich/sitecomber.git
    cd sitecomber
```

Copy the contents of env.example into a file called .env at the root of the 
project directory. Update the SECRET_KEY value with some other random string, 
update FIELD_ENCRYPTION_KEY with a value generated from 'python manage.py generate_encryption_key'

Then run the following commands:

```bash
    virtualenv venv -p python3
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py loaddata sitecomber/apps/config/fixtures/example_data.json
    python manage.py setpassword admin
    # Follow interactive commands to reset admin password
    python manage.py runserver
```

With the local server running, you may browse the admin CMS at: 

http://localhost:8000/admin/

Log in with the credentials you provided when you ran the 'createsuperuser' command.

## SiteComber Worker

A background worker can run along side the web server to execute the crawling.

To run the worker locally, follow the "Local Development Quickstart" instructions above, and then run:

```bash
    python site_comber_worker.py
```

## Development Tools

#### Manually crawl a single page result:
```
    # Crawl page result with primary key = 1
    crawl_page 1
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
