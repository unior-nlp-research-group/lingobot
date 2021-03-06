import telegram
import telegram.error
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
# from main_exception import retry_on_network_error
import key
import logging
import traceback
import time
import ndb_person
from ndb_person import Person
import ndb_utils
from ndb_utils import client_context

BOT = telegram.Bot(token=key.TELEGRAM_TOKEN)

def get_chat_id(p):
    return p if isinstance(p, int) else p.chat_id

'''
If kb==None keep last keyboard
'''
# @retry_on_network_error
def send_message(p, text, kb=None, markdown=True, remove_keyboard=False, \
    inline_keyboard=False, sleep=False, **kwargs):

    if kb or remove_keyboard:
        if inline_keyboard:
            reply_markup = {  
                'inline_keyboard': kb
            }
        elif remove_keyboard:
            p.set_keyboard(kb=[])            
            reply_markup = telegram.ReplyKeyboardRemove()
        else:
            p.set_keyboard(kb)
            reply_markup = telegram.ReplyKeyboardMarkup(kb, resize_keyboard=True)
        BOT.send_message(
            chat_id = get_chat_id(p),
            text = text,
            parse_mode = telegram.ParseMode.MARKDOWN if markdown else None,
            reply_markup = reply_markup,
            **kwargs
        )
    else:
        try:
            BOT.send_message(
                chat_id = get_chat_id(p),
                text = text,
                parse_mode = telegram.ParseMode.MARKDOWN if markdown else None,
                **kwargs
            )
        except Unauthorized:
            logging.debug('User has blocked Bot: {}'.format(get_chat_id(p)))
            p.switch_notifications()
            return False
        except TelegramError as e:
            logging.debug('Exception in reaching user {}: {}'.format(get_chat_id(p), e))
            p.switch_notifications()
            return False
    if sleep:
        time.sleep(0.1)
    return True

def send_location(p, lat, lon):
    loc = telegram.Location(lon,lat)
    BOT.send_location(get_chat_id(p), location = loc)

def send_typing_action(p, sleep_time=None):    
    BOT.sendChatAction(
        chat_id = get_chat_id(p),
        action = telegram.ChatAction.TYPING
    )
    if sleep_time:
        time.sleep(sleep_time)


def send_media_url(p, url_attachment, kb=None, caption=None):
    attach_type = url_attachment.split('.')[-1].lower()            
    if attach_type in ['jpg','png','jpeg']:
        BOT.send_photo(get_chat_id(p), photo=url_attachment, caption=caption)
    elif attach_type in ['mp3']:
        BOT.send_audio(get_chat_id(p), audio=url_attachment, caption=caption)
    elif attach_type in ['ogg']:
        BOT.send_voice(get_chat_id(p), voice=url_attachment, caption=caption)       
    elif attach_type in ['gif']:        
        BOT.send_animation(get_chat_id(p), animation=url_attachment, caption=caption)
    elif attach_type in ['mp4']:
        BOT.send_audio(get_chat_id(p), audio=url_attachment, caption=caption)
    else:            
        error_msg = "Found attach_type: {}".format(attach_type)
        logging.error(error_msg)
        raise ValueError('Wrong attach type: {}'.format(error_msg))

def send_text_document(p, file_name, file_content):
    import requests
    files = [('document', (file_name, file_content, 'text/plain'))]
    data = {'chat_id': get_chat_id(p)}
    resp = requests.post(key.TELEGRAM_API_URL + 'sendDocument', data=data, files=files)
    logging.debug("Sent documnet. Response status code: {}".format(resp.status_code))

def send_photo_from_data(p, file_name, file_data, caption=None, sleep=False):
    import requests
    files = [('photo', (file_name, file_data, 'image/png'))]
    data = {'chat_id': get_chat_id(p)}
    if caption:
        data['caption'] = caption
    resp = requests.post(key.TELEGRAM_API_URL + 'sendPhoto', data=data, files=files)
    logging.debug('Sent photo. Response status code: {}'.format(resp.status_code))
    if sleep:
        time.sleep(0.1)


def get_photo_url_from_telegram(file_id):
    import requests
    r = requests.post(key.TELEGRAM_API_URL + 'getFile', data={'file_id': file_id})
    r_json = r.json()
    r_result = r_json['result']
    file_path = r_result['file_path']
    url = key.TELEGRAM_BASE_URL_FILE + file_path
    return url

def tell_admin(message):
    max_length = 2000    
    for uid in key.ADMIN_IDS:
        if len(message)>max_length:
            chunks = (message[0+i:max_length+i] for i in range(0, len(message), max_length))
            for m in chunks:
                send_message(uid, m, markdown=False)    
        else:
            send_message(uid, message, markdown=False)

import utility

# ---------
# BROADCAST
# ---------

BROADCAST_COUNT_REPORT = utility.unindent(
    """
    Messaggio inviato a {} persone
    Ricevuto da: {}
    Non rivevuto da : {} (hanno disattivato il bot)
    """
)

def broadcast(sender, msg, qry = None, blackList_sender=False, sendNotification=True, test=False):

    from bot_telegram_dialogue import restart
    if qry is None:
        qry = Person.query()
    qry = qry.order(Person._key) #_MultiQuery with cursors requires __key__ order

    more = True
    cursor = None
    total, enabledCount = 0, 0

    while more:
        users, cursor, more = qry.fetch_page(100, start_cursor=cursor)
        for p in users:
            if not p.enabled:
                continue
            if get_chat_id(p)[0] == '-': # negative id for groups
                continue
            if test and not p.is_manager():
                continue
            if blackList_sender and sender and p.get_id() == sender.get_id():
                continue
            total += 1
            if send_message(p, msg, sleepDelay=True): #p.enabled
                enabledCount += 1

    disabled = total - enabledCount
    msg_debug = BROADCAST_COUNT_REPORT.format(total, enabledCount, disabled)
    logging.debug(msg_debug)
    if sendNotification:
        send_message(sender, msg_debug)
    #return total, enabledCount, disabled

# ---------
# Restart All
# ---------

def reset_all_users(qry = None, message=None):
    from bot_telegram_dialogue import restart
    if qry is None:
        qry = Person.query()
    qry = qry.order(Person._key)  # _MultiQuery with cursors requires __key__ order

    more = True
    cursor = None
    total = 0

    while more:
        users, cursor, more = qry.fetch_page(100, start_cursor=cursor)
        for p in users:
            if p.state == 'state_INITIAL':
                continue
            if p.enabled:
                total += 1
                if message:
                    send_message(p, message, remove_keyboard=True)
                p.reset_tmp_variables()
                restart(p)
                time.sleep(0.2)

    msg_admin = 'Resetted {} users.'.format(total)
    tell_admin(msg_admin)

