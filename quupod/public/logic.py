"""Logic for public views."""

from apiclient.discovery import build
from flask import request
from flask import session
from oauth2client import client
from quupod.views import url_for

import httplib2

# Google API service object for Google Plus
service = build('plus', 'v1')


def get_google_auth_flow(login: str=None) -> client.Flow:
    """Return Google auth flow object."""
    return client.flow_from_clientsecrets(
        'client_secrets.json',
        scope='openid profile email',
        redirect_uri=login or url_for('public.login', _external=True))


def get_google_authorize_uri(flow: client.Flow) -> str:
    """Return the authorization url given the flow."""
    return flow.step1_get_authorize_url() + '&prompt=select_account'


def get_google_person(flow: client.Flow):
    """Get Google person from the Google flow object."""
    credentials = flow.step2_exchange(request.args.get('code'))
    session['credentials'] = credentials.to_json()

    http = credentials.authorize(httplib2.Http())
    return service.people().get(userId='me').execute(http=http)
