
from __future__ import with_statement
from core import util

import os
import simplejson
import time


class Control():
	@staticmethod
	def GetControls(dict):
		return util.GetDictValueOrList(dict, 'controls')

	@staticmethod
	def GetOptions(dict):
		return util.GetDictValueOrDict(dict, 'options')

	def __init__(self, appServer, parent, type, id, templatePath = None, options = None):
		dirPath = '/base/controls/' + type.strip('/')[:type.rfind('/')]
		if not os.path.isdir(appServer.MapPath(dirPath)):
			raise util.AppServerError('notfound', [dirPath], False, '404')
		self.appServer = appServer
		self.controls = []
		self.templateLoadTime = 0
		self.templatePath = templatePath
		self.options = None
		self.SyncBase(parent, type, id, templatePath, options)

	def ControlsToJsonList(self):
		ctls, d = [], None
		for c in self.controls:
			ctls.append({ 'id': c.id, 'type': c.type, 'options': c.options, 'controls': c.ControlsToJsonList() })
		return ctls

	def CreateJson(self, options, controls):
		return { 'id': self.id, 'type': self.type, 'options': options or {}, 'controls': controls or [] }

	def CreateJsonFromDict(self, dict):
		return self.CreateJson(Control.GetOptions(dict), Control.GetControls(dict))

	def LoadFromTemplate(self, templatePath):
		self.SyncFromJson(self.appServer.RenderTemplate(templatePath))
		if templatePath == self.templatePath:
			self.templateLoadTime = time.time()

	def SyncBase(self, parent, type, id, templatePath, options):
		self.parent = parent
		self.type = type
		self.id = id
		pos = type.find('/')
		self.typeName = type[pos + 1:]
		self.typePath = type[:pos]
		self.options = (self.options and options and util.SyncDict(self.options, options)) or options or self.options or {}
		if (not templatePath and not self.templatePath) or (self.templatePath and templatePath and templatePath != self.templatePath):
			if not templatePath:
				self.templatePath = 'base/controls/' + type + '/' + self.typeName + '.dyn.json'
			elif templatePath.find('/') < 0:
				self.templatePath = 'base/controls/' + type + '/' + templatePath + '.dyn.json'
			else:
				self.templatePath = templatePath.strip('/')
			if os.path.isfile(self.appServer.MapPath(self.templatePath)):
				self.LoadFromTemplate(self.templatePath)
		return self

	def SyncFromJson(self, json):
		def merge(target, source, idProp, added, removed):
			ls, lt, c, r, it, ctl = source and len(source) or 0, len(target), 0, True, 0, None
			# find items in source to be added to target
			for si in xrange(0, ls):
				if not util.ListContains(target, lambda obj: obj.__dict__[idProp] == source[si][idProp]):
					added.append(source[si])
			# find items not in source, to be removed from target
			for ti in xrange(0, lt):
				if not util.ListContains(source, lambda obj: obj[idProp] == target[ti].__dict__[idProp]):
					removed.append(target[ti])
					target[ti] = None
			# shrink target to get rid of removed (empty) slots
			while it < lt:
				if not target[it]:
					c = c + 1
				if c and (it + c) < len(target):
					target[it] = target[it + c]
				if not target[it] and util.ListHasValue(target, it):
					it = it - 1
				it = it + 1
			if c:
				del target[lt - c:]
			# append to target items to be added
			for ia in xrange(0, len(added)):
				ctl = Control(self.appServer, self, added[ia]['type'], added[ia]['id'], None, Control.GetOptions(added[ia]))
				ctl.SyncFromJson(ctl.CreateJsonFromDict(added[ia]))
				target.append(ctl)
			# fix order of items now that target only contains items that "are" also in source
			# note: ADDED items are the same instances as those in source, however,
			# pre-EXISTING items only have the same id property value [idProp], to be synced -- if desired -- outside this function
			while r:
				r = False
				for ti in xrange(0, ls):
					if (target[ti].__dict__[idProp] != source[ti][idProp]):
						# find current index in target thats to be moved to it
						c = util.ListIndexOf(target, lambda obj: obj.__dict__[idProp] == source[ti][idProp])
						if c < ti:
							r = True
						target[ti], target[c] = target[c], target[ti]
						if r:
							break
		def preprocessTemplates(json, temps):
			if type(json) == list:
				for i in xrange(0, len(json)):
					json[i] = preprocessTemplates(json[i], temps)
			elif type(json) == dict:
				for k, v in json.items():
					if k != '$template_id' or not v in temps:
						json[k] = preprocessTemplates(json[k], temps)
					else:
						del json[k]
						for tk, tv in temps[v].items():
							if not tk in json:
								json[tk] = tv
			return json
		if util.IsString(json):
			json = simplejson.loads(util.FixupJson(json))
		if 'options' in json and '$templates' in json['options']:
			temps = json['options']['$templates']
			if type(temps) == dict:
				del json['options']['$templates']
				preprocessTemplates(json, temps)
		util.SyncDict(self.options, Control.GetOptions(json))
		added, removed, ctls = [], [], Control.GetControls(json)
		merge(self.controls, ctls, 'id', added, removed)
		for c in xrange(0, len(self.controls)):
			self.controls[c].SyncFromJson(ctls[c])

	def ToJson(self):
		tempPath = self.templatePath and self.appServer.MapPath(self.templatePath) or ''
		if self.templatePath and os.path.isfile(tempPath) and (os.path.getmtime(tempPath) > self.templateLoadTime):
			self.LoadFromTemplate(self.templatePath)
		return util.ToJson(self.CreateJson(self.options, self.ControlsToJsonList()))
