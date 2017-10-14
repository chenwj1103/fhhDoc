package main

import (
	"fmt"
	"io"
	"net"
	"os"

	"path"
	"time"

	"flag"
	"strings"

	"github.com/robfig/cron"
)

const BUFFERSIZE = 1024

func main() {
	var second string
	var minite string
	var hour string
	var logPath string
	var host string
	var now bool
	flag.StringVar(&second, "second", "0", "crontab seconds")
	flag.StringVar(&minite, "minite", "0", "crontab minite")
	flag.StringVar(&hour, "hour", "1", "crontab hour")
	flag.StringVar(&logPath, "logPath", ".", "log file path")
	flag.StringVar(&host, "host", "127.0.0.1", "log file path")
	flag.BoolVar(&now, "now", false, "send it right now")
	flag.Parse()

	fmt.Println(second, minite, hour)
	fmt.Println("host", host)
	fmt.Println("logPath", logPath)

	if now == true {
		fmt.Println("send it now")
		sendFile(logPath, host)
		return
	}

	c := cron.New()
	crontabS := strings.Join([]string{second, minite, hour, "*", "*", "*"}, " ")
	fmt.Println("crontab is", crontabS)
	c.AddFunc(crontabS, func() {
		sendFile(logPath, host)
	})
	c.Start()

	select {}
}

func fillString(s string) string {
	for {
		length := len(s)
		if length < BUFFERSIZE {
			s = s + ":"
			continue
		}
		break
	}
	return s
}

func sendFile(logPath string, host string) {
	// 找到日志文件
	fileName := "kafkaConnect." + time.Now().AddDate(0, 0, -1).Format("2006-01-02") + ".log"
	file, err := os.Open(path.Join(logPath, fileName))
	if err != nil {
		fmt.Println("Failed to open log file", err)
		return
	}
	defer file.Close()

	connection, err := net.Dial("tcp", host+":25001")
	if err != nil {
		fmt.Println("connect error:", err)
		return
	}
	defer connection.Close()

	fmt.Println("Connected to server, start sending file", fileName)

	fmt.Println("send target type")
	targetBuffer := make([]byte, 1)
	targetBuffer[0] = 1 // target type 1
	connection.Write(targetBuffer)

	sendBuffer := make([]byte, BUFFERSIZE)
	fmt.Println("Start to sending file")
	for {
		n, err := file.Read(sendBuffer)
		if err != nil {
			if err == io.EOF {
				break
			}
			fmt.Println("read error:", err)
			return
		}

		n, err = connection.Write(sendBuffer[:n])
		if err != nil {
			fmt.Println("Write error:", err)
			return
		}
	}
	fmt.Println("File has been sent. closing connection")

	fmt.Println("Send file ok!!!!!")
}
