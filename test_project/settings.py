from os.path import join, dirname
PROJECT_ROOT = join(dirname(__file__))

ADMINS = ('Cairotext test user', 'cairotext-test@localhost'),
DATABASE_ENGINE = 'sqlite3'
INSTALLED_APPS = 'cairotext',
MEDIA_ROOT = 'media'
MEDIA_URL = '/media/'
CAIROTEXT_DIR = 'cairotext_cache'
CAIROTEXT_PRESETS = dict(
    fancy=dict(
        font='Serif',
        size=40,
        background='#fc8',
        color='#630'))
