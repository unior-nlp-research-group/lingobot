import key
import utility

LANG_DICT = None

def reload_ux():
    global LANG_DICT

    LANG_DICT = utility.get_google_spreadsheet_dict_list(
        key.LOCATIZATION_GDOC_KEY, 
        key.LOCATIZATION_GDOC_GID
    )

    LANG_DICT = {
        c['VARIABLE']: {k:v for k,v in c.items() if k!='VARIABLE'} for c in LANG_DICT
    }

reload_ux()

class UX_LANG:
    
    def __init__(self, lang):
        self.lang = lang

    def __getattr__(self, attr):
        from params import LANGUAGES
        var_mapping = LANG_DICT.get(attr, {self.lang: '⚠️ MISSING {} IN TRANSLATION TABLE'.format(attr)})
        var_mapping_lang = var_mapping[self.lang]
        if var_mapping_lang:
            return var_mapping_lang
        # lang_name = LANGUAGES[self.lang]['lang']
        # return '{} translation for "{}"'.format(lang_name, var_mapping['EN'])
        return var_mapping['EN']



