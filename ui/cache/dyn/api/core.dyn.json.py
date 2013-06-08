from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1247513861.233598
_template_filename=u'/Users/roxor/dev-py/metaleap/src/metaleap/ui/api/core.dyn.json'
_template_uri=u'/api/core.dyn.json'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
_exports = []


# SOURCE LINE 1

import random


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        Session = context.get('Session', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 3
        __M_writer(u'\n{\n')
        # SOURCE LINE 5
        if not Session.Database:
            # SOURCE LINE 6
            __M_writer(u"\t$title: 'res:wait',\n\tpollUrl: '/api/user.dyn.json'\n")
            # SOURCE LINE 8
        else:
            # SOURCE LINE 9
            __M_writer(u'\ttitle: "')
            __M_writer(unicode( Session.UserName ))
            __M_writer(u'",\n\tcontrols: [\n\t]\n')
        # SOURCE LINE 13
        __M_writer(u'}\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


