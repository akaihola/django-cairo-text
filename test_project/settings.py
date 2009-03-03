from os.path import join, dirname
PROJECT_ROOT = join(dirname(__file__))

DATABASE_ENGINE = 'sqlite3'
INSTALLED_APPS = 'cairotext',
MEDIA_ROOT = join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'
CAIROTEXT_PRESETS = dict(
    fancy=dict(
        font='Serif',
        size=40,
        background='#fc8',
        color='#630'))
