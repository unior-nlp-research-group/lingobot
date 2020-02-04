import logging
import bot_telegram
from bot_telegram import BOT, send_message, send_location, send_typing_action, \
    report_master, send_text_document, send_media_url, \
    broadcast, tell_admin, reset_all_users
import utility
import telegram
import ndb_person
from ndb_person import Person
from ndb_utils import client_context
import params
import key
import json
import random
import api
from params import LANGUAGES
import bot_ux
import re

# ================================
# CONFIG
# ================================
WORK_IN_PROGRESS = False


# ================================
# RESTART
# ================================
def restart_multi(users):
    for u in users:
        redirect_to_state(u, state_INITIAL)

def restart(user):
    redirect_to_state(user, state_INITIAL)

# ================================
# REDIRECT TO STATE
# ================================
def redirect_to_state(user, new_function, message_obj=None):
    new_state = new_function.__name__
    if user.state != new_state:
        logging.debug("In redirect_to_state. current_state:{0}, new_state: {1}".format(str(user.state), str(new_state)))
        user.set_state(new_state)
    repeat_state(user, message_obj)


# ================================
# REPEAT STATE
# ================================
def repeat_state(user, message_obj=None):
    state = user.state
    if state is None:
        restart(user)
        return
    method = possibles.get(state, None)
    if not method:
        msg = "⚠️ User {} sent to unknown method state: {}".format(user.get_name_last_name_username(), state)
        report_master(msg)
        restart(user)
    else:
        method(user, message_obj)

# ================================
# Initial State
# ================================

def state_INITIAL(p, message_obj=None, **kwargs):    
    if message_obj is None:
        kb = [
            [p.ux().BUTTON_VOCAB_GAME],
            [p.ux().BUTTON_POINTS, p.ux().BUTTON_LEADERBOARD],
            [p.ux().BUTTON_CHANGE_LANGUAGE, p.ux().BUTTON_INFO]
        ]
        new_notifications_number = api.update_notifications(p)
        if new_notifications_number>0:
            #send_message(p, "New notification!!")
            p.ux().BUTTON_NUM_NOTIFICATIONS = '{} ({})'.format('🌟', new_notifications_number)
            kb[1].insert(1, p.ux().BUTTON_NUM_NOTIFICATIONS)
        lang = p.language_exercise if p.language_exercise in LANGUAGES else 'en'
        lang_info = LANGUAGES[lang]
        flag_lang = '{} {}'.format(lang_info['flag'],lang_info['lang'])
        send_message(p, p.ux().MSG_LETS_PLAY.format(flag_lang), kb)
    else: 
        text_input = message_obj.text
        kb = p.get_keyboard()
        if text_input in utility.flatten(kb):
            if text_input == p.ux().BUTTON_VOCAB_GAME:
                redirect_to_exercise_type(p)            
            elif text_input.startswith('🌟'):
                notifications = p.get_variable('notifications')
                logging.debug("New notifications: {}".format(notifications))
                if len(notifications) > 0:
                    notifications_str = '\n'.join(["{} {}: {}".format( # → {}
                        '🏅' if r['badge'] else '•', 
                        r['exercise'],
                        r['response']) for r in notifications]  #r['exercise']
                    )
                    msg = p.ux().MSG_NEW_NOTIFICATIONS.format(notifications_str)
                    send_message(p, msg)
                    p.set_variable('notifications', [])
                    repeat_state(p)
                else:
                    send_message(p, p.ux().MSG_NO_NEW_POINTS)
            elif text_input == p.ux().BUTTON_POINTS:
                response = api.get_points(p.user_telegram_id())
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
                send_message(p, msg, kb)
            elif text_input == p.ux().BUTTON_LEADERBOARD:
                leaderboard = api.get_leaderboard()
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
                bot_telegram.send_photo_from_data(p.chat_id, 'leaderboard.png', imgData)
            elif text_input == p.ux().BUTTON_INFO:            
                msg = (
                    "Vocabulary trainer on word relations for vocabulary of level C1."
                    "\nRelated-to words can be single words or multiword expressions of any word class."
                    "\n\nYour telegram id: {}"
                ).format(p.chat_id)
                send_message(p, msg, kb)
            elif text_input == p.ux().BUTTON_CHANGE_LANGUAGE:
                redirect_to_state(p, state_CHANGE_LANGUAGE)
            else:
                assert False
        else:
            send_message(p, p.ux().MSG_NOT_VALID_INPUT)

