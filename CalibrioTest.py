from requests import Session, Request
import sys
from getpass import getpass

ROOT_URL = 'http://calabrio.tlcinternal.com'
API_ROOT = ROOT_URL + '/api/rest'

BASE_DATA = [{
	"id": "recording",
	"data": {
		"domain": "corp",
		"locale": "en"
	},
	"userId": "",
	"password": "",
	"locale": "en"
}]


if __name__ == '__main__':
	user = input('Username: ')
	password = getpass()
	contactId = input('Contact ID: ')
	
	data = BASE_DATA
	data[0]['userId'] = user
	data[0]['password'] = password
	
	ses = Session()
	req = Request('POST', API_ROOT + '/authorize', json=data)
	prep = ses.prepare_request(req)
	res = ses.send(prep)
	try:
		res.raise_for_status()
	except Exception as e:
		print(e)
		sys.exit(1)
	set_cookies = res.headers['Set-Cookie'].split(',')
	token = ''
	for cookie in set_cookies:
		if cookie.startswith('CSRFTOKEN'):
			values = cookie.split(';')
			token = values[0].split('=')[1]
	if '' == token:
		print('Unable to login. Please try again.')
		sys.exit(5)
	print('Logged in successfully, requesting export of {}'.format(contactId))
	data = { "mediaFormat": "wav" }
	headers = { 'X-CSRF-Token': token }
	req = Request('post', API_ROOT + '/recording/contact/{}/export/'.format(contactId), json=data, headers=headers)
	prep = ses.prepare_request(req)
	res = ses.send(prep)
	try:
		res.raise_for_status()
	except Exception as e:
		print(e)
		sys.exit(1)
	exportId = res.json()['id']
	print('Requested export successfully, waiting for export to be ready.')
	downloadReady = False
	while not downloadReady:
		res = ses.get(API_ROOT + '/recording/contact/{}/export/{}'.format(contactId, exportId), headers=headers)
		try:
			res.raise_for_status()
		except Exception as e:
			print(e)
			sys.exit(1)
		downloadReady = res.json()['isComplete']
	print('Export is ready, beginning download')
	downloadLink = res.json()['exportUrl']
	downloadLink = downloadLink.replace('http://las-qmb-wp01.Corp.tlcinternal.us:80', ROOT_URL)
	res = ses.get(downloadLink, headers=headers, stream=True)
	try:
		res.raise_for_status()
	except Exception as e:
		print(e)
		sys.exit(1)
	chunk_size = 16 * 1024
	with open('{}.mp3'.format(contactId), 'wb') as f:
		for chunk in res.iter_content(chunk_size):
			if chunk:
				f.write(chunk)
	print('Download completed')