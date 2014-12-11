import os


def _default(val=''):
    def _fn(key):
        return os.getenv(key, val)
    return _fn


def _is_true(key):
    return os.getenv(key, '').lower() in ['true', '1', 'yes']


settings_vars = {
    'DEBUG': _is_true,
    'SECRET_KEY': _default(),
    'SERVICE_NAME': _default('Data'),
    'SERVICE_URL': _default('http://example.com'),
    'CONTACT_EMAIL': _default('team@example.com'),
    'API_ROOT': _default('//example.com'),

    # external APIs
    'GOOGLE_CLIENT_ID': _default(),
    'GOOGLE_CLIENT_SECRET': _default(),
    'MONGO_HOST': _default('localhost:27017'),
    'MONGO_USER': _default(),
    'MONGO_PASS': _default(),
    'MONGO_DB': _default('main'),
    'REDIS_HOST': _default('localhost'),
    'REDIS_PORT': _default('6379'),
    'REDIS_PASS': _default(None),
    'FORMS_API': _default('//forms.brace.io') # for collecting feedback on the landing page
}

for k, v in settings_vars.items():
    globals()[k] = v(k)
