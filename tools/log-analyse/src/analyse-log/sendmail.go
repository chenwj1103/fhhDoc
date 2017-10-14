package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

type MailParams struct {
	To          string `json:"to"`
	Title       string `json:"title"`
	Content     string `json:"content"`
	ContentType string `json:"contentType"`
}

type MailResponse struct {
	Ok  bool   `json:"ok"`
	Err string `json:"err"`
}

func SendMail(to string, title string, content string) error {
	params := &MailParams{To: to, Title: title, Content: content, ContentType: "html"}

	url := `http://10.90.13.148/api/send_mail`
	bodyStr, err := json.Marshal(params)
	if err != nil {
		return nil
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(bodyStr))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	res, err := client.Do(req)
	if err != nil {
		return err
	}
	defer res.Body.Close()

	body, _ := ioutil.ReadAll(res.Body)
	fmt.Println(string(body))

	result := &MailResponse{}
	err = json.Unmarshal(body, result)
	if err != nil {
		return err
	}
	if result.Ok != true {
		return fmt.Errorf("response err:%s", result.Err)
	}

	return nil
}
