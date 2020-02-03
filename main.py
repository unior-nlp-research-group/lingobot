# -*- coding: utf-8 -*-

import json
import logging
import urllib
import urllib2
import requests
import datetime
from datetime import datetime
from time import sleep
import re

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.ext import deferred
from google.appengine.ext.db import datastore_errors

import key
import person
from person import Person
import utility
import jsonUtil
import string

import webapp2
import exercise_synonim, exercise_intruder
import random
#from ConversionGrid import GRID
import exercise_vocab

########################
WORK_IN_PROGRESS = False
########################

STATES = {
    0:   'Initial Screen',
    1:   'Synonim Game',
    2:   'Intruder Game',
}

INFO_TEXT = "CrowdFest - V-Trel 2.0"

CANCEL = '❌'
CHECK = '✅'
LEFT_ARROW = '⬅️'
UNDER_CONSTRUCTION = '🚧'
FROWNING_FACE = '🙁'
BULLET_RICHIESTA = '🔹'
BULLET_OFFERTA = '🔸'
BULLET_POINT = '🔸'

BUTTON_YES = "✅ YES"
BUTTON_NO = "❌ NO"
BUTTON_VOCAB_GAME = "🎯 PLAY VOCABULARY GAME"
# BUTTON_CLOSE_GAME = "✔️ CHECK GAME"
BUTTON_SYNONYM_GAME = "🖇 SYNONYM GAME"
BUTTON_INTRUDER_GAME = "🐸 INTRUDER GAME"
BUTTON_ACCEPT = CHECK + " ACCEPT"
BUTTON_CONFIRM = CHECK + " CONFIRM"
BUTTON_CANCEL = CANCEL + " CANCEL"
BUTTON_POINTS = "💰 MY POINTS"
BUTTON_LEADERBOARD = "🏆 LEADERBOARD"
BUTTON_NOTIFICATIONS = "🌟"
BUTTON_BACK = "⬅ BACK"
BUTTON_EXIT = CANCEL + " EXIT"
BUTTON_DONT_KNOW = "🤔 DON'T KNOW"
BUTTON_NO_INTRUDER = "NO INTRUDER"

BUTTON_INFO = "ℹ INFO"
BUTTON_CHANGE_LANGUAGE = '🌍 CHANGE LANGAUGE'

LANGUAGES = {
    'eng': {
        'flag': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
        'lang': 'ENGLISH'
    },
    'fin': {
        'flag': '🇫🇮',
        'lang': 'FINNISH'
    },
    'fra': {
        'flag': '🇫🇷',
        'lang': 'FRENCH'
    },
    'deu': {
        'flag': '🇩🇪',
        'lang': 'GERMAN'
    },
    'ell': {
        'flag': '🇬🇷',
        'lang': 'GREEK'
    }, 
    'ita': {
        'flag': '🇮🇹',
        'lang': 'ITALIAN'
    }, 
    'por': {
        'flag': '🇵🇹',
        'lang': 'PORTUGUESE'
    }, 
    'ron': {
        'flag': '🇷🇴',
        'lang': 'RUMANIAN'    
    }, 
    'rus': {
        'flag': '🇷🇺',
        'lang': 'RUSSIAN'
    }, 
    'hbs': {
        'flag': '🇧🇦🇭🇷🇲🇪🇷🇸',
        'lang': 'SERBO-CROATIAN'
    }, 
}

# ================================
# ================================
# ================================


def broadcast(sender_chat_id, msg, restart_user=False, curs=None, enabledCount = 0):    
    try:
        users, next_curs, more = Person.query().fetch_page(500, start_cursor=curs)
    except datastore_errors.Timeout:
        sleep(1)
        deferred.defer(broadcast, sender_chat_id, msg, restart_user, curs, enabledCount)
        return

    for p in users:
        if p.enabled:
            if restart_user:
                restart(p)
            if send_message(p.chat_id, msg, sleepDelay=True):
                enabledCount += 1

    if more:
        deferred.defer(broadcast, sender_chat_id, msg, restart_user, next_curs, enabledCount)
    else:
        total = Person.query().count()
        disabled = total - enabledCount
        msg_debug = 'Message sent to ' + str(total) + ' players.\n' + \
                    'Message received to ' + str(enabledCount) + ' players.\n' + \
                    'Players disabled: ' + str(disabled)
        send_message(sender_chat_id, msg_debug)

def getInfoCount():
    c = Person.query().count()
    msg = "{} Users".format(c)
    return msg


def tell_masters(msg):
    for id in key.MASTER_CHAT_ID:
        send_message(id, msg, markdown=False)

