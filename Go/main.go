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

func printAdvancedImage(image AdvancedImage) {
	fmt.Println(image.Src)
	fmt.Println(image.Size)
	fmt.Println(image.Alt)
	fmt.Println(image.Byte)
}

func main() {
	fileName := os.Args[1]
	jsonFile := openFile(fileName)

	if jsonFile == nil {
		return
	}

	jsonContent := *getFileContent(jsonFile)

	jsonFile.Close()

	imageLinks := gjson.Get(jsonContent, "body.img").Array()

	var completeImageList []AdvancedImage
	for i := 0; i < len(imageLinks); i++ {

		var image Image
		err := json.Unmarshal([]byte(imageLinks[i].String()), &image)

		if checkError(err) {
			fmt.Println(err.Error())
			continue
		}

		url := image.Src
		imageLocation := "Images/" + *getImageName(url)

		err, size := downloadFile(url, imageLocation)

		if checkError(err) {
			fmt.Println(err.Error())
			continue
		}

		err, width, height := getImageDimension(imageLocation)

		if checkError(err) {
			fmt.Println(err.Error())
			continue
		}

		image.Size[0] = width
		image.Size[1] = height

		err = os.Remove(imageLocation)

		if checkError(err) {
			fmt.Println(err.Error())
		}

		advancedImage := *createAdvancedImage(&image, size)

		completeImageList = append(completeImageList, advancedImage)
	}

	deleteFile(fileName)
	updatedJson, _ := sjson.Set(jsonContent, "body.img", completeImageList)

	file, err := os.Create("ScrapedContent/" + fileName)
	if checkError(err) {
		log.Fatal("could nor create file", err.Error())
	}

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

	image, _, err := image.DecodeConfig(file)
	if checkError(err) {
		return err, -1, -1
	}
	return nil, image.Width, image.Height
}

func getImageName(url string) *string {
	temp := strings.Split(url, "/")
	imageName := temp[len(temp)-1]
	return &imageName
}

func openFile(fileName string) *os.File {
	jsonFile, err := os.Open("WebsiteContents/" + fileName)

	if checkError(err) {
		return nil
	}

	return jsonFile
}

func deleteFile(fileName string) {
	err := os.Remove("WebsiteContents/" + fileName)

	if checkError(err) {
		fmt.Println(err.Error())
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
	//Get the response bytes from the url
	response, err := http.Get(URL)
	if checkError(err) {
		return err, -1
	}
	defer response.Body.Close()

	if response.StatusCode != 200 {
		return errors.New("received non 200 response code"), -1
	}
	//Create a empty file
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
