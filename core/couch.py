
import couchdb


def GetOrCreateDB(server, name, create = True):
	if name in server:
		return server[name]
	elif create:
		return server.create(name)
	return None


class CouchObject():
	def __init__(self):
		pass


class CouchManager():
	def __init__(self, name):
		self.Name = name
		self.Server = couchdb.Server('http://localhost:5984/')
		self.DBNameSystem = 'metaleap_' + name + '_system'
		self.DBSystem = None
		self.Reconnect()

	def Reconnect(self, throw = False):
		try:
			self.DBSystem = GetOrCreateDB(self.Server, self.DBNameSystem)
		except:
			self.DBSystem = None
			if throw:
				raise
