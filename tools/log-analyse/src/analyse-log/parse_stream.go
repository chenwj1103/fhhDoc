package main

import (
	"fmt"
	"net/url"
	"regexp"
)

func Parse(URL string, data string) (string, error) {
	switch URL {
	case "http://auto.cmpp.ifeng.com/Cmpp/runtime/interface_182.jhtml":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}
		res := regexp.MustCompile(`"articleId":(\d*?),`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.innerapi.fhh.ifengidc.com/support/spider/addArticle":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}
		// TODO upId ??? 是文章id ??
		res := regexp.MustCompile(`\\"upId\\":\\"(.*?)\\",`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.fhhapi.ifeng.com/account/cache/build":
		res := regexp.MustCompile(`id=(\d*)`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.innerapi.fhh.ifengidc.com/support/onePoint/status":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}
		// TODO aid 是啥？？
		res := regexp.MustCompile(`\\"aid\\":\\"(.*?)\\",`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://ifeng_guard.go2yd.com/ifeng/post/add":
		res := regexp.MustCompile(`"article_id":(\d*?),`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
		res = regexp.MustCompile(`"video_id":"(.*?)"`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://api.auto.ifeng.com/wemedia/api/user":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}
		// TODO fhhId ????
		res := regexp.MustCompile(`"fhhId":"(\d*)"`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.fhhapi.ifeng.com/localization/callback":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}
		res := regexp.MustCompile(`"articleId":"(.*?)"`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.innerapi.fhh.ifengidc.com/wapi/callback/yiDianArticle":
		res := regexp.MustCompile(`"articleId":"(.*?)"`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://ifeng_guard.go2yd.com/ifeng/media/change-status":
		res := regexp.MustCompile(`ifeng_id=(\d*)`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.fhhapi.ifeng.com/integral/grade":
		res := regexp.MustCompile(`id=(.*?)&`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://ent.cmpp.ifeng.com/Cmpp/runtime/interface_350.jhtml":
		fallthrough
	case "http://o.cmpp.ifeng.com/Cmpp/runtime/interface_396.jhtml":
		fallthrough
	case "http://fashion.cmpp.ifeng.com/Cmpp/runtime/interface_387.jhtml":
		fallthrough
	case "http://finance.cmpp.ifeng.com/Cmpp/runtime/interface_392.jhtml":
		fallthrough
	case "http://news.cmpp.ifeng.com/Cmpp/runtime/interface_415.jhtml":
		fallthrough
	case "http://book.cmpp.ifeng.com/Cmpp/runtime/interface_384.jhtml":
		// TODO articleId 数字？还有个id
		res := regexp.MustCompile(`articleId=(\d*)`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.fhhapi.ifeng.com/content/client":
		res := regexp.MustCompile(`articleId=(.*)`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.innerapi.fhh.ifengidc.com/wapi/clean/receive":
		fallthrough
	case "http://local.fhhapi.ifeng.com/clean/callback":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}

		res := regexp.MustCompile(`"eArticleId":"(\d*)"`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://house.ifeng.com/zmt/zmtapi/article":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}

		res := regexp.MustCompile(`"articleId":"(\d*)"`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.fhhapi.ifeng.com/article/transCode/callback":
		fallthrough
	case "http://local.fhhapi.ifeng.com/video/transCode/callback":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}

		res := regexp.MustCompile(`<id>(.*?)</id>`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.innerapi.fhh.ifengidc.com/support/cmpp/addVideo":
		fallthrough
	case "http://v.cmpp.ifeng.com/Cmpp/runtime/interface_515.jhtml":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}

		res := regexp.MustCompile(`"guid":"(.*?)"`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.innerapi.fhh.ifengidc.com/support/onePoint/add":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}
		res := regexp.MustCompile(`\\"article_id\\":\\"(.*?)\\"`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://10.90.11.47:9994/":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}
		// todo id ?? fhhId ??
		res := regexp.MustCompile(`id=(\d*)`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.innerapi.fhh.ifengidc.com/wapi/article/cmppinsert":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}
		res := regexp.MustCompile(`"id":(\d*)`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://house.ifeng.com/zmt/zmtapi/cate":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}
		res := regexp.MustCompile(`"fhhId":"(\d*?)"`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.innerapi.fhh.ifengidc.com/sApi/transCode/getInfo":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}
		res := regexp.MustCompile(`<id>(.*?)</id>`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://ifeng_guard.go2yd.com/ifeng/post/change-status":
		res := regexp.MustCompile(`ifeng_postid=(\d*)`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://api.auto.ifeng.com/wemedia/api/article":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}
		res := regexp.MustCompile(`"articleId":"(\d*?)"`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.fhhapi.ifeng.com/hawkeye/cache/publish":
		fallthrough
	case "http://local.fhhapi.ifeng.com/searchEngine/data/sync":
		res := regexp.MustCompile(`id=(.*?)&`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.fhhapi.ifeng.com/account/client/push":
		fallthrough
	case "http://local.fhhapi.ifeng.com/searchEngine/data/queue":
		res := regexp.MustCompile(`id=(.*)`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://nyx.staff.ifeng.com/project/api/recommendMgr/offlineFromFhh":
		res := regexp.MustCompile(`ids=(.*)`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.fhhapi.ifeng.com/onePoint/data":
		d, err := url.PathUnescape(data)
		if err != nil {
			return "", err
		}
		res := regexp.MustCompile(`"article_id":"(.*?)"`).FindAllStringSubmatch(d, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.fhhapi.ifeng.com/onePoint/data/status":
		res := regexp.MustCompile(`"aid":"(.*?)"`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://local.pgcstat.ifengidc.com/pgc/add.do":
		res := regexp.MustCompile(`mediaId=(\d*)`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://v.cmpp.ifeng.com/Cmpp/runtime/interface_20593.jhtml":
		res := regexp.MustCompile(`guid=(.*)`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	case "http://g.cmpp.ifeng.com/Cmpp/runtime/interface_484.jhtml":
		res := regexp.MustCompile(`aid=(\d*)`).FindAllStringSubmatch(data, -1)
		if len(res) > 0 && len(res[0]) >= 2 {
			return res[0][1], nil
		}
	default:
		return "", fmt.Errorf("Unkonw url: %s", URL)
	}
	return "", fmt.Errorf("Failed to parse")
}
