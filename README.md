# Queue
CS70 tutoring queue

## Installation

**Dependencies**

Check that Python3 and MySQL are installed using `make check`.

**Getting Started**

Run the installation using `make install`. Then, add valid mysql user
credentials to `queue.cfg`.

In case the installation script fails, you may execute the contents of the bash script line by line:

1. Setup a new virtual environment: `python3 -m virtualenv env`.
1. Start the virtual environment: `source env/bin/activate`.
1. Install all requirements `pip install -r requirements.txt`.

> To activate the virtual environment for the future, use `source activate.sh`.

## Launch

To launch the app, start your mysql server. Then, use `make run`.

> For Mac OSX installations of MySQL, via Brew, start the server using
`mysql.server start`.
