import os
import json
import asyncmongo
from tornado import web, gen

class Server(web.Application):
    def __init__(self, mongo_address, mongo_port, mongo_database):
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
        web.Application.__init__(self, handlers, **settiings)
        
class BaseHandler(web.RequestHandler):    
    @property
    def mongodb(self):
        if not hasattr(self, '_mongodb'):
            self._mongodb = asyncmongo.Client(pool_id='mongostat', host=self.application.mongo_address, port=self.application.mongo_port, dbname=self.application.mongo_database)
        return self._mongodb

class CommonInfoHandler(BaseHandler):
    @web.asynchronous
    def get(self):        
        self.render('info.html', title='monMongo')

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
    pass