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
        self.downloadReady = False
        self.downloadLink = ''
        self.lastError = ''
        self.lastFriendlyError = ''

    def authorize(self, username, password):
        data = BASE_DATA
        data[0]['userId'] = username.strip()
        data[0]['password'] = password
        req = Request('POST', API_ROOT + '/authorize', json=data)
        prep = self.ses.prepare_request(req)
        try:
            res = self.ses.send(prep)
            res.raise_for_status()
        except HTTPError as e:
            self.lastError = 'Authorize: {}'.format(e.response.status_code)
            self.lastFriendlyError = 'Unable to login. Error code {}.'.format(e.response.status_code)
            return False
        except Exception as e:
            self.lastError = 'Authorize: {}'.format(type(e))
            self.lastFriendlyError = 'Unable to login, please try again.'
            return False

        set_cookies = res.headers['Set-Cookie'].split(',')
        self.token = ''
        for cookie in set_cookies:
            if cookie.startswith('CSRFTOKEN'):
                values = cookie.split(';')
                self.token = values[0].split('=')[1]
        if '' == self.token:
            self.lastError = 'NoCookie'
            self.lastFriendlyError = 'Unable to get login cookie, please try again.'
            return False

        return True

    def requestContactExport(self, contactId):
        data = { 'mediaFormat': 'wav' }
        headers = { 'X-CSRF-Token': self.token }
        self.contactId = contactId.strip()
        req = Request('post', API_ROOT + '/recording/contact/{}/export/'.format(self.contactId), json=data, headers=headers)
        prep = self.ses.prepare_request(req)
        try:
            res = self.ses.send(prep)
            res.raise_for_status()
        except HTTPError as e:
            self.lastError = 'requestContactExport: {}'.format(e.response.status_code)
            self.lastFriendlyError = 'Unable to request an export for chosen contact ID. Error code {}.'.format(e.response.status_code)
            return False
        except Exception as e:
            self.lastError = 'requestContactExport: {}'.format(type(e))
            self.lastFriendlyError = 'Unable to request an export for chosen contact ID, please try again.'
            return False
        self.exportId = res.json()['id']
        self.downloadReady = False
        return True
    
    def checkIfExportIsReady(self):
        headers = { 'X-CSRF-Token': self.token }
        res = self.ses.get(API_ROOT + '/recording/contact/{}/export/{}'.format(self.contactId, self.exportId), headers=headers)
        try:
            res.raise_for_status()
        except HTTPError as e:
            self.lastError = 'checkIfExportIsReady: {}'.format(e.response.status_code)
            self.lastFriendlyError = 'Unable to get the status of the selected export. Error code {}.'.format(e.response.status_code)
            return False
        except Exception as e:
            self.lastError = 'checkIfExportIsReady: {}'.format(type(e))
            self.lastFriendlyError = 'Unable to get the status of the selected export, please try again.'
            return False
        self.downloadReady = res.json()['isComplete']
        downloadLink = res.json()['exportUrl']
        self.downloadLink = downloadLink.replace('http://las-qmb-wp01.Corp.tlcinternal.us:80', ROOT_URL)
        return True
    
    def downloadExport(self):
        headers = { 'X-CSRF-Token': self.token }
        try:
            res = self.ses.get(self.downloadLink, headers=headers, stream=True)
            res.raise_for_status()
        except HTTPError as e:
            self.lastError = 'downloadExport: {}'.format(e.response.status_code)
            self.lastFriendlyError = 'Unable to download the exported contact. Error code {}.'.format(e.response.status_code)
            return False
        except Exception as e:
            self.lastError = 'downloadExport: {}'.format(type(e))
            self.lastFriendlyError = 'Unable to download the exported contact, please try again.'
            return False
        chunk_size = 16 * 1024
        with open('{}.mp3'.format(self.contactId), 'wb') as f:
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