def redirect_to_exercise_type(p):
    type_of_exercise = api.choose_exercise(p.user_telegram_id())["exercise_type"]
    assert type_of_exercise in ['open','close']
    logging.debug("New exercise of type: {}".format(type_of_exercise))
    if type_of_exercise=='open':
        # first_time_instructions = "Let’s play some vocabulary game!"
        # send_message(p, first_time_instructions)
        redirect_to_state(p, state_OPEN_EXERCISE)
    else:
        redirect_to_state(p, state_CLOSE_EXERCISE)


# ================================
# CHANGE LANGUAGE
# ================================

def state_CHANGE_LANGUAGE(p, message_obj=None, **kwargs):    
    give_instruction = message_obj is None
    language_list = [
        '{} {}'.format(v['flag'],v['lang'])
        for k,v in sorted(LANGUAGES.items(), key=lambda x:x[1]['lang'])
        if k != p.language_exercise
    ]
    if give_instruction:
        kb = [[b] for b in language_list]
        kb.insert(0, [p.ux().BUTTON_CANCEL])
        kb.append([p.ux().BUTTON_CANCEL])
        lang = p.language_exercise if p.language_exercise in LANGUAGES else 'en'
        lang_info = LANGUAGES[lang]
        flag_lang = '{} {}'.format(lang_info['flag'],lang_info['lang'])
        reply_txt = "Your are learning {}.\nPlease select a new language you want to learn.".format(flag_lang)
        send_message(p, reply_txt, kb)
    else:
        text_input = message_obj.text
        kb = p.get_keyboard()
        if text_input in utility.flatten(kb):
            if text_input in language_list:
                lang = next(k for k,v in LANGUAGES.items() if text_input == '{} {}'.format(v['flag'],v['lang']))
                p.set_language_exercise(lang)
                p.set_language_interface(lang)
                api.update_user(p.user_telegram_id(), p.name, language_exercise=lang, language_interface=lang)
                restart(p)
            elif text_input == p.ux().BUTTON_CANCEL:
                restart(p)
            else: 
                assert False
        else:
            send_message(p, p.ux().MSG_NOT_VALID_INPUT)

# ================================
# OPEN EXERCISE
# ================================

