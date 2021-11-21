"""
Environment for Behave Testing
"""
from os import getenv
from selenium import webdriver


WAIT_SECONDS = int(getenv('WAIT_SECONDS', '60'))
BASE_URL = getenv('BASE_URL', 'http://localhost:5000')

def before_all(context):
    context.base_url = BASE_URL
    # -- SET LOG LEVEL: behave --logging-level=ERROR ...
    # on behave command-line or in "behave.ini"
    context.config.setup_logging()

def after_all(context):
    """ Executed after all tests """