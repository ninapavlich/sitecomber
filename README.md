# Sitecomber
Website crawling and testing platform

## One-click Heroku Deployment Quickstart

...TODO...

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
project directory. Update the SECRET_KEY value with some other random string.

Then run the following commands

```bash
    virtualenv venv -p python3
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py loaddata sitecomber/post/fixtures/example_data.json
    python manage.py runserver
    python manage.py createsuperuser
```

With the local server running, you may browse the admin CMS at:

http://localhost:9999/admin/
Username: admin
Password: admin



### Development Tools

#### Update Example Data Fixture
```
    python manage.py dumpdata config --natural-foreign --indent=4 > sitecomber/apps/config/fixtures/example_data.json
```
