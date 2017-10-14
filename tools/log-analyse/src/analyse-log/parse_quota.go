package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"math"
	"os"
	"regexp"
	"strconv"
	"strings"
	"time"
)

type MgrDetail struct {
}

type MgrRequestDetail struct {
	TotalReq    int64
	ReturnError int64 // 返回为 false
	BadResponse int64 // 错误格式返回数目
	TotalTime   int64 // 请求所有时间
	Min         int64 // 最小请求 ms
	Max         int64 // 最大请求 ms
	Errors      map[string]int
}

func ParseMgr(fileName string, quota, yidian *map[string]*MgrRequestDetail) {
	file, err := os.Open(fileName)
	if err != nil {
		panic(fmt.Errorf("Found no file", fileName, err))
	}

	var total int = 0
	startTime := time.Now()
	scanner := bufio.NewScanner(file)
	const BUFFER_SIZE = 32 * 1024 * 1024
	buf := make([]byte, 0, BUFFER_SIZE)
	scanner.Buffer(buf, BUFFER_SIZE)
	for scanner.Scan() {
		line := scanner.Text()
		total++
		if total%10000 == 0 {
			fmt.Printf("%s %d is done, takes %s\n", fileName, total, time.Since(startTime))
		}

		parseQuota(&line, quota)
		parseYidianQuota(&line, yidian)
	}
	if err := scanner.Err(); err != nil {
		fmt.Println("scanner err", err)
	}
}

func parseQuota(line *string, result *map[string]*MgrRequestDetail) {
	if !strings.Contains(*line, "QuotaService") {
		return
	}
	res := regexp.MustCompile(`\[INFO\] fhh-mgr - QuotaService (\d*?)ms (.*?) data: {.*?}. result: err:(.*?), body: (.*)`).FindAllStringSubmatch(*line, -1)
	if len(res) > 0 && len(res[0]) >= 5 {
		ms, err := strconv.ParseInt(res[0][1], 10, 64)
		if err != nil {
			fmt.Println("Failed to parse ms", *line)
			return
		}
		url := res[0][2]
		errstr := res[0][3]
		isBadResponse := false
		if errstr == "null" {
			errstr = ""
			body := res[0][4]
			isBadResponse = !isJSON(body)
		}

		addIntoResult(result, url, ms, errstr, isBadResponse)
	} else {
		fmt.Println("Failed to parse ???", *line)
	}
}

func parseYidianQuota(line *string, result *map[string]*MgrRequestDetail) {
	if !strings.Contains(*line, "ifeng_guard.go2yd.com") || !strings.Contains(*line, " result:") {
		return
	}

	// fmt.Println(*line)
	// 因为body可能带了回车，所以err可能打印到另外一行了
	res := regexp.MustCompile(` console - (\d*?)ms (.*?)\?.* result:`).FindAllStringSubmatch(*line, -1)
	if len(res) > 0 && len(res[0]) >= 2 {
		ms, err := strconv.ParseInt(res[0][1], 10, 64)
		if err != nil {
			fmt.Println("Failed to parse ms", *line)
			return
		}
		url := res[0][2]
		errstr := ""
		res = regexp.MustCompile(` console - (\d*?)ms (.*?)\?.* result:.* err:(.*)`).FindAllStringSubmatch(*line, -1)
		if len(res) > 0 && len(res[0]) >= 3 {
			errstr = res[0][3]
		}

		addIntoResult(result, url, ms, errstr, false)
		return
	}

	fmt.Println("Failed to parse ???", *line)
}

func addIntoResult(result *map[string]*MgrRequestDetail, url string, ms int64, errstr string, isBadResponse bool) {
	v, ok := (*result)[url]
	if !ok {
		detail := MgrRequestDetail{TotalReq: 1, TotalTime: ms, Min: ms, Max: ms}
		detail.Errors = make(map[string]int)
		(*result)[url] = &detail
		v = (*result)[url]
	} else {
		v.TotalReq++
		v.TotalTime += ms
		v.Max = int64(math.Max(float64(v.Max), float64(ms)))
		v.Min = int64(math.Min(float64(v.Min), float64(ms)))
	}

	if errstr != "" && errstr != "null" {
		errcount, ok := v.Errors[errstr]
		if !ok {
			v.Errors[errstr] = 1
		} else {
			v.Errors[errstr] = errcount + 1
		}
	}

	if isBadResponse {
		v.BadResponse++
	}
}

func isJSON(s string) bool {
	var js map[string]interface{}
	return json.Unmarshal([]byte(s), &js) == nil
}
