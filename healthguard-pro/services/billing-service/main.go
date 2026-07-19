package main

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
)

// TODO Sprint 2: implement this service
func main() {
	r := gin.New()
	r.Use(gin.Logger(), gin.Recovery())
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})
	log.Fatal(r.Run(":8080"))
}
