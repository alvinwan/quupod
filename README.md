# Queue
in-session questions queue management and analytics

## Features

**Guest**

- ease of use: *Anonymous users can submit inquiries without creating an account*
- easy inquiry creation: *Registered users only need to select an assignment and a question. All other fields are automatically filled.*

**Staff**

- data race prevention: *Staff can click the 'help' button to assign the next unresolved inquiry to him/herself. This prevents multiple staff members from trying to resolve the same inquiry.*
- mutex lock: *Once a staff member locks (or starts resolving) an inquiry, other staff members will be notified. Additionally other staff members cannot modify the same inquiry until the original staff member releases or resolves it.*
- simple user flow: *For each inquiry, staff members need only two clicks: 'help' to help and 'resolved' to resolve.*
- verified users: *Staff members need to register to gain access to the admin panel.*
- whitelist: *In your configuration file, add a comma-separated list of emails
to the whitelist parameter. Users registering with those emails will
automatically be granted staff status.*

**Analytics**

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

### Details

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

## Launch

> These instructions assume the mySQL server has been started. See MySQL below.

Use `make run`.

> If the bash script does not work, see the Details section below for an outline
of `make run`.

### Details

1. Start the virtual environment: `source env/bin/activate`.
1. Launch server: `python3 run.py`.

## MySQL

For Mac OSX installations of MySQL, via Brew, start the server using
`mysql.server start`. For other Linux-based operating systems, use
`sudo service mysql start`. For Windows, just start the server using `services.msc`.


## Windows Notes
Because of incompatbility issues with the makefile, on Windows you will have to manually run the installation instructions.
1. Setup a new virtual environment by calling `python3 -m virtualenv env`.
1. Start the virtual environment by calling `env/Scripts/activate.bat` in cmd.
1. Install all requirements `pip install -r requirements.txt`.
1. Make a new configuration file: `cp default-queue.cfg queue.cfg`.
1. Add valid MySQL user credentials to `queue.cfg`.
1. Create the database: 
 ```
python3 -i
from queue import db
db.drop_all()
db.create_all()
```

1. Run with `python run.py`
