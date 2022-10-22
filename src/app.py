'''
Application Implementation
'''

import requests
from flask import Flask
from pyngrok import ngrok
from environment import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET


app = Flask(__name__)
processed_activities = {}
VERIFY_TOKEN = 'STRAVA'


@app.route('/')
def index():
    '''
    Delete existing webhook subscriptions and create a new one
    '''
    def view_subscription():
        try:
            base_url = 'https://www.strava.com/api/v3/push_subscriptions'
            params = {
                'client_id': STRAVA_CLIENT_ID,
                'client_secret': STRAVA_CLIENT_SECRET
            }
            resp = requests.get(base_url, params=params)
        except requests.exceptions.RequestException:
            return None
        return resp.json()

    def delete_subscription(subscription_id):
        try:
            base_url = f'https://www.strava.com/api/v3/push_subscriptions/{subscription_id}'
            params = {
                'client_id': STRAVA_CLIENT_ID,
                'client_secret': STRAVA_CLIENT_SECRET
            }
            requests.delete(base_url, params=params)
        except requests.exceptions.RequestException:
            return None

    def create_subscription(callback_url):
        try:
            base_url = 'https://www.strava.com/api/v3/push_subscriptions'
            data = {
                'client_id': STRAVA_CLIENT_ID,
                'client_secret': STRAVA_CLIENT_SECRET,
                'callback_url': callback_url,
                'verify_token': VERIFY_TOKEN
            }
            requests.post(base_url, data=data)
        except requests.exceptions.RequestException:
            return None

    existing_subscription = view_subscription()
    if existing_subscription:
        existing_subscription_id = existing_subscription[0]['id']
        delete_subscription(existing_subscription_id)
    tunnels = ngrok.connect(5000, bind_tls=True)
    ngrok_url = tunnels.public_url
    create_subscription(ngrok_url + '/webhook')
    return ('SUCCESS', 200)
