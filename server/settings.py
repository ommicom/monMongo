http_settings = {'server':'', 'port':5000}
mongo_settings = {'server':'127.0.0.1', 'port':27017, 'dbname':'statistics'}
log_settings = {'level':'info', 'outlet':'con'}
table_val = {}
#graf_val = {'mem':({'param':'virtual', 'format':'{0:.0f}'},{'param':'mapped', 'format':'{0:.0f}'}),
#            'backgroundFlushing':({'param':'flushes', 'format':'{0:.0f}'}),
#            'globalLock':({'param':{'currentQueue':({'param':'total','format':'{0:.0f}'})}})}

_graf_val = ({'param':'mem.virtual', 'format':'{0:.0f}', 'act':None},{'param':'mem.mapped', 'format':'{0:.0f}', 'act':None},
            {'param':'backgroundFlushing.flushes', 'format':'{0:.0f}', 'act':None},
            {'param':'globalLock.currentQueue.total', 'format':'{0:.0f}', 'act':None},
            {'param':'globalLock.currentQueue.writers', 'format':'{0:.0f}', 'act':None},
            {'param':'globalLock.currentQueue.readers', 'format':'{0:.0f}', 'act':None},
            {'param':'localTime', 'format':'{0:.0f}', 'act':None})

graf_val = (
             {"group":"backgroundFlushing", "yaxis":("backgroundFlushing.flushes",),"xaxis":"localTime", "xdt": True},
             {"group":"globalLock", "yaxis":("globalLock.currentQueue.total", "globalLock.currentQueue.readers","globalLock.currentQueue.total"),"xaxis":"localTime", "xdt":True},
             {"group":"memory", "yaxis":("mem.virtual", "mem.mapped"),"xaxis":"localTime", "xdt":True},
            )