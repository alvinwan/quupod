# [Quupod](http://quupod.com)
In-session questions queue management, with a one-click Google sign in; now being used by ~3100 students across four courses - [CS61A](http://oh.cs61a.org), [CS61B](http://oh.cs61b.ug), [CS70](http://oh.eecs70.org), [DS8](http://oh.data8.org) - at UC Berkeley.

created by [Alvin Wan](http://alvinwan.com), Spring 2016

To get started, see [quupod.com](http://quupod.com).

See the [Contributors](https://github.com/alvinwan/quupod#contributors) section below for important contributors like Sumukh Sridhara, who spent many hours helping deploy and debug Quupod.

## Features

**Google login**
Login with Google, or use the built-in login/registration system.

**Live updates**
All public pages will silently poll for updates, meaning that the queue and help screens will update live, without a page refresh!

**Ease of use**
Anonymous users can submit inquiries without creating an account. (may be disabled, requiring registration)

**Concurrent Enqueue Restrictions**
Restrict the number of times users can enqueue themselves at once

**Mutex Lock**
Only one staff member can be assigned to an inquiry at a time.

**Staff Approval**
Add staff emails to the whitelist to auto-promote staff, or give staff members a link to auto-promote themselves (optionally add a codeword)

**Basic Statistics**
Queue calculates estimated time until resolution, and extra statistics are included for each active staff member.

## Preview

<img width="1280" alt="screen shot 2016-03-22 at 11 09 43 pm" src="https://cloud.githubusercontent.com/assets/2068077/13977085/343428f0-f083-11e5-86f5-c2e633403ee2.png">
<img width="1279" alt="screen shot 2016-03-22 at 11 05 17 pm" src="https://cloud.githubusercontent.com/assets/2068077/13977033/c68214d4-f082-11e5-9dfd-251ec161b022.png">
<img width="1280" alt="screen shot 2016-03-22 at 11 11 01 pm" src="https://cloud.githubusercontent.com/assets/2068077/13977115/74edc72a-f083-11e5-8423-08a9043f5ba3.png">
<img width="1280" alt="screen shot 2016-03-22 at 11 06 19 pm" src="https://cloud.githubusercontent.com/assets/2068077/13977036/c6a272b0-f082-11e5-9dbe-f300db41a624.png">
<img width="1280" alt="screen shot 2016-03-22 at 11 06 29 pm" src="https://cloud.githubusercontent.com/assets/2068077/13977034/c6a04bd4-f082-11e5-961d-1a0520d8ba67.png">


## Installation

Check that Python3 and MySQL are installed using `make check`.

1. Run the installation using `make install`.
1. Add valid mysql user credentials to `configvars.py`.
1. Create the database using `make db`.

During development, you may additionally want to remember the following:

- In the future, use `source activate.sh` to activate the virtual environment.
- Any model modifications should be followed by `make migrate`.

### Unix and Mac OSX Details

In case the installation script fails, you may execute the contents of the
installation bash script line by line:

1. Setup a new virtual environment: `python3 -m virtualenv env`.
1. Start the virtual environment: `source env/bin/activate`.
1. Install all requirements: `pip install -r requirements.txt`.
1. Make a new configuration file: `cp defaultconfigvars.py configvars.py`.
1. Add valid MySQL user credentials to `configvars.py`.
1. Create the database: `python3 run.py -db create'`.

Any model modifications should be followed by the following, which will
**delete** the old database and replace it with a new one: `python3 run.py -db refresh`

### Windows Details

Because of incompatibility issues with the makefile, on Windows you will have to manually run the installation instructions.

1. Setup a new virtual environment by calling `python -m virtualenv env`.
1. Start the virtual environment by calling `env/Scripts/activate.bat` in cmd.
1. Install all requirements `pip install -r requirements.txt`.
1. Make a new configuration file: `cp defaultconfigvars.py configvars.py`.
1. Add valid MySQL user credentials to `configvars.py`.
1. Start the MySQL service using services.msc
1. Create the database by using `mysql -u root -p`, then entering `create database queue;` in the interactive prompt.
1. Setup the database using `python3 run.py -db create`.

## Launch

Use `make run`.

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

## Contributors

- [Sumukh Sridhara](http://sumukh.me) - production deployment and hosting
- [Ben Kha](http://github.com/benkha) - Windows setup
