package main

import (
	"bufio"
	"fmt"
	"hash/fnv"
	"os"
	"regexp"
	"strings"
	"time"
)

type Detail struct {
	Num         int
	IdsHashList []uint64
}

type StreamStatistic struct {
	details map[string]*Detail
}

func NewStreamStatistic() *StreamStatistic {
	return &StreamStatistic{make(map[string]*Detail)}
}

func (s *StreamStatistic) Add(url, id string) {
	v, ok := s.details[url]
	if !ok {
		s.details[url] = &Detail{}
		v = s.details[url]
	}

	v.Num++
	if id == "" {
		return
	}

	hashv := fnvhash(id)
	for _, hash := range v.IdsHashList {
		if hash == hashv {
			return
		}
	}
	v.IdsHashList = append(v.IdsHashList, hashv)
}

func (s *StreamStatistic) ToHtml() string {
	html := ""
	for url, detail := range s.details {
		html += fmt.Sprintf("<p>%s 总数%d　去重:%d</p>\n", url, detail.Num, len(detail.IdsHashList))
	}
	return html
}

func fnvhash(id string) uint64 {
	h := fnv.New64()
	h.Write([]byte(id))
	return h.Sum64()
}

func AnalyseStreamLogs(logPath string) {
	files, err := getLogFiles(logPath, "fhh-stream")
	if err != nil {
		panic(fmt.Errorf("get stream logs err:%s", err.Error()))
	}

	fmt.Println("Get stream logs", files)
	if len(files) != 3 {
		panic(fmt.Errorf("Only got %d stream logs", len(files)))
	}

	statistic := NewStreamStatistic()
	for _, file := range files {
		var ip string
		res := regexp.MustCompile(`-(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})-`).FindAllStringSubmatch(file, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			ip = res[0][1]
			fmt.Println("ip is", ip)
		} else {
			panic(fmt.Errorf("Failed to parse ip from file"))
		}

		analyseLog(file, statistic)
	}

	mailContent := statistic.ToHtml()
	fmt.Println(mailContent)
	receivers := "qinfj@ifeng.com,chenwj3@ifeng.com,licheng1@ifeng.com,penghb@ifeng.com,renxf@ifeng.com"
	title := fmt.Sprintf("自媒体接口每日统计(%s)", time.Now().AddDate(0, 0, -1).Format("2006-01-02"))
	if err := SendMail(receivers, title, mailContent); err != nil {
		fmt.Println("Send mail failed", err.Error())
	}
}

func analyseLog(fileName string, statistic *StreamStatistic) {
	file, err := os.Open(fileName)
	if err != nil {
		panic(fmt.Errorf("Found no file", err))
	}

	total, found := 0, 0
	startTime := time.Now()
	scanner := bufio.NewScanner(file)
	buf := make([]byte, 0, 64*1024*1024)
	scanner.Buffer(buf, 1024*1024*64)
	for scanner.Scan() {
		line := scanner.Text()
		total++
		if total%50000 == 0 {
			fmt.Printf("%s %d is done, found %d, takes %s\n", fileName, total, found, time.Since(startTime))
		}
		if !strings.Contains(line, "sink task request url : ") {
			continue
		}

		res := regexp.MustCompile(`sink task request url : (.*?), params : (.*)`).FindAllStringSubmatch(line, -1)
		if len(res) > 0 && len(res[0]) >= 3 {
			found++
			url := res[0][1]
			if n := strings.Index(url, "?"); n != -1 {
				url = url[0:n]
			}
			params := res[0][2]

			// parse
			id, err := Parse(url, params)
			if err != nil {
				fmt.Printf("Failed to parse url:%s, params: %s\n", url, params)
			}

			statistic.Add(url, id)
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Println("scanner err", err)
	}
	fmt.Printf("%s all is done, total %d, found %d, takes %s\n", fileName, total, found, time.Since(startTime))
	fmt.Println("--------------------")
}
