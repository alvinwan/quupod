#!/usr/bin/env bash

# check for virtualenv
[ -d "env" ] && python3 -m venv env

# activate virtualenv
source env/bin/activate

echo "
You are now in the virtualenv. Note the (env) prefix before your command prompt:
- To exit, CTRL+C or 'deactivate'.
- To re-enter the virtual environment, 'source activate.sh'.
"
