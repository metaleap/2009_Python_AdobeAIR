
from __future__ import with_statement
from datetime import datetime
from subprocess import Popen
from core import couch, gfx, page, user, util

import clevercss
import Image
import mako, mako.lookup
import os
import random
import shutil
import signal
import socket
import sys
import threading
import time
import urllib2
import werkzeug, werkzeug.serving

print('Booting up application server...')

MODE_AIR = (__name__ == '__main__') and not ('--server' in sys.argv)
MODE_AIR_BOTH = False
MODE_AIR_CLIENT = False
MODE_AIR_SERVICE = False
NAME_APP = 'MetaLeap'
NAME_CREATOR = 'roxority.com'
TIMER_INTERVAL = 1
TIMEOUT_AIR_BOTH = 20
DEBUG = (__name__ == '__main__') and not ('--nodebug' in sys.argv)
PORTS = [54321, 56789, 65432]

CommandLineNoCache = '--nocache' in sys.argv or DEBUG
CommandLineInstance = '--name' in sys.argv and sys.argv[sys.argv.index('--name') + 1].strip() or 'default'
CommandLinePort = ('--port' in sys.argv and int(sys.argv[sys.argv.index('--port') + 1]) or 0)
OSIsMac = sys.platform.__contains__('darwin')
OSIsWin = not OSIsMac and sys.platform.__contains__('win')
OSIsUnix = not OSIsWin and not OSIsMac
PathCore = os.path.abspath(os.path.dirname(__file__))
Resources = util.Resources(os.path.join(PathCore, 'resources'))

if OSIsWin:
	PathAirApp = 'C:\\Program Files\\' + NAME_CREATOR + '\\' + NAME_APP + '\\' + NAME_APP + '.exe'
elif OSIsMac:
	PathAirApp = '/Applications/' + NAME_CREATOR + '/' + NAME_APP + '.app/Contents/MacOS/' + NAME_APP
else:
	PathAirApp = '/opt/' + NAME_CREATOR + '/' + NAME_APP + '/' + NAME_APP


def ConvertCcssFile(ccssPath, cssPath, targetDirName = '', convertImports = True):
	def fixupImport(tdn, imps):
		imports = []
		for i in xrange(0, len(imps)):
			if imps[i].startswith('/'):
				imports.append(imps[i])
			else:
				imports.append(('/' + os.path.join(tdn.strip('/'), imps[i]).strip('/')).replace(PathCore, '').replace('/ui/', '/').replace('/cache/css', ''))
		return imports
	if not targetDirName:
		targetDirName = os.path.dirname(cssPath)
	if not os.path.isdir(targetDirName):
		os.makedirs(targetDirName)
	with open(ccssPath, 'r') as ccssFile:
		with open(cssPath, 'w') as cssFile:
			imports = []
			cssFile.write('/* Auto-generated with CleverCSS from: ~' + ccssPath.replace(PathCore, '') + ' [' + util.GetDateTimeString() + '] */\n\n' + util.FixupCcss(clevercss.convert(util.PreprocessCcss(ccssFile.read(), imports)), fixupImport(targetDirName, imports), not DEBUG))
			if convertImports:
				for imp in imports:
					tp = (imp.startswith('/') and MapPath('ui/' + imp.strip('/')) or os.path.join(targetDirName, imp))
					ConvertCcssFile(tp.replace('cache/css/', ''), tp.replace('.ccss', '.css'))


def ConvertCcssFiles(force):
	def handleCcss(arg, dirName, fileNames):
		if dirName.find('cache') < 0:
			for fileName in fileNames:
				if fileName.find('cache') < 0:
					targetDirName = MapPath('ui/cache/css') + dirName.replace(MapPath('ui'), '')
					targetFilePath = os.path.join(targetDirName, fileName.replace('.ccss', '.css'))
					sourceFilePath = os.path.join(dirName, fileName)
					if os.path.isfile(sourceFilePath) and sourceFilePath.rfind('.ccss') > 0 and (force or (not os.path.exists(targetFilePath)) or (os.path.getmtime(sourceFilePath) > os.path.getmtime(targetFilePath))):
						ConvertCcssFile(sourceFilePath, targetFilePath, targetDirName)
	os.path.walk(MapPath('ui'), handleCcss, None)


def GenerateFiles(clearCaches = False, convertCcss = False, forceCcss = False):
	if clearCaches:
		tempPath = MapPath('ui/cache')
		util.ClearDirectory(tempPath)
		os.mkdir(tempPath + '/css')
		os.mkdir(tempPath + '/gfx')
		os.mkdir(tempPath + '/gfx/bg')
		os.mkdir(tempPath + '/gfx/dyn')
		os.mkdir(tempPath + '/dyn')
		os.mkdir(tempPath + '/scripts')
	if convertCcss:
		ConvertCcssFiles(forceCcss)


