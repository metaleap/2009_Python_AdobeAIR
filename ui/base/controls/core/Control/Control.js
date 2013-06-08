$M.defType('core/Control', null, {

	init: function(parent, id, json) {
		this.dataProps = [];
		this.defaults = {};
		this.id = id;
		this.isDomAppended = false;
		this.ignoreControls = false;
		this.pulseUp = true;
		this.pulseTimer = undefined;
		this.pulseOpacity = undefined;
		this.typeName = $B.Text.Safe(this.type = json.type);
		if (!(this.controls = json.controls)) this.controls = [];
		if (!(this.options = json.options)) this.options = {};
		$M.syncObject(this.options, { opacityPulseUp: '0.7', opacityPulseDown: '0.3', disabled: $B.Meta.ToBool(parent.disabled) });
		this.parent = (((typeof parent) == 'string') ? null : parent);
		if (!this.options.ext) {
			this.$ext = this.ext = null;
			this.$dom = $J(this.dom = $D.createElement(this.options.domType ? this.options.domType : (this.options.domType = 'DIV')));
		} else {
			this.$ext = new (eval(this.options.ext.__type))(this.ext = $B.Meta.Set($B.Meta.Clone(this.options.ext, '__type'), 'id', ((this.parent && this.parent.dom) ? this.parent.dom.id : parent) + '_' + this.id));
			if (!(this.$dom = ((this.dom = this.$ext.getEl()) ? $J(this.dom) : null)))
				this.dom = null;
		}
		if (this.dom && this.$dom)
			this.initDom(parent);
	},

	append: function(tagName, id, className) {
		var elem, $elem;
		if (this.dom) {
			(elem = $D.createElement(tagName)).id = this.dom.id + '_' + id;
			return ($elem = $J(elem)).attr({ 'class': className }).appendTo(this.$dom);
		}
	},

	dataSetup: function(prop) {
		if (this.dom && !$B.Array.Contains(this.dataProps, prop)) {
			this.dataProps.push(prop);
			for (var i = 1; i < arguments.length; i++)
				this.$dom[arguments[i]](this.onDataSync ? this.onDataSync : (this.onDataSync = this.method(this.dataSync)));
		}
	},

	dataSync: function(e) {
		var dataID, pos, prop, domProp, jsonProp, get, tmp;
		if (this.dom)
			for (var i = 0, l = this.dataProps.length; i < l; i++) {
				dataID = this.dom.id + '_' + $B.Text.Safe(prop = this.dataProps[i]);
				if ((pos = prop.indexOf(':')) > 0) {
					jsonProp = prop.substr(0, pos);
					domProp = prop.substr(pos + 1);
				} else
					domProp = jsonProp = prop;
				get = this.method(function() { return ((domProp[0] == '$') ? (this.$dom[domProp.substr(1)]()) : (this.dom[domProp])); });
				if ((((tmp = get()) == undefined) ? (this.defaults[jsonProp]) : (tmp)) == ((this.options[jsonProp] == undefined) ? (this.defaults[jsonProp]) : (this.options[jsonProp]))) {
					this.stopPulse();
					delete $M.poll.data[dataID];
				} else {
					this.startPulse();
					$M.poll.data[dataID] = tmp;
				}
			}
	},

	eachControl: function(fn, self) {
		for (var i = 0, l = this.controls.length; i < l; i++)
			fn.apply(this.controls[i]);
		if (self)
			fn.apply(this);
	},

	getDefaultClassNames: function() {
		var classes = [], typeName = this.typeName;
		while (typeName && (typeName != '__')) {
			classes[classes.length] = typeName;
			typeName = $M.reflection[typeName].baseTypeName;
		}
		return classes;
	},

	initDom: function(parent) {
		this.dom.id = ((this.parent && this.parent.dom) ? this.parent.dom.id : parent) + '_' + this.id;
		if (this.options.domStyle)
			for (var cssProp in this.options.domStyle)
				this.dom.style[cssProp] = this.options.domStyle[cssProp];
		this.syncDomProps(true);
		this.$dom.blur(this.method(function(e) {
			delete this.focused;
		}));
		this.$dom.focus(this.method(function(e) {
			this.focused = true;
		}));
	},

	isDisabled: function() {
		return ((parent && parent.isDisabled && parent.isDisabled()) || (this.options.disabled));
	},

	logError: function(methodName, error) {
		$M.log('(' + this.type + ') "' + (this.dom ? this.dom.id : this.id) + '"' + '.' + methodName + '()---' + error);
	},

	method: function(fn) {
		return $B.Meta.CreateMethod(this, fn);
	},

	onAppendToDom: function() {
		this.isDomAppended = true;
	},

	onCreateChildControl: function(childControl, childJson) {
	},

	setDisabled: function(v) {
		this.options.disabled = v = ((v == undefined) ? (undefined) : ($B.Meta.ToBool(v)));
		if (this.dom)
			this.dom.disabled = this.isDisabled();
		this.eachControl(function() { this.setDisabled(this.isDisabled()); }, true);
	},

	setDefaults: function(json) {
		for(var p in json) {
			this.defaults[p] = json[p];
			if (this.options[p] == undefined)
				this.options[p] = json[p];
		}
	},

	setOption: function(json, option, value) {
		return $B.Meta.Set(json, 'options', option, value);
	},

	setOptionDomStyle: function(json, option, value) {
		return $B.Meta.Set(json, 'options', 'domStyle', option, value);
	},

	startPulse: function() {
		if (this.dom && !this.pulseTimer) {
			this.pulseOpacity = this.dom.style.opacity;
			this.pulseTimer = setInterval(this.method(this.stepPulse), 500);
			this.stepPulse();
		}
	},

	stepPulse: function() {
		if (this.dom)
			this.$dom.animate($B.Meta.Set('opacity', (this.pulseUp = !this.pulseUp) ? (this.options.opacityPulseUp) : (this.options.opacityPulseDown)), { queue: false });
	},

	stopPulse: function() {
		if (this.dom && this.pulseTimer) {
			clearInterval(this.pulseTimer);
			this.pulseTimer = undefined;
			this.pulseUp = true;
			this.$dom.stop();
			this.dom.style.opacity = this.pulseOpacity;
		}
	},

	syncDom: function(controls) {
		var cls, className = this.options.domClass, userClasses = className ? className.split(' ') : [], controlClasses = this.getDefaultClassNames(), last, tmp, anim = null, added, removed;
		this.stopPulse();
		for (var c = 0; c < controlClasses.length; c++)
			if (!$B.Array.Contains(userClasses, cls = controlClasses[c]))
				userClasses.push(cls);
		if (this.dom.className != (className = userClasses.join(' ')))
			this.dom.className = className;
		if (this.options.domStyle && this.dom.style)
			if (this.dom.style.length == 0)
				for (var cssProp in this.options.domStyle)
					this.dom.style[cssProp] = this.options.domStyle[cssProp];
			else
				for (var cssProp in this.options.domStyle)
					if (this.dom.style[cssProp] != this.options.domStyle[cssProp])
						if ($B.UI.Anim.enabled && ((!this.options.anims) || (this.options.anims[cssProp] !== false)))
							(anim ? anim : (anim = {}))[cssProp] = this.options.domStyle[cssProp];
						else
							this.dom.style[cssProp] = this.options.domStyle[cssProp];
		this.syncDomProps();
		if (anim)
			$M.animateChanges(this, anim, function(animated) {
				//	jQuery animations ignore some css properties that also get lost instead of being set. just to be on the safe side after anim:
				for (var cssProp in this.options.domStyle)
					if (this.dom.style[cssProp] != this.options.domStyle[cssProp])
						this.dom.style[cssProp] = this.options.domStyle[cssProp];
				//	any updates still pending because they were initiated between poll.send and poll.onResponse? restart the flashing then.
				for (var i = 0, l = this.dataProps.length; i < l; i++)
					if ($M.poll.data[this.dom.id + '_' + this.dataProps[i]]) {
						this.startPulse();
						break;
					}
			});
		if (controls != null) {
			$B.Array.MergeObjects(this.controls, controls, 'id', added = [], removed = []);
			for (var i = 0, l = removed.length; i < l; i++) {
				var cleanUp = this.method(function() {
					$M.controls[removed[i].dom.id] = undefined;
					delete $M.controls[removed[i].dom.id];
					this.dom.removeChild(removed[i].dom);
				});
				if (removed[i].options.fade)
					$B.UI.Anim.FadeOut(removed[i].$dom, cleanUp);
				else
					cleanUp();
			}
			for (var i = 0, l = this.controls.length; i < l; i++) {
				if (((typeof controls[i]) == 'object') && ((tmp = $M.syncControl(this, this.dom.id, this.controls[i].id, controls[i])) != this.controls[i])) {
					this.controls[i] = tmp;
					if (tmp.options.fade)
						tmp.$dom.hide();
					if (last)
						last.$dom.after(tmp.dom);
					else
						this.$dom.prepend(tmp.dom);
					if (tmp.options.fade)
						$B.UI.Anim.FadeIn(tmp.$dom);
				}
				last = this.controls[i];
			}
		}
	},

	syncDomProps: function(force) {
		if (this.options.domProps && this.dom)
			for (var p in this.options.domProps)
				if (force || (this.$dom.attr(p) != this.options.domProps[p]))
					this.$dom.attr($B.Meta.Set(p, this.options.domProps[p]));
		//if (this.$ext && this.dom && this.dom.id && this.isDomAppended)
		//	this.$ext.render(this.dom.id);
	},

	toString: function(escapeForHtml) {
		return $B.Meta.ToString(this, escapeForHtml, ['parent', '$dom', 'dom']);
	}

});


