# CS425 mp1 Distributed grep
Group Member: Fangwei Gao, Xiaoli Ke
## instructions to run the distributed_grep program:
- Pull all the files to your local machine
- Inside the mp1 folder, compile the logServer.go and logClient.go:
```
go build logClient.go
go build logServer.go
```
- Run LogServer on all the 10 VMs, and pick one VM to run LogClient
- Input your grep options and patterns in the terminal according to the prompt. Our program should support all grep's optional arguments
- The terminal will show the results from all the VMs and the numbers of their matched lines. The results will be automatically stored in files named result with proper format. Next grep command will overwrite the previous results
- The client can identify fail-stop VMs, and their results will be empty

## Instructions to run the unit test:
- generate randome log files using logGen.py
```
python logGen.py
```
- run the test.py file to launch the unit test(need to change some of the address name and uncomment some part)
```
python test.py user, password, clientId
```
