import sys
from getpass import getpass, getuser

from SessionHandler import SessionHandler
from Analytics import Analytics

def showError(handler):
	print(handler.getLastFriendlyError())
	Analytics.sendAnalytics('AppError', handler.getLastError())
	raw_input()
	sys.exit(1)

if __name__ == '__main__':
	Analytics.sendAnalytics('AppEvent', 'AppLaunch')
	user = raw_input('Username: ')
	password = getpass()
	contactId = raw_input('Contact ID: ')

	handler = SessionHandler()
	if not handler.authorize(user, password):
		showError(handler)
	print('Logged in successfully, requesting export of {}'.format(contactId))
	if not handler.requestContactExport(contactId):
		showError(handler)
	print('Requested export successfully, waiting for export to be ready.')
	while not handler.isDownloadReady():
		if not handler.checkIfExportIsReady(exportId):
			showError(handler)
	print('Export is ready, beginning download')
	if not handler.downloadExport(exportId):
		showError(handler)
	Analytics.sendAnalytics('AppEvent', 'AppCompleted')
	print('Download completed')