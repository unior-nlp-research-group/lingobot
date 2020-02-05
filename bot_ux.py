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

def check_consistencies():
    for k,d in LANG_DICT.items():
        num_inputs = d['EN'].count('{}')
        end_char = d['EN'][-1]
        wrong_lang_inputs = [l for l,s in d.items() if s!='' and s.count('{}')!=num_inputs]
        wrong_lang_ending = [l for l,s in d.items() if s!='' and s[-1]!=end_char]
        if wrong_lang_inputs:
            print('Inconsistent inputs for {}: {}'.format(k, wrong_lang_inputs))
        if wrong_lang_ending:
            print('Inconsistent ending for {}: {}'.format(k, wrong_lang_ending))

class UX_LANG:
    
    def __init__(self, lang):
        self.lang = lang

    def __getattr__(self, attr):
        from params import LANGUAGES
        var_mapping = LANG_DICT.get(attr, {self.lang: '⚠️ {}'.format(attr)})
        var_mapping_lang = var_mapping[self.lang]
        if var_mapping_lang:
            return var_mapping_lang
        return var_mapping['EN']

    def __getitem__(self, attr):
        return self.__getattr__(attr)