def state_OPEN_EXERCISE(p, message_obj=None, **kwargs):    
    give_instruction = message_obj is None
    user_telegram_id = p.user_telegram_id()
    if give_instruction:
        kb = [[p.ux().BUTTON_DONT_KNOW],[p.ux().BUTTON_EXIT]]
        response = api.get_exercise(user_telegram_id) #elevel='', etype=''        
        # send_message(key.FEDE_CHAT_ID, 'DEBUG:\n{}'.format(json.dumps(response)), markdown=False)
        if response is None:
            report_msg = "None response in get_exercise ({})".format(user_telegram_id)
            send_message(key.FEDE_CHAT_ID, report_msg, markdown=False)
            send_message(p, p.ux().MSG_AN_ERROR_HAS_OCCURED)
            return
        if response.get('success', True) == False:
            report_msg = 'Detected success false in get_exercise ({})'.format(user_telegram_id)
            send_message(key.FEDE_CHAT_ID, report_msg, markdown=False)
            send_message(p, p.ux().MSG_AN_ERROR_HAS_OCCURED)
            return
        r_eid = response['eid']
        wiki_url = response.get('hint_url', None)
        exercise = response['exercise'] # "exercise": "Name a thing that is located at a desk",                
        subject = response['subject']
        # exercise = exercise[:exercise.rfind(subject)] + '*{}*'.format(subject)
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
            kb.insert(1, BUTTON_NUM_NOTIFICATIONS)
        send_message(p, msg, kb)    
    else:
        text_input = message_obj.text
        kb = p.get_keyboard()
        eid = p.get_variable('eid')        
        if text_input in utility.flatten(kb):            
            if text_input == p.ux().BUTTON_EXIT:
                restart(p)
            elif text_input == p.ux().BUTTON_DONT_KNOW:
                response_json = api.get_random_response(eid, user_telegram_id)
                msg = "No worries, a possible response would have been *{}*.".format(response_json['response'])
                send_message(p, msg, sleepDelay=True, remove_keyboard=True)            
                send_typing_action(p, sleep_time=1)
                exercise = p.get_variable('exercise')
                send_message(p, exercise, kb)  
                # repeat the same question and stay in current state
            elif text_input.startswith('🌟'):
                notifications = p.get_variable('notifications')
                logging.debug("New notifications: {}".format(notifications))
                if len(notifications) > 0:
                    notifications_str = '\n'.join(["{} {}: {}".format( # → {}
                        '🏅' if r['badge'] else '•', 
                        r['exercise'],
                        r['response']) for r in notifications]  #r['exercise']
                    )
                    msg = "New potential points converted to real points:\n{}".format(notifications_str)
                    send_message(p, msg, kb)
                    p.set_variable('notifications', [])
                    repeat_state(p)                
                else:
                    send_message(p, msg, p.ux().MSG_NO_NEW_POINTS)   
                send_typing_action(p, sleep_time=1)
                exercise = p.get_variable('exercise')
                send_message(p, exercise, kb)  
            else: 
                assert False
        else:                
            subject = p.get_variable('subject') 
            if text_input == subject:
                msg = "❌ You have inserted the same word of the exercise (*{}*)".format(subject)
                send_message(p, msg, sleepDelay=True, remove_keyboard=True)            
                send_typing_action(p, sleep_time=1)
                exercise = p.get_variable('exercise')
                send_message(p, exercise, kb)  
                return
            response = api.store_response(eid, user_telegram_id, text_input)
            # send_message(key.FEDE_CHAT_ID, 'DEBUG:\n{}'.format(json.dumps(response)), markdown=False)
            logging.debug("Response from store_response eid={}, user_telegram_id={}, text_input={}: {}".format(eid, user_telegram_id, text_input, response))            
            if 'points' in response:
                r_points = response['points']
                points_str = '*{} points*'.format(r_points) if r_points and r_points>1 else '*1 point*'
                if r_points is None:
                    msg = utility.unindent(
                        '''
                        You have inserted *{}*. Thanks for your answer!\n 
                        🤞 This is a potential double point you can earn in the future if enough people confirm it!
                        '''.format(text_input)
                    )                
                elif r_points>0:
                    msg = utility.unindent(
                        '''
                        You have inserted *{}*.\n
                        👍 Good job! You earned {}
                        '''.format(text_input, points_str)
                    )
                elif r_points == 0:
                    msg = utility.unindent(
                        '''
                        You have inserted *{}*.\n 
                        🙄 You get 0 points:  you have already entered this answer!
                        '''.format(text_input)
                    )                
                send_message(p, msg)
            else:
                # debugging
                error_msg = response['error']
                msg = 'Backend found an error: {}.\nPlease report this to @kercos'.format(error_msg)
                send_message(p, msg)
            send_typing_action(p, sleep_time=1)    
            redirect_to_exercise_type(p)            


def get_notification_button(p, debug=False):
    new_notifications_number = api.update_notifications(p)
    if new_notifications_number>0:
        #send_message(p, "New notification!!")
        BUTTON_NUM_NOTIFICATIONS = '{} ({})'.format('🌟', new_notifications_number)
        return BUTTON_NUM_NOTIFICATIONS
    elif debug and random.choice([True, False]):
        # testing if it works
        BUTTON_NUM_NOTIFICATIONS = '{} ({})'.format('🌟', 0)
        return BUTTON_NUM_NOTIFICATIONS
    return None


# ================================
# CLOSE EXERCISE
# ================================

