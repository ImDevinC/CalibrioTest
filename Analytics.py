import hashlib
from socket import gethostname
from getpass import getuser
import requests

VERSION = 1.0
ANALYTICS_ID = 'UA-47032439-9'
ANALYTICS_URL = 'https://google-analytics.com/collect'

class Analytics:
    @staticmethod
    def sendAnalytics(category, action):
        try:
            userId = getuser()
            hostname = gethostname()
            machineId = hashlib.sha256('{}:!:{}'.format(userId, hostname)).hexdigest()
        except HTTPError as ex:
            machineId = 'ERROR'
        payload = {
            'v': 1,
            'tid': ANALYTICS_ID,
            'uid': machineId,
            't': 'event',
            'av': VERSION,
            'ec': category,
            'ea': action,
            'an': 'CalibrioTest'
        }
        try:
            r = requests.post(ANALYTICS_URL, data=payload, headers={'User-Agent': 'CalibrioTest-'.format(VERSION)})
        except Exception:
            pass