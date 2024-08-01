from dotenv import load_dotenv
import os
import sys
from _datetime import datetime

# extDataDir = os.getcwd()
# if getattr(sys, 'frozen', False):
#    extDataDir = sys._MEIPASS
# load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))

load_dotenv()

URL = os.environ.get('url')

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

EMPTY_DATE = datetime.strptime('01.01.2000 00:00:00', '%d.%m.%Y %H:%M:%S')
TASK_FIELDS = ["ID", "TITLE", "STATUS", "CREATED_DATE", "CREATED_BY", "CLOSED_DATE", "DEADLINE",
               "START_DATE_PLAN", "END_DATE_PLAN", "TIME_ESTIMATE", "PRIORITY"]