$M.defType('core/Html', 'core/Control', {
});


$M.defType('core/HtmlAnchor', 'core/Html', {

	init: function(parent, id, json) {
		json.options.domType = 'A';
		this._base(parent, id, json);
	}

});


$M.defType('core/HtmlInput', 'core/Html', {

	init: function(parent, id, json) {
		json.options.domType = 'INPUT';
		this._base(parent, id, json);
	}

});


$M.defType('core/HtmlCheckBox', 'core/HtmlInput', {

	init: function(parent, id, json) {
		$B.Meta.Set(json, 'options', 'domProps', 'type', 'checkbox');
		this._base(parent, id, json);
		this.setDefaults({ checked: false });
		$B.Meta.SyncBool(this.dom, json.options, 'checked', true);
		this.dataSetup('checked', 'click');
	},

	syncDom: function(controls) {
		$B.Meta.SyncBool(this.dom, this.options, 'checked');
		this._base(controls);
	}

});


$M.defType('core/HtmlHeadline', 'core/Html', {

	init: function(parent, id, json) {
		if ((!json.options.size) || (!parseInt(json.options.size)))
			json.options.size = 1;
		if (!json.options.domType)
			json.options.domType = 'H' + json.options.size;
		this._base(parent, id, json);
	},

	syncDom: function(controls) {
		this._base(controls);
		if (this.$dom.text() != this.options.title)
			this.$dom.text(this.options.title);
	}

});


