from requests import Session, Request, HTTPError

ROOT_URL = 'http://calabrio.tlcinternal.com'
API_ROOT = ROOT_URL + '/api/rest'
BASE_DATA = [{
    'id': 'recording',
    'data': {
        'domain': 'corp',
        'locale': 'en'
    },
    'userId': '',
    'password': '',
    'locale': 'en'
}]

class SessionHandler:
    def __init__(self):
        self.ses = Session()
        self.isDownloadReady = False
        self.isExportReady = False
        self.downloadLink = ''
        self.lastError = ''
        self.lastFriendlyError = ''

    def authorize(self, username, password):
        data = BASE_DATA
        data[0]['userId'] = username
        data[0]['password'] = password
        req = Request('POST', API_ROOT + '/authorize', json=data)
        prep = self.ses.prepare_request(req)
        try:
            res = self.ses.send(prep)
            res.raise_for_status()
        except HTTPError as e:
            self.lastFriendlyError = 'Authorize: {}'.format(e.code)
            self.lastError = e
            return False
        except Exception as e:
            self.lastFriendlyError = 'Authorize: {}'.format(type(e))
            self.lastError = e
            return False

        set_cookies = res.headers['Set-Cookie'].split(',')
        self.token = ''
        for cookie in set_cookies:
            if cookie.startswith('CSRFTOKEN'):
                values = cookie.split(';')
                self.token = values[0].split('=')[1]
        if '' == self.token:
            self.lastFriendlyError = 'Unable to get login cookie, please try again.'
            self.lastError = 'NoCookie'
            return False

        return True

    def requestContactExport(self, contactId):
        data = { 'mediaFormat': 'wav' }
        headers = { 'X-CSRF-Token': self.token }
        req = Request('post', API_ROOT + '/recording/contact/{}/export/'.format(contactId), json=data, headers=headers)
        prep = self.ses.prepare_request(req)
        try:
            res = self.ses.send(prep)
            res.raise_for_status()
        except HTTPError as e:
            self.lastFriendlyError = 'requestContactExport: {}'.format(e.code)
            self.lastError = e
            return False
        except Exception as e:
            self.lastFriendlyError = 'requestContactExport: {}'.format(type(e))
            self.lastError = e
            return False
        self.exportId = res.json()['id']
        self.isExportReady = False
        self.isDownloadReady = False
        return True
    
    def checkIfExportIsReady(self, exportId):
        res = self.ses.get(API_ROOT + '/recording/contact/{}/export/{}'.format(contactId, exportId), headers=headers)
        try:
            res.raise_for_status()
        except HTTPError as e:
            self.lastFriendlyError = 'checkIfExportIsReady: {}'.format(e.code)
            self.lastError = e
            return False
        except Exception as e:
            self.lastFriendlyError = 'checkIfExportIsReady: {}'.format(type(e))
            self.lastError = e
            return False
        self.downloadReady = res.json()['isComplete']
        downloadLink = res.json()['exportUrl']
        self.downloadLink = downloadLink.replace('http://las-qmb-wp01.Corp.tlcinternal.us:80', ROOT_URL)
        return True
    
    def downloadExport(self, exportId):
        try:
            res = self.ses.get(downloadLink, headers=headers, stream=True)
            res.raise_for_status()
        except HTTPError as e:
            self.lastFriendlyError = 'downloadExport: {}'.format(e.code)
            self.lastError = e
            return False
        except Exception as e:
            self.lastFriendlyError = 'downloadExport: {}'.format(type(e))
            self.lastError = e
            return False
        chunk_size = 16 * 1024
        with open('{}.mp3'.format(contactId), 'wb') as f:
            for chunk in res.iter_content(chunk_size):
                if chunk:
                    f.write(chunk)
        return True

    def getLastError(self):
        return self.lastError

    def getLastFriendlyError(self):
        return self.lastFriendlyError

    def isDownloadReady(self):
        return self.downloadReady