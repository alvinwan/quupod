#!/usr/bin/python3

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/queue/queue")
sys.path.insert(0,"/var/www/queue")

from quuupod import app as application
from run import run

if __name__ == "__main__":
    run(application)
