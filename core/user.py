
from core import couch, util
import getpass
import socket
import time


def GetAcceptLanguages(request):
	try:
		langs = request.environ.get('HTTP_ACCEPT_LANGUAGE').split(',')
		pos = -1
		for i in xrange(0, len(langs)):
			pos = langs[i].find(';')
			if pos > 0:
				langs[i] = langs[i] [:pos]
		return langs
	except:
		return []


def GetSessionForRequest(appServer, request):
	userName = ''
	if appServer.Sessions.LocalOnly:
		userName = getpass.getuser()
	elif 'metauser' in request.cookies:
		userName = request.cookies['metauser']
	if userName == '':
		userName = 'anon_' + str(time.time()).replace('.', '_')
		request.cookies['metauser'] = userName
	if not userName in appServer.Sessions:
		appServer.Sessions[userName] = Session(appServer, userName, request)
	return appServer.Sessions[userName]


class Session():
	def __init__(self, appServer, userName, request):
		self.AppServer = appServer
		self.Manager = appServer.Sessions
		self.IsAuth = appServer.Sessions.LocalOnly and request.remote_addr in ('127.0.0.1', 'localhost', socket.gethostname(), appServer.WsgiServer.socket.getsockname()[0])
		self.IsLocal = self.IsAuth
		self.IsNew = True
		self.Database = appServer.CouchManager.DBSystem and couch.GetOrCreateDB(appServer.CouchManager.Server, 'metaleap_' + appServer.CouchManager.Name + '_user_' + userName, self.IsLocal) or None
		self.LastRequest = time.time()
		self.Languages = GetAcceptLanguages(request)
		self.PreferredLanguage = appServer.Resources.PickLanguage('', self.Languages)
		self.UserName = userName
		self.Vars = {}

	def __call__(self, key, creator, recreate = None):
		obj = None
		if not key in self.Vars:
			self.Vars[key] = obj = creator(None)
		else:
			obj = self.Vars[key]
			if recreate and recreate(obj):
				self.Vars[key] = obj = creator(obj)
		return obj

	def __getitem__(self, key):
		return key in self.Vars and self.Vars[key] or None

	def __setitem__(self, key, value):
		self.Vars[key] = value


class SessionManager():
	def __init__(self, localOnly):
		self.LocalOnly = localOnly
		self.Sessions = {}

	def __contains__(self, userName):
		return userName in self.Sessions

	def __getitem__(self, userName):
		return self.Sessions[userName]

	def __setitem__(self, userName, session):
		self.Sessions [userName] = session
