command = 'gunicorn'
pythonpath = 'exchange_account_api/exchange_account_api'
bind = '0.0.0.0:8201'
workers = 1
user = 'og'
limit_request_fields = 32000
limit_request_field_size = 0
raw_env = 'DJANGO_SETTINGS_MODULE=exchange_account_api.settings'
