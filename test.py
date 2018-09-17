from deploy import *
from paramiko import *
import matplotlib.pyplot as plt
import sys
import time
import os
from threading import Thread
import subprocess
from latency import *
#run the test
def serverUp(id):
    server = "fangwei2@fa18-cs425-g17-%02d.cs.illinois.edu" % (id)
    args = ['ssh','-i','~/.ssh/mykey',server,'./server.sh']
    subprocess.call(args)
    #os.system("ssh -i ~/.ssh/mykey %s ./server.sh" % (server))
# run client
def clientUp(id,cmd):
    client = "fangwei2@fa18-cs425-g17-%02d.cs.illinois.edu" % (id)
    args = ['ssh','-i','~/.ssh/mykey',client,'./client.sh']
    process = subprocess.Popen(args, stdin=subprocess.PIPE)
    process.communicate(cmd)
    #os.system("ssh -i ~/.ssh/mykey %s ./client.sh"  % (client))

#start servers and client with multithreading
def run(clientId,cmd,num):
    ts = []
    for id in range(1,num+1):
        t = Thread(target=serverUp, args=(id,))
        ts.append(t)
        t.start()
    tc  = Thread(target=clientUp, args=(int(clientId),cmd))
    time.sleep(3)
    tc.start()
    for t in ts:
        t.join()
    tc.join()

#run cmd remotely on each individual vms and get the result back
#./remoteGrepResults/
def remoteGrep(cmd):
    os.system("rm ./remoteGrepResults/vm*")
    for id in range(1,11):
        server = "fangwei2@fa18-cs425-g17-%02d.cs.illinois.edu" % (id)
        logName = "vm%02d" % (id)
        os.system("ssh -i ~/.ssh/mykey " + server + " " + cmd + " >> ./remoteGrepResults/" + logName)
        #args = ['ssh','-i','~/.ssh/mykey',server] + cmd + ['>>', './remoteGrepResults/%s' % (logName)]
        #subprocess.call(args)

def compare():
    #parse result
    f = open("result")
    res = f.read()
    res = res.split("##########")
    map = {}
    for str in res:
        tmp = str.rstrip("\n").split("\n")
        if not tmp[0]:
            del tmp[0]
        if tmp:
            id = [int(s) for s in tmp[0].split() if s.isdigit()][0]
            map[id] = tmp[1:-1]
    f.close()

    #compare line by line
    for id in map:
        file = "./remoteGrepResults/vm%02d" % (id)
        remoteResult = open(file)
        i = 0
        for line in remoteResult:
            if line.rstrip("\n") != map[id][i]:
                return False
            i += 1
    return True

def test():
    #cmds = ["grep GET *.log", "grep abcd *.log", "grep html *.log" ]
    cmds = ["grep ^[0-9]*\,[\/] *.log"]
    user, password, clientId = sys.argv[1:]
    print(user, password, clientId)
    conns = setSSH(user, password, clientId)
    deploy(conns, clientId)
    closeSSH(conns)
    res = []
    latencyDict = {}
    for cmd in cmds:
        ls = []
        #for i in range(5):
        run(clientId,cmd,10)
        ls.append(getLatency(clientId))
        latencyDict[cmd] = ls
        #get client result back
        #client = "fangwei2@fa18-cs425-g17-%02d.cs.illinois.edu" % (int(clientId))
        #os.system("scp -i ~/.ssh/mykey %s:./result ./result" % (client))
        #remoteGrep(cmd)
        #res.append(compare())
    for cmd in latencyDict:
        print (latencyDict[cmd])
    return res
print(test())
