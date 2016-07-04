"""Configuration file containing per-mode settings."""

import os


class Config(object):
    """General configuration settings."""

    DATABASE_URL = os.environ.get(
        'DATABASE_URL',
        'mysql://cs70:cs70r0ck$@localhost/queue')
    DOMAIN = os.environ.get('DOMAIN', 'http://localhost:5000')
    GOOGLECLIENTID = os.environ.get('GOOGLECLIENTID', '')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dEf@u1t$eCRE+KEY')
    TZ = os.environ.get('TZ', 'US/Pacific')


class ProductionConfig(Config):
    """Use when in production."""

    INIT = {
        'host': os.environ.get('INIT_HOST', '0.0.0.0'),
        'port': os.environ.get('INIT_PORT', 8000),
        'debug': os.environ.get('INIT_DEBUG', False)
    }


class DevelopmentConfig(Config):
    """Use when in development."""

    INIT = {
        'host': '0.0.0.0',
        'port': 5000,
        'debug': True
    }
