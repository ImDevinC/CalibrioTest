import sys
from getpass import getpass, getuser

from SessionHandler import SessionHandler
from Analytics import Analytics

if __name__ == '__main__':
	Analytics.sendAnalytics('AppEvent', 'AppLaunch')
	user = raw_input('Username: ')
	password = getpass()
	contactId = raw_input('Contact ID: ')

	handler = SessionHandler()
	if not handler.authorize(user, password):
		print(handler.getLastFriendlyError())
		Analytics.sendAnalytics('AppError', handler.getLastError())
		sys.exit(1)
	print('Logged in successfully, requesting export of {}'.format(contactId))
	if not handler.requestContactExport(contactId):
		print(handler.getLastFriendlyError())
		Analytics.sendAnalytics('AppError', handler.getLastError())
		sys.exit(1)
	print('Requested export successfully, waiting for export to be ready.')
	while not handler.isDownloadReady():
		if not handler.checkIfExportIsReady(exportId):
			print(handler.getLastFriendlyError())
			Analytics.sendAnalytics('AppError', handler.getLastError())
			sys.exit(1)
	print('Export is ready, beginning download')
	if not handler.downloadExport(exportId):
		print(handler.getLastFriendlyError())
		Analytics.sendAnalytics('AppError', handler.getLastError())
		sys.exit(1)
	Analytics.sendAnalytics('AppEvent', 'AppCompleted')
	print('Download completed')