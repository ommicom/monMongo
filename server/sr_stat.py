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
    
    def _get_fields_(self, dst, prefix=None):  
        pre_el = dict()
        for el in dst:
            pre_el.update(dict([('{0}.{1}').format(prefix, param_nm), 1] for param, param_nm in el.iteritems() if param=='param'))            
        pre_el.update({'_id':0})        
        return pre_el
    
    def get_fields_(self, dst, prefix=None):
        pre_el = dict()                    
        for el in dst:
            lst = [lst for lst_nm, lst in el.items() if lst_nm == 'yaxis']            
            yaxis = el['xaxis']
            pre_el.update(dict([[("{0}.{1}").format(prefix, yaxis),1]]))
            for l in lst:
                pre_el.update(dict([[("{0}.{1}").format(prefix, el),1] for el in l]))
        pre_el.update({'_id':0}) 
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
        
        def get_rec_val(v, p):            
            v_ = v            
            for point in p.split("."):
                v_ = v_[point]                                                   
            return v_
        
             
        cmd_host_list = {'distinct':'statistics','key':'host'}
        cmd_mongo_list = {'distinct':'statistics','key':'mongodb','query':{}}        
                 
        from_ = self.get_argument('from', datetime.datetime.now().strftime('%Y-%m-%d'))
        to_ = self.get_argument('to', (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'))        
        fields = self.get_fields_(self.application.val['graf'], 'statistic')               
        
        hosts_ = yield gen.Task(self.mongodb.command, cmd_host_list)        
        hosts = hosts_[0][0]['values'] 
        res = dict()       
        for host in hosts:      
            res[host] = dict()                  
            cmd_mongo_list['query'] = {'host':host}
            mongos_ = yield gen.Task(self.mongodb.command, cmd_mongo_list)
            mongos = mongos_[0][0]['values']
            
            for mongo in mongos:                
                res[host][mongo] = dict()                
                stats_ = yield gen.Task(self.mongodb.statistics.find,{'host':host, 'mongodb':mongo, 'statistic.localTime':{'$gte':'{0}T00:00:00.000000'.format(from_), '$lt':'{0}T00:00:00.000000'.format(to_)}}, sort=[('statistic.localTime', 1)],  fields=fields)
                
                for grafs in self.application.val['graf']:
                    res[host][mongo][grafs['group']] = dict()
                    
                    for graf_val_nm in grafs['yaxis']:
                        res[host][mongo][grafs['group']][graf_val_nm]=dict()
                        
                        for stats in stats_[0][0]:
                            xaxis = stats['statistic'][grafs['xaxis']]
                            if grafs['xdt']:
                                xaxis_parts = xaxis.split('T')                                                                                            
                                dt = datetime.datetime.strptime(' '.join(xaxis_parts), '%Y-%m-%d %H:%M:%S.%f') if len(xaxis_parts[1].split('.'))>1 else datetime.datetime.strptime(' '.join(xaxis_parts), '%Y-%m-%d %H:%M:%S')
                                xaxis = dt.strftime('%Y/%m/%d %H:%M:%S')
                                
                            print xaxis
                            val = get_rec_val(stats['statistic'], graf_val_nm)
                            res[host][mongo][grafs['group']][graf_val_nm].update({xaxis:val})
                                                                      
        self.render('graf.html', statistics = res)