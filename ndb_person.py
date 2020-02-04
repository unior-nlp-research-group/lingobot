from google.cloud import ndb
import logging
import key
import params
import bot_ux

class Person(ndb.Model):
    chat_id = ndb.IntegerProperty()
    name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    username = ndb.StringProperty()
    state = ndb.StringProperty(indexed=True)
    last_state  = ndb.StringProperty()
    last_mod = ndb.DateTimeProperty(auto_now=True)
    enabled = ndb.BooleanProperty(default=True)
    variables = ndb.JsonProperty(indexed=False)
    language_interface = ndb.StringProperty(default=params.default_language_interface)
    language_exercise = ndb.StringProperty(default=params.default_language_exercise)

    def user_telegram_id(self):
        return 'telegram_{}'.format(self.chat_id)

    def ux(self):
        return bot_ux.UX_LANG(self.language_interface)

    def get_name(self):
        return self.name

    def get_last_name(self):
        return self.last_name if self.last_name else ''

    def get_username(self):
        return self.username

    def get_name_last_name(self):
        return self.get_name() + ' ' + self.get_last_name()

    def get_name_last_name_username(self):
        result = self.get_name_last_name()
        if self.username:
            result += ' @' + self.get_username()
        return result

    def set_enabled(self, enabled, put=False):
        self.enabled = enabled
        if put:
            self.put()

    def update_user(self, name, last_name, username, put=False):
        import params
        changed = False
        if self.name!=name:
            self.name = name
            changed = True
        if self.last_name!=last_name:
            self.last_name = last_name
            changed = True
        if self.username!=username:
            self.username = username
            changed = True
        if self.language_exercise not in params.LANGUAGES:
            self.language_exercise = params.default_language_exercise
        if self.language_interface not in params.LANGUAGES:
            self.language_interface = params.default_language_interface
        if changed and put:
            self.put()

    def set_language_interface(self, lang):
        self.language_interface = lang

    def set_language_exercise(self, lang):
        self.language_exercise = lang

    def set_state(self, newstate, put=True):
        self.last_state = self.state
        self.state = newstate
        if put:
            self.put()

    def is_administrator(self):
        result = self.chat_id in key.ADMIN_IDS
        #logging.debug("Amministratore: " + str(result))
        return result

    def set_last_exercise_id_and_options(self, ex_id, options):
        self.set_variable('Exercise_ID', ex_id)
        self.set_variable('Exercise_Options', options)
        self.put()

    def get_last_exercise_id_and_options(self):
        options = [x for x in self.get_variable('Exercise_Options')]
        return self.get_variable('Exercise_ID'), options

    def set_keyboard(self, kb, put=True):
        self.set_variable("keyboard", kb, put=put)

    def get_keyboard(self):
        return self.get_variable("keyboard", [])

    def set_variable(self, var_key, var_value, put=True):
        self.variables[var_key] = var_value
        if put:
            self.put()
    
    def get_variable(self, var_key, default_value=None):
        return self.variables.get(var_key, default_value)

    def is_admin(self):
        import key
        return self.chat_id in key.ADMIN_IDS

    def is_manager(self):
        import key
        return self.chat_id in key.MANAGER_IDS


def add_person(chat_id, name, last_name, username):
    p = Person(
        id=str(chat_id),
        chat_id=chat_id,
        name=name,
        last_name = last_name,
        username = username,
        variables = {}
    )    
    p.put()
    return p


def get_person_by_id(chat_id):
    return Person.get_by_id(str(chat_id))