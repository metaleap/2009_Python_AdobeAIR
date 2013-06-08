from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1247513411.65626
_template_filename=u'/Users/roxor/dev-py/metaleap/src/metaleap/ui/api/stylesheet.dyn.css'
_template_uri=u'/api/stylesheet.dyn.css'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
_exports = []


# SOURCE LINE 1

import random, simplejson
from core import util


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        type = context.get('type', UNDEFINED)
        Request = context.get('Request', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        str = context.get('str', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 4

        for k in Request.args:
                if k and type(k) == str and k.endswith('.ccss'):
                        vpath = _.GetCssUrl(k)
                        if vpath:
                                raise util.RedirectError(vpath + '?r=' + str(random.random()))
                        break
        
        
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin()[__M_key]) for __M_key in ['k','vpath'] if __M_key in __M_locals_builtin()]))
        return ''
    finally:
        context.caller_stack._pop_frame()


