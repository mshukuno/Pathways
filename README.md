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

## Running web dashboard

Restart the containers (for the first time database is empty) and go to http://localhost:8050/

<br>
<br>


## Windows 10 Installation

### 1. Modify docker-compose-win10.yml

Replace **{source file}** with a your *database.sql* file path
```
  db:
    image: postgres
    restart: always
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
        - {source file}:/docker-entrypoint-initdb.d/database.sql
```
example: 
```
C:/Users/mshukun/Desktop/database.sql:/docker-entrypoint-initdb.d/database.sql
```
Note:
You can set folder to volume instead of file such as: 
```
C:/Users/mshukun/Desktop/data:/docker-entrypoint-initdb.d/
```
In this case, all file contents in the **data** folder will be copied in *docker-entrypoint-initdb.d* folder, but sql file will not be loaded into database. You will need to load the data after successfuly build Docker containers.
```
docker exec -it pathways-visualization-tool_db_1 bash
```
```
psql -U postgres -f /docker-entrypoint-initdb.d/pathways.sql
``` 

<br>

### 2. Modify .env file

The .env file in the same directory as .yml files sets environment variables.  The content of curent .env file is example. Note that you only need to replace **seacretpassword** for *SQLALCHEMY_DATABASE_URI*. It should be the same as *POSTGRES_PASSWORD*.

```
POSTGRES_PASSWORD=secretpassword
PGADMIN_DEFAULT_EMAIL=example@example.com
PGADMIN_DEFAULT_PASSWORD=example
SQLALCHEMY_DATABASE_URI=postgresql://postgres:secretpassword@db/postgres
```

<br>

### 3. Run docker-compose-win10.yml file
Open CMD or Powershell
```
cd <path to >/pathwyas-visualization-tool
```
```
docker-compose -f docker-compose-win10.yml up --build
```
You will see something like below after successful run.
```
Successfully built 04e25c98d625
Successfully tagged pathways-visualization-tool_dash:latest
Creating pathways-visualization-tool_pgadmin_1 ... done
Creating pathways-visualization-tool_adminer_1 ... done
Creating pathways-visualization-tool_db_1      ... done
Creating pathways-visualization-tool_dash_1    ... done
```

<br>

### 4. Open Dash application
Go to http://localhost:8050/

<br>


### Little More...


#### Checking network
```
docker network ls
```
You will see something like:
```
1aa0d4fa2c31        pathways-visualization-tool_default   bridge              local
```
Then inspect the network:
```
docker network inspect pathways-visualization-tool_default
```
You see four containers in "*Containers*" JSON variable with the name listed below.
- pathways-visualization-tool_adminer_1
- pathways-visualization-tool_pgadmin_1
- pathways-visualization-tool_db_1
- pathways-visualization-tool_dash_1

<br>

#### Conecting PostgreSQL database in pgAdmin
1. Open the browser and go to http://localhost:8000/
2. It will open pgAdmin4 login page.  Enter email address and password you used in .env file.
3. Now, you will add a new server in pgAdmin which connect to **pathways-visualization-tool_db_1** that we just created.

        * Click Add New Server and name the server.  You can name whatever you want here.
        * Click Connection tab
                - Host name/address: pathways-visualization-tool_db_1
                - Port: 5432
                - Maintenance database: postgres
                - Username: postgres
                - Password: <Use POSTGRES_PASSWORD in your .env file>
        * Click Save. You will see a new server just you created in the left pane.
4. In the left pane, click Database > Schemas > Tables.  You should see tables created from database.sql file.

<br>

#### Query without pgAdmin
You will need to get into container
```
docker exec -it pathways-visualization-tool_db_1 bash
```
```
psql -U postgres
``` 
To quit PostgreSQL
```
\q
```
To quit bash
``` 
exit
```

#### Run Dash application on your local machine

It seems Windows doesn't know the IvP address of Postgresql DB.  There might have other solutions, but I was successful by using steps below.

1. Add 'ports: 5432:5432' in docker-compose-win10.yml.
2. Create .env file in the same directory as run.py.
3. Add a line below and change your password for database and save.
```
SQLALCHEMY_DATABASE_URI="postgresql://postgres:<your_password>@localhost:5432/postgres"
```
4. Run docker-compose:
```
docker-compose -f docker-compose-win10.yml up --build
```
5. Stop container that runs Dash application.
```
docker stop pathways-visualization-tool_dash_1
```
7. Activate your local python virtual environment and run:
```
python run.py
```
6. Go to http://localhost:8050/
