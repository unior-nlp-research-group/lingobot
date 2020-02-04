import api

default_language_interface = 'EN'
default_language_exercise = 'EN'

SUPPORTED_LANGUAGES = [x.upper() for x in api.get_exercise_languages()]

#todo: must query API: 
# http://cognition-srv1.ouc.ac.cy/nvt/webservice/api.php?method=get_exercise_languages

LANGUAGES = {
    'EN': {
        'flag': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
        'lang': 'ENGLISH'
    },
    'FI': {
        'flag': '🇫🇮',
        'lang': 'FINNISH'
    },
    'FR': {
        'flag': '🇫🇷',
        'lang': 'FRENCH'
    },
    'DE': {
        'flag': '🇩🇪',
        'lang': 'GERMAN'
    },
    'EL': {
        'flag': '🇬🇷',
        'lang': 'GREEK'
    }, 
    'IT': {
        'flag': '🇮🇹',
        'lang': 'ITALIAN'
    }, 
    'PT': {
        'flag': '🇵🇹',
        'lang': 'PORTUGUESE'
    }, 
    'RO': {
        'flag': '🇷🇴',
        'lang': 'ROMANIAN'    
    }, 
    'RU': {
        'flag': '🇷🇺',
        'lang': 'RUSSIAN'
    }, 
    'SH': {
        'flag': '🇧🇦🇭🇷🇲🇪🇷🇸',
        'lang': 'SERBO-CROATIAN'
    }, 
    'CS': {
        'flag': '🇨🇿',
        'lang': 'CZECH'
    }, 
}

LANGUAGES = {k:v for k,v in LANGUAGES.items() if k in SUPPORTED_LANGUAGES}