package main

import (
	"flag"
	"fmt"
	"os"
	"runtime/debug"
)

func main() {
	// TODO 处理异常,发送邮件
	defer func() {
		if err := recover(); err != nil {
			debug.PrintStack()
			fmt.Println("Got err:", err)
		}
	}()

	var logPath string
	var logType string
	flag.StringVar(&logPath, "logpath", "", "abs path where logs is stored")
	flag.StringVar(&logType, "logtype", "", "log type (stream, mgr)")
	flag.Parse()

	if logPath == "" || logType == "" {
		flag.Usage()
		os.Exit(1)
	}

	switch logType {
	case "stream":
		AnalyseStreamLogs(logPath)
	case "mgr":
		AnalyseMrgLogs(logPath)
	default:
		flag.Usage()
	}
}
