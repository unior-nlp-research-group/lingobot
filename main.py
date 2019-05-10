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

CANCEL = '❌'
CHECK = '✅'
LEFT_ARROW = '⬅️'
UNDER_CONSTRUCTION = '🚧'
FROWNING_FACE = '🙁'
BULLET_RICHIESTA = '🔹'
BULLET_OFFERTA = '🔸'
BULLET_POINT = '🔸'

BUTTON_VOCAB_GAME = "🎯 PLAY VOCABULARY GAME"
BUTTON_SYNONYM_GAME = "🖇 SYNONYM GAME"
BUTTON_INTRUDER_GAME = "🐸 INTRUDER GAME"
BUTTON_ACCEPT = CHECK + " ACCEPT"
BUTTON_CONFIRM = CHECK + " CONFIRM"
BUTTON_ABORT = CANCEL + " ABORT"
BUTTON_POINTS = "💰 MY POINTS"
BUTTON_LEADERBOARD = "🏆 LEADERBOARD"
BUTTON_NOTIFICATIONS = "🌟"
BUTTON_BACK = "⬅ BACK"
BUTTON_EXIT = CANCEL + " EXIT"
BUTTON_DONT_KNOW = "🤔 DON'T KNOW"
BUTTON_NO_INTRUDER = "NO INTRUDER"

BUTTON_INFO = "ℹ INFO"

# ================================
# ================================
# ================================


INFO_TEXT = "CrowdFest - Task3 - Vocabulary trainer"


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
        send_message(id, msg)

def tellAdministrators(msg):
    for id in key.AMMINISTRATORI_ID:
        send_message(id, msg)


def send_message(chat_id, msg, kb=None, markdown=True, inlineKeyboardMarkup=False,
         one_time_keyboard=False, sleepDelay=False):
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
        [BUTTON_INFO]
    ]
    
    # update notifications
    new_notifications_number = exercise_vocab.update_notifications(p)
    if new_notifications_number>0:
        #send_message(p.chat_id, "New notification!!")
        BUTTON_NUM_NOTIFICATIONS = '{} ({})'.format(BUTTON_NOTIFICATIONS, new_notifications_number)
        kb[1].insert(1, BUTTON_NUM_NOTIFICATIONS)
    if giveInstruction:
        reply_txt = "Let's play some language game!"
        send_message(p.chat_id, reply_txt, kb)
    else:
        if input_text == '':
            send_message(p.chat_id, "Not a valid input.")
        elif input_text == BUTTON_VOCAB_GAME:
            # first_time_instructions = "Let’s play some vocabulary game!"
            # send_message(p.chat_id, first_time_instructions)
            redirectToState(p, 3)
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
            send_message(p.chat_id, INFO_TEXT, kb)
        elif p.chat_id in key.AMMINISTRATORI_ID:
            dealWithAdminCommands(p, input_text)
        else:
            send_message(p.chat_id, FROWNING_FACE + " Sorry, I don't understand what you have input")


# ================================
# GO TO STATE 3: VOCABULARY GAME
# ================================

def goToState3(p, **kwargs):    
    input_text = kwargs['input_text'] if 'input_text' in kwargs.keys() else None
    giveInstruction = input_text is None
    player_id = p.player_id()
    if giveInstruction:        
        #level = 'A1','A2',...
        #etype = 'RelatedTo', 'AtLocation', 'PartOf'
        response = exercise_vocab.get_exercise(player_id, elevel='', etype='RelatedTo')
        r_eid = response['eid']
        exercise = response['exercise'] # "exercise": "Name a thing that is located at a desk",                
        subject = response['subject']
        exercise = exercise[:exercise.rfind(subject)] + '*{}*'.format(subject)
        previous_responses = response["previous_responses"]
        msg = exercise
        if previous_responses:
            msg += '\n(you previously inserted: {})'.format(', '.join('*{}*'.format(pr) for pr in  previous_responses))
        p.set_variable('eid',r_eid)
        p.set_variable('exercise',exercise)
        kb = [[BUTTON_DONT_KNOW],[BUTTON_EXIT]]
        new_notifications_number = exercise_vocab.update_notifications(p)
        if new_notifications_number>0:
            #send_message(p.chat_id, "New notification!!")
            BUTTON_NUM_NOTIFICATIONS = '{} ({})'.format(BUTTON_NOTIFICATIONS, new_notifications_number)
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
            send_message(p.chat_id, msg, sleepDelay=True)            
            exercise = p.get_variable('exercise')
            send_message(p.chat_id, exercise)            
            #repeatState(p)
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
        else:                        
            response = exercise_vocab.store_response(eid, player_id, input_text)
            logging.debug("Response from store_response eid={}, player_id={}, input_text={}: {}".format(eid, player_id, input_text, response))
            r_points = response['points']
            if r_points>0:
                msg = utility.unindent(
                    '''
                    You have inserted *{}*.\n
                    👍 Good job! You earned *{} points*!
                    '''.format(input_text, r_points)
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
            sendWaitingAction(p.chat_id, sleep_time=1)
            repeatState(p)         

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
                reply("Hi {0}, welcome in LingoGameBot!".format(name))
                restart(p)
            else:
                reply("Press on /start if you want to begin. "
                      "If you encounter any problem, please contact @kercos")
        else:
            # known user
            p.updateUsername(username)            
            if text == '/state':
                if p.state in STATES:
                    reply("You are in state " + str(p.state) + ": " + STATES[p.state])
                else:
                    reply("You are in state " + str(p.state))
            elif text.startswith("/start"):
                reply("Hi {0}, welcome back in LingoGameBot!".format(name))
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
