"""Temporary configuration file.

TODO: Replace with a configuration file that Flask can digest.
"""

import os

try:
    from configvars import ConfigVars
except ImportError:
    from sampleconfigvars import ConfigVars
    print(
        'Configuration file not found. Rerun `make install` and update the new'
        'configvars.py accordingly OR make sure your environment variables are'
        'correct.')

__all__ = ['config']

# Setup configuration dictionary, and check for environment variables.
config = {}
for attr in (
        'username',
        'password',
        'host',
        'port',
        'database',
        'secret_key',
        'debug',
        'googleclientID',
        'allowed_netlocs',
        'app_port',
        'domain',
        'timezone'):
    config[attr] = os.environ.get(attr.uppercase(), getattr(ConfigVars, attr))
