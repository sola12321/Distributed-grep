import matplotlib.pyplot as plt
import os
import time
#read latency from remote client
def getLatency(clientId):
    client = "fangwei2@fa18-cs425-g17-%02d.cs.illinois.edu" % (int(clientId))
    os.system("scp -i ~/.ssh/mykey %s:./latency ./latency" % (client))
    f = open('./latency')
    l = f.readlines()
    f.close()
    return l

#getLatency("1")


#out_GET = [2.110459876, 1.311093373], 1.586511107, 1.299006959, 1.391859514]
#out_abcd = [0.265037008, 0.218349527, 0.24143865, 0.239553938, 0.239477517]
#out_html = [4.728062747, 4.002370197, 2.707832128, 4.483503797s, 3.525314285]