def state_CLOSE_EXERCISE(p, message_obj=None, **kwargs):    
    give_instruction = message_obj is None
    user_telegram_id = p.user_telegram_id()
    if give_instruction:        
        response = api.get_close_exercise(user_telegram_id) #elevel='', etype='RelatedTo'
        if response is None:
            report_msg = "None response in get_close_exercise ({})".format(user_telegram_id)
            send_message(key.FEDE_CHAT_ID, report_msg, markdown=False)
            send_message(p, p.ux().MSG_AN_ERROR_HAS_OCCURED)
            return
        if response.get('success', True) == False:
            report_msg = 'Detected success false in get_close_exercise ({})'.format(user_telegram_id)
            send_message(key.FEDE_CHAT_ID, report_msg, markdown=False)
            send_message(p, p.ux().MSG_AN_ERROR_HAS_OCCURED)
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
        kb = [[p.ux().BUTTON_YES, p.ux().BUTTON_NO], [p.ux().BUTTON_DONT_KNOW], [p.ux().BUTTON_EXIT]]
        send_message(p, msg, kb)  
    else:
        pass
        text_input = message_obj.text
        kb = p.get_keyboard()
        eid = p.get_variable('eid')
        if text_input in utility.flatten(kb):
            if text_input == p.ux().BUTTON_EXIT:
                restart(p)
            elif text_input.upper() in [p.ux().BUTTON_YES, 'YES', 'Y', p.ux().BUTTON_NO, 'NO', 'N', p.ux().BUTTON_DONT_KNOW]:
                response = 1 if text_input.upper() in [p.ux().BUTTON_YES, 'YES', 'Y'] \
                    else -1 if text_input.upper() in [p.ux().BUTTON_NO, 'NO', 'N'] \
                    else 0
                evalutaion_json = api.store_close_response(eid, user_telegram_id, response)
                if response==0:
                    correct_response = p.ux().BUTTON_YES if evalutaion_json['correct_response'] == 1 else p.ux().BUTTON_NO
                    msg = "💪 Don’t worry, the correct response was {}.".format(correct_response)    
                else:
                    correct = evalutaion_json['points']==1            
                    msg = "👍 Correct!" if correct else "👎 Wrong (according to the information we currently have)."
                send_message(p, msg, sleepDelay=True, remove_keyboard=True)            
                send_typing_action(p, sleep_time=1)
                # repeat_state(p)
                redirect_to_exercise_type(p)
            else: 
                assert False
        else:
            send_message(p, p.ux().MSG_NOT_VALID_INPUT)



## +++++ END OF STATES +++++ ###

# ================================
# ADMIN COMMANDS
# ================================

def deal_with_admin_commands(p, message_obj):
    text_input = message_obj.text
    if p.is_admin():
        if text_input == '/debug':
            #send_message(p, game.debugTmpVariables(p), markdown=False)
            send_text_document(p, 'tmp_vars.json', p.variables)
            return True
        # if text_input == '/testInlineKb':
        #     send_message(p, "Test inline keypboard", kb=[[p.bot_ux().BUTTON_YES_CALLBACK('test'), p.bot_ux().BUTTON_NO_CALLBACK('test')]], inline_keyboard=True)
        #     return True
        if text_input == '/random':
            from random import shuffle
            numbers = ['1','2','3','4','5']
            shuffle(numbers)
            numbers_str = ', '.join(numbers)
            send_message(p, numbers_str)
            return True
        if text_input == '/exception':
            1/0
            return True
        if text_input == '/wait':
            import time
            for i in range(5):
                send_message(p, str(i+1))
                time.sleep(i+1)
            send_message(p, "end")
            return True
        if text_input.startswith('/testText '):
            text = text_input.split(' ', 1)[1]
            msg = '🔔 *Messagge from LingoGame* 🔔\n\n' + text
            logging.debug("Test broadcast " + msg)
            send_message(p, msg)
            return True
        if text_input.startswith('/broadcast '):
            text = text_input.split(' ', 1)[1]
            msg = '🔔 *Messagge from LingoGame* 🔔\n\n' + text
            logging.debug("Starting to broadcast " + msg)
            broadcast(p, msg)
            return True
        if text_input.startswith('/textUser '):
            p_id, text = text_input.split(' ', 2)[1]
            p = Person.get_by_id(p_id)
            if send_message(p, text, kb=p.get_keyboard()):
                msg_admin = 'Message sent successfully to {}'.format(p.get_first_last_username())
                tell_admin(msg_admin)
            else:
                msg_admin = 'Problems sending message to {}'.format(p.get_first_last_username())
                tell_admin(msg_admin)
            return True
        if text_input.startswith('/restartUser '):
            p_id = ' '.join(text_input.split(' ')[1:])
            p = Person.get_by_id(p_id)
            if p:
                restart(p)
                msg_admin = 'User restarted: {}'.format(p.get_first_last_username())
                tell_admin(msg_admin)                
            else:
                msg_admin = 'No user found: {}'.format(p_id)
                tell_admin(msg_admin)
            return True
        if text_input == '/reset_all_users':            
            reset_all_users(message=None) #message=p.bot_ux().MSG_THANKS_FOR_PARTECIPATING
            return True
    return False

