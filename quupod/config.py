"""Temporary configuration file.

TODO: Replace with a configuration file that Flask can digest.
"""

from urllib.parse import urlparse
import os

try:
    from configvars import ConfigVars
except ImportError:
    from sampleconfigvars import ConfigVars

    # TODO: Clean up this mess
    database_url = os.environ.get(
        'DATABASE_URL',
        'mysql://root:root@localhost/queue')
    url = urlparse(database_url)
    ConfigVars.username = url.username
    ConfigVars.password = url.password
    ConfigVars.host = url.hostname
    ConfigVars.port = url.port
    ConfigVars.database = database_url.split('/')[3].split('?')[0]
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
        'tz'):
    config[attr] = os.environ.get(attr.upper(), getattr(ConfigVars, attr))
