package main

import (
	"bufio"
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
	"sync"
	"time"

	"github.com/gocolly/colly"
)

type Site struct {
	request_url string
	status_code string
	title       string
	h1          string
	h2          string
	h3          string
	h4          string
	h5          string
	strong      string
	p           string
	mark        string
	script      string
	link        string
	meta        string
	a           string
}

func scrape(url string, ch chan<- Site) {
	var site Site
	c := colly.NewCollector()
	var request_url, status_code, title, h1, h2, h3, h4, h5, strong, p, mark, script, link, meta, a string
	c.OnRequest(func(request *colly.Request) { request_url = request.URL.String() })
	c.OnResponse(func(r *colly.Response) { status_code = strconv.Itoa(r.StatusCode) })
	c.OnHTML("title", func(element *colly.HTMLElement) { title = element.Text })
	c.OnHTML("h1", func(element *colly.HTMLElement) { h1 = element.Text })
	c.OnHTML("h2", func(element *colly.HTMLElement) { h2 = element.Text })
	c.OnHTML("h3", func(element *colly.HTMLElement) { h3 = element.Text })
	c.OnHTML("h4", func(element *colly.HTMLElement) { h4 = element.Text })
	c.OnHTML("h5", func(element *colly.HTMLElement) { h5 = element.Text })
	c.OnHTML("strong", func(element *colly.HTMLElement) { strong = element.Text })
	c.OnHTML("p", func(element *colly.HTMLElement) { p = element.Text })
	c.OnHTML("mark", func(element *colly.HTMLElement) { mark = element.Text })
	c.OnHTML("script", func(element *colly.HTMLElement) { script = element.Text })
	c.OnHTML("link", func(element *colly.HTMLElement) { link = element.Text })
	c.OnHTML("meta", func(element *colly.HTMLElement) { meta = element.Text })
	c.OnHTML("a", func(element *colly.HTMLElement) { a = element.Text })
	c.OnError(func(_ *colly.Response, err error) { fmt.Println("Something went wrong:", err) })
	c.OnScraped(func(r *colly.Response) { fmt.Println("Finished", r.Request.URL) })
	c.Visit(url)
	site = Site{request_url, status_code, title, h1, h2, h3, h4, h5, strong, p, mark, script, link, meta, a}
	ch <- site
}

func main() {
	t := time.Now()
	file, ferr := os.Open("tranco.txt")
	if ferr != nil {
		panic(ferr)
	}
	scanner := bufio.NewScanner(file)
	var urls []string
	for scanner.Scan() {
		url := scanner.Text()
		urls = append(urls, "http://"+url)
	}
	var sites []Site
	var batch int = 100
	for i := 0; i < 10; i++ {
		var wg sync.WaitGroup
		ch := make(chan Site)
		for _, url := range urls[i*batch : i*batch+batch] {
			go scrape(url, ch)
		}
		wg.Add(batch)
		for range urls {
			go func() {
				defer wg.Done()
				site := <-ch
				sites = append(sites, site)
			}()
		}
		wg.Wait()
	}
	file, err := os.Create("tranco_links.csv")
	if err != nil {
		log.Fatalln(err)
	}
	defer file.Close()
	writer := csv.NewWriter(file)
	defer writer.Flush()
	writer.Write([]string{"request_url", "status_code", "title", "h1", "h2", "h3", "h4", "h5", "strong", "p", "mark", "script", "link", "meta", "a"})
	for _, site := range sites {
		writer.Write(([]string{site.request_url, site.status_code, site.title, site.h1, site.h2, site.h3, site.h4, site.h5, site.strong, site.p, site.mark, site.script, site.link, site.meta, site.a}))
	}
	elapsed := time.Since(t).Seconds()
	fmt.Println(elapsed)
}
