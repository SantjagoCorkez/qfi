import logging
import os
import unittest

os.environ['QFI_CONFIG_PATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ['QFI_CORE_INI'] = 'config_sample.ini'

logging.getLogger('sqlalchemy.engine').disabled = True
# from test_init_db import InitDBTestCase

# unittest.main()
