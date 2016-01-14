# [Office Hours Queue](http://ohquu.herokuapp.com)
in-session questions queue management ([demo](http://ohquu.herokuapp.com))

## Features

**Guest**

- ease of use: *Anonymous users can submit inquiries without creating an account*

**Staff**

- mutex lock: *Once a staff member starts resolving an inquiry, other staff members will not be able to modify the inquiry until it has been released or resolved.*
- verified users: *Add staff emails to the whitelist, to auto-promote staff members upon registration or login.*
- configurability: *Add inquiry types, restrict assignments per inquiry, specify locations and more.*

**Analytics**

- helpful statistics: *Queue calculates estimated time until resolution, and extra statistics are included for each active staff member.*

## Preview

<img width="1276" alt="screen shot 2016-01-14 at 1 43 15 am" src="https://cloud.githubusercontent.com/assets/2068077/12320929/3febef6a-ba60-11e5-9e4a-77d3b4678b56.png">

<img width="1273" alt="screen shot 2016-01-14 at 1 45 03 am" src="https://cloud.githubusercontent.com/assets/2068077/12320973/7f262aec-ba60-11e5-8cbc-c09be036967b.png">

## Installation

> These instructions assume the mySQL server has been started. See MySQL below.

### Dependencies

Check that Python3 and MySQL are installed using `make check`.

### Getting Started

1. Run the installation using `make install`.
1. Add valid mysql user credentials to `queue.cfg`.
1. Create the database using `make db`.
1. In the future, use `source activate.sh` to activate the virtual environment.
1. Any model modifications, in the **development** environment, should be
followed by `make refresh`, which will **delete** the old database and replace
it with a new one.

> If the bash scripts do not work, see the Details section below for an outline
of what each script does.

### Unix and Mac OSX Details

In case the installation script fails, you may execute the contents of the
installation bash script line by line:

1. Setup a new virtual environment: `python3 -m virtualenv env`.
1. Start the virtual environment: `source env/bin/activate`.
1. Install all requirements: `pip install -r requirements.txt`.
1. Make a new configuration file: `cp default-queue.cfg queue.cfg`.
1. Add valid MySQL user credentials to `queue.cfg`.
1. Create the database: `python3 -c 'from queue import db; db.create_all()'`.

Any model modifications should be followed by the following, which will
**delete** the old database and replace it with a new one.

```
python3 -c 'from queue import db; db.drop_all(); db.create_all()'
```

### Windows Details

Because of incompatbility issues with the makefile, on Windows you will have to manually run the installation instructions.

1. Setup a new virtual environment by calling `python -m virtualenv env`.
1. Start the virtual environment by calling `env/Scripts/activate.bat` in cmd.
1. Install all requirements `pip install -r requirements.txt`.
1. Make a new configuration file: `cp default-config.cfg config.cfg`.
1. Add valid MySQL user credentials to `config.cfg`.
1. Start the MySQL service using services.msc
1. Create the database by using `mysql -u root -p`, then entering `create database queue;` in the interactive prompt.
1. Setup the database; enter the python interactive shell `python -i`. Then, do the following: 
```
>>> from queue import db
>>> db.drop_all()
>>> db.create_all()
>>> from default_settings import load_settings
>>> load_settings()
```

## Launch

> These instructions assume the mySQL server has been started. See MySQL below.

Use `make run`.

> If the bash script does not work, see the Details section below for an outline
of `make run`.

### Details

1. Start the virtual environment: `source env/bin/activate`.
1. Launch server: `python3 run.py`.

## MySQL

- For Mac OSX installations of MySQL, via Brew, start the server using
`mysql.server start`. For other Linux-based operating systems, use
`sudo service mysql start`. 
- For Windows, just start the server using `services.msc`.