def tellAdministrators(msg):
    for id in key.AMMINISTRATORI_ID:
        send_message(id, msg)


def send_message(chat_id, msg, kb=None, markdown=True, inlineKeyboardMarkup=False,
         one_time_keyboard=False, sleepDelay=False, remove_keyboard=False):
    if remove_keyboard:
        replyMarkup = { #ReplyKeyboardHide
            'remove_keyboard': remove_keyboard
        }
    else:
        replyMarkup = {
            'resize_keyboard': True,
            'one_time_keyboard': one_time_keyboard
        }
    if kb:
        if inlineKeyboardMarkup:
            replyMarkup['inline_keyboard'] = kb
        else:
            replyMarkup['keyboard'] = kb
    try:
        data = {
            'chat_id': chat_id,
            'text': msg,
            'disable_web_page_preview': 'true',
            'parse_mode': 'Markdown' if markdown else '',
            'reply_markup': json.dumps(replyMarkup),
        }
        resp = requests.post(key.BASE_URL + 'sendMessage', data)
        logging.info('Response: {}'.format(resp.text))
        #logging.info('Json: {}'.format(resp.json()))
        respJson = json.loads(resp.text)
        success = respJson['ok']
        if success:
            if sleepDelay:
                sleep(0.1)
            return True
        else:
            status_code = resp.status_code
            error_code = respJson['error_code']
            description = respJson['description']
            if error_code == 403:
                # Disabled user
                p = person.getPersonByChatId(chat_id)
                p.setEnabled(False, put=True)
                logging.info('Disabled user: ' + p.getUserInfoString())
            elif error_code == 400 and description == "INPUT_USER_DEACTIVATED":
                p = person.getPersonByChatId(chat_id)
                p.setEnabled(False, put=True)
                debugMessage = '❗ Input user disactivated: ' + p.getUserInfoString()
                logging.debug(debugMessage)
                send_message(key.FEDE_CHAT_ID, debugMessage, markdown=False)
            else:
                debugMessage = '❗ Raising unknown err in send_message() when sending msg={} kb={}.' \
                          '\nStatus code: {}\nerror code: {}\ndescription: {}.'.format(
                    msg, kb, status_code, error_code, description)
                logging.error(debugMessage)
                send_message(key.FEDE_CHAT_ID, debugMessage, markdown=False)
    except:
        report_exception()


def sendPhotoData(chat_id, file_data, filename):
    from google.appengine.api import urlfetch
    urlfetch.set_default_fetch_deadline(20)
    try:
        files = [('photo', (filename, file_data, 'image/png'))]
        data = {
            'chat_id': chat_id,
        }
        resp = requests.post(key.BASE_URL + 'sendPhoto', data=data, files=files)
        logging.info('Response: {}'.format(resp.text))
    except urllib2.HTTPError, err:
        report_exception()

# ================================
# SEND WAITING ACTION
# ================================

def sendWaitingAction(chat_id, action_type='typing', sleep_time=1.0):
    data = {
        'chat_id': chat_id,
        'action': action_type,
    }
    requests.post(key.BASE_URL + 'sendChatAction', data=data)
    if sleep_time:
        sleep(sleep_time)

# ================================
# SEND GAME
# ================================
#telegram.me/LingoGame_bot?game=LingoGame

def sendGame(chat_id):

    replyMarkup = {
        'inline_keyboard': [
            [
                {
                    'text': 'play',
                    'url': 'http://dialectbot.appspot.com/audiomap/mappa.html',
                    'callback_data': 'data',
                    'callback_game': 'LingoGame'
                }
            ]
        ]
    }

    data = {
        'chat_id': chat_id,
        'game_short_name': 'LingoGame',
    }
    #'reply_markup': json.dumps(replyMarkup),

    try:

        resp = requests.post(key.BASE_URL + 'sendGame', data)
        logging.info('Response: {}'.format(resp.text))
    except:
        report_exception()

# ================================
# ANSWER ONLINE QUERY
# ================================

def answerCallbackQueryGame(callback_query_id):
    data = {
        'callback_query_id': callback_query_id,
        'url': 'http://dialectbot.appspot.com/audiomap/mappa.html'
    }
    try:
        resp = requests.post(key.BASE_URL + 'answerCallbackQuery', data)
        logging.info('Response: {}'.format(resp.text))
    except:
        report_exception()


# ================================
# RESTART
# ================================
def restart(p, msg=None):
    if msg:
        send_message(p.chat_id, msg)
    redirectToState(p, 0)


# ================================
# SWITCH TO STATE
# ================================
def redirectToState(p, new_state, **kwargs):
    if p.state != new_state:
        logging.debug("In redirectToState. current_state:{0}, new_state: {1}".format(str(p.state),str(new_state)))
        p.setState(new_state)
    repeatState(p, **kwargs)

