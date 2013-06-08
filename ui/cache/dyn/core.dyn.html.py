from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1247513843.1187241
_template_filename='/Users/roxor/dev-py/metaleap/src/metaleap/ui/core.dyn.html'
_template_uri='core.dyn.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
_exports = []


# SOURCE LINE 2

from core import gfx, util
import random


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        Session = context.get('Session', UNDEFINED)
        Request = context.get('Request', UNDEFINED)
        str = context.get('str', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 5
        __M_writer(u'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http//www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml">\n\t<head id="__head">\n\t\t<title>')
        # SOURCE LINE 8
        __M_writer(unicode(_('wait')))
        __M_writer(u'</title>\n\t\t<style type="text/css">\n\t\tbody {\n\t\t\tbackground-image: url(\'')
        # SOURCE LINE 11
        __M_writer(unicode(_.DynGfx(gfx.Texturize, '/gfx/bg/bg' + str(random.randint(1, 15)) + '.jpg', ext = 'jpg' )))
        __M_writer(u'\');\n\t\t}\n\t\t.preload-img {\n\t\t\tposition: absolute;\n\t\t\ttop: 100000px;\n\t\t\tleft: 100000px;\n\t\t}\n\t\t</style>\n\t\t<link rel="stylesheet" type="text/css" href="')
        # SOURCE LINE 19
        __M_writer(unicode( _.GetCssUrl('/styles/core.ccss') ))
        __M_writer(u'" />\n\t\t<xlink rel="stylesheet" type="text/css" href="/base/_lib/extjs/resources/css/ext-all.css"/>\n\t\t<script type="text/javascript" language="JavaScript" src="/base/_lib/')
        # SOURCE LINE 21
        __M_writer(unicode( _.IsDebugMode and 'jquery-1.3.2' or 'jquery-1.3.2.min' ))
        __M_writer(u'.js"></script>\n\t\t<script type="text/javascript" language="JavaScript" src="/base/_lib/jquery.color.js"></script>\n\t\t<script type="text/javascript" language="JavaScript" src="/base/_lib/jquery.scrollTo.js"></script>\n\t\t<script type="text/javascript" language="JavaScript" src="/base/_lib/extjs/adapter/')
        # SOURCE LINE 24
        __M_writer(unicode( _.IsDebugMode and 'ext-jquery-adapter-debug' or 'ext-jquery-adapter' ))
        __M_writer(u'.js"></script>\n\t\t<script type="text/javascript" language="JavaScript" src="/base/_lib/extjs/')
        # SOURCE LINE 25
        __M_writer(unicode( _.IsDebugMode and 'ext-all-debug' or 'ext-all' ))
        __M_writer(u'.js"></script>\n\t\t<script type="text/javascript" language="JavaScript" src="/base/base.js"></script>\n\t\t<script type="text/javascript" language="JavaScript" src="/base/metaleap/core.js"></script>\n')
        # SOURCE LINE 28
        if _.AirMode:
            # SOURCE LINE 29
            __M_writer(u'\t\t<script type="text/javascript" language="JavaScript" src="/base/metaleap/air/mode.js"></script>\n')
        # SOURCE LINE 31
        if Request.IsAir:
            # SOURCE LINE 32
            __M_writer(u'\t\t<script type="text/javascript" language="JavaScript" src="/base/metaleap/air/client.js"></script>\n')
        # SOURCE LINE 34
        __M_writer(u'\t\t<script type="text/javascript" language="JavaScript" src="/cache/scripts/res_')
        __M_writer(unicode(Session and Session.PreferredLanguage or 'en'))
        __M_writer(u'.js"></script>\n\t\t<script language="JavaScript" type="text/javascript">\n\t\t\tExt.BLANK_IMAGE_URL = \'/base/_lib/extjs/resources/images/default/s.gif\';\n\n\t\t\tfunction __onPageBlur() {\n\t\t\t\t$M.windowFocused = false;\n\t\t\t\t$M.poll.deferring = true;\n\t\t\t}\n\n\t\t\tfunction __onPageError(msg, url, line) {\n\t\t\t\t$M.clearBootTimeout();\n\t\t\t\t$M.onError(null, null, { error: msg, pollurl: $M.poll.url, lastcontrolurl: $M.reflection.__.__lastControlUrl, line: line }, url, false);\n\t\t\t\treturn true;\n\t\t\t}\n\n\t\t\tfunction __onPageFocus() {\n\t\t\t\t$M.poll.deferring = false;\n\t\t\t\t$M.windowFocused = true;\n\t\t\t\t$M.poll.lastResponseTime = $B.DateTime.Ticks();\n\t\t\t}\n\n\t\t\tfunction __onPageLoad() {\n\t\t\t\t$J(\'.--preload-img\').hide();\n\t\t\t\t$J(\'#__error_info_debug_toggle\')[0].checked = false; // otherwise, if this is checked just before you do a simple F5 refresh, it might be re-checked by the browser without firing onclick\n\t\t\t}\n\n\t\t\t$M.debug = ')
        # SOURCE LINE 60
        __M_writer(unicode( _.IsDebugMode and 'true' or 'false' ))
        __M_writer(u';\n\t\t</script>\n\t\t<link rel="shortcut icon" id="__icon" type="image/png" href="/gfx/icon32.png" />\n\t</head>\n\t<body id="__body" onfocus="__onPageFocus();" onblur="__onPageBlur();" onload="__onPageLoad();" onerror="return __onPageError(arguments[0], arguments[1], arguments[2]);">\n\t\t<div id="__loader" class="rox-overlay --preload-bg" style="display: none; background-image: url(\'')
        # SOURCE LINE 65
        __M_writer(unicode( _.DynGfx(gfx.Color, (0, 0, 0, 0.8)) ))
        __M_writer(u'\');">\n\t\t\t<div id="__loader_info" class="rox-overlay-box rox-boxshadow rox-maxheight --preload-bg" style="background-image: url(\'')
        # SOURCE LINE 66
        __M_writer(unicode( _.DynGfx(gfx.Alpha, 'gfx/bg_02.png', 0.6, 0.5, 0.5, 0.5) ))
        __M_writer(u'\');">\n\t\t\t\t<div>\n\t\t\t\t\t<h2><span></span><div>')
        # SOURCE LINE 68
        __M_writer(unicode(_('fail01')))
        __M_writer(u'</div></h2>\n\t\t\t\t\t<p>')
        # SOURCE LINE 69
        __M_writer(unicode(_('fail02')))
        __M_writer(u'</p>\n\t\t\t\t\t<ul class="--preload-bg rox-overlay-box-inner rox-autoscroll" style="background-image: url(\'')
        # SOURCE LINE 70
        __M_writer(unicode( _.DynGfx(gfx.Alpha, 'gfx/bg_03.png', 0.5) ))
        __M_writer(u'\');">\n')
        # SOURCE LINE 71
        if _.AirMode:
            # SOURCE LINE 72
            __M_writer(u'\t\t\t\t\t\t<li><b>')
            __M_writer(unicode(_('fail04')))
            __M_writer(u'</b><div>')
            __M_writer(unicode(_('fail05')))
            __M_writer(u'</div></li>\n\t\t\t\t\t\t<li><b>')
            # SOURCE LINE 73
            __M_writer(unicode(_('fail06')))
            __M_writer(u'</b><div>')
            __M_writer(unicode(_('fail07')))
            __M_writer(u'</div></li>\n\t\t\t\t\t\t<li><b>')
            # SOURCE LINE 74
            __M_writer(unicode(_('fail08')))
            __M_writer(u'</b><div>')
            __M_writer(unicode(_('fail09', str(_.DefaultPorts)[1:-1])))
            __M_writer(u'</div></li>\n')
            # SOURCE LINE 75
        else:
            # SOURCE LINE 76
            __M_writer(u'\t\t\t\t\t\t<li><b>')
            __M_writer(unicode(_('fail10')))
            __M_writer(u'</b><div>')
            __M_writer(unicode(_('fail11')))
            __M_writer(u'</div><div>')
            __M_writer(unicode(_('fail12')))
            __M_writer(u'</div></li>\n\t\t\t\t\t\t<li><b>')
            # SOURCE LINE 77
            __M_writer(unicode(_('fail13', _.HostName)))
            __M_writer(u'</b><div>')
            __M_writer(unicode(_('fail14', _.HostName)))
            __M_writer(u'</div></li>\n\t\t\t\t\t\t<li><b>')
            # SOURCE LINE 78
            __M_writer(unicode(_('fail15', _.HostName)))
            __M_writer(u'</b><div>')
            __M_writer(unicode(_('fail16')))
            __M_writer(u'</div></li>\n')
        # SOURCE LINE 80
        __M_writer(u'\t\t\t\t\t</ul>\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n\t\t<div id="__error" class="rox-overlay --preload-bg" style="display: none; background-image: url(\'')
        # SOURCE LINE 84
        __M_writer(unicode( _.DynGfx(gfx.Color, (0, 0, 0, 0.8)) ))
        __M_writer(u'\');">\n\t\t\t<div id="__error_info" class="rox-overlay-box rox-boxshadow rox-maxheight --preload-bg" style="background-image: url(\'')
        # SOURCE LINE 85
        __M_writer(unicode( _.DynGfx(gfx.Alpha, 'gfx/bg_02.png', 0.6, 0.5, 0.5, 0.5) ))
        __M_writer(u'\');">\n\t\t\t\t<div>\n\t\t\t\t\t<h2><span>\n\t\t\t\t\t\t<div id="__error_info_debug_toggle_controls" style="display: inline-block;"><input type="checkbox" id="__error_info_debug_toggle" onclick="$M.onErrorShowServerResponse();" /><label for="__error_info_debug_toggle">')
        # SOURCE LINE 88
        __M_writer(unicode(_('error_sh')))
        __M_writer(u'</label></div>\n\t\t\t\t\t\t<button onclick="$M.recoverFromError();" class="--preload-bg" style="display: inline;">')
        # SOURCE LINE 89
        __M_writer(unicode(_('error_rc')))
        __M_writer(u'</button>\n\t\t\t\t\t</span><div>')
        # SOURCE LINE 90
        __M_writer(unicode(_('error_title')))
        __M_writer(u'</div></h2>\n\t\t\t\t\t<ul class="--preload-bg rox-overlay-box-inner rox-autoscroll" style="background-image: url(\'')
        # SOURCE LINE 91
        __M_writer(unicode( _.DynGfx(gfx.Alpha, 'gfx/bg_03.png', 0.5) ))
        __M_writer(u'\');">\n\t\t\t\t\t\t<li id="__error_info_status"></li>\n\t\t\t\t\t\t<li id="__error_info_textstatus"></li>\n\t\t\t\t\t\t<li id="__error_info_url"></li>\n\t\t\t\t\t</ul>\n\t\t\t\t\t<div style="display: none;" id="__error_info_debug"></div>\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n\t\t<div id="__scriptloader" class="rox-boxshadow" style="position: absolute; top: -1.8em;"></div>\n\t\t<span style="display: none;">\n\t\t\t<img src="')
        # SOURCE LINE 102
        __M_writer(unicode( _.DynGfx(gfx.Alpha, 'gfx/bg_02.png', 0.6, 0.5, 0.5, 0.5) ))
        __M_writer(u'" class="--preload-img" style="display: inline;" onload="this.style.display=\'none\';" />\n\t\t\t<img src="')
        # SOURCE LINE 103
        __M_writer(unicode( _.DynGfx(gfx.Alpha, 'gfx/bg_03.png', 0.5) ))
        __M_writer(u'" class="--preload-img" style="display: inline;" onload="this.style.display=\'none\';" />\n\t\t\t<img src="')
        # SOURCE LINE 104
        __M_writer(unicode( _.DynGfx(gfx.Color, (0, 0, 0, 0.8)) ))
        __M_writer(u'" class="--preload-img" style="display: inline;" onload="this.style.display=\'none\';" />\n\t\t\t<img src="')
        # SOURCE LINE 105
        __M_writer(unicode( _.DynGfx(gfx.Color, (1, 1, 0.8, 0.85)) ))
        __M_writer(u'" class="--preload-img" style="display: inline;" onload="this.style.display=\'none\';" />\n\t\t</span>\n\t\t<noscript>\n\t\t\t<div id="__error_nojs">\n\t\t\t\t<div style="background-image: url(\'')
        # SOURCE LINE 109
        __M_writer(unicode( _.DynGfx(gfx.Color, [1, 1, 0.8, 0.85]) ))
        __M_writer(u'\');">\n\t\t\t\t\t')
        # SOURCE LINE 110
        __M_writer(unicode(_('fail_nojs', Request.user_agent.browser.title())))
        __M_writer(u'\n\t\t\t\t\t<a target="_blank" href="')
        # SOURCE LINE 111
        __M_writer(unicode(_('fail_nojs_url', Request.user_agent.browser.title())))
        __M_writer(u'">')
        __M_writer(unicode(_('fail_nojs_url_title')))
        __M_writer(u'</a>\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</noscript>\n\t</body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


