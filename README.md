# Sitecomber
Website crawling and testing platform

## Heroku One-Click Deployment Quickstart

### Pre-reqs for deploying this project to Heroku:
 * Create a free [Heroku account](https://signup.heroku.com/) 
 * Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/ninapavlich/sitecomber/blob/master)

When configuring the fields, be sure to take note of the App Name, as you will be using this in the next steps. 

After your application has deployed, run the following commands through the command line Heroku CLI and follow the prompts:

    > heroku run python manage.py createsuperuser --app=<replace-with-app-name>
    > heroku run python manage.py drf_create_token <replace-with-username> --app=<replace-with-app-name>
    > heroku run python manage.py generate_encryption_key
    > heroku config:set FIELD_ENCRYPTION_KEY='<replace-with-value-from-previous-command>'
    > heroku ps:scale web=1 --app=<replace-with-app-name>

## Manual Heroku Configuration:
    
    > heroku create
    > heroku addons:create heroku-postgresql:hobby-dev
    > heroku config:set ENVIRONMENT='heroku' AWS_ACCESS_KEY_ID='REPLACEME' AWS_SECRET_ACCESS_KEY='REPLACEME' AWS_STORAGE_BUCKET_NAME='REPLACEME' SECRET_KEY='REPLACEME' APP_HOST_NAME='my-heroku-app-name.herokuapp.com'
    > heroku run python manage.py generate_encryption_key
    > heroku config:set FIELD_ENCRYPTION_KEY='<replace-with-value-from-previous-command>'
    > git push heroku master

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
    python manage.py createsuperuser
    # Follow interactive commands to create a super user
    python manage.py loaddata sitecomber/post/fixtures/example_data.json
    python manage.py runserver
```

With the local server running, you may browse the admin CMS at: 

http://localhost:8000/admin/

Log in with the credentials you provided when you ran the 'createsuperuser' command.

## SiteComber Worker

A background worker can run along side the web server to execute the crawling.

To run the server locally, follow the "Local Development Quickstart" instructions above, and then run:

```bash
    python site_comber_worker.py
```

## Development Tools

#### Manually crawl a batch of URLs within a site:
```
    # Crawl 5 URLs on the Site with primary key = 1
    python manage.py crawl_site 1 5  
```

#### Update Example Data Fixture
```
    python manage.py dumpdata config --natural-foreign --indent=4 > sitecomber/apps/config/fixtures/example_data.json
```