# ================================
# REPEAT STATE
# ================================
def repeatState(p, **kwargs):
    methodName = "goToState" + str(p.state)
    method = possibles.get(methodName)
    if not method:
        send_message(p.chat_id, "Si è verificato un problema (" + methodName +
              "). Segnalamelo mandando una messaggio a @kercos" + '\n' +
              "Ora verrai reindirizzato/a nella schermata iniziale.")
        restart(p)
    else:
        method(p, **kwargs)


# ================================
# GO TO STATE 0: Initial Screen
# ================================

def goToState0(p, **kwargs):
    input_text = kwargs['input_text'] if 'input_text' in kwargs.keys() else None
    giveInstruction = input_text is None
    kb = [
        [BUTTON_VOCAB_GAME],
        #[BUTTON_SYNONYM_GAME,BUTTON_INTRUDER_GAME],
        [BUTTON_POINTS, BUTTON_LEADERBOARD],
        [BUTTON_CHANGE_LANGUAGE, BUTTON_INFO]
    ]
    
    # update notifications
    new_notifications_number = exercise_vocab.update_notifications(p)
    if new_notifications_number>0:
        #send_message(p.chat_id, "New notification!!")
        BUTTON_NUM_NOTIFICATIONS = '{} ({})'.format(BUTTON_NOTIFICATIONS, new_notifications_number)
        kb[1].insert(1, BUTTON_NUM_NOTIFICATIONS)
    if giveInstruction:
        lang = p.language_exercise if p.language_exercise else 'eng'
        lang_info = LANGUAGES[lang]
        flag_lang = '{} {}'.format(lang_info['flag'],lang_info['lang'])
        reply_txt = "Let's play some language game for {}!".format(flag_lang)
        send_message(p.chat_id, reply_txt, kb)
    else:
        if input_text == '':
            send_message(p.chat_id, "Not a valid input.")
        elif input_text == BUTTON_VOCAB_GAME:
            redirect_to_exercise_type(p)            
        elif input_text == BUTTON_SYNONYM_GAME:
            first_time_instructions = utility.unindent(
                """
                Let’s train your vocabulary! Can you find a word with the same meaning?
                You will see a series of sentences with certain words highlighted.
                Which words describe the highlighted parts best?
                """
            )
            send_message(p.chat_id, first_time_instructions)
            sendWaitingAction(p.chat_id, sleep_time=1)
            redirectToState(p, 1)
        elif input_text == BUTTON_INTRUDER_GAME:
            first_time_instructions = utility.unindent(
                """
                Let’s find the intruder! 🐸
                """
            )
            send_message(p.chat_id, first_time_instructions)
            sendWaitingAction(p.chat_id, sleep_time=1)
            redirectToState(p, 2)
        elif input_text.startswith(BUTTON_NOTIFICATIONS):
            notifications = p.get_variable('notifications')
            logging.debug("New notifications: {}".format(notifications))
            if len(notifications) > 0:
                notifications_str = '\n'.join(["{} {}: {}".format( # → {}
                    '🏅' if r['badge'] else '•', 
                    r['exercise'],
                    r['response']) for r in notifications]  #r['exercise']
                )
                msg = "New potential points converted to real points:\n{}".format(notifications_str)
                send_message(p.chat_id, msg)
                p.set_variable('notifications', [])
                repeatState(p)
            else:
                msg = "No new points."
                send_message(p.chat_id, msg)
        elif input_text == BUTTON_POINTS:
            response = exercise_vocab.get_points(p.player_id())
            summary = response['summary']
            earned_points = summary['earned_points']
            potential_points = summary['potential_points']
            badges = summary['badges']
            msg = utility.unindent(
                '''
                💰 Earned Points: {}
                🤞 Potential Points: {}
                🏅 Badges: {}
                '''.format(earned_points, potential_points, badges)
            )
            send_message(p.chat_id, msg, kb)
        elif input_text == BUTTON_LEADERBOARD:
            leaderboard = exercise_vocab.get_leaderboard()
            leaderboard_sorted = sorted(leaderboard, key=lambda e: e["earned_points"], reverse=True)
            leaderboard_sorted = leaderboard_sorted[:9]            
            board_rows = [['RANK', 'NAME', 'POINTS', 'BADGES']] #potential_points
            alignment = 'clcc'
            for i in range(len(leaderboard_sorted)):
                row = leaderboard_sorted[i]
                medal = '🥇' if i==0 else '🥈' if i==1 else '🥉' if i==2 else str(i+1)
                player_name = row['uname'] #utility.escapeMarkdown(row['uname'])
                board_rows.append([medal, player_name, str(row['earned_points']), str(row['badges'])])
            import render_leaderboard
            imgData = render_leaderboard.getResultImage(board_rows,alignment)
            sendPhotoData(p.chat_id, imgData, 'leaderboard.png')
        elif input_text == BUTTON_INFO:            
            msg = (
                "Vocabulary trainer on word relations for vocabulary of level C1."
                "\nRelated-to words can be single words or multiword expressions of any word class."
                "\n\nYour telegram id: {}"
            ).format(p.chat_id)
            send_message(p.chat_id, msg, kb)
        elif input_text == BUTTON_CHANGE_LANGUAGE:
            redirectToState(p, 9)
        elif p.chat_id in key.AMMINISTRATORI_ID:
            dealWithAdminCommands(p, input_text)
        else:
            send_message(p.chat_id, FROWNING_FACE + " Sorry, I don't understand what you have input")


