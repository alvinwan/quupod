#!/usr/bin/env bash

echo '2 checks:'

exit=`python3 --version`
[ $? != 0 ] && echo '[Error] Python3 not found' || echo '[OK] Python3 found'

exit=`mysql --version`
[ $? != 0 ] && echo '[Error] MySQL not found' || echo '[OK] MySQL found'
