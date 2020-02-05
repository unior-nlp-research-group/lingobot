import api

default_level = 'C1'
default_relation = 'RelatedTo'
default_language_interface = 'EN'
default_language_exercise = 'EN'

SUPPORTED_LANGUAGES = [x.upper() for x in api.get_exercise_languages()]

#todo: must query API: 
# http://cognition-srv1.ouc.ac.cy/nvt/webservice/api.php?method=get_exercise_languages

LANGUAGES = {
    'EN': {
        'flag': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
        'en_lang': 'ENGLISH'
    },
    'FI': {
        'flag': '🇫🇮',
        'en_lang': 'FINNISH'
    },
    'FR': {
        'flag': '🇫🇷',
        'en_lang': 'FRENCH'
    },
    'DE': {
        'flag': '🇩🇪',
        'en_lang': 'GERMAN'
    },
    'EL': {
        'flag': '🇬🇷',
        'en_lang': 'GREEK'
    }, 
    'IT': {
        'flag': '🇮🇹',
        'en_lang': 'ITALIAN'
    }, 
    'PT': {
        'flag': '🇵🇹',
        'en_lang': 'PORTUGUESE'
    }, 
    'RO': {
        'flag': '🇷🇴',
        'en_lang': 'ROMANIAN'    
    }, 
    'RU': {
        'flag': '🇷🇺',
        'en_lang': 'RUSSIAN'
    }, 
    'SH': {
        'flag': '🇧🇦🇭🇷🇲🇪🇷🇸',
        'en_lang': 'SERBO-CROATIAN'
    }, 
    'CS': {
        'flag': '🇨🇿',
        'en_lang': 'CZECH'
    }, 
}

LANGUAGES = {k:v for k,v in LANGUAGES.items() if k in SUPPORTED_LANGUAGES}