# ================================
# GO TO STATE 9: Change Language
# ================================

def goToState9(p, **kwargs):
    input_text = kwargs['input_text'] if 'input_text' in kwargs.keys() else None
    giveInstruction = input_text is None
    language_list = [
        '{} {}'.format(v['flag'],v['lang'])
        for k,v in sorted(LANGUAGES.items(), key=lambda x:x[1]['lang'])
        if k != p.language_exercise
    ]
    kb = [[b] for b in language_list]
    kb.insert(0,[BUTTON_CANCEL])
    kb.append([BUTTON_CANCEL])
    
    if giveInstruction:
        lang = p.language_exercise if p.language_exercise else 'eng'
        lang_info = LANGUAGES[lang]
        flag_lang = '{} {}'.format(lang_info['flag'],lang_info['lang'])
        reply_txt = "Your are learning {}.\nPlease select a new language you want to learn.".format(flag_lang)
        send_message(p.chat_id, reply_txt, kb)
    else:
        if input_text == '':
            send_message(p.chat_id, "Not a valid input.")
        elif input_text in language_list:
            lang = next(k for k,v in LANGUAGES.items() if input_text == '{} {}'.format(v['flag'],v['lang']))
            p.set_language_exercise(lang)
            exercise_vocab.update_user(p.player_id(), p.name, language_interface=lang)
            redirectToState(p, 0)
        elif input_text == BUTTON_CANCEL:
            redirectToState(p, 0)
        else:
            send_message(p.chat_id, FROWNING_FACE + " Sorry, I don't understand what you have input")


def redirect_to_exercise_type(p):
    type_of_exercise = exercise_vocab.choose_exercise(p.player_id())["exercise_type"]
    assert type_of_exercise in ['open','close']
    logging.debug("New exercise of type: {}".format(type_of_exercise))
    if type_of_exercise=='open':
        # first_time_instructions = "Let’s play some vocabulary game!"
        # send_message(p.chat_id, first_time_instructions)
        redirectToState(p, 3)
    else:
        redirectToState(p, 4)

def get_notification_button(p, debug=False):
    new_notifications_number = exercise_vocab.update_notifications(p)
    if new_notifications_number>0:
        #send_message(p.chat_id, "New notification!!")
        BUTTON_NUM_NOTIFICATIONS = '{} ({})'.format(BUTTON_NOTIFICATIONS, new_notifications_number)
        return BUTTON_NUM_NOTIFICATIONS
    elif debug and random.choice([True, False]):
        # testing if it works
        BUTTON_NUM_NOTIFICATIONS = '{} ({})'.format(BUTTON_NOTIFICATIONS, 0)
        return BUTTON_NUM_NOTIFICATIONS
    return None

# ================================
# GO TO STATE 3: VOCABULARY GAME
# ================================

