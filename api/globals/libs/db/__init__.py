import logging
import os, sys, stat
import time
import re
import inspect

try: 
    from gevent.coros import RLock, Semaphore
except: 
    from gevent.lock import RLock, Semaphore

from sqlalchemy.schema import MetaData
from sqlalchemy.engine import create_engine
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.interfaces import ConnectionProxy
from sqlalchemy.orm.session import sessionmaker, Session
from sqlalchemy.orm import scoped_session

from libs.singletone import Singleton
from gsettings import settings

log = logging.getLogger("user_server")
db_log = logging.getLogger("db_log")



def comes_from(depth=2):
    try:
        frame = inspect.stack()[depth][0]
    except IndexError:
        return "n/a"

    return "{0}<{1}>:{2}".format(frame.f_code.co_filename, frame.f_lineno, frame.f_code.co_name)


class DBSession(Session):
    def __init__(self, **kwargs):
        self.context = kwargs.pop('context', None) or {
            "id": "-",
            "type": "-",
            "reference": "-",
            "caller": comes_from(3)
        }

        self.language = kwargs.pop('language', getattr(settings, 'LANGUAGE_CODE', 'en'))

        #kwargs.update({
        #    'binds': _database._binds,
        #})

        #binds_ = {}
        #for tbl_ in _database._get_metadata().sorted_tables:
        #    binds_[tbl_] = engine
        #for db_, engine_ in _database._binds.items():
        #    print "FFF", db_, engine_, type(db_), isinstance(db_, type)

        super(DBSession, self).__init__(**kwargs)
        db_log.debug(u"GET_CNN %s(%s)", self._id, comes_from(5))



    @property
    def _id(self):
        if not getattr(self, "__x", None):
            self.__x = hex(id(self)) #.connection().connection))
        return self.__x

    def close(self):
        db_log.debug(u"PUT_CNN(%s): %s", self._id, comes_from())
        return super(DBSession, self).close()

    def add(self, instance):
        validate = getattr(instance, 'sa_validate', None)
        if callable(validate):
            log.debug(u"Call %s of %s", validate, instance)
            if not validate():
                log.debug(u"instance %s not valid - SKIP add to session", instance)
                return
        return super(DBSession, self).add(instance)


    def __get_bind(self, mapper, clause=None):
        bind_key = 'default'

        # mapper is None if someone tries to just get a connection
        if mapper is None:
            return super(DBSession, self).get_bind(mapper, clause), bind_key

        engine = None

        bind_key = getattr(self, '__bind_key', None)

        ## Flush bindkey for next request:
        if bind_key is not None:
            setattr(self, '__bind_key', None)

        if bind_key is None:
            bind_key = getattr(mapper.class_, 'db_config', {}).get('bind_key', None)
        access = None

        ## Try to find bind_key by access:
        if bind_key is None and self._flushing:
            access = 'w'
        else:
            access = 'r'

        if bind_key is not None or access is not None:
            engine = get_engine(bind_key=bind_key, access=access)

        if bind_key not in _database._connections:
            _database._connections[bind_key] = scoped_session(sessionmaker(
                bind=engine,
                class_=DBSession,
                expire_on_commit=False,
            ))

        return engine, bind_key


    def get_bind(self, mapper, clause=None):
        engine, bind_key = self.__get_bind(mapper, clause=clause)
        log.debug(u'Bind initiated as %s <%s>', bind_key, engine.pool.status())
        return engine


    def using_bind(self, name):
        setattr(self, '__bind_key', name)
        return self
        #s = DBSession()
        #vars(s).update(vars(self))
        #s._name = name
        #return s


class GreenQueuePool(QueuePool):
    def __init__(self, *args, **kwargs):
        super(GreenQueuePool, self).__init__(*args, **kwargs)
        if self._overflow_lock is not None:
            self._overflow_lock = RLock()


class TimingProxy(ConnectionProxy):
    def cursor_execute(self, execute, cursor, statement, parameters, context, executemany):
        now = time.time()
        try:
            return execute(cursor, statement, parameters, context)
        finally:
            total = (time.time() - now) * 1000
            _w = comes_from(10)
            _id = hex(id(context.connection.connection))
            _q = cursor.query

            try:
                query = statement % parameters
            except TypeError:
                query = statement

            try:
                if total < 100:
                    db_log.debug(u"QUERY %0.3f %s(%s): %s", total, _id, _w, re.sub("\s\s+", " ", query))
                else:
                    db_log.error(u"QUERY %0.3f %s(%s): %s", total, _id, _w, re.sub("\s\s+", " ", query))
            except Exception as e:
                log.debug('Error on log by: %s', e)



