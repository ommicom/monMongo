http_settings = {'server':'', 'port':5000}
mongo_settings = {'server':'127.0.0.1', 'port':27017, 'dbname':'statistics'}
log_settings = {'level':'info', 'outlet':'con'}
table_val = {}
#graf_val = {'mem':({'param':'virtual', 'format':'{0:.0f}'},{'param':'mapped', 'format':'{0:.0f}'}),
#            'backgroundFlushing':({'param':'flushes', 'format':'{0:.0f}'}),
#            'globalLock':({'param':{'currentQueue':({'param':'total','format':'{0:.0f}'})}})}

graf_val = (
             {"group":"backgroundFlushing", "yaxis":("backgroundFlushing.total_ms","backgroundFlushing.average_ms"),"xaxis":"localTime", "xdt": True},
             {"group":"globalLock", "yaxis":("globalLock.currentQueue.total", "globalLock.currentQueue.readers","globalLock.currentQueue.total"),"xaxis":"localTime", "xdt":True},
             {"group":"cursors", "yaxis":("cursors.timedOut",),"xaxis":"localTime", "xdt":True},
             {"group":"memory", "yaxis":("mem.virtual", "mem.mapped", "mem.resident"),"xaxis":"localTime", "xdt":True},
             {"group":"network", "yaxis":("network.bytesIn", "network.bytesOut", "network.numRequests"),"xaxis":"localTime", "xdt":True}
            )