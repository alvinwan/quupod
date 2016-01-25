from urllib.parse import urlparse
import os

# Extract information from environment.
get = lambda v, default: os.environ.get(v, default)

database_url = get('DATABASE_URL', 'mysql://root:root@localhost/queue')
url = urlparse(database_url)
config = {
    'NAME': url.path[1:],
    'USERNAME': url.username,
    'PASSWORD': url.password,
    'HOST': url.hostname,
    'PORT': url.port,
    'DATABASE': database_url.split('/')[3].split('?')[0],
    'SECRET_KEY': get('SECRET_KEY', 'dEf@u1t$eCRE+KEY'),
    'DEBUG': get('DEBUG', 'False'),
    'WHITELIST': get('WHITELIST', ''),
    'GOOGLECLIENTID': get('GOOGLECLIENTID', None),
    'ALLOWED_NETLOCS': get('ALLOWED_NETLOCS', 'ohquu.herokuapp.com')
}
try:
    lines = filter(bool, open('config.cfg').read().splitlines())
    for k, v in (map(lambda s: s.strip(), d.split(':')) for d in lines):
        if v:
            config[k.upper()] = v
except FileNotFoundError:
    print(' * Configuration file not found. Rerun `make install` and \
update the new config.cfg accordingly.')
    if not (config['HOST'] and config['USERNAME'] and config['DATABASE']):
        raise UserWarning('Environment variables do not supply database \
credentials, and configuration file is missing.')
except KeyError:
    raise UserWarning('config.cfg is missing critical information that is not \
found in the environment. All of the following must be present: username, \
password, server, database, secret_key, debug')

secret_key = config['SECRET_KEY']
debug = config['DEBUG'].lower() == 'true'
whitelist = config['WHITELIST'].split(',')
googleclientID = config['GOOGLECLIENTID']
