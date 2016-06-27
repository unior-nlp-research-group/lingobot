# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
import logging
import key


class Person(ndb.Model):
    chat_id = ndb.IntegerProperty()
    name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    username = ndb.StringProperty()
    state = ndb.IntegerProperty(default=-1, indexed=True)
    last_state  = ndb.IntegerProperty()
    last_mod = ndb.DateTimeProperty(auto_now=True)
    enabled = ndb.BooleanProperty(default=True)
    lastExerciseId = ndb.IntegerProperty()
    lastExerciseOptions = ndb.StringProperty(repeated=True)

    def getName(self):
        return self.name.encode('utf-8')

    def getLastName(self):
        return self.last_name.encode('utf-8') if self.last_name else '(null)'

    def getUsername(self):
        return self.username.encode('utf-8')

    def getNameLastName(self):
        return self.getName() + ' ' + self.getLastName()

    def getNameLastNameUserName(self):
        result = self.getNameLastName()
        if self.username:
            result += ' @' + self.getUsername()
        return result

    def setEnabled(self, enabled, put=False):
        self.enabled = enabled
        if put:
            self.put()

    def updateUsername(self, username, put=False):
        if (self.username!=username):
            self.username = username
            if put:
                self.put()

    def setState(self, newstate, put=True):
        self.last_state = self.state
        self.state = newstate
        if put:
            self.put()

    def isAdministrator(self):
        result = self.chat_id in key.AMMINISTRATORI_ID
        #logging.debug("Amministratore: " + str(result))
        return result

    def setLastExerciseIdAndOptions(self, exerciseId, options):
        self.lastExerciseId = exerciseId
        self.lastExerciseOptions = options
        self.put()

    def getLastExerciseIdAndOptions(self):
        options = [x.encode('utf-8') for x in self.lastExerciseOptions]
        return self.lastExerciseId, options

def addPerson(chat_id, name, last_name, username):
    p = Person(
        id=str(chat_id),
        chat_id=chat_id,
        name=name,
        last_name = last_name,
        username = username
    )
    p.put()
    return p

def getPersonByChatId(chat_id):
    return Person.get_by_id(str(chat_id))

def getPeopleWithLastName(lastName, number):
    lastName_uni = lastName.decode('utf-8')
    return Person.query(Person.last_name==lastName_uni).fetch(number)
