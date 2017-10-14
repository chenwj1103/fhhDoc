package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

func AnalyseMrgLogs(logPath string) {
	files, err := getLogFiles(logPath, "-out-")
	if err != nil {
		panic(fmt.Errorf("Failed to get log files %s", err.Error()))
	}
	fmt.Println("Got files", len(files))

	quota := make(map[string]*MgrRequestDetail)
	yidian := make(map[string]*MgrRequestDetail)
	for _, file := range files {
		fmt.Println(file)
		ParseMgr(file, &quota, &yidian)
	}

	content := resutlToString("林瑞接口统计", &quota)
	content += "\n-------------------------------\n"
	content += resutlToString("一点接口统计", &yidian)
	fmt.Println(content)

	sendmail(content)
}

func resutlToString(title string, result *map[string]*MgrRequestDetail) string {
	content := "<p>" + title + "</p>"
	blank := "   "
	for url, v := range *result {
		totalerror := 0
		errcontent := fmt.Sprintf("<p>%s异常请求分布</p>\n", blank)
		for errstr, count := range v.Errors {
			totalerror += count
			errcontent += fmt.Sprintf("<p> %s-%s %d</p>\n", blank, errstr, count)
		}

		content += blank + url + "\n"
		content += fmt.Sprintf("<p>%s总请求数: %d,　异常请求数: %d. 错误返回格式数: %d, 平均耗时:%d ms, 最大耗时:%d ms, 最小耗时: %d ms</p>\n", blank, v.TotalReq, totalerror, v.BadResponse, v.TotalTime/v.TotalReq, v.Max, v.Min)
		content += errcontent
	}

	return content
}

func getLogFiles(logPath, label string) (files []string, err error) {
	fmt.Println("Search logs in", logPath)
	err = filepath.Walk(logPath, func(filename string, fi os.FileInfo, err error) error {
		if err != nil {
			return nil
		}
		if fi.IsDir() {
			return nil
		}

		if strings.Contains(filename, label) {
			files = append(files, filename)
		}
		return nil
	})
	return files, err
}

func sendmail(content string) {
	receivers := "qinfj@ifeng.com,chenwj3@ifeng.com,licheng1@ifeng.com,penghb@ifeng.com,renxf@ifeng.com,caizw@ifeng.com"
	title := fmt.Sprintf("林瑞和一点的指标接口统计(%s)", time.Now().AddDate(0, 0, -1).Format("2006-01-02"))
	SendMail(receivers, title, content)
}