def deal_with_manager_commands(p, message_obj):
    text_input = message_obj.text
    # logging.debug("In deal_with_manager_commands with user:{} ismanager:{}".format(p.get_id(), p.is_manager()))
    if p.is_manager():
        if text_input == '/admin':
            msg = "No commands available for now.\n"
            send_message(p, msg, markdown=False)
            return True
        if text_input == '/info':
            return True
        # if text_input == '/update':
        #     p.ux().reload_ux()
        #     key.reload_config()
        #     send_message(p, p.bot_ux().MSG_RELOADED_CONFIG_TABLE)
        #     return True
        if text_input == '/stats':
            return True
        return False


def deal_with_universal_command(p, message_obj):
    text_input = message_obj.text
    if text_input.startswith('/start'):
        restart(p)
        return True
    if text_input == '/state':
        state = p.state
        msg = "You are in state {}".format(state)
        send_message(p, msg, markdown=False)
        return True
    if text_input == '/update':
        bot_ux.reload_ux()
        send_message(p, '💨 Reloaded translation table!', markdown=False)
        return True
    if text_input == '/refresh':
        repeat_state(p)
        return True
    if text_input in ['/help', 'HELP', 'AIUTO']:
        pass
        return True
    if text_input in ['/stop']:
        p.set_enabled(False, put=True)
        msg = "🚫 Hai *disabilitato* il bot.\n" \
              "In qualsiasi momento puoi riattivarmi scrivendomi qualcosa."
        send_message(p, msg)
        return True
    return False

# ================================
# DEAL WITH REQUEST
# ================================
@client_context
def deal_with_request(request_json):
    # retrieve the message in JSON and then transform it to Telegram object
    update_obj = telegram.Update.de_json(request_json, BOT)
    # if update_obj.callback_query:
    #     deal_with_callback_query(update_obj.callback_query)
    #     return 
    message_obj = update_obj.message    
    user_obj = message_obj.from_user
    chat_id = user_obj.id    
    username = user_obj.username
    last_name = user_obj.last_name if user_obj.last_name else ''
    name = (user_obj.first_name + ' ' + last_name).strip()
    # language = user_obj.language_code
    
    p = ndb_person.get_person_by_id(user_obj.id)
    user_name = 'telegram_{}'.format(chat_id)

    if not api.is_user_registered(user_name):
        api.add_user(user_name, name)

    if p == None:
        p = ndb_person.add_person(chat_id, name, last_name, username)
        report_master('New user: {}'.format(p.get_name_last_name_username()))
    else:
        p.update_user(name, last_name, username)

    if message_obj.forward_from and not p.is_manager():
        send_message(p, p.bot_ux().MSG_NO_FORWARDING_ALLOWED)
        return

    text = message_obj.text
    if text:
        text_input = message_obj.text        
        logging.debug('Message from @{} in state {} with text {}'.format(chat_id, p.state, text_input))
        if WORK_IN_PROGRESS and not p.is_manager():
            send_message(p, p.bot_ux().MSG_WORK_IN_PROGRESS)    
            return
        if deal_with_admin_commands(p, message_obj):
            return
        if deal_with_universal_command(p, message_obj):
            return
        if deal_with_manager_commands(p, message_obj):
            return
    logging.debug("Sending {} to state {} with input message_obj {}".format(p.get_name_last_name_username(), p.state, message_obj))
    repeat_state(p, message_obj=message_obj)

possibles = globals().copy()
possibles.update(locals())