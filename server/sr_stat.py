import os
import json
import datetime
import asyncmongo
from tornado import web, gen

class Server(web.Application):
    def __init__(self, mongo_address, mongo_port, mongo_database, **val):
        handlers =[(r'/PUT_STAT', PutStatHanlder),
                   (r'/GET_STAT', GetStatHandler),
                   (r'/GET_GRAF', GetGrafHandler),
                   (r'/', CommonInfoHandler)
        ]
        settiings = dict(template_path=os.path.join(os.path.dirname(__file__), 'templates'),
                         static_path=os.path.join(os.path.dirname(__file__), 'static')
        )
        self.mongo_address = mongo_address
        self.mongo_port = mongo_port
        self.mongo_database = mongo_database
        self.val = val
        
        web.Application.__init__(self, handlers, **settiings)
        
class BaseHandler(web.RequestHandler):    
    @property
    def mongodb(self):
        if not hasattr(self, '_mongodb'):
            self._mongodb = asyncmongo.Client(pool_id='mongostat', host=self.application.mongo_address, port=self.application.mongo_port, dbname=self.application.mongo_database)
        return self._mongodb
    
    def get_fields_(self, dst, prefix=None):  
        pre_el = dict()
        for el in dst:
            pre_el.update(dict([prefix+'.'+param_nm, 1] for param, param_nm in el.iteritems() if param=='param'))        
        return pre_el
        
                            
class CommonInfoHandler(BaseHandler):
    @web.asynchronous
    def get(self):        
        self.render('info.html', title='monMongo', page_title='monMongo')

class PutStatHanlder(BaseHandler):
    @web.asynchronous
    @gen.engine
    def post(self):
        try:
            datas = json.loads(self.get_argument('stat'))
            for data in datas['mongodb_stat']:
                yield gen.Task(self.mongodb.statistics.insert,{'host':self.request.host, 'mongodb':data, 'statistic':datas['mongodb_stat'][data]})
        except Exception as err:
            print err
        self.finish()

class GetStatHandler(BaseHandler):
    pass

class GetGrafHandler(BaseHandler):
    @web.asynchronous
    @gen.engine
    def get(self):       
        cmd_host_list = {'distinct':'statistics','key':'host'}
        cmd_mongo_list = {'distinct':'statistics','key':'mongodb','query':{}}        
                 
        from_ = self.get_argument('from', datetime.datetime.now().strftime('%Y-%m-%d'))
        to_ = self.get_argument('to', (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'))        
        fields = self.get_fields_(self.application.val['graf'], 'statistic')
        
        hosts_ = yield gen.Task(self.mongodb.command, cmd_host_list)
        hosts = hosts_[0][0]['values']        
        for host in hosts:                        
            cmd_mongo_list['query'] = {'host':host}
            mongos_ = yield gen.Task(self.mongodb.command, cmd_mongo_list)
            mongos = mongos_[0][0]['values']
            for mongo in mongos:
                print host, mongo, from_, to_, fields
                #, 'statistic.localTime':{'$gte':from_, '$lt':to_}
                stats_ = yield gen.Task(self.mongodb.statistics.find,{'host':host, 'mongodb':mongo}, sort=[('statistic.localTime', 1)], fields=fields)
                print stats_
        
        
        self.render('graf.html')