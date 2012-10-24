__author__ = 'Omic'
__version__ = '0.7.0'
__build__ = '2'

import sys
import logging
from tornado import ioloop, httpserver
from settings import log_settings, http_settings, mongo_settings, table_val, graf_val
from sr_stat import Server

def main():
    _LOG_FORMAT = logging.Formatter('%(asctime)s\t%(levelname)s\t%(lineno)d\t%(message)s')
    _LOG_HANDLER = {'FILE':logging.FileHandler('monstat-server.log'),'CON':logging.StreamHandler(sys.stdout)}
    _LOG_LEVEL = {'DEBUG':logging.DEBUG,'INFO':logging.INFO,'WARNING':logging.WARNING,'ERROR':logging.ERROR,'CRITICAL':logging.CRITICAL,
               'NOTSET':logging.NOTSET}
    
    log_handler = _LOG_HANDLER[log_settings.get('outlet', 'FILE').upper()]
    log_level = _LOG_LEVEL[log_settings.get('level', 'ERROR').upper()]
    
    http_server = http_settings.get('server', '127.0.0.1')
    http_port = http_settings.get('port', 80)
    mongo_server = mongo_settings.get('server', '127.0.0.1')
    mongo_port = mongo_settings.get('port', 27017)
    mongo_database = mongo_settings.get('dbname', 'statistics')
    
    log = logging.getLogger()
    log.setLevel(log_level)
    log.addHandler(log_handler)
    log.handlers[0].setFormatter(_LOG_FORMAT)
    
    log.info('Start monMongo-server ver.{0}.{1} on {2}:{3}'.format(__version__, __build__, http_server, http_port))
    
    val = dict(table=table_val, graf=graf_val)
    http = httpserver.HTTPServer(request_callback=Server(mongo_server, mongo_port, mongo_database, **val))
    http.listen(http_port, http_server)
    ioloop.IOLoop.instance().start()
    
    
if __name__ == '__main__':
    sys.exit(main())