"""Deployment transport settings only; analytical and provider contracts stay unchanged."""
import hmac
import json
import os
import re

LOCAL_ORIGINS={'http://localhost:3000','http://127.0.0.1:3000'}

def settings(environ=None):
    env=os.environ if environ is None else environ
    production=env.get('DASHBOARD_ENV')=='production' or bool(env.get('RAILWAY_ENVIRONMENT_ID'))
    token=env.get('DASHBOARD_BACKEND_TOKEN','')
    if production and (len(token)<43 or not re.fullmatch(r'[A-Za-z0-9_-]+',token)):
        raise ValueError('Production requires a strong DASHBOARD_BACKEND_TOKEN')
    port=int(env.get('PORT','8001'))
    if not 1<=port<=65535:raise ValueError('Invalid PORT')
    return {'production':production,'token':token,'port':port,
        'origins':LOCAL_ORIGINS|{v.strip() for v in env.get('DASHBOARD_ALLOWED_ORIGINS','').split(',') if v.strip()},
        'restore_saved':env.get('DASHBOARD_RESTORE_SAVED_RESULTS','1')!='0'}

def authenticated(headers,config):
    if not config['token']:return not config['production']
    supplied=headers.get('Authorization','')
    expected='Bearer '+config['token']
    return hmac.compare_digest(supplied.encode(),expected.encode())

def log_event(**fields):
    # Call sites pass fixed enums, server IDs and numeric timing only. Never headers/bodies.
    print(json.dumps(fields,separators=(',',':'),ensure_ascii=True),flush=True)
