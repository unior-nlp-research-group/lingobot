# -*- coding: utf-8 -*-

# import json
import json
import logging
import urllib
import urllib2
import datetime
from datetime import datetime
from time import sleep
import re

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.ext import deferred

import key
import person
from person import Person
import utility
import jsonUtil
import string

import webapp2
import exercise
import random
#from ConversionGrid import GRID


########################
WORK_IN_PROGRESS = False
########################

BASE_URL = 'https://api.telegram.org/bot' + key.TOKEN + '/'


STATES = {
    0:   'Initial Screen',
    1:   'Game',
}

CANCEL = u'\U0000274C'.encode('utf-8')
CHECK = u'\U00002705'.encode('utf-8')
LEFT_ARROW = u'\U00002B05'.encode('utf-8')
UNDER_CONSTRUCTION = u'\U0001F6A7'.encode('utf-8')
FROWNING_FACE = u'\U0001F641'.encode('utf-8')
BULLET_RICHIESTA = '🔹'
BULLET_OFFERTA = '🔸'
BULLET_POINT = '🔸'

BUTTON_GAME = "🕹 GAME"
BUTTON_ACCEPT = CHECK + " ACCEPT"
BUTTON_CONFIRM = CHECK + " CONFIRM"
BUTTON_ABORT = CANCEL + " ABORT"
BUTTON_BACK = "⬅ BACK"
BUTTON_NEXT = "➡ NEXT"
BUTTON_EXIT = CANCEL + " EXIT"
BUTTON_NEXT_SENTENCE = "➡ NEXT SENTENCE"

BUTTON_INFO = "ℹ INFO"

# ================================
# ================================
# ================================


ISTRUZIONI = UNDER_CONSTRUCTION + "*Instruction* LingoBot to complete..."
INFO_TEXT = UNDER_CONSTRUCTION +  "*INFO* LingoBot to complete..."


# ================================
# ================================
# ================================


def broadcast(msg, restart_user=False, sender_id=None):
    qry = Person.query().order(-Person.last_mod)
    disabled = 0
    count = 0
    for p in qry:
        if p.enabled:
            count += 1
            tell(p.chat_id, msg, sleepDelay=True)
            if restart_user:
                restart(p)
        else:
            disabled += 1
    if sender_id:
        enabledCount = qry.count() - disabled
        msg_debug = 'Messaggio inviato a ' + str(qry.count()) + ' persone.\n' + \
                    'Messaggio ricevuto da ' + str(enabledCount) + ' persone.\n' + \
                    'Persone disabilitate: ' + str(disabled)
        tell(sender_id, msg_debug)

def getInfoCount():
    c = Person.query().count()
    msg = "Attualmente siamo in " + str(c) + " persone iscritte a BancaTempoBot! " + \
          "Vogliamo crescere assieme! Invita altre persone ad aunirsi!"
    return msg


def tell_masters(msg):
    for id in key.MASTER_CHAT_ID:
        tell(id, msg)

def tellAdministrators(msg):
    for id in key.AMMINISTRATORI_ID:
        tell(id, msg)


def tell_queue(chat_id, msg, kb=None, markdown=True, inlineKeyboardMarkup=False, one_time_keyboard=True):
    deferred.defer(tell,chat_id, msg, kb=kb, markdown=markdown,
                   inlineKeyboardMarkup=inlineKeyboardMarkup, one_time_keyboard=one_time_keyboard,
                   _queue="messages-queue")


def tell(chat_id, msg, kb=None, markdown=True, inlineKeyboardMarkup=False,
         one_time_keyboard=True, sleepDelay=False):
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
        resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
            'chat_id': chat_id,
            'text': msg,  # .encode('utf-8'),
            'disable_web_page_preview': 'true',
            'parse_mode': 'Markdown' if markdown else '',
            # 'reply_to_message_id': str(message_id),
            'reply_markup': json.dumps(replyMarkup),
        })).read()
        logging.info('send response: ')
        logging.info(resp)
    except urllib2.HTTPError, err:
        if err.code == 403:
            p = person.getPersonByChatId(chat_id)
            p.setEnabled(False)
            logging.info('Disabled user: ' + p.name.encode('utf-8') + ' ' + str(chat_id))
    if sleepDelay:
        sleep(0.1)

# ================================
# RESTART
# ================================
def restart(p, msg=None):
    if msg:
        tell(p.chat_id, msg)
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
        tell(p.chat_id, "Si è verificato un problema (" + methodName +
              "). Segnalamelo mandando una messaggio a @kercos" + '\n' +
              "Ora verrai reindirizzato/a nella schermata iniziale.")
        restart(p)
    else:
        method(p, **kwargs)


# ================================
# GO TO STATE 0: Initial Screen
# ================================

