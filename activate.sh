#!/usr/bin/env bash

# check for virtualenv
[ -d "env" ] && python3 -m venv env

# activate virtualenv
source env/bin/activate

echo "---

[OK] Virtualenv activated.
"
