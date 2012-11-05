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
    data_ = None        
    
    @property
    def mongodb(self):
        if not hasattr(self, '_mongodb'):
            self._mongodb = asyncmongo.Client(pool_id='mongostat', host=self.application.mongo_address, port=self.application.mongo_port, dbname=self.application.mongo_database)
        return self._mongodb        
    
        
    def get_fields_(self, dst, prefix=None):
        pre_el = dict()                    
        for el in dst:
            lst = [lst for lst_nm, lst in el.items() if lst_nm == 'yaxis']            
            xaxis = el['xaxis']            
            pre_el.update(dict([[("{0}.{1}").format(prefix, xaxis),1]]))
            for l in lst:
                pre_el.update(dict([[("{0}.{1}").format(prefix, el.split(':')[0]),1] for el in l]))                
        pre_el.update({'_id':0}) 
        return pre_el
    
    def dt_convert(self, dt):
        dt_part = dt.split('T')
        return datetime.datetime.strptime(' '.join(dt_part), '%Y-%m-%d %H:%M:%S.%f') if len(dt_part[1].split('.'))>1 else datetime.datetime.strptime(' '.join(dt_part), '%Y-%m-%d %H:%M:%S')
                                            
    def get_hosts_list(self, dt_gte=None, dt_lte=None):                
        cmd_host_list = {'distinct':'statistics','key':'host'}        
        if dt_gte and dt_lte:            
            cmd_host_list['query'] = {'statistic.localTime':{'$gte':'{0}T00:00:00.000000'.format(dt_gte), '$lt':'{0}T00:00:00.000000'.format(dt_lte)}}                
        return gen.Task(self.mongodb.command, cmd_host_list)
    
    def get_mongodb_list(self, host, dt_gte=None, dt_lte=None):
        cmd_mongodb_list = {'distinct':'statistics', 'key':'mongodb', 'query':{}}
        cmd_mongodb_list['query']['host'] = host
        if dt_gte and dt_lte:            
            cmd_mongodb_list['query']['statistic.localTime']={'$gte':'{0}T00:00:00.000000'.format(dt_gte), '$lt':'{0}T00:00:00.000000'.format(dt_lte)}        
        #print 'cmd_mongodb_list=', cmd_mongodb_list
        return gen.Task(self.mongodb.command, cmd_mongodb_list)          
    
    def get_rec_val(self, v, p):            
            v_ = v            
            for point in p.split("."):
                v_ = v_[point]                                                   
            return v_    
    
    def get_stats(self, host, mongo, dt_gte=None, dt_lte=None, fields_=None, sort_=None, limit_=0):
        cmd_stats_list = {'host':host, 'mongodb':mongo}
        if dt_gte and dt_lte:
            cmd_stats_list.update({'statistic.localTime':{'$gte':'{0}T00:00:00.000000'.format(dt_gte), '$lt':'{0}T00:00:00.000000'.format(dt_lte)}})
        return gen.Task(self.mongodb.statistics.find, cmd_stats_list, fields=fields_, sort=sort_, limit=limit_)                    
            
            
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
    @web.asynchronous
    @gen.engine
    def get(self):
        def get_rate_val(vals, param):
            xy = list()
            ddt = list()                        
            
            ddt.append(self.dt_convert(vals[0]['statistic']['localTime']))
            ddt.append(self.dt_convert(vals[1]['statistic']['localTime']))
            xy.append(self.get_rec_val(vals[0]['statistic'],param))
            xy.append(self.get_rec_val(vals[1]['statistic'],param))            
                        
            return int(reduce(lambda res, x: res-x, xy)/reduce(lambda res, x: res-x, ddt).total_seconds())

        def get_direct_val(vals, param):
            ret = self.get_rec_val(vals[0]['statistic'],param)             
            return ret if isinstance(ret, basestring) else int(ret)                     
              
        calc_selector = {'RATE':get_rate_val}
        
        from_ = self.get_argument('from', datetime.datetime.now().strftime('%Y-%m-%d'))
        #from_ = self.get_argument('from', (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime('%Y-%m-%d'))
        to_ = self.get_argument('to', (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
        fields_ = self.get_fields_(self.application.val['table'], 'statistic')        
        groups_list_ = self.application.val['table']        
        
        res = dict()
        
        hosts = yield self.get_hosts_list(from_, to_)
        for host in hosts[0][0]['values']:            
            res[host] = dict()
            mongos = yield self.get_mongodb_list(host, from_, to_)
            for mongo in mongos[0][0]['values']:
                res[host][mongo] = dict()       
                stats_ = yield self.get_stats(host, mongo, from_, to_, fields_, sort_=[('statistic.localTime', -1)])
                if len(stats_[0][0]) == 0:
                    continue
                
                groups = (groups['group'] for groups in groups_list_ )
                
                for group in groups:
                    res[host][mongo][group] = dict()
                    yaxis_params = (yaxis['yaxis'] for yaxis in groups_list_ if yaxis['group'] == group)
                    
                    for yaxis_vals in yaxis_params:
                        for yaxis in yaxis_vals:
                            yaxis_nm, yaxis_act = yaxis.split(':')
                            calc_act = calc_selector.get(yaxis_act.upper(),get_direct_val)
                            res[host][mongo][group][yaxis_nm] = calc_act(stats_[0][0], yaxis_nm)
  
        
        print res
        self.render('stat.html', statistics=res, ver='{0} build {1}'.format(self.application.val['version'], self.application.val['build']))

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
                                xaxis = self.dt_convert(xaxis).strftime('%Y/%m/%d %H:%M:%S')                                
                                                            
                            val = get_rec_val(stats['statistic'], graf_val_nm)
                            res[host][mongo][grafs['group']][graf_val_nm].update({xaxis:val})
                                                                      
        self.render('graf.html', statistics = res)