def goToState3(p, **kwargs):    
    input_text = kwargs['input_text'] if 'input_text' in kwargs.keys() else None
    giveInstruction = input_text is None
    player_id = p.player_id()
    kb = [[BUTTON_DONT_KNOW],[BUTTON_EXIT]]
    if giveInstruction:        
        #elevel = 'A1','A2',...
        #etype = 'RelatedTo', 'AtLocation', 'PartOf'
        response = exercise_vocab.get_exercise(player_id) #elevel='', etype=''        
        if response is None:
            report_msg = "None risponse in get_exercise ({})".format(player_id)
            send_message(key.FEDE_CHAT_ID, report_msg, markdown=False)
            repeatState(p)
            return
        if response.get('success', True) == False:
            report_msg = 'Detected success false in get_exercise ({})'.format(player_id)
            send_message(key.FEDE_CHAT_ID, report_msg, markdown=False)
            repeatState(p)
            return
        r_eid = response['eid']
        wiki_url = response.get('hint_url', None)
        exercise = response['exercise'] # "exercise": "Name a thing that is located at a desk",                
        subject = response['subject']
        exercise = exercise[:exercise.rfind(subject)] + '*{}*'.format(subject)
        previous_responses = response["previous_responses"]
        msg = exercise
        if previous_responses:
            msg += '\n(you previously inserted: {})'.format(', '.join('*{}*'.format(pr) for pr in  previous_responses))
        if wiki_url:
            msg += '\n\nFor some inspiration check out\n{}'.format(wiki_url)
        p.set_variable('eid',r_eid)
        p.set_variable('exercise',exercise)   
        p.set_variable('subject',subject)        
        BUTTON_NUM_NOTIFICATIONS = get_notification_button(p, debug=False)
        if BUTTON_NUM_NOTIFICATIONS:
            kb.insert(1, [BUTTON_NUM_NOTIFICATIONS])
        send_message(p.chat_id, msg, kb)        
    else:
        eid = p.get_variable('eid')        
        if input_text == '':
            send_message(p.chat_id, "Not a valid input.")        
        elif input_text == BUTTON_EXIT:
            restart(p)
        elif input_text == BUTTON_DONT_KNOW:
            response_json = exercise_vocab.get_random_response(eid, player_id)
            msg = "No worries, a possible response would have been *{}*.".format(response_json['response'])
            send_message(p.chat_id, msg, sleepDelay=True, remove_keyboard=True)            
            sendWaitingAction(p.chat_id, sleep_time=1)
            exercise = p.get_variable('exercise')
            send_message(p.chat_id, exercise, kb)  
            # repeat the same question and stay in current state
        elif input_text.startswith(BUTTON_NOTIFICATIONS):
            notifications = p.get_variable('notifications')
            logging.debug("New notifications: {}".format(notifications))
            if len(notifications) > 0:
                notifications_str = '\n'.join(["{} {}: {}".format( # → {}
                    '🏅' if r['badge'] else '•', 
                    r['exercise'],
                    r['response']) for r in notifications]  #r['exercise']
                )
                msg = "New potential points converted to real points:\n{}".format(notifications_str)
                send_message(p.chat_id, msg, kb)
                p.set_variable('notifications', [])
                repeatState(p)                
            else:
                msg = "No new points."
                send_message(p.chat_id, msg, kb)   
            sendWaitingAction(p.chat_id, sleep_time=1)
            exercise = p.get_variable('exercise')
            send_message(p.chat_id, exercise, kb)  
        else:                
            subject = p.get_variable('subject') 
            if input_text == subject:
                msg = "❌ You have inserted the same word of the exercise (*{}*)".format(subject)
                send_message(p.chat_id, msg, sleepDelay=True, remove_keyboard=True)            
                sendWaitingAction(p.chat_id, sleep_time=1)
                exercise = p.get_variable('exercise')
                send_message(p.chat_id, exercise, kb)  
                return
            response = exercise_vocab.store_response(eid, player_id, input_text)
            logging.debug("Response from store_response eid={}, player_id={}, input_text={}: {}".format(eid, player_id, input_text, response))
            if 'points' in response:
                r_points = response['points']
                points_str = '*{} points*'.format(r_points) if r_points>1 else '*1 point*'
                if r_points>0:
                    msg = utility.unindent(
                        '''
                        You have inserted *{}*.\n
                        👍 Good job! You earned {}
                        '''.format(input_text, points_str)
                    )
                elif r_points == 0:
                    msg = utility.unindent(
                        '''
                        You have inserted *{}*.\n 
                        🙄 You get 0 points:  you have already entered this answer!
                        '''.format(input_text)
                    )
                elif r_points is None:
                    msg = utility.unindent(
                        '''
                        You have inserted *{}*. Thanks for your answer!\n 
                        🤞 This is a potential double point you can earn in the future if enough people confirm it!
                        '''.format(input_text)
                    )                
                send_message(p.chat_id, msg)
            else:
                # debugging
                error_msg = response['error']
                msg = 'Backend found an error: {}.\nPlease report this to @kercos'.format(error_msg)
                send_message(p.chat_id, msg)
            sendWaitingAction(p.chat_id, sleep_time=1)
            # repeatState(p)         
            redirect_to_exercise_type(p)


# ================================
# GO TO STATE 3: CLOSE GAME
# ================================

