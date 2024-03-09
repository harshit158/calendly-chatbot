'''This module contains the Calendly class which is used to interact with the Calendly API. It has methods to list events and cancel events.'''

import requests
import json
from pprint import pprint
import os

class Calendly:
    base_url = 'https://api.calendly.com/'
    token = None
    userid = None
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    @classmethod
    def update_attributes(cls, new_token):
        cls.token = new_token
        cls.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {new_token}"
        }
        cls.set_userid()

    @staticmethod
    def set_userid():
        url = Calendly.base_url + "users/me"
        response = requests.request("GET", url, headers=Calendly.headers)
        Calendly.userid = json.loads(response.text)['resource']['uri']

    @staticmethod
    def list_events(args):
        url = Calendly.base_url + "scheduled_events"
        args['user'] = Calendly.userid
        response = requests.request("GET", url, params=args, headers=Calendly.headers)
        return response.text

    @staticmethod
    def cancel_event(args):
        url = Calendly.base_url + f"scheduled_events/{args['uuid']}/cancellation"
        payload = {"reason": args.get('reason', 'Not provided')}
        response = requests.request("POST", url, json=payload, headers=Calendly.headers)
        return response.text