def IsServiceRunning():
	for port in CommandLinePort and [CommandLinePort] or PORTS:
		try:
			if (urllib2.urlopen('http://localhost:' + str(port) + '/?spam_eggs=' + str(random.random())).read() == 'the_full_monthy'):
				return port
		except:
			pass
	return 0


def MapPath(relativePath):
	return os.path.join('/' + PathCore.strip('/') + '/', relativePath.strip('/'))


def OnTimerTick():
	if MODE_AIR_BOTH and appServer.LastRequestTime:
		if ((time.time() - appServer.LastRequestTime) > TIMEOUT_AIR_BOTH):
			appServer.Exit()


def WsgiApplication(environ, start_response):
	appServer.LastRequestTime = time.time()
	appServer.Local.Request = request = werkzeug.Request(environ)
	response = appServer.ProcessRequest(request)
	return response(environ, start_response)


class AppServer():
	AirMode_None = 0
	AirMode_Service = 1
	AirMode_Client = 2
	OS_Unix = 0
	OS_Mac = 1
	OS_Windows = 2

	def __init__(self):
		print(Resources('initappserver'))
		self.AirMode = MODE_AIR and ((MODE_AIR_SERVICE and AppServer.AirMode_Service) or (MODE_AIR_BOTH and AppServer.AirMode_Client)) or AppServer.AirMode_None
		self.CouchManager = couch.CouchManager(CommandLineInstance)
		self.OS = (OSIsMac and AppServer.OS_Mac) or (OSIsWin and AppServer.OS_Windows) or AppServer.OS_Unix
		self.IsDebugMode = DEBUG
		self.IsOSMac = OSIsMac
		self.IsOSWin = OSIsWin
		self.IsOSUnix = OSIsUnix
		self.IsShutDown = False
		self.Resources = Resources
		self.Sessions = user.SessionManager(self.AirMode)
		self.WsgiServer = None
		self.LastRequestTime = 0
		self.Local = werkzeug.Local()
		self.LocalManager = werkzeug.LocalManager([self.Local])
		self.HostName = 'localhost'
		self.TemplateLookup = mako.lookup.TemplateLookup(directories = [MapPath('ui')], module_directory = MapPath('ui/cache/dyn'), input_encoding = 'utf-8', output_encoding = 'utf-8', filesystem_checks = DEBUG)
		self.UrlMap = werkzeug.routing.Map()
		self.WsgiApplication = werkzeug.SharedDataMiddleware(self.LocalManager.make_middleware(WsgiApplication), { '/': MapPath('ui') }, '*.dyn.*', cache = not CommandLineNoCache and not DEBUG)
		self.Port = CommandLinePort
		self.DefaultPorts = PORTS
		if not self.Port:
			for port in PORTS:
				try:
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
					sock.bind((self.HostName, port))
					sock.close()
					self.Port = port
					break
				except:
					pass
		self.WsgiServer = werkzeug.serving.make_server(self.HostName, self.Port, self.WsgiApplication, True, 1, None)
		GenerateFiles(DEBUG)
		self.Resources.WriteJavaScripts(MapPath('ui/cache/scripts/res_'))

	def __call__(self, name, *args):
		lang = ''
		if self.Local and self.Local.Request and self.Local.Request.Session and self.Local.Request.Session.Languages:
			lang = self.Local.Request.Session.PreferredLanguage
		return self.Resources.Get(name, lang, *args)

	def __getitem__(self, name):
		if name in self.Local.Request.args:
			return self.Local.Request.args[name]
		if name in self.Local.Request.form:
			return self.Local.Request.form[name]
		return None

	def Control(self, parent, type, id, templatePath = None, options = None):
		return self.Local.Request.Session('ctl_' + id,
										lambda recreate: recreate and recreate.SyncBase(parent, type, id, templatePath, options) or page.Control(self, parent, type, id, templatePath, options),
										lambda checkExisting: checkExisting.type != type or checkExisting.templatePath != templatePath or options)

	def DynGfx(self, func, *args, **options):
		return util.DynGfx(func, *args, **options)

	def Exit(self):
		self.IsShutDown = True
		self.WsgiServer.socket.close()
		self.WsgiServer.server_close()
		self.WsgiServer = None
		print(Resources('bye'))
		util.KillProcess(win = OSIsWin)
		quit()

	def GetCssUrl(self, ccssVPath):
		ccssPPath, cssVPath = self.MapPath(ccssVPath), '/cache/css/' + ccssVPath.strip('/').replace('.ccss', '.css')
		cssPPath = self.MapPath(cssVPath)
		if (os.path.isfile(ccssPPath) and not os.path.isfile(cssPPath)) or (os.path.isfile(ccssPPath) and os.path.isfile(cssPPath) and os.path.getmtime(ccssPPath) > os.path.getmtime(cssPPath)):
			ConvertCcssFile(ccssPPath, cssPPath)
		return os.path.isfile(cssPPath) and cssVPath or ''

	def MapPath(self, relativePath):
		return MapPath('/ui/' + relativePath.strip('/'))

	def ProcessRequest(self, request):
		def jsonErrorFilter(k, v):
			return [k != 'source', k, isinstance(v, str) and v.replace(PathCore + '/ui', '~') or (isinstance(v, unicode) and v.replace(unicode(PathCore) + u'/ui', u'~') or v)]
		result = ''
		notfound = False
		if not self.CouchManager.DBSystem:
			self.CouchManager.Reconnect()
		request.IsAir = 'AdobeAIR' in request.user_agent.string
		request.Session = user.GetSessionForRequest(self, request)
		reqpath = request.path and request.path != '/' and (request.path.endswith('/') and request.path[:-1] or request.path) or 'core.dyn.html'
		self.Local.ContentType = 'text/html'
		if 'spam_eggs' in request.args:
			return werkzeug.Response('the_full_monthy', mimetype = self.Local.ContentType)
		else:
			try:
				if reqpath.endswith('.dyn.json') and not self.CouchManager.DBSystem:
					try:
						self.CouchManager.Reconnect(True)
					except Exception, dbEx:
						raise Exception(self('error_couch', str(dbEx)))
				reqext = reqpath[reqpath.rfind('.') + 1:]
				if reqext in ['json', 'js']:
					self.Local.ContentType = "text/javascript"
					if self.IsShutDown:
						result = "{ error: 'servershutdown' }"
				elif reqext == 'png':
					self.Local.ContentType = "text/html"
				elif reqext.endswith('css'):
					self.Local.ContentType = "text/css"
				if not result:
					result = self.RenderTemplate(reqpath)
			except mako.exceptions.TopLevelLookupException:
				if reqpath.startswith('/cache/css/') and reqpath.endswith('.css'):
					# edge case: server cache was cleared, ccss/css not yet re-generated, and the
					# css url requested directly from user agent without a call to AppServer.GetCssUrl
					ccssPath = self.MapPath(reqpath[11:-4] + '.ccss')
					if os.path.isfile(ccssPath):
						ConvertCcssFile(ccssPath, self.MapPath(reqpath))
						return self.ProcessRequest(request)
				result = "404 Not Found"
				notfound = True
			except util.RedirectError, r:
				return werkzeug.redirect(r.Location)
			except Exception, ex:
				if reqpath.endswith('.dyn.json'):
					ex.__dict__['__error_message'] = str(ex).replace('\\r', '\r').replace('\\n', '\n').replace('\\t', '\t')
					result = '{ error: ' + util.ToJson(ex, dicFilter = jsonErrorFilter) + '}'
				else:
					result = mako.exceptions.html_error_template().render()
			resp = werkzeug.Response(result, mimetype = self.Local.ContentType, headers = { 'Pragma': 'no-cache', 'cache-control': 'no-cache' })
			if notfound:
				resp.mimetype = 'text/plain'
				resp.status = result
			today = datetime.today()
			if request.Session and request.Session.IsNew and not request.Session.IsLocal:
				request.Session.IsNew = False
				resp.set_cookie('metauser', request.Session.UserName, max_age = 31536000, expires = datetime(today.year + 1, today.month, today.day))
			return resp

	def RenderTemplate(self, templatePath):
		return self.TemplateLookup.get_template(templatePath).render(_ = self, Request = self.Local.Request, Session = self.Local.Request.Session)

	def StartAirService(self):
		print(Resources('listening', self.Port))
		self.WsgiServer.serve_forever()


if MODE_AIR:
	port = 0
	if ('--service' in sys.argv):
		MODE_AIR_SERVICE = True
	else:
		port = IsServiceRunning()
		if port:
			MODE_AIR_CLIENT = True
			appServer = None
		else:
			MODE_AIR_BOTH = True

	if MODE_AIR_BOTH or MODE_AIR_SERVICE:
		appServer = AppServer()
		port = appServer.Port

	if not MODE_AIR_CLIENT:
		util.RepeatTimer(TIMER_INTERVAL, OnTimerTick).Start()

	if MODE_AIR_BOTH:
		#os.spawnv(os.P_NOWAIT, PathAirApp, ['--port', str(port)])
		Popen([PathAirApp, str(port)])
	elif MODE_AIR_CLIENT:
		Popen([PathAirApp, str(port)])
		#os.execv(PathAirApp, ['--port', str(port)])

	if appServer:
		appServer.StartAirService()
else:
	appServer = AppServer()
	util.RepeatTimer(TIMER_INTERVAL, OnTimerTick).Start()
	if (__name__ == '__main__'):
	   appServer.StartAirService()
