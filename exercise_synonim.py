# -*- coding: utf-8 -*-

import urllib2
import csv
import logging
import random
from utility import fixWhiteSpaces

from google.appengine.ext import ndb

EXERCISE_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/" \
                       "1qWCkGkIoR2ZDmSd3O31fMnNy1iTytHNMNrrTLxwdhnQ/" \
                       "export?format=tsv" \
                       "&gid=806141225"


def getExercisesFromUrl():
    languageStructure = {}
    try:
        spreadSheetTsv = urllib2.urlopen(EXERCISE_SPREADSHEET_URL)
        spreadSheetReader = csv.reader(spreadSheetTsv, delimiter='\t')
        next(spreadSheetReader)  # skip first row
        for row in spreadSheetReader:
            lang_code = row[2].strip()
            if lang_code:
                exercise_id = int(row[0].strip())
                entryItem = {}
                entryItem["Words to replace"] = fixWhiteSpaces(row[1].strip())
                entryItem["Word Index"] = int(row[2].strip())-1
                entryItem["True Synonymes"] = [fixWhiteSpaces(x.strip()) for x in row[3].split(',') if x.strip() != '']
                entryItem["False Synonymes"] = [fixWhiteSpaces(x.strip()) for x in row[4].split(',') if x.strip() != '']
                entryItem["Sentence"] = fixWhiteSpaces(row[5].strip())
                languageStructure[exercise_id] = entryItem
    except Exception, e:
        logging.debug("Problem retreiving language structure from url: " + str(e))
    return languageStructure

EXERCISES = getExercisesFromUrl()

def getExercizeId(exerciseId):
    if exerciseId in EXERCISES.keys():
        entryItem = EXERCISES[exerciseId]
        sentence = entryItem["Sentence"]
        wordsToReplace = entryItem["Words to replace"]
        wordIndexToReplace = entryItem["Word Index"]
        falseSynonymes = entryItem["False Synonymes"]
        trueSynonymes = entryItem["True Synonymes"]
        result = exerciseId, sentence, wordIndexToReplace, wordsToReplace, falseSynonymes, trueSynonymes
        logging.debug("Chosen exercise: " + str(result))
        return result
    return None

def getRandomExercise():
    randomId = random.choice(EXERCISES.keys())
    return getExercizeId(randomId)

