# -*- coding: utf-8 -*-

import urllib2
import csv
import logging
import random

EXERCISE_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/" \
                       "1qWCkGkIoR2ZDmSd3O31fMnNy1iTytHNMNrrTLxwdhnQ/" \
                       "export?format=tsv" \
                       "&gid=1562228297"


def getExercisesFromUrl():
    try:
        spreadSheetTsv = urllib2.urlopen(EXERCISE_SPREADSHEET_URL)
    except Exception, e:
        logging.debug("Problem retreiving language structure from url: " + str(e))

    spreadSheetReader = csv.reader(spreadSheetTsv, delimiter='\t')
    pos_types = spreadSheetReader.next()
    pos_words = {pt:set() for pt in pos_types}
    for row in spreadSheetReader:
        for i, word in enumerate(row):
            pos_words[pos_types[i]].add(word)
    return set(pos_types), pos_words

POS_TYPES, POS_WORDS = getExercisesFromUrl()

def getExerciseWithIntruder():
    intruder_pos, correct_pos = random.sample(POS_TYPES, 2)
    intruder_word = random.sample(POS_WORDS[intruder_pos],1)
    correct_words = random.sample(POS_WORDS[correct_pos],3)
    options = intruder_word + correct_words
    random.shuffle(options)
    intruder_index = options.index(intruder_word[0])
    return intruder_index, options

def getExerciseWithoutIntruder():
    correct_pos = random.sample(POS_TYPES,1)[0]
    correct_words = random.sample(POS_WORDS[correct_pos],4)
    return -1, correct_words

def getRandomExercise():
    withIntruder = bool(random.getrandbits(1))
    if withIntruder:
        return getExerciseWithIntruder()
    return getExerciseWithoutIntruder()