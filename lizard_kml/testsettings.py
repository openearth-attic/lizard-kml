import os

from lizard_ui.settingshelper import setup_logging
from lizard_ui.settingshelper import STATICFILES_FINDERS

DEBUG = True
TEMPLATE_DEBUG = True

# SETTINGS_DIR allows media paths and so to be relative to this settings file
# instead of hardcoded to c:\only\on\my\computer.
SETTINGS_DIR = os.path.dirname(os.path.realpath(__file__))

# BUILDOUT_DIR is for access to the "surrounding" buildout, for instance for
# BUILDOUT_DIR/var/static files to give django-staticfiles a proper place
# to place all collected static files.
BUILDOUT_DIR = os.path.abspath(os.path.join(SETTINGS_DIR, '..'))
LOGGING = setup_logging(BUILDOUT_DIR)

# ENGINE: 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
# In case of geodatabase, prepend with:
# django.contrib.gis.db.backends.(postgis)
DATABASES = {
    # If you want to use another database, consider putting the database
    # settings in localsettings.py. Otherwise, if you change the settings in
    # the current file and commit them to the repository, other developers will
    # also use these settings whether they have that database or not.
    # One of those other developers is Jenkins, our continuous integration
    # solution. Jenkins can only run the tests of the current application when
    # the specified database exists. When the tests cannot run, Jenkins sees
    # that as an error.
    'default': {
        'NAME': os.path.join(BUILDOUT_DIR, 'var', 'sqlite', 'test.db'),
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',  # empty string for localhost.
        'PORT': '',  # empty string for default.
        }
    }
SITE_ID = 1
INSTALLED_APPS = [
    'lizard_kml',
    'lizard_ui',
    'staticfiles',
    'compressor',
    'south',
    'django_nose',
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.gis',
    'django.contrib.sites',
    ]
ROOT_URLCONF = 'lizard_kml.urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    # Uncomment this one if you use lizard-map.
    # 'lizard_map.context_processors.processor.processor',
    # Default django 1.3 processors.
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages"
    )

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--with-doctest', '--verbosity=3']
SOUTH_TESTS_MIGRATE = False # To disable migrations and use syncdb instead
SKIP_SOUTH_TESTS = True # To disable South's own unit tests

# Used for django-staticfiles (and for media files
STATIC_URL = '/static_media/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BUILDOUT_DIR, 'var', 'static')
MEDIA_ROOT = os.path.join(BUILDOUT_DIR, 'var', 'media')
STATICFILES_FINDERS = STATICFILES_FINDERS

# optional, download local: wget http://opendap.deltares.nl/thredds/fileServer/opendap/rijkswaterstaat/jarkus/profiles/transect.nc
# and override in local_testsettings.py if necessary
NC_RESOURCE = 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/jarkus/profiles/transect.nc'
# Use this if we break the deltares server....
NC_RESOURCE = 'http://opendap.tudelft.nl/thredds/dodsC/data2/deltares/rijkswaterstaat/jarkus/profiles/transect.nc'
if os.getlogin() == 'fedorbaart':
    NC_RESOURCE = '/Users/fedorbaart/Downloads/transect.nc'
DEBUG_SHOW_EXAMPLE_KML_ON_EXCEPTION = False

try:
    # Import local settings that aren't stored in svn/git.
    from lizard_kml.local_testsettings import *
except ImportError:
    pass
