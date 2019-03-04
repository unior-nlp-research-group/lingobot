# -*- coding: utf-8 -*-

import requests
import logging
import json
import key

API_URL = "http://cognition-srv1.ouc.ac.cy/nvt/webservice/api.php"

def reset_db():
    payload = {
        'method': 'reset_db',
        'apikey': key.NVT_API_KEY,
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('add_user method. payload={} response={}'.format(payload, r.text))
    return r.json()

def add_user(uid, first_name):
    payload = {
        'method': 'add_user',
        'uid': uid,
        'first_name': first_name,
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('add_user method. payload={} response={}'.format(payload, r.text))
    return r.json()
    #"success": boolean

def get_user_info(uid):
    payload = {
        'method': 'get_user_info',
        'uid': uid,
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('add_user method. payload={} response={}'.format(payload, r.text))
    return r.json()
    # "uid": string,
    # "first_name": string


def get_exercise(uid):
    payload = {
        'method': 'get_exercise',
        'userid': uid
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('get_exercise method. payload={} response={}'.format(payload, r.text))
    return r.json()
    # "eid": int,
    # "uid": string,
    # "exercise": string


def store_response(uid, eid, response):
    payload = {
        'method': 'store_response',
        'userid': uid,
        'eid': eid,
        'response': response
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('store_response method. payload={} response={}'.format(payload, r.text))
    return r.json()
    # "eid": int,
    # "uid": string,
    # "response": string,
    # "points": int/null (null means pending evaluation),


def get_points(uid):
    payload = {
        'method': 'get_points',
        'userid': uid,
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('get_points method. payload={} response={}'.format(payload, r.text))
    return r.json()
    # {
    # "summary": {
    #     "earned_points": int,
    #     "potential_points": int,
    #     "badges": int, (number of time user was the first inputing a new "correct" response"
    # }
    # "responses": [
    #     {
    #         "eid": int,
    #         "uid": string,
    #         "response": string,
    #         "points": int/null (null means pending evaluation),
    #         "notified": boolean,
    #         "badge": boolean (true if this response is the first being validated as "correct")
    #     },
    #     ...
    # ]
    # }


def update_notifications(p):
    notifications = p.get_variable('notifications', [])    
    uid = 'telegram_{}'.format(p.chat_id)
    new_notifications = get_notifications(uid)
    if new_notifications:
        notifications.extend(new_notifications)
        p.set_variable('notifications', notifications)
    return len(notifications)

def get_notifications(uid):
    payload = {
        'method': 'get_notifications',
        'userid': uid,
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('get_notifications method. payload={} response={}'.format(payload, r.text))
    responses = r.json()['responses']
    responses = [r for r in responses if r['points']>0] # related to issue https://gitlab.com/crowdfest_task3/nvt_dispatcher/issues/1
    return responses
    # "responses": [
    #     {
    #         "eid": int,
    #         "uid": string,
    #         "exercise": string,
    #         "response": string,
    #         "points": int
    #     },
    #     ...
    # ]


def get_leaderboard():
    payload = {
        'method': 'get_leaderboard'
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('get_leaderboard method. payload={} response={}'.format(payload, r.text))
    return r.json()
    # [
    # {
    #     "uid": string,
    #     "rank": int,
    #     "earned_points": int,
    #     "potential_points": int,
    #     "badges": int
    # },
    # ...
    # ]

if __name__ == "__main__":
    response = get_exercise('telegram_111')
    print(json.dumps(response, indent=3))
    '''
    {
        "eid": 1,
        "uid": "2",
        "exercise": "Name a thing that is located at a desk",
        "relation": "AtLocation",
        "subject": "desk",
        "object": "a stapler|paper clips|telephone"
    }
    '''