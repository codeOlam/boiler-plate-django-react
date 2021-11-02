![Django Logo](/src/django-banner.jpg)

## About

Django is a web-framework written in Python and runs the backend for many of the internet's most popular websites. This is a multi-user type auth app, it is built ontop of Django 3.2.8 and Django Rest Framework 3.12.4

This app features the following:

-- BaseUserManager and AbstractUser for custom user authentication

-- Authentication Backend configured to authenticate users, using email and password

-- Allow you to CreateUser Type e.g: Teacher or Student at signup

-- Signup With Email Verification Token

-- Login

-- Very basic profile dashboard

-- simple permission to restrict unauthenticate users and unauthorized access

## Technology and Requirements

1. Django==3.2.8
2. Python3
3. djangorestframework==3.12.4

## Installations

1. [installing Python3](https://www.python.org/downloads/)
2. [installing Django 3.0](https://docs.djangoproject.com/en/3.0/topics/install/)
3. [installing Virtualenv](https://www.geeksforgeeks.org/creating-python-virtual-environment-windows-linux/)
4. installing requirements from requirements.txt. After activating vitualenv run:

`(venv)path/to/app/src$ pip install -r requirements.txt `

6. [psycopg2](http://initd.org/psycopg/docs/install.html)
7. set up an env file with:

`SECRET_KEY={your secret key value} `

## Run App

1. After cloning this repo, make sure your virtualenv is ativated and change your path to $app root/.

`(venv)path/to/app$`

2. install packages required by running
   `(venv)path/to/app$ pip install -r requirements.txt `

3. change director to src/ make sure you are in the same directory where manage.py is then run

`(venv)path/to/app/src$ python manage.py makemigrations `

4. The migrate the app
   `(venv)path/to/app/src$ python manage.py migrate `

5. To run the development server
   `(venv)path/to/app/src$ python manage.py runserver `

6. go to your web browser and enter 127.0.0.1:8000

## Recommendations

This App is not designed to be used full in deployement. You are free to make any adjustments to it and include in you project

## Resources

1. [Django 3.x Doc](https://docs.djangoproject.com/en/3.2/)
2. [My Previous Repo](https://github.com/codeOlam/dj-multi-user-auth)

### Other Resources

1. [Customizing authentication in Django](https://docs.djangoproject.com/en/3.2/topics/auth/customizing/)
