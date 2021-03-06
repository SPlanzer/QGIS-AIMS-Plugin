################################################################################
#
# Copyright 2016 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the 
# LICENSE file for more information.
#
################################################################################

import psycopg2
from Error import Error
import AIMSDataManager.Config
import getpass
from AIMSDataManager.Config import ConfigReader
from AimsUI.AimsLogging import Logger

aimslog = Logger.setup()

_db = None
_autocommit = True
_restartRequired = False

config = ConfigReader()
_host = config.configSectionMap('db')['host']
_port = config.configSectionMap('db')['port']
_name = config.configSectionMap('db')['name']
_user=getpass.getuser()
_password=''

_aimsSchema='reference'


def setup(d):
    aimslog.info('Setting DB, {}'.format(d))
    setHost(d['host'])
    setPort(d['port'])
    setDatabase(d['name']) 
    setAimsSchema(d['aimsschema'])
    setUser(d['user'])
    setPassword(d['password'])

def host(): return _host
def setHost(host): 
    global _host
    if _host!=host:
        _host=host; 
        _reset()

def port(): return _port
def setPort(port): 
    global _port
    if _port!=port:
        _port=port
        _reset()

def database(): return _name
def setDatabase(name): 
    global _name
    if _name!=name:
        _name=name
        _reset()

def user(): return _user
def setUser(user): 
    global _user
    if _user!=user:
        _user=user
        _reset()

def password(): return _password
def setPassword(password): 
    global _password
    if _password!=password:
        _password=password
        _reset()

def aimsSchema(): return _aimsSchema
def setAimsSchema(aimsSchema): 
    global _aimsSchema
    if _aimsSchema!=aimsSchema:
        _aimsSchema=aimsSchema
        _reset()

def _reset():
    global _db
    global _restartRequired
    if _db:
        _restartRequired = True
        _db = None

def connection():
    global _db, _autocommit
    if _db == None:
        if _restartRequired:
            raise Error("You need to restart the application after changing database settings")
        db = psycopg2.connect(
            host=_host, 
            port=_port,
            database=_name, 
            user=_user, 
            password=_password
        )
        db.set_isolation_level(0)
        c = db.cursor()
        c.execute('set search_path='+_aimsSchema+', public' )
        _db = db
        _autocommit = True
    return _db

def execute(  sql, *params ):
    global _db
    # Handle special case where sql is just a function name
    if ' ' not in sql:
        sql = 'select ' + sql + '(' + ','.join(('%s',)*len(params))+')'
    db = connection()
    if not db:
        return None
    cur = db.cursor()
    try:
        cur.execute( sql, params )
        if _autocommit:
            db.commit()
    except:
        if _autocommit:
            db.rollback()
        raise
    return cur

def executeScalar(  sql, *params ):
    cur = execute( sql, *params )
    for r in cur:
        if len(r) == 1:
            return r[0]
        break
    return None

def executeRow(  sql, *params ):
    cur = execute( sql, *params )
    for r in cur:
        return r
        break
    return None

def beginTransaction( ):
    global _autocommit
    if _db:
        _db.commit()
        _autocommit = False

def commit( ):
    global _autocommit
    if _db:
        _db.commit()
        _autocommit = True

def rollback( ):
    global _autocommit
    if _db:
        _db.rollback()
        _autocommit = True