$M.defType('core/OverlayPrompt', 'core/Control', {

	init: function(parent, id, json) {
		json.options.fade = true;
		json.options.domClass = 'rox-overlay';
		this._base(parent, id, json);
	}

});


$M.defType('core/AccordionControl', 'core/Control', {

	init: function(parent, id, json) {
		this._base(parent, id, json);
	}

});


$M.defType('core/FlexiPanel', 'core/Control', {

	init: function(parent, id, json) {
		this._base(parent, id, json);
	}

});


$M.defType('core/FlexiBox', 'core/Control', {

	init: function(parent, id, json) {
		this.ctlHead = this.ctlPanel = null;
		json.controls = [{ id: 'headline', type: 'core/HtmlHeadline', options: $B.Meta.Set(json.options.ctlHeadline, 'size', 2), controls: [] },
		                 { id: 'panel', type: 'core/FlexiPanel', options: json.options.ctlPanel || {}, controls: [] }];
		this._base(parent, id, json);
		this.ignoreControls = true;
	},

	onCreateChildControl: function(childControl, childJson) {
		if (childControl.id == 'headline')
			this.ctlHead = childControl;
		else if (childControl.id == 'panel')
			this.ctlPanel = childControl;
	},

	syncDom: function(controls) {
		this._base(controls);
	}

});
