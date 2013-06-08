
var $D = document;
var $W = window;
var $R = function(prefix, resName, args) {
	return $B.Resources.__Get.apply($B.Resources, arguments);
};

var $M = {
	air: null,
	bootTimeout: null,
	box: null,
	controls: {},
	debug: false,
	lastJson: null,
	preload: {},
	reflection: { __: {} },
	timerBusy: false,
	timerHandlers: [],
	windowFocused: true,

	poll: {
		busy: false,
		currentBackgroundDefers: 0,
		data: {},
		defaultBackgroundDefers: 4,
		deferring: false,
		error: false,
		fail: false,
		interval: 2000,
		lastResponseTime: 0,
		lastSendTime: 0,
		paused: false,
		reconnectFactor: 10,
		timeout: 5000,
		url: '/api/core.dyn.json',

		__createCallback: function(name, callback, index, count) {
			return function() { $M['cb_' + $B.Text.Safe(name)] = callback; $M.loadType(name, null, index, count); };
		},

		__collectTypeDependencies: function(controls, arr) {
			if (controls && controls.length)
				for (var i = 0, l = controls.length; i < l; i++) {
					if (controls[i] && controls[i].type && ($J.inArray(controls[i].type, arr) < 0))
						arr.push(controls[i].type);
					$M.poll.__collectTypeDependencies(controls[i].controls, arr);
				}
		},

		onOffline: function() {
			$M.setTitle($R('fail00'));
			$M.poll.fail = true;
			$M.poll.deferring = false;
			$B.UI.Anim.FadeIn($J('#__loader'));
			if ($M['failanim'])
				$J('#__loader_info').attr('style', 'background-image: none;');
		},

		onOnline: function() {
			$M.setTitle($R('wait'));
			$M.poll.fail = false;
			$B.UI.Anim.FadeOut($J('#__loader'));
		},

		onResponse: function(json) {
			var callback = $M.syncPageJson, arr;
			$M.poll.paused = true;
			$M.poll.lastResponseTime = $B.DateTime.Ticks();
			if ($M.poll.fail)
				$M.poll.onOnline();
			$M.poll.busy = false;
			if (($M.lastJson = json = $B.UI.PreprocessJson(json)) && (json.controls)) {
				$M.poll.__collectTypeDependencies(json.controls, arr = []);
				for (var i = 0, l = arr.length; i < l; i++)
					if (!$M.reflection[$B.Text.Safe(arr[i])])
						callback = $M.poll.__createCallback(arr[i], callback, i, l);
			}
			try {
				callback();
			} catch(e) {
				$M.onError(e);
			}
		},

		send: function() {
			var tmp, now;
			if ($M.poll.deferring && ($M.poll.currentBackgroundDefers != $M.poll.defaultBackgroundDefers)) {
				$M.poll.lastResponseTime = $B.DateTime.Ticks();
				$M.poll.currentBackgroundDefers++;
			} else {
				$M.poll.currentBackgroundDefers = 0;
				if (!($M.poll.paused || $B.UI.Anim.Counter || $M.poll.error))
					if ((!$M.poll.busy) || (($M.poll.fail) && ((($B.DateTime.Ticks() - $M.poll.lastResponseTime) % ($M.poll.interval * $M.poll.reconnectFactor)) > ($M.poll.interval * ($M.poll.reconnectFactor - 1))))) {
						$M.poll.busy = true;
						$J('#__loader_info h2 span').html($R('fail19'));
						if ($M['failanim'])
							$J('#__loader_info').attr('style', 'background-image: url("' + $M['failanim'] + '");');
						$J.post($M.poll.url + '?l=' + $M.poll.lastSendTime + '&_=' + (now = $B.DateTime.Ticks()), $B.Meta.Set('data', $B.Meta.ToString($M.poll.data)), $M.poll.onResponse, 'json');
						$M.poll.data = {};
						$M.poll.lastSendTime = now;
					} else if ((($B.DateTime.Ticks() - $M.poll.lastResponseTime) > $M.poll.timeout) && (!$M.poll.fail) && $M.windowFocused)
						$M.poll.onOffline();
					else if ($M.poll.fail) {
						if ($M['failanim'])
							$J('#__loader_info').attr('style', 'background-image: none;');
						$J('#__loader_info h2 span').html($R('fail18', [((($M.poll.interval / 1000) * $M.poll.reconnectFactor) - Math.round((($B.DateTime.Ticks() - $M.poll.lastResponseTime) % ($M.poll.interval * $M.poll.reconnectFactor)) / 1000))]));
					}
			}
		}

	},

	__defCore: function(name, baseTypeName, definition) {
		var baseType = (baseTypeName ? $M.reflection[baseTypeName] : $B.Meta.__), meta;
		if ($M.reflection[name])
			throw $R('error_id_type_redefined', [name]);
		if (!baseTypeName)
			baseTypeName = '__';
		if (!baseType)
			throw $R('error_id_type_unknownbase', [name, baseTypeName]);
		if (!(baseType.__Extend || (baseType.ctor && baseType.ctor.__Extend)))
			throw $R('error_id_type_notinheritable', [name, baseTypeName]);
		return ($M.reflection[name] = meta = { baseTypeName: baseTypeName, name: name, def: definition, ctor: (baseType.ctor || baseType).__Extend(definition) });
	},

	animateChanges: function(ctl, anim, callback) {
		var doAnim = false;
		for (var p in anim)
			if ((!(parseInt(anim[p]))) && (!(parseFloat(anim[p]))) && (p.toLowerCase().indexOf('color') < 0))
				delete anim[p];
		for (var p in anim) { doAnim = true; break; }
		if (doAnim)
			$B.UI.Anim.Animate(ctl.$dom, anim, function() { if (callback) callback.apply(ctl, [doAnim]); });
		else if (callback)
			callback.apply(ctl, [doAnim]);
		return doAnim;
	},

	cancelEvent: function(event) {
		event.preventDefault();
		event.stopPropagation();
		return false;
	},

	clearBootTimeout: function() {
		if ($M.bootTimeout != null) {
			clearTimeout($M.bootTimeout);
			$M.bootTimeout = null;
			$M.clearBootTimeout = $M.noOp;
		}
	},

	defType: function(name, dependencies, typeDef) {
		var cb, n = $B.Text.Safe(name), sn;
		if (dependencies) {
			if (!$B.Meta.IsArray(dependencies))
				dependencies = [dependencies];
			this.loadTypes(dependencies, function() {
				$M.__defCore(n, $B.Text.Safe(dependencies[0]), typeDef);
				if (cb = $M['cb_' + n]) {
					$M['cb_' + n] = undefined;
					delete $M['cb_' + n];
					cb();
				}
			});
		} else
			return $M.__defCore(n, null, typeDef);
	},

	fixupPageIssues: function() {
		jQuery('.rox-maxheight').each(function() {
			var maxHeight = jQuery(this).height(), realHeight, diffHeight, child = jQuery(this).children()[0];
			if ((this.id) && ((diffHeight = ((realHeight = jQuery(child).height()) - maxHeight)) > 0))
				jQuery('#' + this.id + ' .rox-autoscroll').each(function() {
					$B.UI.Anim.Animate(jQuery(this), { 'height': ((realHeight - diffHeight) / 2) });
				});
		});
	},

	loadType: function(name, callback, index, count) {
		var loader = $J('#__scriptloader'), loaderHide = function() { $B.UI.Anim.FadeOut($B.UI.Anim.Animate(loader, { top: '-1.8em' })); }, loaderShow = function() { $B.UI.Anim.FadeIn($B.UI.Anim.Animate(loader, { top: '0em' })); }, cn = $B.Meta.TypeName(name), sn = $B.Text.Safe(name), sp = '/base/controls/' + cn.namespace + '/' + cn.name + '/' + cn.name + '.js', cb = callback;
		if (!count) count = 1;
		if (!index) index = 0;
		callback = function() {
			if ((count > 1) && (index == 0)) loaderHide();
			if ((!$M.reflection[sn]) && (!$M.poll.error))
				$M.onError(null, 'type_notdefined', [name], sp, false);
			else if ($M.reflection[sn] && cb)
				cb();
		};
		if(!$M.reflection[sn]) {
			if (count <= 1)
				loaderHide();
			else if (index >= (count - 1))
				loaderShow();
			$J('#__scriptloader').html($R('loading', [count, $B.Math.Percent(index, count)]));
			$M.reflection.__.__lastControlUrl = sp;
			$J.getScript(sp, callback);
			$M.loadStyleSheet('/api/stylesheet.dyn.css?/base/controls/' + cn.namespace + '/' + cn.name + '/' + cn.name + '.ccss');
		} else
			callback();
	},

	loadTypes: function(names, callback) {
		var callbackCreator = function(n, cb, i, l) { return function() { $M.loadType(n, cb, i, l) }; };
		for (var i = 0, l = names.length; i < l; i++)
			callback = callbackCreator(names[i], callback, i, l);
		callback();
	},

	loadStyleSheet: function(href) {
		if (!$B.Array.Exists($D.styleSheets, function(val) { return $B.Text.StartsWith(val.href, href); }))
			$J($D.createElement('link')).attr({ type: 'text/css', rel: 'stylesheet', href: (href + '=' + $B.DateTime.Ticks()) }).appendTo('#__head');
	},

	log: function(msg, idProp) {
		var fb = null;
		try {
			if (!$B.Meta.IsString(msg)) msg = $B.Meta.ToString(msg, idProp);
			try { fb = firebug; } catch(ex) { fb = null; }
			if (fb && fb.d && fb.d.console && fb.d.console.cmd && fb.d.console.cmd.log)
				fb.d.console.cmd.log(msg);
			else if (console && console.log)
				console.log(msg);
			return msg;
		} catch(e) {
			return e;
		}
	},

	noOp: function() {
	},

	onError: function(xhr, textStatus, error, url, retryContinueEnabled) {
		var xhr_status = ($B.Meta.IsString(xhr)) ? xhr : (xhr ? xhr.status || '999' : '999'), details = '', resErr;
		if (arguments.length == 1) {
			if ($B.Meta.IsObject(xhr))
				xhr['lastControlUrl'] = $M.reflection.__.__lastControlUrl;
			return $M.onError(null, xhr['message'], xhr, null, true);
		}
		if (!url)
			url = $M.poll.url;
		$M.clearBootTimeout();
		$M.poll.error = true;
		$M.poll.onOnline();
		$M.poll.paused = true;
		if ($B.Meta.IsEmptyObject(textStatus))
			textStatus = 'parsererror';
		else if ($B.Meta.IsObject(textStatus) && error == null) {
			error = textStatus;
			textStatus = '';
		}
		if ((resErr = $R('error_id_' + $B.Text.Safe(textStatus))) == ('error_id_' + $B.Text.Safe(textStatus)))
			resErr = '';
		$J('#__error_info_status').html((xhr_status == '999') ? '' : ('<b>' + ((xhr_status && $R('error_status_' + xhr_status)) ? ($R('error_status_' + xhr_status) + ' [' + xhr_status + ']') : ($R('error') + ' ' + (xhr_status ? xhr_status : ((error && error.__error_message) ? $B.Web.EscapeForHtml(error.__error_message) : $R('unknown'))) + ': ')) + '</b>'));
		$J('#__error_info_textstatus').html(textStatus ? (resErr ? (resErr + ' [' + $B.Text.Safe(textStatus) + ']') : textStatus) : ((error && error.__error_message) ? $B.Web.EscapeForHtml(error.__error_message) : $R('unknown')));
		$J('#__error_info button')[retryContinueEnabled === false ? 'hide' : 'show']();
		if (error) {
			if (($B.Meta.IsArray(error)) && textStatus && resErr)
				$J('#__error_info_textstatus').html($B.Text.Format(resErr, error));
			else if ($B.Meta.IsObject(error)) {
				details = '<div id="__error_info_details"><table cellpadding="4" cellspacing="4" width="100%">';
				for (var p in error)
					if ((!$B.Util.In(p, ['__error_message', '__source'])) && (!(($B.Util.In(p, ['stack', 'stacktrace'])) && (xhr_status == '200') && (textStatus == 'parsererror'))))
						details += ('<tr><td valign="top" align="right"><b>' + p + ':</b></td><td width="99%" valign="top">' + $B.Web.EscapeForHtml($B.Meta.ToString(error[p])) + '</td></tr>');
				details += ('</table></div>');
			} else
				details = $B.Meta.ToString(error);
			if (details)
				$J('#__error_info_textstatus').html($J('#__error_info_textstatus').html() + details);
		}
		$J('#__error_info_url').html($R('url') + ': <b style="display: inline;">' + url + '</b>');
		$J('#__error_info_debug_toggle')[0].checked = false;
		if (xhr && xhr.responseText) {
			$J('#__error_info_debug_toggle_controls')[0].style.display = 'inline-block';
			$J('#__error_info_debug').html((xhr.responseText.indexOf('Mako Runtime Error') < 0) ? ((xhr.responseText.indexOf('<html>') >= 0) ? (xhr.responseText) : ($B.Web.EscapeForHtml(xhr.responseText))) : (xhr.responseText.substring(xhr.responseText.indexOf('<style>'), xhr.responseText.indexOf('</head>')).replace('body', 'xbody') + xhr.responseText.substring(xhr.responseText.indexOf('<h3>'), xhr.responseText.lastIndexOf('</body>'))));
		} else
			$J('#__error_info_debug_toggle_controls')[0].style.display = 'none';
		$B.UI.Anim.FadeIn($J('#__error'));
		$M.setTitle('[ ' + $R('error') + ' ]');
	},

	onErrorShowServerResponse: function() {
		$B.UI.Anim.SlideToggle($J('#__error_info_debug'));
		$B.UI.Anim.ScrollTo($J('#__error_info'), $J('#__error_info_debug')[0]);
	},

	onTimer: function() {
		if (!$M.timerBusy)
			try {
				$M.timerBusy = true;
				for (var h = 0; h < $M.timerHandlers.length; h++)
					$M.timerHandlers[h]();
			} catch(e) {
				$M.onError(e);
			} finally {
				$M.timerBusy = false;
			}
	},

	recoverFromError: function(minimal) {
		$M.poll.error = false;
		if ($J('#__error_info_debug')[0].style.display != 'none')
			$B.UI.Anim.SlideUp($J('#__error_info_debug'));
		$J('#__error_info_debug_toggle')[0].checked = false;
		$B.UI.Anim.FadeOut($J('#__error'));
		if (!minimal) {
			$M.poll.onOnline();
			$M.setTitle($R('wait'));
			$M.poll.busy = false;
			$M.poll.lastResponseTime = $B.DateTime.Ticks();
			$M.poll.paused = false;
		}
	},

	setTitle: function(title) {
		if ($D.title != title)
			$D.title = title;
	},

	syncControl: function(parentControl, parentID, id, jsonControl) {
		var isRoot, sn, parent = ((parentControl && parentControl.dom) ? (parentControl.dom) : ($D.getElementById(parentID = (parentID ? parentID : (isRoot = $M.box.id))))), $parent = $J(parent), controlID = parent.id + '_' + id, control, $control, ctl, isNew = false;
		if (parent && id && jsonControl && jsonControl.type && (sn = $B.Text.Safe(jsonControl.type))) {
			if ((isNew = (!(control = document.getElementById(controlID)))) && $M.reflection[sn]) {
				control = ($M.controls[controlID] = ctl = new $M.reflection[sn].ctor(parentControl ? parentControl : parentID, id, jsonControl)).dom;
				if ((!control) && ctl.$ext && parent && (parentControl || ((parent == $M.box) && (parentControl = $M.$box))) && (parentControl.$ext)) {
					parentControl.$ext.add(ctl.$ext);
					parentControl.$ext.doLayout();
					ctl.$dom = $J(control = ctl.dom = ctl.$ext.getEl());
					ctl.initDom(parentControl);
				}
				if (parentControl && parentControl.onCreateChildControl)
					parentControl.onCreateChildControl(ctl, jsonControl);
			}
			if (control && ($control = $J(control)) && (ctl || (ctl = $M.controls[controlID]))) {
				if (!isNew)
					$M.syncObject(ctl.options, jsonControl.options, ctl.defaults);
				else if (isRoot) {
					$M.$box.html('');
					if (ctl.options.fade)
						$control.hide();
					if (ctl.$ext && $M.$box.$ext) {
						$M.$box.$ext.add($control);
						$M.$box.$ext.doLayout();
					} else
						$M.$box.append($control);
					ctl.onAppendToDom();
					if (ctl.options.fade)
						$B.UI.Anim.FadeIn($control);
				}
				ctl.syncDom(ctl.ignoreControls ? ctl.controls : jsonControl.controls);
			}
		}
		return ctl;
	},

	syncPageJson: function(json) {
		var redir;
		if (!json)
			json = $M.lastJson;
		$M.lastJson = null;
		if (json) {
			$M.setTitle(json.title);
			if (json.error)
				$M.onError(json.error.status || null, json.error.id || json.error, json.error.details || null, json.error.url || $M.poll.url);
			else if (redir = (json.pollUrl && ($M.poll.url != json.pollUrl)))
				$M.poll.url = json.pollUrl;
			else if (json.controls && json.controls.length)
				try {
					for (var i = 0, l = json.controls.length; i < l; i++)
						$M.syncControl(null, null, json.controls[i].id, json.controls[i]);
				} catch(ex) {
					$M.onError(ex);
				}
		}
		$M.poll.paused = false;
		//	JSON redirect? then let's not wait another 2 seconds but do it immediately
		if (redir && (!$M.poll.paused)) {
			$M.poll.lastSendTime = 0;
			$M.poll.send();
		}
		$M.fixupPageIssues();
	},

	syncObject: function(target, json, defaults) {
		var o, oc, tmp;
		if (defaults && json)
			for (var p in defaults)
				if ((typeof json[p]) == 'undefined')
					json[p] = defaults[p];
		if ((target && json) && ((typeof target) == 'object') && ((typeof json) == 'object'))
			for (var p in json)
				if (p && (p != 0) && (p != '0') && (!parseInt(p)) && (p[0] != '_') && (p != 'length'))
					if ((typeof (o = json[p])) != 'function')
						if (((typeof o) == 'object') && (!$B.Meta.IsArray(o)) && ((typeof target[p]) == 'object'))
							$M.syncObject(target[p], o, defaults ? defaults[p] : null);
						else
							target[p] = o;
		return target;
	}

};

