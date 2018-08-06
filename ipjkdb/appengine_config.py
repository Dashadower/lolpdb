# appengine_config.py
from google.appengine.ext import vendor

# Add any libraries install in the "lib" folder.
vendor.add('lib')
from requests_toolbelt.adapters import appengine as requests_toolbelt_appengine
requests_toolbelt_appengine.monkeypatch()