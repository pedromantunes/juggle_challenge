# juggle_challenge api
Juggle Challenge Django API

The current API provides the hability to:

 - List all entities listed on the website
 - Allow professional to apply for any job
 - Allow to list all applicants for any job
 - Limit to 5 applications per job per day
 - Search for jobs, professionals

Time Spent: 5h

## Considerations ##

 - All the code and scripts were only tested on Ubuntu 20.04
 - There are two ways of running the APP (virtualenv/docker). In this readme only the docker steps were considered, as it's simpler to test the API.
 - To test the API and the happy path, a smoke test file was created to show the entire flow as required
 - A basic OAuth was introduced 

## System Configuration ##

### Install Docker Compose ###

To install docker compose locally see: 
https://docs.docker.com/engine/install/ubuntu/

### Create Docker Instance ###

```
#!shell
docker-compose create
```

### Create tables in database ###

```
#!shell
docker-compose run juggle_challenge python manage.py migrate
```

### Start docker instance ###

```
#!shell
docker-compose up
```


### Access Swagger doc page ###

 All the endpoints are documented in swagger, for that, access directly: http://127.0.0.1:8000/

### Test API ###

In order to test the API, the following make command can be used under /juggle_challenge dir:

```
#!shell
make docker-smoke
```

The script will output all the endpoints called and respective payloads