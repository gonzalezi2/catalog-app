# Item Catalog
The item catalog is a full-stack CRUD app that uses flask and python for backend server logic and html rendering.
It allows for multiple users to each manage data in two tables in the database: categories and items. Each user has
the ability to add both but each are limited to modifying only those items that belong to them.

Authorization and authentication is handled using Google's Oauth2 log in service which ties into a local permission
system for data manipulation.

--

## Setting up your environment
There are a few applications and tools we will need in order to run this application properly

**Requirements**: Python 3, VirtualBox, Vagrant, terminal application

### Using a terminal
If you are using a linux or Mac system, you can use your OS' terminal application.

If you are a windows users, you can install Git Bash terminal from [here](https://git-scm.com/downloads).

### Install Python 3
This project requires Python 3 to run the code. You can install it [here under Download](https://www.python.org/download/releases/3.0/#download). You can also follow the ["Installing Python"](https://docs.python.org/3.0/using/windows.html#installing-python) guide.

### Install VirtualBox
In order to simulate running a database from a separate server, you need to install a linux subsystem on your
machine. You can do this with virtualbox which creates this subsystem through a virtual machine.

You can install VirtualBox from the downloads page [here](https://www.virtualbox.org/wiki/Downloads). From here
you can navigate to the downloads page relevant to your platform.

You'll only need to download and install VirtualBox; Vagrant will do the rest!

### Install Vagrant
"Vagrant is a tool for building and managing virtual machine environments"[1] and will let us create
the environment inside our VirtualBox VM to run our database using PostgreSQL.

You can find the download files based on your platform [here](https://www.vagrantup.com/downloads.html).

[1]:https://www.vagrantup.com/intro/index.html

### Downloading the virtual machine configuration file
Download the virtual machine configuration file. [Download](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip). Unzip this directory somewhere you want to run the virtual machine from.

### Run Vagrant
Once you unzip the directory onto your system, navigate to the Vagrant folder and open a terminal window. Here you
can run the `vagrant up` command to set up and start the vagrant environment in the VirtualBox VM. This will
take a few minutes to set up. After you see your terminal prompt again, run `vagrant ssh` to connect to the vagrant
environment you just set up.

### Set up the newsdata database
Download the newsdata sql file. [Download](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip). Unzip this file inside the vagrant directory you set up before. In your terminal, navigate to the vagrant directory and run the `psql -d news -f newsdata.sql` command. This is a PostgreSQL command that will connect to the "news" database you created through the
`vagrant up` command before and then populate the database with all of the newsdata tables and their corresponding
data.

*If you want to learn more about PostgreSQL and how to use it, you will find documentaion [here](https://www.postgresql.org/docs/manuals/).*

--

## Running the code

### Run the python script
Inside of the vagrant VM, you can run the application using the `python application.py` command. This will instantiate
a server that will handle all the backend logic and server-side rendering of pages, all through flask.

This command will output the uri and port where the application is running. Simple type this address into your browser
address bar to begin. In order to perform any data manipulation, you will need a Google account to sign in.