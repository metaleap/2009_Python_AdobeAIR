
$M.defType('frame/MainFrame', 'core/Control', {

	init: function(parent, id, json) {
		this._base(parent, id, json);
	},

	syncDom: function(controls) {
		this._base(controls);
	}

});
