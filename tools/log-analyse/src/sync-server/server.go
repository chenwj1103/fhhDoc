package main

import (
	"flag"
	"fmt"
	"net"
	"os"
	"path"
	"strings"
	"time"
)

const BUFFERSIZE = 1024

func main() {
	var dataPath string
	flag.StringVar(&dataPath, "dataPath", ".", "data path that we save logs")
	flag.Parse()

	fmt.Println("data path", dataPath)

	server, err := net.Listen("tcp", "0.0.0.0:25001")
	if err != nil {
		fmt.Println("Error listening:", err)
		os.Exit(1)
	}

	defer server.Close()
	fmt.Println("Server started! Waiting for connections...")

	for {
		conn, err := server.Accept()
		if err != nil {
			fmt.Println("Error accept:", err)
			continue
		}

		go receiveFile(conn, dataPath)
	}
}

func receiveFile(conn net.Conn, dataPath string) {
	defer conn.Close()
	fmt.Println("A client has connected:", conn.RemoteAddr().String())

	// receive file name and size
	targetBuffer := make([]byte, 1)
	n, _ := conn.Read(targetBuffer)
	if n == 0 {
		fmt.Println("Got no type, exit")
		return
	}
	target := targetBuffer[0]
	fmt.Println("Target is", target, target == 1)
	if target != 1 {
		fmt.Println("Unknown host, disconnect")
		return
	}

	fileName := "fhh-stream-" + strings.Split(conn.RemoteAddr().String(), ":")[0] + "-" + time.Now().AddDate(0, 0, -1).Format("2006-01-02") + ".log"
	file, err := os.Create(path.Join(dataPath, fileName))
	if err != nil {
		fmt.Println("Failed to create file", err)
		return
	}
	defer file.Close()

	readBuffer := make([]byte, BUFFERSIZE)
	for {
		n, err := conn.Read(readBuffer)
		if err != nil {
			if err.Error() == "EOF" {
				fmt.Println("Read EOF")
				break
			}
			fmt.Println("Read error:", err)
			return
		}
		file.Write(readBuffer[:n])
	}
	fmt.Println("Receive file ok")
}
