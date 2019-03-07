# Pathways

## Install dependencies

Install on your local machine (Docker and psql):

```
sudo apt install docker.io docker-compose postgresql-client
```

## Running the setup

To run the app and set the passwords use (assuming a Linux computer
the following is one command):

```
POSTGRES_PASSWORD="secretpassword" \
PGADMIN_DEFAULT_EMAIL=example@example.com PGADMIN_DEFAULT_PASSWORD=example \
SQLALCHEMY_DATABASE_URI=postgresql://postgres:${POSTGRES_PASSWORD}@db/postgres \
docker-compose -f docker-compose.yml up --build
```

The `--build` ensures that the image is rebuild from the Dockerfile.

## Uploading the data

When the setup is running (i.e. after `docker-compose up`), you can
connect from your local machine using `psql`.
To do that, determine which Docker network the setup is using:

```
docker network ls
```

You should see something like:

```
d8b0289eebdc        pathways_default    bridge              local
```

Then inspect the network:

```
docker network inspect pathways_default
```

You will get JSON where you can find IP address of the database machine:

```
            ...
            "c0e2970e62a3a7c1abc23649a08b9317158e22edae84288ba02ce5b9c9ed676e": {
                "Name": "pathways_db_1",
                "EndpointID": "c230ed3e70738a699c924135719365e0d93dfde0fdb588cf27b1d74bd9188a55",
                "MacAddress": "02:42:ac:12:00:02",
                "IPv4Address": "172.18.0.2/16",
                "IPv6Address": ""
            }
```

Then you can connect load the data from a dump to the database:

```
psql -h 172.18.0.2 -U postgres -f database.sql
```

## Performing SQL queries

To just connect to the database and perform SQL queries, use the
instructions above to get to the database container IP address and then
use `psql`:

```
psql -h 172.18.0.2 -U postgres
```
