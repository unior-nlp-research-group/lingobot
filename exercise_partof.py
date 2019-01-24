# -*- coding: utf-8 -*-

import requests
import logging
import json

API_URL = "http://cognition-srv1.ouc.ac.cy/nvt/webservice/api.php"

def getExercisesFromAPI(uid):
    payload = {
        'method': 'get_exercise',
        'userid': uid
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('getExercisesFromAPI method. payload={} response={}'.format(payload, r.text))
    return r.json()

def sendResponse(uid, eid, response):
    payload = {
        'method': 'store_response',
        'userid': uid,
        'eid': eid,
        'response': response
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('sendResponse method. payload={} response={}'.format(payload, r.text))

if __name__ == "__main__":
    response = getExercisesFromAPI('telegram_111')
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