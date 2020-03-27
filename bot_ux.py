import key
import utility
import json

LANG_DICT = None
LANG_UX_ERRORS = None

def check_consistencies(write_to_file=False):
    from collections import defaultdict    
    from params import LANGUAGES
    import string    
    
    global LANG_UX_ERRORS
    LANG_UX_ERRORS = defaultdict(lambda: defaultdict(list))        
    
    punct = [p for p in string.punctuation if p!='*']
    final_punct = lambda s: s[-1] if s and s[-1] in punct else None    
    for k,d in LANG_DICT.items():
        num_inputs = d['EN'].count('{}')
        num_stars = d['EN'].count('*')
        end_punct = final_punct(d['EN'])
        wrong_lang_empty = [l for l,s in d.items() if len(s)==0 if l in LANGUAGES]
        wrong_lang_inputs = [l for l,s in d.items() if s and s.count('{}')!=num_inputs if l in LANGUAGES]        
        wrong_lang_stars = [l for l,s in d.items() if s and s.count('*')!=num_stars if l in LANGUAGES]
        wrong_lang_ending_punct = [l for l,s in d.items() if s and final_punct(s) != end_punct if l in LANGUAGES]
        wrong_empty_msg = 'Missing string for {}'.format(k)
        wrong_inputs_msg = 'Wrong number of inputs ({1}) for {0}'.format(k, '{}')        
        wrong_stars_msg = 'Wrong number of * in {}'.format(k)
        wrong_ending_punct_msg = 'Inconsistent punctuation ending for {}'.format(k)
        for l in wrong_lang_empty:
            LANG_UX_ERRORS[l]['MISSING'].append(wrong_empty_msg)
        for l in wrong_lang_inputs:
            LANG_UX_ERRORS[l]['ERRORS ({})'].append(wrong_inputs_msg)
        for l in wrong_lang_stars:
            LANG_UX_ERRORS[l]['ERRORS (*)'].append(wrong_stars_msg)
        for l in wrong_lang_ending_punct:
            LANG_UX_ERRORS[l]['PUNCTUATION WARNINGS'].append(wrong_ending_punct_msg)
    if write_to_file:
        from json2html import json2html
        with open('./tmp/consistency_check.json', 'w') as f_out:
            json.dump(LANG_UX_ERRORS, f_out, indent=3, sort_keys=True, ensure_ascii=False)
        with open('./tmp/consistency_check.html', 'w') as f_out:
            f_out.write(json2html.convert(json = LANG_UX_ERRORS))

def get_error_for_lang(p):
    lang = p.language_interface
    if LANG_UX_ERRORS[lang]:
        num_problems = sum(len(LANG_UX_ERRORS[lang][x]) for x in LANG_UX_ERRORS[lang])
        msg = '⚠️ {} Localization problems for language {}\n'.format(num_problems, lang)
        msg += 'For more details go to {}/localization?lang={}'.format(key.APP_BASE_URL, lang)
        return msg
    return "👍 No localization problems for language {}".format(lang)

def get_html_errors():
    from json2html import json2html
    return json2html.convert(json = LANG_UX_ERRORS)

def get_html_error_for_lang(lang):
    from json2html import json2html
    if LANG_UX_ERRORS[lang]:
        return json2html.convert(json = LANG_UX_ERRORS[lang])
    return "👍 No localization problems for language {}".format(lang)

def reload_ux():
    global LANG_DICT

    LANG_DICT = utility.get_google_spreadsheet_dict_list(
        key.LOCATIZATION_GDOC_KEY, 
        key.LOCATIZATION_GDOC_GID
    )

    LANG_DICT = {
        c['VARIABLE']: {k:v for k,v in c.items() if k!='VARIABLE'} for c in LANG_DICT
    }

    check_consistencies()

reload_ux()

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

if __name__ == '__main__':
    check_consistencies(write_to_file=True)
    