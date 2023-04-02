# Filmoteque REST API 
An application for managing the movie collection using Flask to build a REST API Server with Swagger documentation.

Main libraries used:

* Flask-RESTX
* Flask-SQLAlchemy
* Flask-Login
* Gunicorn

## Installation
### Git Clone 
```git clone https://github.com/virginia-wolfi/filmoteque.git```

Install with pipenv:

```
$ pipenv install --dev

```
Install with pip:
```
$ pip install -r requirements.txt
```


## Flask Configuration
```
#api/filmoteque/config.py


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://postgres:password@localhost/film_collection" #create database in Postgres and insert your database URI for development config
    )


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://postgres:password@localhost/film_collection_test" #create database in Postgres and insert your database URI for testing config
    )
    TESTING = True
```
api/.env contains environment variables 
## Preparations

Run following commands from api/ to fill the database:
```
$ flask commands create_db
$ flask commands insert_db
```

## Run Flask
from /api:
```
$ flask run
```
In flask, Default port is `5000`

Swagger document page:  `http://127.0.0.1:5000/api/`

** Run with gunicorn **

from api/

```
$ gunicorn -w 4 'filmoteque:create_app()'
```

* -w : number of worker

** Configure Nginx to proxy application **

Remove or comment out any existing server section in nginx.conf. Add a server section and use the proxy_pass directive to point to the address the WSGI server is listening on. We’ll assume the WSGI server is listening locally at http://127.0.0.1:8000.
```
server {
    listen 80;
    server_name your_host-ip; #replace this with your host-ip

    location / {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Prefix /;
    }
}
```
Now, after running command 
```
$ gunicorn -w 4 'filmoteque:create_app()'
```
page will be also available at `http://your_host-ip/api/` and requests will be proxied through Nginx.

### Run with Docker
from project root:
```
$ docker compose -f docker-compose.yaml build

$ docker compose up
```
access to document page:
`http://your_host-ip_or_localhost:8080/api/`

access to pgAdmin:
`http://your_host-ip_or_localhost:8080/pg/`

## Pytest
from project root:
```
$ pytest -s
```
 
