from flask import Flask, Response, request, jsonify
import key

import logging
import google.cloud.logging
client = google.cloud.logging.Client()
# logging.debug #format='%(asctime)s  [%(levelname)s]: %(message)s'
client.setup_logging(log_level=logging.DEBUG)


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

@app.route('/')
def root():
    logging.debug("in root function")
    """Return a friendly HTTP greeting."""
    return "LingoGame!!", 200

@app.route('/localization', methods=['GET'])
def localization():
    from params import LANGUAGES
    import bot_ux
    lang = request.args.get('lang', '').upper()
    if lang and lang in LANGUAGES:
        return bot_ux.get_html_error_for_lang(lang)
    return bot_ux.get_html_errors()

@app.errorhandler(404)
def page_not_found(e):
    logging.debug("page_not_found")
    # note that we set the 404 status explicitly
    return "url not found", 404

@app.errorhandler(500)
def internal_error(error):
    return "500 error: {}".format(error), 500

@app.route(key.WEBHOOK_TELEGRAM_ROUTING, methods=['POST'])
def telegram_webhook_handler():
    from main_exception import run_new_thread_and_report_exception
    from bot_telegram_dialogue import deal_with_request    
    import json
    
    request_json = request.get_json(force=True)

    logging.debug("TELEGRAM POST REQUEST: {}".format(json.dumps(request_json)))

    run_new_thread_and_report_exception(deal_with_request, request_json)

    return '', 200
