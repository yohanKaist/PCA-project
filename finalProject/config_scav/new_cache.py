from m5.objects import *

class L1DCache(BaseCache):
    size = '32kB'
    assoc = 8
    hit_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

class L1ICache(BaseCache):
    size = '32kB'
    assoc = 8
    hit_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

class L2Cache(BaseCache):
    size = '1MB'
    assoc = 8
    hit_latency = 50
    response_latency = 50
    mshrs = 20
    tgts_per_mshr = 12
