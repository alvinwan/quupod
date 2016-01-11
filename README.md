# Queue
CS70 tutoring queue

## Installation

> These instructions assume the mySQL server has been started. See MySQL below.

**Dependencies**

Check that Python3 and MySQL are installed using `make check`.

**Getting Started**

1. Run the installation using `make install`.
2. Add valid mysql user credentials to `queue.cfg`.
3. Migrate the database using `make db`.

**Details**

In case the installation script fails, you may execute the contents of the bash script line by line:

1. Setup a new virtual environment: `python3 -m virtualenv env`.
1. Start the virtual environment: `source env/bin/activate`.
1. Install all requirements `pip install -r requirements.txt`.

> To activate the virtual environment for the future, use `source activate.sh`.

## Launch

> These instructions assume the mySQL server has been started. See MySQL below.

Use `make run`.

## MySQL

For Mac OSX installations of MySQL, via Brew, start the server using
`mysql.server start`. For other Linux-based operating systems, use
`sudo service mysql start`.
