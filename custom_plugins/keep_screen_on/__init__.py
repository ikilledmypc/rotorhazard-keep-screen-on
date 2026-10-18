'''Keep Screen On: adds a button to every RotorHazard page that keeps the
viewing device's screen from sleeping (uses NoSleep.js, works over plain HTTP).'''

import json
import logging
import os

from flask import Blueprint, request
from RHUI import UIField, UIFieldType

logger = logging.getLogger(__name__)

SECTION = 'KeepScreenOn'
PANEL = 'keep_screen_on'
OPT_SHOW = 'show_button'
URL_PREFIX = '/keep_screen_on'
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))


def _read_version():
    try:
        with open(os.path.join(PLUGIN_DIR, 'manifest.json')) as f:
            return json.load(f).get('version', '0')
    except Exception:
        return '0'


SCRIPT_VERSION = _read_version()  # used as cache-buster for the injected scripts

# Pages that are not meant for interactive viewing (OBS/stream overlays, JSON, etc.)
SKIP_PREFIXES = ('/stream', '/api', '/socket.io', URL_PREFIX)


def _is_true(val):
    return not (val is None or val is False or val == 0 or val == '0' or val == ''
                or (isinstance(val, str) and val.lower() == 'false'))


def initialize(rhapi):
    rhapi.config.register_section(SECTION)

    rhapi.ui.register_panel(PANEL, 'Keep Screen On', 'settings')
    rhapi.fields.register_option(
        UIField(OPT_SHOW, 'Show keep-screen-on button', UIFieldType.CHECKBOX,
                value=True, persistent_section=SECTION,
                desc='Adds a floating button (bottom right) to every page. '
                     'Tap it on your phone to keep the screen awake.'),
        PANEL)
    rhapi.ui.register_markdown(PANEL, 'keep_screen_on_help',
        'Tap the round button in the bottom-right corner to toggle. '
        'Green = screen stays on. Amber = enabled on this device, tap anywhere '
        'on the page to resume (browsers need one tap after loading a page).')

    static_dir = os.path.join(PLUGIN_DIR, 'static')
    bp = Blueprint('keep_screen_on', __name__,
                   static_folder=static_dir,
                   static_url_path=URL_PREFIX + '/static')

    @bp.after_app_request
    def inject_script(response):
        try:
            if response.status_code != 200 or response.mimetype != 'text/html':
                return response
            if response.direct_passthrough or request.path.startswith(SKIP_PREFIXES):
                return response
            if not _is_true(rhapi.config.get(SECTION, OPT_SHOW)):
                return response
            body = response.get_data(as_text=True)
            idx = body.rfind('</body>')
            if idx == -1:
                return response
            tag = ('<script src="{0}/static/NoSleep.min.js?v={1}"></script>'
                   '<script src="{0}/static/keep_screen_on.js?v={1}"></script>'
                   ).format(URL_PREFIX, SCRIPT_VERSION)
            response.set_data(body[:idx] + tag + body[idx:])
        except Exception:
            logger.exception('Keep Screen On: failed to inject script')
        return response

    rhapi.ui.blueprint_add(bp)
    logger.info('Keep Screen On plugin loaded')
