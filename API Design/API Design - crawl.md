## Bot Crawl
* `Bot Crawl` - Bot Crawl Manage
    * `POST crawl:createTask` - [create a crawl task](#create a crawl task)
    * `GET  crawl/status/{operationId}` - [Get crawl status](#Get crawl status)
    * `GET  crawl/data/{operationId}` - [Query](#get crawl stream data)

### create a crawl task
  `POST crawl:createTask`

- #### Parameters:
```json
  {
    "siteId": 10000, //每个site代表一个客户
    "gptBotId": "", //GUID gpt bot
    "urls": [], // website url or others
  } 
  ```
- #### Response:
```json
  {
    "operationId": "56A2EF45-7D46-EB11-8100-00155D081D0B",
    "status": "in progress", // in progress , error
    "error": {    //如果出错了 需要返回error 信息
        "code": 0,
        "message": ""
    }
  } 
  ``` 

  ### Get crawl status
  `GET crawl/status/{operationId}`
- #### Response:
```json
  {
    "operationId": "56A2EF45-7D46-EB11-8100-00155D081D0B",
    "status": "processing", // in progress ， completed
    "crawlStatus":
    [{
        "url":"xxxx",
        "status":"processing",// in progress ， completed , error
        "error": 
        {    //如果出错了 需要返回error 信息
        "code": 0,
        "message": ""
        }
    }]
  } 
  ``` 

### get crawl stream data
  `POST crawl/data/{operationId}`
  
- #### Response: stream io
```json
  {
      "title" : "xxx",
      "filename":"guid.html",
      "url" : "xxx",
      "content" : "xxx",
      "source" : "xxx" 
  }
  ``` 