def goToState4(p, **kwargs):    
    input_text = kwargs['input_text'] if 'input_text' in kwargs.keys() else None
    giveInstruction = input_text is None
    player_id = p.player_id()
    if giveInstruction:        
        #level = 'A1','A2',...
        #etype = 'RelatedTo', 'AtLocation', 'PartOf'
        response = exercise_vocab.get_close_exercise(player_id) #elevel='', etype='RelatedTo'
        if response is None:
            report_msg = "None risponse in get_close_exercise ({})".format(player_id)
            send_message(key.FEDE_CHAT_ID, report_msg, markdown=False)
            repeatState(p)
            return
        if response.get('success', True) == False:
            report_msg = 'Detected success false in get_close_exercise ({})'.format(player_id)
            send_message(key.FEDE_CHAT_ID, report_msg, markdown=False)
            repeatState(p)
            return
        r_eid = response['eid']
        exercise = response['exercise'] # "exercise": "Is it true that sheep is related to herd?",
        exercise = re.sub(
            r"Is it true that (.+) is related to (.+)\?", 
            r"Is it true that *\1* is related to *\2*?", 
            exercise
        )
        # subject = response['subject']
        # if subject in exercise:
        #     exercise = exercise[:exercise.rfind(subject)] + '*{}*'.format(subject)
        msg = exercise
        p.set_variable('eid',r_eid)
        p.set_variable('exercise',exercise)
        kb = [[BUTTON_YES,BUTTON_NO],[BUTTON_DONT_KNOW], [BUTTON_EXIT]]
        send_message(p.chat_id, msg, kb)        
    else:
        eid = p.get_variable('eid')        
        if input_text == '':
            send_message(p.chat_id, "Not a valid input.")        
        elif input_text == BUTTON_EXIT:
            restart(p)
        elif input_text.upper() in [BUTTON_YES, 'YES', 'Y', BUTTON_NO, 'NO', 'N', BUTTON_DONT_KNOW]:
            response = 1 if input_text.upper() in [BUTTON_YES, 'YES', 'Y'] \
                else -1 if input_text.upper() in [BUTTON_NO, 'NO', 'N'] \
                else 0
            evalutaion_json = exercise_vocab.store_close_response(eid, player_id, response)
            if response==0:
                correct_response = BUTTON_YES if evalutaion_json['correct_response'] == 1 else BUTTON_NO
                msg = "💪 Don’t worry, the correct response was {}.".format(correct_response)    
            else:
                correct = evalutaion_json['points']==1            
                msg = "👍 Correct!" if correct else "👎 Wrong (according to the information we currently have)."
            send_message(p.chat_id, msg, sleepDelay=True, remove_keyboard=True)            
            sendWaitingAction(p.chat_id, sleep_time=1)
            # repeatState(p)
            redirect_to_exercise_type(p)
        else:
            send_message(p.chat_id, "Not a valid input, please press one of the buttons below (or type Y/YES N/NO).")        


# ================================
# GO TO STATE 1: GAME SYNONYM
# ================================


def goToState1(p, **kwargs):
    input_text = kwargs['input_text'] if 'input_text' in kwargs.keys() else None
    giveInstruction = input_text is None
    if giveInstruction:
        exerciseId, sentence, wordIndexToReplace, wordsToReplace, falseSynonymes, trueSynonymes = exercise_synonim.getRandomExercise()
        sentenceWithBoldWord = getSentenceWithBoldedWord(sentence, wordIndexToReplace, wordsToReplace)
        plural = 's' if len(wordsToReplace.split()) > 1 else ''
        instructions = utility.unindent(
            """
            I've chosen the following sentence for you:\n
            {0}\n
            Select an option from the following list which is a synonym of the word{1} in bold text ({2}).
            """.format(sentenceWithBoldWord, plural, wordsToReplace)
        )
        options = falseSynonymes + trueSynonymes
        random.shuffle(options)
        options_text = [BULLET_POINT + ' /' + str(n) + ': ' + x for n, x in enumerate(options, 1)]
        instructions += '\n'.join(options_text)
        number_buttons = [str(x) for x in range(1,len(options)+1)]
        kb = utility.distributeElementMaxSize(number_buttons)
        kb.append([BUTTON_EXIT])
        send_message(p.chat_id, instructions, kb)
        p.setLastExerciseNumberAndOptions(exerciseId, options)
    else:
        if input_text == '':
            send_message(p.chat_id, "Not a valid input.")
        elif input_text == BUTTON_EXIT:
            restart(p)
        #elif input_text == BUTTON_DONT_KNOW:
        #    repeatState(p)
        else:
            exerciseId, exerciseOptions = p.getLastExerciseIdAndOptions()
            exerciseId, sentence, wordIndexToReplace, wordsToReplace, falseSynonymes, trueSynonymes = exercise_synonim.getExercizeId(exerciseId)
            if input_text.startswith('/'):
                input_text = input_text[1:]
            if utility.representsIntBetween(input_text, 1, len(exerciseOptions)+1):
                number = int(input_text)
                chosenWord = exerciseOptions[number - 1]
            else:
                #send_message(p.chat_id, FROWNING_FACE + " Sorry, I don't understand what you have input")
                chosenWord = input_text
            msg = "You have chosen *{0}*.\n".format(chosenWord)
            sendWaitingAction(p.chat_id, sleep_time=0.5)
            if chosenWord in trueSynonymes:
                msg += "😄 Great, your answer is correct!"
                #kb = [[BUTTON_DONT_KNOW], [BUTTON_EXIT]]
                kb = [[BUTTON_EXIT]]
                send_message(p.chat_id, msg, kb)
                sendWaitingAction(p.chat_id, sleep_time=1)
                repeatState(p)
            else:
                msg += "🙁 I'm sorry, your answer is NOT correct, try again"
                send_message(p.chat_id, msg)

