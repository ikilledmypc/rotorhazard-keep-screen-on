"""Tests the plugin against a minimal stand-in for RotorHazard's RHAPI.

Run with:  python3 tests/test_plugin.py   (needs only Flask, which RotorHazard already uses)
"""
import importlib
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'custom_plugins'))

# --- Fake RHUI module -------------------------------------------------------
rhui = types.ModuleType('RHUI')


class UIFieldType:
    CHECKBOX = 'checkbox'


class UIField:
    def __init__(self, name, label, field_type, **kw):
        self.name = name
        self.kw = kw


rhui.UIField = UIField
rhui.UIFieldType = UIFieldType
sys.modules['RHUI'] = rhui

from flask import Flask, jsonify, make_response  # noqa: E402

app = Flask(__name__)
cfg = {}


class Config:
    def register_section(self, section):
        cfg.setdefault(section, {})

    def get(self, section, name, as_int=False):
        return cfg.get(section, {}).get(name, False)


class UI:
    def register_panel(self, *a, **k):
        pass

    def register_markdown(self, *a, **k):
        pass

    def blueprint_add(self, bp):
        app.register_blueprint(bp)


class Fields:
    def register_option(self, field, panel=None):
        cfg[field.kw['persistent_section']].setdefault(field.name, field.kw['value'])


rhapi = types.SimpleNamespace(config=Config(), ui=UI(), fields=Fields())
plugin = importlib.import_module('keep_screen_on')
plugin.initialize(rhapi)

HTML = '<html><body><p>hi</p></body></html>'


@app.route('/')
def home():
    return make_response(HTML)


@app.route('/streamheat')
def stream():
    return HTML


@app.route('/api/x')
def api():
    return jsonify(a=1)


def main():
    c = app.test_client()
    sec = cfg['KeepScreenOn']

    body = c.get('/').text
    assert 'keep_screen_on.js' in body and body.index('keep_screen_on.js') < body.index('</body>')
    assert '?v=' + plugin.SCRIPT_VERSION in body
    print('ok  script injected into HTML pages')

    assert 'keep_screen_on' not in c.get('/streamheat').text
    print('ok  stream pages skipped')

    assert c.get('/api/x').json == {'a': 1}
    print('ok  JSON responses untouched')

    for f in ('NoSleep.min.js', 'keep_screen_on.js'):
        r = c.get('/keep_screen_on/static/' + f)
        assert r.status_code == 200 and len(r.data) > 1000, f
        r.close()
    print('ok  static files served')

    for off in ('0', False, ''):
        sec['show_button'] = off
        assert 'keep_screen_on' not in c.get('/').text, repr(off)
    print('ok  setting off hides the button')

    sec['show_button'] = '1'
    assert 'keep_screen_on' in c.get('/').text
    print('ok  setting on shows the button')
    print('All tests passed')


if __name__ == '__main__':
    main()