def goToState0(p, **kwargs):
    input = kwargs['input'] if 'input' in kwargs.keys() else None
    giveInstruction = input is None
    if giveInstruction:
        reply_txt = 'Hi {0}, press 🕹 if you want to play!'.format(p.getName())

        kb = [
            [BUTTON_GAME],
            [BUTTON_INFO]
        ]

        tell(p.chat_id, reply_txt, kb)
    else:
        if input == '':
            tell(p.chat_id, "Not a valid input.")
        elif input == BUTTON_GAME:
            redirectToState(p, 1)
        elif input == BUTTON_INFO:
            tell(p.chat_id, INFO_TEXT)
        else:
            tell(p.chat_id, FROWNING_FACE + " Sorry, I don't understand what you have input")

# ================================
# GO TO STATE 1: GAME
# ================================

GAME_INSTRUCTIONS = \
"""
I've chosen the following sentence for you:

{0}

Select an option from the following list which is a synonym of the word{1} in bold text ({2}).
"""

def goToState1(p, **kwargs):
    input = kwargs['input'] if 'input' in kwargs.keys() else None
    giveInstruction = input is None
    if giveInstruction:
        exerciseId, sentence, wordIndexToReplace, wordsToReplace, falseSynonymes, trueSynonymes = exercise.getRandomExercise()
        sentenceWithBoldWord = getSentenceWithBoldedWord(sentence, wordIndexToReplace, wordsToReplace)
        plural = 's' if len(wordsToReplace.split()) > 1 else ''
        instructions = GAME_INSTRUCTIONS.format(sentenceWithBoldWord, plural, wordsToReplace)
        options = falseSynonymes + trueSynonymes
        random.shuffle(options)
        options_text = [BULLET_POINT + ' /' + str(n) + ': ' + x for n, x in enumerate(options, 1)]
        instructions += '\n'.join(options_text)
        number_buttons = [str(x) for x in range(1,len(options)+1)]
        kb = utility.distributeElementMaxSize(number_buttons)
        kb.append([BUTTON_EXIT])
        tell(p.chat_id, instructions, kb, one_time_keyboard=False)
        p.setLastExerciseIdAndOptions(exerciseId, options)
    else:
        if input == '':
            tell(p.chat_id, "Not a valid input.")
        elif input == BUTTON_EXIT:
            restart(p)
        elif input == BUTTON_NEXT_SENTENCE:
            repeatState(p)
        else:
            exerciseId, exerciseOptions = p.getLastExerciseIdAndOptions()
            exerciseId, sentence, wordIndexToReplace, wordsToReplace, falseSynonymes, trueSynonymes = exercise.getExercizeId(exerciseId)
            if input.startswith('/'):
                input = input[1:]
            if utility.representsIntBetween(input, 1, len(exerciseOptions)+1):
                number = int(input)
                chosenWord = exerciseOptions[number - 1]
            else:
                #tell(p.chat_id, FROWNING_FACE + " Sorry, I don't understand what you have input")
                chosenWord = input
            msg = "You have chosen *{0}*.\n".format(chosenWord)
            sleep(1)
            if chosenWord in trueSynonymes:
                msg += "😄 Great, your answer is correct!"
                kb = [[BUTTON_NEXT_SENTENCE], [BUTTON_EXIT]]
                tell(p.chat_id, msg, kb)
            else:
                msg += "🙁 I'm sorry, your answer is NOT correct, try again"
                tell(p.chat_id, msg)

def getSentenceWithBoldedWord(sentence, wordIndexToReplace, wordsToReplace):
    words = sentence.split()
    logging.debug("Split words: " + str(words))
    numberOfWordsToReplace = len(wordsToReplace.split())
    for i in range(wordIndexToReplace, wordIndexToReplace+numberOfWordsToReplace):
        words[i] = '*' + words[i] + '*'
    logging.debug("Chosend index: {0}. Word: {1} ".format(str(wordIndexToReplace), words[wordIndexToReplace]))
    return ' '.join(words)

# ================================
# ================================
# ================================


class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(
                json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))



# ================================
# ================================
# ================================


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

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
        text = message.get('text').encode('utf-8') if "text" in message else ''
        name = chat["first_name"].encode('utf-8')
        last_name = chat["last_name"].encode('utf-8') if "last_name" in chat else None
        username = chat["username"] if "username" in chat else None
        location = message["location"] if "location" in message else None
        contact = message["contact"] if "contact" in message else None

        # u'contact': {u'phone_number': u'393496521697', u'first_name': u'Federico', u'last_name': u'Sangati',
        #             u'user_id': 130870321}
        # logging.debug('location: ' + str(location))

        def reply(msg=None, kb=None, markdown=False, inlineKeyboardMarkup=False):
            tell(chat_id, msg, kb, markdown, inlineKeyboardMarkup)

        p = person.getPersonByChatId(chat_id)

        if p is None:
            # new user
            logging.info("Text: " + text)
            if text == '/help':
                reply(ISTRUZIONI)
            elif text.startswith("/start"):
                tell_masters("New user: " + name)
                p = person.addPerson(chat_id, name, last_name, username)
                reply("Ciao {0}, welcome in LingoGameBot!".format(name))
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
                repeatState(p, input=text, contact=contact)


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    #    ('/_ah/channel/connected/', DashboardConnectedHandler),
    #    ('/_ah/channel/disconnected/', DashboardDisconnectedHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)

possibles = globals().copy()
possibles.update(locals())