def getSentenceWithBoldedWord(sentence, wordIndexToReplace, wordsToReplace):
    words = sentence.split()
    logging.debug("Split words: " + str(words))
    numberOfWordsToReplace = len(wordsToReplace.split())
    for i in range(wordIndexToReplace, wordIndexToReplace+numberOfWordsToReplace):
        words[i] = '*' + words[i] + '*'
    logging.debug("Chosend index: {0}. Word: {1} ".format(str(wordIndexToReplace), words[wordIndexToReplace]))
    return ' '.join(words)

# ================================
# GO TO STATE 2: INTRUDER GAME
# ================================

def goToState2(p, **kwargs):
    input_text = kwargs['input_text'] if 'input_text' in kwargs.keys() else None
    giveInstruction = input_text is None
    if giveInstruction:
        intruder_index, options = exercise_intruder.getRandomExercise()
        options.append(BUTTON_NO_INTRUDER)
        instructions = "Which word does not belong here? " \
                       "Click on the intruder or on *{}* if you think there is no intruder.\n".format(BUTTON_NO_INTRUDER)
        options_text = [BULLET_POINT + ' /' + str(n) + ': ' + x for n, x in enumerate(options, 1)]
        instructions += '\n'.join(options_text)
        number_buttons = [str(x) for x in range(1,len(options)+1)]
        kb = utility.distributeElementMaxSize(number_buttons)
        kb.append([BUTTON_NO_INTRUDER])
        kb.append([BUTTON_EXIT])
        send_message(p.chat_id, instructions, kb)
        p.setLastExerciseNumberAndOptions(intruder_index, options)
    else:
        if input_text == '':
            send_message(p.chat_id, "Not a valid input.")
        elif input_text == BUTTON_EXIT:
            restart(p)
        #elif input_text == BUTTON_DONT_KNOW:
        #    repeatState(p)
        else:
            intruder_index, exerciseOptions = p.getLastExerciseIdAndOptions()
            if input_text.startswith('/'):
                input_text = input_text[1:]
            if utility.representsIntBetween(input_text, 1, len(exerciseOptions)):
                number = int(input_text)
                chosenWord = exerciseOptions[number - 1]
            else:
                chosenWord = input_text
            if chosenWord not in exerciseOptions:
                send_message(p.chat_id, FROWNING_FACE + " Sorry, your answer is not valid")
                sendWaitingAction(p.chat_id, sleep_time=1)
                repeatState(p)
            else:
                msg = "You have chosen *{0}*.\n".format(chosenWord)
                sendWaitingAction(p.chat_id, sleep_time=0.5)
                chosen_index =  exerciseOptions.index(chosenWord) if chosenWord in exerciseOptions else None
                if (chosenWord==BUTTON_NO_INTRUDER and intruder_index==-1) or chosen_index == intruder_index:
                    msg += "😄 Great, your answer is correct!"
                    #kb = [[BUTTON_DONT_KNOW], [BUTTON_EXIT]]
                    kb = [[BUTTON_EXIT]]
                    send_message(p.chat_id, msg, kb)
                    sendWaitingAction(p.chat_id, sleep_time=1)
                    repeatState(p)
                else:
                    msg += "🙁 I'm sorry, your answer is NOT correct, try again"
                    send_message(p.chat_id, msg)   
            
# ================================
# ================================
# ================================


