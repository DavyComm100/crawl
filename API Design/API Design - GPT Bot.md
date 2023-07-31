## Bot Crawl
* `Bot Crawl` - Bot Crawl Manage
    * `POST gptbots/{gptbotId:Guid}/sessions}` - [session](#session)
    * `POST gptbots/{gptbotId:Guid}/query` - [query](#query)

### session
  `POST gptbots/{gptbotId:Guid}/sessions`

- #### Parameters:
```json
  {
    "siteId": 10000, //每个site代表一个客户
    "gptBotId": "", //GUID gpt bot
    "sessionId": "", //GUID
    "querySource": "chatbot", // enum gptbot、chatbot、taskbot
    "fromBotId": "",//GUID has value when querySource is chatbot、taskbot
    "context": 
    {
      "istest" : false,
      "channel" : "Livechat"
    }
  } 
```
- #### Response:
```json
  {
    "greetingmessage":{
      "messages":
      [{
          "type":"gptbotsendmessage",
          "content":{
            "message" : "welcome  xxx"
          }
      }]
    }
    "context": 
    {
      "siteId": 10000, //每个site代表一个客户
      "sessionId": "", //GUID
      "gptBotId": "", //GUID gpt bot
      "istest" : false,
      "querySource": "chatbot", // enum gptbot、chatbot、taskbot
      "fromBotId": "",//GUID has value when querySource is chatbot、taskbot
      "channel" : "Livechat"
    }
  }
  ``` 

### query
  `POST gptbots/{gptbotId:Guid}/query`

- #### Parameters:
```json
  {
    "siteId": 10000, //每个site代表一个客户
    "gptBotId": "", //GUID gpt bot
    "sessionId": "", //GUID
    "query": "i want to know ...",
    "context": 
    {
      "siteId": 10000, //每个site代表一个客户
      "sessionId": "", //GUID
      "gptBotId": "", //GUID gpt bot
      "istest" : false,
      "querySource": "chatbot", // enum gptbot、chatbot、taskbot
      "fromBotId": "",//GUID has value when querySource is chatbot、taskbot
      "channel" : "Livechat"
    }
  } 
```
- #### Response:
```json
  {
    "answertype":"hasanswer", // hasanswer,noaswer
    "answer":{
      "messages":
      [{
          // when answertype == "hasanswer"
          "type":"gptbotsendmessage",
          "content":{
            "message" : "welcome  xxx"
          },

          // when answertype == "noaswer"
          // "type":"gptbottransfer",
          // "content":{
          //   "messager":"",
          //   "isshowbutton":"",
          //   "buttontext":"",
          //   "transfertype":"", // enum agent,department,chatbot,taskbot,routing rules.
          //   "transfertargetid":"" // agent,department,chatbot,taskbot
          // }
      }]
    },
   
    "context": 
    {
      "siteId": 10000, //每个site代表一个客户
      "sessionId": "", //GUID
      "gptBotId": "", //GUID gpt bot
      "istest" : false,
      "querySource": "chatbot", // enum gptbot、chatbot、taskbot
      "fromBotId": "",//GUID has value when querySource is chatbot、taskbot
      "channel" : "Livechat"
    }
  }
  ``` 