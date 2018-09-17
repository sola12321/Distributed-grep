package main

import (
	"bufio"
	"encoding/binary"
	"fmt"
	"io"
	"io/ioutil"
	"net"
	"os"
	"strings"
	"time"
)

//error checker
func checkError(err error) {
	if err != nil {
		fmt.Printf("Fatal error: %s", err.Error())
		os.Exit(1)
	}
}

//parser the arguments
func get_args() string {
	fmt.Println("Enter command")
	input := ""
	//scan input arguments
	scanner := bufio.NewScanner(os.Stdin)
	if scanner.Scan() {

		input = scanner.Text()
		fmt.Printf("Input was: %q\n", input)
	}
	return input
}

func main() {
	//start measuring time
	start := time.Now()
	//read file to get vm server names
	nodeServerFile, err := ioutil.ReadFile("./vm_server_names")
	checkError(err)
	nodeServerNames := strings.Split(string(nodeServerFile), "\n")

	//make channel
	ch := make(chan string)
	cnts := make(chan int)
	//scan arguments
	inputArgs := get_args()
	activeMachineNum := 10
	totalCnt := 0
	for i, v := range nodeServerNames {
		go handler(ch, v, i+1, inputArgs, &activeMachineNum, cnts)
	}

	//accumulate result from different machines
	//print to the console and also dump to local file for test

	//create a file for logging result
	f, err := os.Create("result")
	checkError(err)
	defer f.Close()
	fmt.Printf("%d\n", activeMachineNum)
	if activeMachineNum == 0 {
		fmt.Println("Failed to set up any connection\ncheck the server side")
		return
	}
	for activeMachineNum > 0 {
		totalCnt += <-cnts
		_, err = f.Write([]byte(<-ch))
		checkError(err)
		activeMachineNum -= 1
	}
	elapsed := time.Since(start)
	//content, err := ioutil.ReadFile("result")
	checkError(err)
	//fmt.Printf(string(content))
	fmt.Printf("%d Lines matched in total\n", totalCnt)
	//record the latency
	f, err = os.Create("latency")
	checkError(err)
	f.WriteString(elapsed.String())
	fmt.Printf("Command took %s\n", elapsed)
	f.Close()
	os.Exit(0)
}

func handler(ch chan<- string, serverName string, id int, input string, activeMachineNum *int, cnts chan<- int) {
	//set up connection to the machine
	tcpAddr, err := net.ResolveTCPAddr("tcp4", serverName+":4020")
	if err != nil {
		*activeMachineNum -= 1
		fmt.Printf("Failed to find address for machine %d\n", id)
		fmt.Println(err.Error())
		return
	}
	conn, err := net.DialTCP("tcp", nil, tcpAddr)
	if err != nil {
		*activeMachineNum -= 1
		fmt.Printf("Failed to set up connection with machine %d\n", id)
		fmt.Println(err.Error())
		return
	}
	//scan terminal input to get grep arguments to send
	fmt.Printf("Trying to send request to machine %d \n", id)
	//send input arguments
	input_as_byte := []byte(input)
	// create the length prefix
	prefix := make([]byte, 4)
	binary.BigEndian.PutUint32(prefix, uint32(len(input_as_byte)))

	// write the prefix and the data to the stream (checking errors)
	_, err = conn.Write(prefix)
	if err != nil {
		*activeMachineNum -= 1
		fmt.Printf("Failed to write to machine %d\n", id)
		conn.Close()
		fmt.Println(err.Error())
		return
	}
	_, err = conn.Write(input_as_byte)
	if err != nil {
		*activeMachineNum -= 1
		fmt.Printf("Failed to write to machine %d\n", id)
		conn.Close()
		fmt.Println(err.Error())
		return
	}
	fmt.Printf("Done sending request to machine %d \n", id)

	// read the length prefix
	prefixLinecnt := make([]byte, 4)
	_, err = io.ReadFull(conn, prefixLinecnt)
	if err != nil {
		*activeMachineNum -= 1
		fmt.Printf("Failed to read response from machine %d\n", id)
		conn.Close()
		fmt.Println(err.Error())
		return
	}
	lineCnt := binary.BigEndian.Uint32(prefixLinecnt)
	//error response write empty string to channel
	if lineCnt == 0 {
		cnts <- 0
		ch <- fmt.Sprintf("Response from machine %d is:\n%s"+"This response contains %d lines\n##########\n", id, "", lineCnt)
		return
	}
	//read arguments from client
	response, err := ioutil.ReadAll(conn)
	if err != nil {
		*activeMachineNum -= 1
		fmt.Printf("Failed to read response from machine %d\n", id)
		conn.Close()
		fmt.Println(err.Error())
		return
	}
	cnts <- int(lineCnt)
	ch <- fmt.Sprintf("Response from machine %d is:\n%s"+"This response contains %d lines\n##########\n", id, string(response), lineCnt)

	conn.Close()
}
