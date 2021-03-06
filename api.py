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
    logging.debug('reset_db method. payload={} response={}'.format(payload, r.text))
    return r.json()

def add_user(userid, uname, language_interface='en', langauge_exercise='en'):
    payload = {
        'method': 'add_user',
        'userid': userid,
        'uname': uname,
        'language_interface': language_interface.lower(),
        'langauge_exercise': langauge_exercise.lower()
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('add_user method. payload={} response={}'.format(payload, r.text))
    return r.json()
    #"success": boolean

def update_user(userid, uname, language_exercise, language_interface):
    payload = {
        'method': 'update_user',
        'userid': userid,
        'uname': uname,
        'language_exercise': language_exercise.lower(),
        'language_interface': language_interface.lower()
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('add_user method. payload={} response={}'.format(payload, r.text))
    return r.json()
    #"success": boolean


def get_user_info(userid):
    payload = {
        'method': 'get_user_info',
        'userid': userid,
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('get_user_info method. payload={} response={}'.format(payload, r.text))
    return r.json()
    # "userid": string,
    # "uname": string

def is_user_registered(userid):
    response_json = get_user_info(userid)
    return len(response_json)>0

# Choose the exercise type that should be presented to the user.
def choose_exercise(userid, elevel=None, etype='RelatedTo'):
    payload = {
        'method': 'choose_exercise',
        'userid': userid
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('choose_exercise method. payload={} response={}'.format(payload, r.text))
    return r.json()

#level = 'A1','A2',...
#etype = 'RelatedTo', 'AtLocation', 'PartOf'
def get_exercise(userid, elevel=None, etype=None):
    import bot_telegram
    payload = {
        'method': 'get_exercise',
        'userid': userid,
        'elevel': elevel,
        'etype': etype
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('get_exercise method. payload={} response={}'.format(payload, r.text))
    try:
        return r.json()
    except json.decoder.JSONDecodeError:
        bot_telegram.tell_admin("JSON error in get_exercise:\n{}".format(r.content))
    # "eid": int,
    # "userid": string,
    # "exercise": string,
    # "category": string, # "animals"
    # "level": string,
    # "relation": string, # "RelatedTo"
    # "subject": string, (bird) # "bird"
    # "previous_responses": list of strings

#level = 'A1','A2',...
#etype = 'RelatedTo', 'AtLocation', 'PartOf'
def get_close_exercise(userid, elevel=None, etype=None):
    payload = {
        'method': 'get_close_exercise',
        'userid': userid,
        'elevel': elevel,
        'etype': etype
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('get_close_exercise method. payload={} response={}'.format(payload, r.text))
    return r.json()
    # "category": "animal", 
    # "language": "en", 
    # "level": "A1", 
    # "object": "herd", 
    # "userid": "telegram_130870321", 
    # "relation": "RelatedTo", 
    # "eid": 5, 
    # "eid_originated": 7, 
    # "exercise": "Is it true that sheep is related to herd?", 
    # "subject": "sheep"

def get_exercise_languages():    
    payload = {
        'method': 'get_exercise_languages',
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('get_supported_languages method. payload={} response={}'.format(payload, r.text))
    return r.json()

def store_response(eid, userid, response):
    payload = {
        'method': 'store_response',        
        'eid': eid,
        'userid': userid,                
        'response': response
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('store_response method. payload={} response={}'.format(payload, r.text))
    return r.json()
    # "eid": int,
    # "userid": string,
    # "response": string,
    # "points": int/null (null means pending evaluation),

def store_close_response(eid, userid, response):
    payload = {
        'method': 'store_close_response',        
        'eid': eid,
        'userid': userid,                
        'response': response
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('store_close_response method. payload={} response={}'.format(payload, r.text))
    return r.json()
    # "eid": int,
    # "userid": string,
    # "response": string,
    # "points": 0/1 (incorrect/correct answer),

def get_random_response(eid, userid):
    payload = {
        'method': 'get_random_response',        
        'eid': eid,
        'userid': userid,                
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('get_random_response method. payload={} response={}'.format(payload, r.text))
    return r.json()
    # "eid": int,
    # "userid": string,
    # "response": string,


def get_points(userid):
    payload = {
        'method': 'get_points',
        'userid': userid,
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
    #         "userid": string,
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
    userid = 'telegram_{}'.format(p.chat_id)
    new_notifications = get_notifications(userid)
    if new_notifications:
        notifications.extend(new_notifications)
        p.set_variable('notifications', notifications)
    return len(notifications)

def get_notifications(userid):
    payload = {
        'method': 'get_notifications',
        'userid': userid,
    }    
    r = requests.get(API_URL, params=payload)
    logging.debug('get_notifications method. payload={} response={}'.format(payload, r.text))
    responses = r.json()['responses']
    responses = [r for r in responses if r['points']>0] # related to issue https://gitlab.com/crowdfest_task3/nvt_dispatcher/issues/1
    return responses
    # "responses": [
    #     {
    #         "eid": int,
    #         "userid": string,
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
    #     "userid": string,
    #     "rank": int,
    #     "earned_points": int,
    #     "potential_points": int,
    #     "badges": int
    # },
    # ...
    # ]

if __name__ == "__main__":
    # response = add_user('telegram_222', 'test')
    # print(json.dumps(response, indent=3))
    response = get_exercise('telegram_130870321')
    print(json.dumps(response, indent=3))
    '''
    {
        "eid": 1,
        "userid": "2",
        "exercise": "Name a thing that is located at a desk",
        "relation": "AtLocation",
        "subject": "desk",
        "object": "a stapler|paper clips|telephone"
    }
    '''