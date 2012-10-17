import pymongo
import json
import multiprocessing
from urllib import urlencode
from tornado import httpclient, ioloop 
from toolkit import observer

class Puller(observer.Publisher):
    def __init__(self, mongo_server, mongo_port, log=None):
        self.__log = log
        self.__mongo_server = mongo_server
        self.__mongo_port = mongo_port
        observer.Publisher.__init__(self)
    
    def pull(self):
        pull_data = {'mongodb_stat':{}}
                
        try:
            mongo_connect = pymongo.Connection(self.__mongo_server, self.__mongo_port)            
        except pymongo.errors as err:
            if self.__log:
                self.__log.error(err)
            return
        
        mongodb_list = mongo_connect.database_names()
        for mongodb_name in mongodb_list:
            mongodb = mongo_connect[mongodb_name]
            pull_data['mongodb_stat'][mongodb_name] = mongodb.command('serverStatus')
        
        data = json.dumps(pull_data, default=self.__set_isoformat)    
        if self.__log:
            self.__log.debug(data)    
        self.notify(data)
    
    def __set_isoformat(self,dat):
        return dat.isoformat() if hasattr(dat, 'isoformat') else dat
    

class Pusher(observer.Subscriber):
    def __init__(self, http_server, http_port, http_method, _qsize=None, log=None): 
        self.__log = log             
        self.__queue = multiprocessing.Queue(_qsize*1024) if _qsize else multiprocessing.Queue()
        self.__http_server = http_server
        self.__http_port = http_port
        self.__http_method = http_method
        observer.Subscriber.__init__(self)
    
    def notification(self, data):        
        self.__queue.put(data)
        p_push = multiprocessing.Process(target=self.push())        
        p_push.start()
        p_push.join()        
    
    def push(self):
        try:
            client = httpclient.AsyncHTTPClient()
            while not self.__queue.empty():
                data = urlencode({'stat':self.__queue.get()})
                req = httpclient.HTTPRequest('http://{0}:{1}/{2}'.format(self.__http_server, self.__http_port, self.__http_method), method='POST', body=data)
                client.fetch(req, self.__async_request)
                ioloop.IOLoop.instance().start()
                if self.__log:
                    self.__log.debug('http://{0}:{1}/{2}'.format(self.__http_server, self.__http_port, self.__http_method))
                if self.__log:
                    self.__log.debug(data)
        except IOError as err:
            if self.__log:
                self.__log.error('Connection with http-server not set. {0}:{1}\nmonMongo will try to connect later. Data not be remove from the queue and will try send later.'.format(type(err), err))
            return
        except httpclient.HTTPError as err:
            if self.__log:
                self.__log.error('When sending a data error occurs. {0}:{1}\nmonMongo will try send data later. Data not be remove from the queue and will try send later.'.format(type(err), err))
            return 
            
    def __async_request(self, response):
        if response.error:
            if self.__log:                
                self.__log.error(response.error)                
        ioloop.IOLoop.instance().stop()        