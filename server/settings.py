http_settings = {'server':'', 'port':5000}
mongo_settings = {'server':'127.0.0.1', 'port':27017, 'dbname':'statistics'}
log_settings = {'level':'info', 'outlet':'con'}
table_val = ({"group":"opcounters", "yaxis":("opcounters.insert:rate", "opcounters.query:rate", "opcounters.command:rate", "backgroundFlushing.flushes:rate", "backgroundFlushing.average_ms:", "version:"),"xaxis":"localTime", "xdt":True},
             {"group":"cursors", "yaxis":("cursors.timedOut:",),"xaxis":"localTime", "xdt":True},
             {"group":"memory", "yaxis":("mem.virtual:", "mem.mapped:", "mem.resident:"),"xaxis":"localTime", "xdt":True},
             {"group":"network", "yaxis":("network.bytesIn:rate", "network.bytesOut:rate", "network.numRequests:"),"xaxis":"localTime", "xdt":True}
            )

graf_val = (
             {"group":"backgroundFlushing", "yaxis":("backgroundFlushing.total_ms","backgroundFlushing.average_ms"),"xaxis":"localTime", "xdt": True},
             {"group":"globalLock", "yaxis":("globalLock.currentQueue.total", "globalLock.currentQueue.readers","globalLock.currentQueue.total"),"xaxis":"localTime", "xdt":True},
             {"group":"cursors", "yaxis":("cursors.timedOut",),"xaxis":"localTime", "xdt":True},
             {"group":"memory", "yaxis":("mem.virtual", "mem.mapped", "mem.resident"),"xaxis":"localTime", "xdt":True},
             {"group":"opcounters", "yaxis":("opcounters.insert", "opcounters.query","opcounters.command"),"xaxis":"localTime", "xdt":True},
             {"group":"network", "yaxis":("network.bytesIn", "network.bytesOut", "network.numRequests"),"xaxis":"localTime", "xdt":True}
            )