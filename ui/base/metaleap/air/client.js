$M.air = {

	bridge: $W.parentSandboxBridge

};

$M.setTitleCore = $M.setTitle;
$M.setTitle = function(title) {
	$M.setTitleCore(title);
	$M.air.bridge.setTitle(title);
};
