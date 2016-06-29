from urllib.parse import urlparse
import os

try:
    from configvars import ConfigVars
except ImportError:
    raise UserWarning('Configuration file not found. Rerun `make install` and \
update the new configvars.py accordingly.')

__all__ = ['config']

# Extract information from environment.
get = lambda v, default: os.environ.get(v, default)

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
    'domain',
    'timezone'):
    config[attr] = get(attr, getattr(ConfigVars, attr))