class __Database(object):
    __metaclass__ = Singleton
    _binds = {}
    _connections = {}
    _db_alias = getattr(settings, "DEFAULT_DB_ALIAS", 'database')
    _metadata = MetaData()
    _metadata_loaded = False

    ## name of module for SA model (default: sa_models.py):
    _sa_models_module_name = getattr(
        settings,
        "SQLALCHEMY_MODELS_MODULE_NAME",
        "sa_models"
    )


    def _get_metadata(self):
        return self.__class__._metadata


    def _set_active_db(self, db_alias):
        self.__class__._db_alias = db_alias

    def _get_engine(self, echo=False, bind_key=None, access=None):
        db_cfg = getattr(settings, 'SA_DATABASES', None)
        if db_cfg is None:
            raise RuntimeError("Please, specify database connection settings")

        if isinstance(access, str):
            access = list(access)
            

        ## No bind_key, try to get it by access:
        if bind_key is None and isinstance(access, (list, tuple)):
            for db_ident, db_params in db_cfg.iteritems():
                for acc_ in access:
                    if acc_ in db_params[1] or 'a' in db_params[1]:
                        bind_key = db_ident
                        break
                if bind_key is not None:
                    break

        db_alias = bind_key or self.__class__._db_alias
        if db_alias in self.__class__._binds:
            return self.__class__._binds[db_alias][0]
        if not db_alias in db_cfg:
            raise RuntimeError("Unknown DB alias '%s'" % db_alias)

        db = db_cfg[db_alias][0]
        access = db_cfg[db_alias][1]
        log.debug(u"Configure engine to %s", db)
        if db.startswith('sqlite'):
            engine = create_engine(db, echo=echo)
        else:
            proxy = TimingProxy()

            pool_size = int(os.environ.get('DB_POOL_SIZE', 5))
            if pool_size == 0:
                return None
            engine = create_engine(
                db,
                echo=echo,
                max_overflow=0,
                pool_size=pool_size,
                poolclass=GreenQueuePool,
                proxy=proxy,
                pool_timeout=5 #if not getattr(settings, "PRODUCTION") else 30,
            )

        self.__class__._binds[db_alias] = [engine, access,]
        return engine


    def _get_db_session(self, bind_key=None, access=None, echo=True, **kwargs):
        db_alias = bind_key or self.__class__._db_alias
        if db_alias not in _database._connections:
            engine = self._get_engine(bind_key=bind_key, echo=echo, access=access)
            self.__class__._connections[db_alias] = scoped_session(sessionmaker(
                bind=engine,
                class_=DBSession,
                expire_on_commit=False,
            ))

        connections_ = self.__class__._connections[db_alias]

        session = connections_(**kwargs)
        log.debug(u"DB<%s>: initiated as %s <%s>", id(session), db_alias, session.bind.pool.status())
        return session


    @staticmethod
    def __get_models_path(dirname):
        for path in sys.path:
            p = "/".join((path, dirname))
            if os.path.exists(p):
                return p

    @classmethod
    def __load_models_by_path(cls, dirpath):
        path_ = cls.__get_models_path(dirpath)
        if path_ is None:
            raise StopIteration()
        sys.path.append(path_)

        for name in os.listdir(path_):
            fpath = os.path.abspath("/".join((path_, name)))
            fstat = os.stat(fpath)

            ## Not a model directory, skip:
            if stat.S_ISREG(fstat.st_mode):
                continue

            ## Generate name of module to load for _load_models:
            yield name



    def _load_models(self, modules=None, dirpath=None):
        if modules is None and dirpath is not None:
            modules = self.__load_models_by_path(dirpath)
        if modules is None:
            modules = getattr(settings, "INSTALLED_APPS", ())
        apps = []
        for app in modules:
            module = __import__(app, fromlist=[self._sa_models_module_name])
            if hasattr(module, self._sa_models_module_name):
                apps.append(module)
        return apps




_database = __Database()

def set_active_db(db_alias):
    _database._set_active_db(db_alias)


def get_metadata():
    return _database._get_metadata()

def get_engine(**kwargs):
    return _database._get_engine(**kwargs)

def get_db_session(bind_key=None, **kwargs):
    return _database._get_db_session(bind_key=bind_key, **kwargs)



def load_orm_models(db_alias=None, **kwargs):
    db_alias = db_alias or _database._db_alias
    return _database._load_models(**kwargs)


def create_all(db_alias=None, **kwargs):
    db_alias = db_alias or _database._db_alias
    apps = _database._load_models(**kwargs)
    engine = _database._binds[db_alias][0]
    return get_metadata().create_all(engine)