class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(key.BASE_URL + 'getMe'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(
                json.dumps(json.load(urllib2.urlopen(key.BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))

# ================================
#  CALLBACK QUERY
# ================================


def dealWithCallbackQuery(callback_query):
    logging.debug('dealing with callback query')
    game_short_name = callback_query['game_short_name'] if 'game_short_name' in callback_query else None
    if game_short_name:
        callback_query_id = callback_query['id']
        answerCallbackQueryGame(callback_query_id)
        return
    logging.debug('callback query not recognized')

def dealWithAdminCommands(p, input_text):
    #splitCommandOnSpace = input_text.split(' ')
    #commandBodyStartIndex = len(splitCommandOnSpace[0]) + 1
    if input_text == '/testGame':
        sendGame(p.chat_id)
    elif input_text == '/debug':
        msg = json.dumps(p.variables, indent=3)
        send_message(p.chat_id, msg)
    elif input_text == '/testInline':
        kb = [['A'],['B'],['C']]
        inlineKb = utility.convertKeyboardToInlineKeyboard(kb)
        #logging.debug("InlineKb: {}".format(inlineKb))
        send_message(p.chat_id, "Test inline", kb = inlineKb, inlineKeyboardMarkup=True)
    elif input_text == '/reset':
        text = input_text.split()[1]
        broadcast(sender_chat_id=p.chat_id, msg=text, restart_user=True)
        #person.reset_registrations()
    elif input_text == '/broadcast':
        text = input_text.split()[1]
        broadcast(sender_chat_id=p.chat_id, msg=text, restart_user=True)
    else:
        send_message(p.chat_id, FROWNING_FACE + " Sorry, I don't understand what you have input")

# ================================
# ================================
# ================================


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = jsonUtil.json_loads_byteified(self.request.body)
        logging.info('request body: {}'.format(body))
        self.response.write(json.dumps(body))

        callback_query = body["callback_query"] if "callback_query" in body else None
        if callback_query:
            dealWithCallbackQuery(callback_query)
            return

        # update_id = body['update_id']
        if 'message' not in body:
            return
        message = body['message']
        # message_id = message.get('message_id')
        # date = message.get('date')
        if "chat" not in message:
            return
        # fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']
        if "first_name" not in chat:
            return
        text = message.get('text') if "text" in message else ''
        name = chat["first_name"]
        last_name = chat["last_name"] if "last_name" in chat else None
        username = chat["username"] if "username" in chat else None
        #location = message["location"] if "location" in message else None
        contact = message["contact"] if "contact" in message else None

        def reply(msg=None, kb=None, markdown=False, inlineKeyboardMarkup=False):
            send_message(chat_id, msg, kb, markdown, inlineKeyboardMarkup)

        p = person.getPersonByChatId(chat_id)
        user_name = 'telegram_{}'.format(chat_id)

        if not exercise_vocab.is_user_registered(user_name):
            exercise_vocab.add_user(user_name, name)

        if p is None:
            # new user
            logging.info("Text: " + text)
            if text == '/help':
                reply(INFO_TEXT)
            elif text.startswith("/start"):
                tell_masters("New user: " + name)
                p = person.addPerson(chat_id, name, last_name, username)                                
                send_message(p.chat_id, "Hi {0}, welcome in LingoGameBot!\n\n*By using this bot you agree that your data is recorded and processed within a scientific experiment.*".format(name))
                restart(p)
            else:
                reply("Press on /start if you want to begin. "
                      "If you encounter any problem, please contact @kercos")
        else:
            # known user
            p.updateUser(username)            
            if text == '/state':
                if p.state in STATES:
                    reply("You are in state " + str(p.state) + ": " + STATES[p.state])
                else:
                    reply("You are in state " + str(p.state))
            elif text.startswith("/start"):
                send_message(p.chat_id, "Hi {0}, welcome back in LingoGameBot!\n\n*By using this bot you agree that your data is recorded and processed within a scientific experiment.*".format(name))
                p.setEnabled(True, put=False)
                restart(p)
            elif WORK_IN_PROGRESS and p.chat_id != key.FEDE_CHAT_ID:
                reply(UNDER_CONSTRUCTION + " The system is under maintanance, try again later.")
            else:
                logging.debug("Sending {0} to state {1}. Input: '{2}'".format(p.getName(), str(p.state), text))
                repeatState(p, input_text=text, contact=contact)

    def handle_exception(self, exception, debug_mode):
        logging.exception(exception)
        send_message(key.FEDE_CHAT_ID, "❗ Detected Exception: " + str(exception), markdown=False)

def report_exception():
    import traceback
    msg = "❗ Detected Exception: " + traceback.format_exc()
    send_message(key.FEDE_CHAT_ID, msg, markdown=False)
    logging.error(msg)


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    #    ('/_ah/channel/connected/', DashboardConnectedHandler),
    #    ('/_ah/channel/disconnected/', DashboardDisconnectedHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)

possibles = globals().copy()
possibles.update(locals())
