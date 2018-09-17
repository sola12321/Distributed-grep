package main

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"io"
	"io/ioutil"
	"net"
	"os"
	"os/exec"
	"strings"
)

func checkError(err error) {
	if err != nil {
		fmt.Printf("Fatal error: %s", err.Error())
		os.Exit(1)
	}
}

func main() {
	port := ":4020"
	tcpAddr, err := net.ResolveTCPAddr("tcp4", port)
	checkError(err)
	listener, err := net.ListenTCP("tcp", tcpAddr)
	checkError(err)
	for {
		fmt.Println("Waiting for connection")
		conn, err := listener.Accept()
		checkError(err)
		fmt.Println("Accepted connection")

		// read the length prefix
		prefix := make([]byte, 4)
		_, err = io.ReadFull(conn, prefix)
		length := binary.BigEndian.Uint32(prefix)
		//read arguments from client
		args := make([]byte, int(length))
		_, err = io.ReadFull(conn, args)
		checkError(err)

		//format grep command using arguments from querying node
		//individualArgs := strings.Split(string(args), " ")
		//fmt.Println(len(individualArgs))
		// for _, v := range individualArgs {
		// 	fmt.Println(v)
		// 	if v == "*.log" {
		// 		fmt.Println("match")
		// 	}
		// }
		temp := []string{"#!/bin/sh", string(args)}
		script := strings.Join(temp, "\n")
		err = ioutil.WriteFile("grep.sh", []byte(script), 0777)
		checkError(err)
		cmd := exec.Command("./grep.sh")
		//cmd.Args = individualArgs

		//get command output
		var out bytes.Buffer
		var stderr bytes.Buffer
		cmd.Stdout = &out
		cmd.Stderr = &stderr
		fmt.Println("Running command")
		err = cmd.Run()
		if err != nil {
			//if grep give error code, send 0 back
			fmt.Println("grep error send 0 back")
			errMsg := make([]byte, 4)
			binary.BigEndian.PutUint32(errMsg, uint32(0))
			_, err = conn.Write(errMsg)
			checkError(err)
			os.Exit(0)
		}
		fmt.Println("Command completed")
		prefixLineCnt := make([]byte, 4)
		// count the line number
		response := out.Bytes()
		arr := bytes.Split(response, []byte("\n"))
		lineCnt := len(arr) - 1
		response = bytes.Join(arr, []byte("\n"))
		binary.BigEndian.PutUint32(prefixLineCnt, uint32(lineCnt))

		// write the prefix and the response data to the stream (checking errors)
		_, err = conn.Write(prefixLineCnt)
		checkError(err)
		_, err = conn.Write(out.Bytes())
		checkError(err)
		break
	}
}
