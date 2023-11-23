# Exchange Account API Project

[![Django](https://img.shields.io/badge/Django-brightgreen.svg?logo=Django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django--Rest--Framework-brightgreen.svg?logo=DRF)](https://www.django-rest-framework.org/)
[![DRK](https://img.shields.io/badge/Django--Rest--Knox-brightgreen.svg?logo=)](https://www.django-rest-framework.org/)
[![PyOTP](https://img.shields.io/badge/PyOTP-gray.svg?logo=pyotp)](https://github.com/pyauth/pyotp)
[![Docker](https://img.shields.io/badge/Docker-blue.svg?logo=docker&logoColor=white)](https://www.docker.com/)

## Description
This project is an exchange account API created using OKX's linkprogram. Responsible for user asset management, login, and membership registration functions.
Additionally, you can retrieve the user's current position information and order execution details in real time through a socket connection.

## virtualenv(venv)

### create
```shell
$ python3 -m venv {venv-name}
~~
$ python3 -m venv venv
```
### execute
```shell
$ source venv/bin/activate

# (django-env) user@path % 
```

### start
```shell
(venv) $ python manage.py runserver
```

### venv out
```shell
deactivate
```

### Useing Libraries

```shell
# package listing
$ pip freeze > requirements.txt
# package install
$ pip install -r requirements.txt
```

## project Create
```shell
$ django-admin startproject {project_name}
```

### migrate
```shell
(venv-bash) % python manage.py makemigrations
(venv-bash) % python manage.py migrate
```

### admin create
```shell
$ python manage.py createsuperuser
```

### App Create
```shell
$ python manage.py startapp {app_name}
```

## Deploy
```shell
$ python manage.py check --deploy
```

## Docker Build
```shell
# Image Build
docker build --tag test/exchange-django:{version} .

# run
docker run -p {host}:{container} --env-file {local_env_path} {image_name}

# run example
docker run -p 8000:8000 --env-file ./.env og/exchange-api:1.0.1
```

## DEV
```shell
(venv) $ gunicorn --bind 0:8201 exchange_account_api.wsgi:application
```

## Docs

[Tutorial](https://docs.djangoproject.com/en/4.2/intro/tutorial01/)<br />
[Docs](https://docs.djangoproject.com/en/4.2/topics/)