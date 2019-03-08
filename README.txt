# Item Catalog
The item catalog is a full-stack CRUD app that uses flask and python for backend server logic and html rendering.
It allows for multiple users to each manage data in two tables in the database: categories and items. Each user has
the ability to add both but each are limited to modifying only those items that belong to them.

Authorization and authentication is handled using Google's Oauth2 log in service which ties into a local permission
system for data manipulation.

--

## Connecting to the server using SSH

The serve requires RSA authentication to connect through SSH. The information to connect is located below:
*Server IP Address*: 3.18.80.16
*SSH Port*: 2200

## Accessing the Application
You can find the running application by navigating to http://www.somecatalog.tk/

## Installed Software & other configuration

### Apache Web Server
In order to serve up the python application from the server, I configured port 80 to allow connections
to the server and then installed apache and configured it to listen to connections on that port. I also had
to configure apache to serve up the python application using the mod_wsgi package.

### Virtual Environment
In order to keep the python modules for this application separate from other python applications
I resorted to using a virtual environment (venv). I installed venv inside the application
directory `/var/www/catalog/venv/`

### Database
The original application used sqllite as a database but for this project I switched to postgres. Installation
was straightforward and connection made easy with sqlalchemy which was already set up. All I had to do was change
the connection to using a postgres connection string instead of the sqllite connection setup previously.

### Other requirements
The rest of the requirements came from the python application itself by generating a `requirements.txt` file using the
`pip freeze requirements.txt` command to get the needed packages from the application and the installing them using the
`pip install -r requirements.txt` command.