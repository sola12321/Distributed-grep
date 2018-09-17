from paramiko import *
def setSSH(user, password, clientId):
    conns = []
    with open("./vm_server_names") as hosts:
        for line in hosts:
            #establish ssh client
            line=line.rstrip()
            ssh_client = SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            ssh_client.connect(hostname=line,username=user,port=22,password=password)
            conns.append(ssh_client)
    hosts.close()
    return conns

def closeSSH(conns):
    for conn in conns:
        conn.close()


def deploy(conns, clientId):
    for i in range(1, len(conns) + 1):
        ssh_client = conns[i-1]
        #clear the directive
        ssh_client = conns[i-1]
        ssh_client.invoke_shell()
        #transfer files to vms and build
        ftp_client=ssh_client.open_sftp()
        remoteAddr = "./vm"+ str(i) + ".log"
        localAddr = "./logs/vm" + str(i) + ".log"
        #remoteAddr = "./vm"+ str(i) + ".log"
        #localAddr = "./randomLogs/randomLogVM" + str(i) + ".log"
        #print(localAddr)
        #ftp_client.put(localAddr,remoteAddr)
        remoteAddr = "./logServer.go"
        localAddr = "./logServer.go"
        ftp_client.put(localAddr,remoteAddr)
        remoteAddr = "./server.sh"
        localAddr = "./server.sh"
        ftp_client.put(localAddr,remoteAddr)
        stdin, stdout, stderr = ssh_client.exec_command("chmod +x ./server.sh")
        #transfer client code to the selected vm and build
        if i == int(clientId):
            remoteAddr = "./logClient.go"
            localAddr = "./logClient.go"
            ftp_client.put(localAddr,remoteAddr)
            remoteAddr = "./client.sh"
            localAddr = "./client.sh"
            ftp_client.put(localAddr,remoteAddr)
            stdin, stdout, stderr = ssh_client.exec_command("chmod +x ./client.sh")
            remoteAddr = "./vm_server_names"
            localAddr = "./vm_server_names"
            ftp_client.put(localAddr,remoteAddr)
        ftp_client.close()
        print("vm" + str(i) + " deployed")
