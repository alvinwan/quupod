# [Office Hours Queue](http://ohquu.herokuapp.com)
in-session questions queue management ([demo](http://ohquu.herokuapp.com))

by [Alvin Wan](http://alvinwan.com), with contributions from [Ben Kha](http://github.com/benkha) and a huge help from [Sumukh Sridhara](http://sumukh.me) for deploying to production.

## Features

**Google login**
Login with Google, or use the built-in login/registration system.

**Live updates**
All public pages will silently poll for updates, meaning that the queue and help screens will update live, without a page refresh!

**Ease of use**
Anonymous users can submit inquiries without creating an account. (may be disabled, requiring registration)

**Mutex Lock**
Only one staff member can be assigned to an inquiry at a time.

**Staff Approval**
Add staff emails to the whitelist to auto-promote staff.

**Basic Statistics**
Queue calculates estimated time until resolution, and extra statistics are included for each active staff member.

## Preview

<img width="1278" alt="screen shot 2016-01-14 at 10 10 10 pm" src="https://cloud.githubusercontent.com/assets/2068077/12346697/a462645a-bb0b-11e5-92b8-0f718e63f9a8.png">

<img width="1278" alt="screen shot 2016-01-14 at 10 12 25 pm" src="https://cloud.githubusercontent.com/assets/2068077/12346724/e9708c84-bb0b-11e5-98da-82fef54dd018.png">

<img width="301" alt="screen shot 2016-01-14 at 10 11 03 pm" src="https://cloud.githubusercontent.com/assets/2068077/12346706/c6d38d5c-bb0b-11e5-91e2-98d724884b27.png">

<img width="301" alt="screen shot 2016-01-14 at 10 11 20 pm" src="https://cloud.githubusercontent.com/assets/2068077/12346708/c8756ce8-bb0b-11e5-8afd-c716064f6578.png">


## Installation

> These instructions assume the mySQL server has been started. See MySQL below.

### Dependencies

Check that Python3 and MySQL are installed using `make check`.

### Getting Started

1. Run the installation using `make install`.
1. Add valid mysql user credentials to `config.cfg`.
1. Create the database using `make db`.

> If the bash scripts do not work, see the Details section below for an outline
of what each script does.

During development, you may additionally want to remember the following:

- In the future, use `source activate.sh` to activate the virtual environment.
- Any model modifications should be followed by `make migrate`.

### Unix and Mac OSX Details

In case the installation script fails, you may execute the contents of the
installation bash script line by line:

1. Setup a new virtual environment: `python3 -m virtualenv env`.
1. Start the virtual environment: `source env/bin/activate`.
1. Install all requirements: `pip install -r requirements.txt`.
1. Make a new configuration file: `cp default-config.cfg config.cfg`.
1. Add valid MySQL user credentials to `queue.cfg`.
1. Create the database: `python3 run.py -db create'`.

Any model modifications should be followed by the following, which will
**delete** the old database and replace it with a new one: `python3 run.py -db refresh`

### Windows Details

Because of incompatbility issues with the makefile, on Windows you will have to manually run the installation instructions.

1. Setup a new virtual environment by calling `python -m virtualenv env`.
1. Start the virtual environment by calling `env/Scripts/activate.bat` in cmd.
1. Install all requirements `pip install -r requirements.txt`.
1. Make a new configuration file: `cp default-config.cfg config.cfg`.
1. Add valid MySQL user credentials to `config.cfg`.
1. Start the MySQL service using services.msc
1. Create the database by using `mysql -u root -p`, then entering `create database queue;` in the interactive prompt.
1. Setup the database using `python3 run.py -db create`.

## Launch

Use `make run`.

> If the bash script does not work, see the Details section below for an outline
of `make run`.

### Unix and Mac OSX Details

1. Start the virtual environment: `source env/bin/activate`.
1. Launch server: `python3 run.py`.

### Windows Details

1. Start the virtual environment by calling `env/Scripts/activate.bat` in cmd.
1. Launch server: `python run.py`.

## MySQL

- For Mac OSX installations of MySQL, via Brew, start the server using
`mysql.server start`. For other Linux-based operating systems, use
`sudo service mysql start`.
- For Windows, just start the server using `services.msc`.
