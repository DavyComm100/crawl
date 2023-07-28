## Bot Crawl
* `Bot Crawl` - Bot Crawl Manage
    * `POST gptbot/query` - [query](#query)

### query
  `POST gptbot/query`

- #### Parameters:
```json
  {
    "siteId": 10000, //每个site代表一个客户
    "gptBotId": "", //GUID gpt bot
    "sessionId": "", //GUID
    "query":"",
    "querySource": "chatbot", // enum itself (default)、chatbot、taskbot
    "fromBotId":"",//GUID
  } 
```
- #### Response:
```json
  {
    
  }
  ``` 