Ext.onReady(function() {
	var preloaders, src, timeout;
	($M.box = new Ext.Viewport({
		items: [
			{ id: '__user', height: '0', region: 'north', split: true, layout: 'fit', title: 'top panel' },
			{ id: '__core', region: 'center', layout: 'fit', title: 'main panel' },
			{ id: '__sys', height: '0', region: 'south', split: true, layout: 'fit', title: 'bottom panel' }
		],
		layout: 'border',
		layoutConfig: {
		}
	})).doLayout();
	$J.ajaxSetup({
		cache: !$M.debug,
		error: function(xhr, textStatus, error) {
			var url = this.url, name, pos, len = '/base/controls/'.length;
			try {
				$M.poll.paused = false;
				if((!xhr) || (!xhr.status)) {
					$M.recoverFromError(true);
					$M.poll.onOffline();
				} else if ((xhr.status == 404 || xhr.status == '404') && textStatus == 'error' && error == undefined && (url = this.url) && (url.length) && (url.length > len) && ((pos = url.lastIndexOf('/')) > len) && (url = url.substring(len, pos)) && (cb = $M['cb_' + (name = $B.Text.Safe(url))]))
					$M.onError(null, 'type_notfound', [name], this.url, false)
				else {
					if ((!error) && xhr && xhr.responseText)
						try {
							eval(xhr.responseText);
						} catch(e) {
							error = e;
						}
					$M.onError(xhr, textStatus, error, this.url);
				}
			} catch(e) {
			}
		},
		timeout: 2000,
		type: 'POST'
	});
	if ($D.images && (preloaders = $J('.--preload-bg')))
		$J.each(preloaders, function(i, v) {
			($M.preload['pre_img_' + v.style.backgroundImage] = new Image()).src = src = v.style.backgroundImage.slice(4, -1);
		});
	$M.reflection.__.__lastControlUrl = '';
	$M.bootTimeout = setTimeout('$M.onError(null, "unloaded", null, $D.location.href, false);', $M.poll.timeout);
	$M.loadType('core/Control', function() {
		$M.timerHandlers.push($M.fixupPageIssues);
		$M.clearBootTimeout();
		$M.recoverFromError(false);
		setInterval('$M.onTimer();', 2500)
		setInterval('$M.poll.send();', $M.poll.interval);
		$M.poll.lastResponseTime = $B.DateTime.Ticks();
		$M.poll.send();
	});
});
