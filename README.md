# Queue
in-session questions queue management and analytics

## Features

**Guest**

- ease of use: *Anonymous users can submit inquiries without creating an account*
- (soon) easy inquiry creation: *Registered users only need to select an assignment and a question. All other fields are automatically filled.*

**Staff**

- data race prevention: *Staff can click the 'help' button to assign the next unresolved inquiry to him/herself. This prevents multiple staff members from trying to resolve the same inquiry.*
- mutex lock: *Once a staff member locks (or starts resolving) an inquiry, other staff members will be notified. Additionally other staff members cannot modify the same inquiry until the original staff member releases or resolves it.*
- simple user flow: *For each inquiry, staff members need only two clicks: 'help' to help and 'resolved' to resolve.*
- (soon) verified users: *Staff members need to register to gain access to the admin panel.*

**Analytics**

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
