package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"github.com/tidwall/gjson"
	"github.com/tidwall/sjson"
	"image"
	_ "image/jpeg"
	_ "image/png"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

type Image struct {
	Src  string `json:"src"`
	Size [2]int `json:"size"`
	Alt  string `json:"alt"`
}

type AdvancedImage struct {
	Src  string `json:"src"`
	Size [2]int `json:"size"`
	Alt  string `json:"alt"`
	Byte int    `json:"byte"`
}

func main() {

	fileName := os.Args[1]

	//deleteFile(fileName)

	log.Fatal()



	jsonFile := openFile(fileName)

	if jsonFile == nil {
		log.Fatal("could not open json file")
		return
	}

	jsonContent := *getFileContent(jsonFile)

	err := jsonFile.Close()
	if checkError(err) {
		fmt.Println(err.Error())
	}

	imageLinks := gjson.Get(jsonContent, "body.img").Array()

	var completeImageList []AdvancedImage
	var biggestImage, smallestImage AdvancedImage

	for i := 0; i < len(imageLinks); i++ {

		var img Image
		err := json.Unmarshal([]byte(imageLinks[i].String()), &img)

		if checkError(err) {
			fmt.Println("6" + err.Error())
			continue
		}

		url := img.Src
		path := *getCurrentDirectory() + "\\Go\\Images\\" + *getImageName(url)
		imageLocation := path

		err, byte := downloadFile(url, imageLocation)

		if checkError(err) {
			fmt.Println("5" + err.Error())
			continue
		}

		err, width, height := getImageDimension(imageLocation)

		if checkError(err) {
			fmt.Println("4" + err.Error())
			continue
		}

		img.Size[0] = width
		img.Size[1] = height

		err = os.Remove(imageLocation)

		if checkError(err) {
			fmt.Println("3" + err.Error())
		}

		advancedImage := *createAdvancedImage(&img, byte)

		completeImageList = append(completeImageList, advancedImage)

		if i == 0 {
			fmt.Println("in if")
			biggestImage = advancedImage
			smallestImage = advancedImage
		} else {
			if advancedImage.Size[0]*advancedImage.Size[1] > biggestImage.Size[0]*biggestImage.Size[1] {
				biggestImage = advancedImage
			}
			if advancedImage.Size[0]*advancedImage.Size[1] < smallestImage.Size[0]*smallestImage.Size[1] {
				smallestImage = advancedImage
			}
		}
	}


	updatedJson, _ := sjson.Set(jsonContent, "body.img", completeImageList)
	updatedJson, _ = sjson.Set(updatedJson, "body.img_biggest", biggestImage)
	updatedJson, _ = sjson.Set(updatedJson, "body.img_smallest", smallestImage)

	path := filepath.Join(*getCurrentDirectory(), "Go", "ScrapedContent", fileName)
	file, err := os.Create(path)
	if checkError(err) {
		log.Fatal("could nor create file", err.Error())
	}

	defer file.Close()

	_, err = io.Copy(file, strings.NewReader(updatedJson))
	if checkError(err) {
		log.Fatal("could not write to file", err.Error())
	}

}

func createAdvancedImage(image *Image, byte int) *AdvancedImage {
	var advancedImage AdvancedImage
	advancedImage.Src = image.Src
	advancedImage.Size = image.Size
	advancedImage.Alt = image.Alt
	advancedImage.Byte = byte
	return &advancedImage
}

func getImageDimension(imagePath string) (error, int, int) {
	file, err := os.Open(imagePath)
	defer file.Close()
	if checkError(err) {
		return err, -1, -1
	}

	img, _, err := image.DecodeConfig(file)
	if checkError(err) {
		return err, -1, -1
	}
	return nil, img.Width, img.Height
}

func getImageName(url string) *string {
	temp := strings.Split(url, "/")
	imageName := temp[len(temp)-1]

	var idx int
	if strings.Index(imageName, "png") != -1 {
		idx = strings.Index(imageName, "png") + 3
	} else {
		idx = strings.Index(imageName, "jpeg") + 4
	}

	imageName = imageName[:idx]

	fmt.Println("img-->", imageName)
	return &imageName
}

func openFile(fileName string) *os.File {
	path := filepath.Join(*getCurrentDirectory(), "Go", "WebsiteContents", fileName)
	fmt.Println(path)
	jsonFile, err := os.Open(path)

	if checkError(err) {
		return nil
	}

	return jsonFile
}

func deleteFile(fileName string) {
	path := filepath.Join(*getCurrentDirectory(), "Go", "WebsiteContents", fileName)
	err := os.Remove(path)

	if checkError(err) {
		fmt.Println("2" + err.Error())
	}
}

func getFileContent(file *os.File) *string {
	fileContent, _ := ioutil.ReadAll(file)
	fileContentString := string(fileContent)
	return &fileContentString
}

func checkError(err error) bool {
	return !(err == nil)
}

func downloadFile(URL, fileName string) (error, int) {

	fmt.Println("path --> ", fileName)

	response, err := http.Get(URL)
	if checkError(err) {
		return err, -1
	}
	defer response.Body.Close()

	if response.StatusCode != 200 {
		return errors.New("received non 200 response code"), -1
	}

	file, err := os.Create(fileName)
	if checkError(err) {
		return err, -1
	}
	defer file.Close()

	//Write the bytes to the file
	size, err := io.Copy(file, response.Body)
	if err != nil {
		return err, -1
	}

	return nil, int(size)
}

func getCurrentDirectory() *string {
	path, err := os.Getwd()
	if err != nil {
		log.Println("1" + err.Error())
	}

	split := strings.Split(path, "\\")
	for split[len(split)-1] != "PhisingDetection" {
		split = split[:len(split)-1]
	}

	finalPath := ""
	for i := 0; i < len(split); i++ {
		finalPath = finalPath + split[i] + "\\"
	}
	finalPath = finalPath[:len(finalPath)-1]

	return &finalPath
}
