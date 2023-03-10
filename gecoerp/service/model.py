# -*- coding: utf-8 -*-

from functools import wraps
import logging
from psycopg2 import IntegrityError, OperationalError, errorcodes
import random
import threading
import time

import gecoerp
from gecoerp.exceptions import UserError, ValidationError, QWebException
from gecoerp.models import check_method_name
from gecoerp.tools.translate import translate
from gecoerp.tools.translate import _

from . import security

_logger = logging.getLogger(__name__)

PG_CONCURRENCY_ERRORS_TO_RETRY = (errorcodes.LOCK_NOT_AVAILABLE, errorcodes.SERIALIZATION_FAILURE, errorcodes.DEADLOCK_DETECTED)
MAX_TRIES_ON_CONCURRENCY_FAILURE = 5

def dispatch(method, params):
    (db, uid, passwd ) = params[0:3]

    # set uid tracker - cleaned up at the WSGI
    # dispatching phase in gecoerp.service.wsgi_server.application
    threading.current_thread().uid = uid

    params = params[3:]
    if method == 'obj_list':
        raise NameError("obj_list has been discontinued via RPC as of 6.0, please query ir.model directly!")
    if method not in ['execute', 'execute_kw']:
        raise NameError("Method not available %s" % method)
    security.check(db,uid,passwd)
    registry = gecoerp.registry(db).check_signaling()
    fn = globals()[method]
    with registry.manage_changes():
        res = fn(db, uid, *params)
    return res

def check(f):
    @wraps(f)
    def wrapper(___dbname, *args, **kwargs):
        """ Wraps around OSV functions and normalises a few exceptions
        """
        dbname = ___dbname      # NOTE: this forbid to use "___dbname" as arguments in http routes

        def tr(src, ttype):
            # We try to do the same as the _(), but without the frame
            # inspection, since we aready are wrapping an osv function
            # trans_obj = self.get('ir.translation') cannot work yet :(
            ctx = {}
            if not kwargs:
                if args and isinstance(args[-1], dict):
                    ctx = args[-1]
            elif isinstance(kwargs, dict):
                if 'context' in kwargs:
                    ctx = kwargs['context']
                elif 'kwargs' in kwargs and kwargs['kwargs'].get('context'):
                    # http entry points such as call_kw()
                    ctx = kwargs['kwargs'].get('context')
                else:
                    try:
                        from gecoerp.http import request
                        ctx = request.env.context
                    except Exception:
                        pass

            lang = ctx and ctx.get('lang')
            if not (lang or hasattr(src, '__call__')):
                return src

            # We open a *new* cursor here, one reason is that failed SQL
            # queries (as in IntegrityError) will invalidate the current one.
            cr = False

            try:
                cr = gecoerp.sql_db.db_connect(dbname).cursor()
                res = translate(cr, name=False, source_type=ttype,
                                lang=lang, source=src)
                if res:
                    return res
                else:
                    return src
            finally:
                if cr: cr.close()

        def _(src):
            return tr(src, 'code')

        tries = 0
        while True:
            try:
                if gecoerp.registry(dbname)._init and not gecoerp.tools.config['test_enable']:
                    raise gecoerp.exceptions.Warning('Currently, this database is not fully loaded and can not be used.')
                return f(dbname, *args, **kwargs)
            except (OperationalError, QWebException) as e:
                if isinstance(e, QWebException):
                    cause = e.qweb.get('cause')
                    if isinstance(cause, OperationalError):
                        e = cause
                    else:
                        raise
                # Automatically retry the typical transaction serialization errors
                if e.pgcode not in PG_CONCURRENCY_ERRORS_TO_RETRY:
                    raise
                if tries >= MAX_TRIES_ON_CONCURRENCY_FAILURE:
                    _logger.info("%s, maximum number of tries reached" % errorcodes.lookup(e.pgcode))
                    raise
                wait_time = random.uniform(0.0, 2 ** tries)
                tries += 1
                _logger.info("%s, retry %d/%d in %.04f sec..." % (errorcodes.lookup(e.pgcode), tries, MAX_TRIES_ON_CONCURRENCY_FAILURE, wait_time))
                time.sleep(wait_time)
            except IntegrityError as inst:
                registry = gecoerp.registry(dbname)
                for key in registry._sql_error.keys():
                    if key in inst.pgerror:
                        raise ValidationError(tr(registry._sql_error[key], 'sql_constraint') or inst.pgerror)
                if inst.pgcode in (errorcodes.NOT_NULL_VIOLATION, errorcodes.FOREIGN_KEY_VIOLATION, errorcodes.RESTRICT_VIOLATION):
                    msg = _('The operation cannot be completed, probably due to the following:\n- deletion: you may be trying to delete a record while other records still reference it\n- creation/update: a mandatory field is not correctly set')
                    _logger.debug("IntegrityError", exc_info=True)
                    try:
                        errortxt = inst.pgerror.replace('??','"').replace('??','"')
                        if '"public".' in errortxt:
                            context = errortxt.split('"public".')[1]
                            model_name = table = context.split('"')[1]
                        else:
                            last_quote_end = errortxt.rfind('"')
                            last_quote_begin = errortxt.rfind('"', 0, last_quote_end)
                            model_name = table = errortxt[last_quote_begin+1:last_quote_end].strip()
                        model = table.replace("_",".")
                        if model in registry:
                            model_class = registry[model]
                            model_name = model_class._description or model_class._name
                        msg += _('\n\n[object with reference: %s - %s]') % (model_name, model)
                    except Exception:
                        pass
                    raise ValidationError(msg)
                else:
                    raise ValidationError(inst[0])

    return wrapper

def execute_cr(cr, uid, obj, method, *args, **kw):
    recs = gecoerp.api.Environment(cr, uid, {}).get(obj)
    if recs is None:
        raise UserError(_("Object %s doesn't exist") % obj)
    return gecoerp.api.call_kw(recs, method, args, kw)


def execute_kw(db, uid, obj, method, args, kw=None):
    return execute(db, uid, obj, method, *args, **kw or {})

@check
def execute(db, uid, obj, method, *args, **kw):
    threading.currentThread().dbname = db
    with gecoerp.registry(db).cursor() as cr:
        check_method_name(method)
        res = execute_cr(cr, uid, obj, method, *args, **kw)
        if res is None:
            _logger.info('The method %s of the object %s can not return `None` !', method, obj)
        return res
