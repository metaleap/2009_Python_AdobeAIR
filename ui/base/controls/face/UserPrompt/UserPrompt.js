
$M.defType('face/UserPrompt', 'core/OverlayPrompt', {

	init: function(parent, id, json) {
		this._base(parent, id, json);
	},

	syncDom: function(controls) {
		this._base(controls);
	}

});
