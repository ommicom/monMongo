__author__ = '0mic'
__version__ = '0.7.0'
__build__ = '6'

import sys
import os
import logging 
from cl_stat import Puller, Pusher
from settings import mongo_settings, common, http_settings, log_settings
sys.path.append(os.path.dirname(os.getcwd()))
from toolkit import mtimer

def main():
    _LOG_FORMAT = logging.Formatter('%(asctime)s\t%(levelname)s\t%(lineno)d\t%(message)s')
    _LOG_HANDLER = {'FILE':logging.FileHandler('monstat-client.log'),'CON':logging.StreamHandler(sys.stdout)}
    _LOG_LEVEL = {'DEBUG':logging.DEBUG,'INFO':logging.INFO,'WARNING':logging.WARNING,'ERROR':logging.ERROR,'CRITICAL':logging.CRITICAL,
               'NOTSET':logging.NOTSET}
    
    log_handler = _LOG_HANDLER[log_settings.get('outlet', 'FILE').upper()]
    log_level = _LOG_LEVEL[log_settings.get('level', 'ERROR').upper()]
    cycle = common.get('cycle', 5)
    qsize = common.get('qsize', None)
    mongo_server = mongo_settings.get('server', '127.0.0.1')
    mongo_port = mongo_settings.get('port', 27017)
    http_server = http_settings.get('server', '127.0.0.1')
    http_port = http_settings.get('port', 80)
    http_method = http_settings.get('method', '/')
    
    log = logging.getLogger()
    log.setLevel(log_level)
    log.addHandler(log_handler)
    log.handlers[0].setFormatter(_LOG_FORMAT)
    
    puller = Puller(mongo_server, mongo_port, log=log)
    pusher = Pusher(http_server, http_port, http_method, log=log)    
    puller.subscribe(pusher)
    
    log.info('Start monMongo-client ver.{0}.{1}'.format(__version__, __build__))
    t = mtimer.Timer(puller.pull, cycle)
    t.start()          
    
if __name__ == '__main__':
    sys.exit(main())