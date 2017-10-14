package main

import (
	"testing"
)

func Test_sendMail(t *testing.T) {
	statistic := NewStreamStatistic()
	statistic.Add("http://local.innerapi.fhh.ifengidc.com/wapi/article/cmppinsert", "1")
	statistic.Add("http://local.innerapi.fhh.ifengidc.com/wapi/article/cmppinsert", "2")
	statistic.Add("http://local.innerapi.fhh.ifengidc.com/wapi/article/cmppinsert", "3")
	statistic.Add("http://local.innerapi.fhh.ifengidc.com/wapi/article/cmppinsert", "4")
	statistic.Add("http://local.innerapi.fhh.ifengidc.com/wapi/article/cmppinsert1", "1")
	statistic.Add("http://local.innerapi.fhh.ifengidc.com/wapi/article/cmppinsert2", "1")
	statistic.Add("http://local.innerapi.fhh.ifengidc.com/wapi/article/cmppinsert3", "1")
	statistic.Add("http://local.innerapi.fhh.ifengidc.com/wapi/article/cmppinsert4", "1")

	SendMail("renxf@ifeng.com", "send mail test", statistic.ToHtml())
}
