## Email Agent Assist
* `Email Agent Assist` - Email Agent Assist Manage
    * `POST bot/agentAssist` - [Create OR Update Agent Assist](#Create-a-agent-assist)
    * `GET bot/agentAssist/operations/{operationId}` - [Get agent Assist Operation status](#Get-agent-Assist-status)
    * `POST bot/agentAssist:query` - [Query](#query)

### Create a Agent Assist
  `POST bot/agentAssist?siteId={siteId}`

- #### Parameters:
```json
  {
    "siteId": 10000, //每个site代表一个客户
    "Comm100AIID": "", //GUID 
    "dataSources": [
      {
        "type": "", // doc, webpage
        "data": [""], //     
      }
    ]  
  } 
  ```
- #### Response:
```json
  {
    "operationId": "56A2EF45-7D46-EB11-8100-00155D081D0B",
    "status": "pending", //@todo: 需要定义一下有哪些状态？
    "error": {    //如果出错了 需要返回error 信息
        "code": 0,
        "message": ""
    }
  } 
  ``` 

  ### Get agent Assist status
  `GET bot/agentAssist?siteId={siteId}&operationId={operationId}`
- #### Response:
```json
  {
    "operationId": "56A2EF45-7D46-EB11-8100-00155D081D0B",
    "status": "processing", //@todo: 需要定义一下有哪些状态？
    "error": {    //如果出错了 需要返回error 信息
        "code": 0,
        "message": ""
    }
  } 
  ``` 

### Query
  `POST bot/agentAssist:query?siteId={siteId}`

- #### Parameters:
```json
  {
    "siteId": 10000, //每个site代表一个客户
    "Comm100AIID": "", //GUID 
    "sessionId": "56A2EF45-7D46-EB11-8100-00155D081D0B",
    "query": "", //完整的query,包含这个session 的多个来回邮件内容  
    "context": {
      "subject": "", 
      "history": []     
    }
  } 
  ```
  
- #### Response:
```json
  {
      "code": 0,
      "msg": "success",
      "data": {
          "can_answer": true,
          "reply": "xxx",
          "sources": [{"file": "xxx.pdf", "segment": "xxxx", "score": 0.86}]
      },
      "usages": {
        "prompt_tokens": 5,
        "completion_tokens": 7,
        "total_tokens": 12
      }
  }
  ``` 

### Data Struct
  ChatHistoryData:
  ```json
  [
    {
      "siteId": 10000,
      "id": "f19e8b8b-9233-4491-8466-934d3ac2b279", 
      "content": "[2023/06/01 16:31:17]:Nash:Hi, welcome. What can I do for you?
                  [2023/06/01 16:31:19]:Amy:Hello sir
                  [2023/06/01 16:31:19]:Nash:Yes?
                  [2023/06/01 16:31:19]:Amy:I have a denied transfer admission.
                  [2023/06/01 16:31:20]:Amy:Bit I met assured admission req?
                  [2023/06/01 16:31:28]:Amy:What is wrong?
                  [2023/06/01 16:31:29]:Nash:Let me check. Your name please?
                  [2023/06/01 16:31:29]:Amy:Amy Parker.
                  [2023/06/01 16:31:29]:Nash:OK. Please wait.
                  [2023/06/01 16:31:29]:Nash:Hi Peter, I’ve checked your admission, it meets the “assured admission” of UH, but it does not meet the requirement of the major you wanted. For Cullen/Business, you need a 3.25 overall, compared to CLASS where you need a 2.5.
                  [2023/06/01 16:31:29]:Nash:I think you may consider changing your major and apply again.
                  [2023/06/01 16:31:29]:Amy:OK, thank you for your help.",
      "createTime":"2023/06/01 16:31:17",           
    }
  ]
  ``` 

  EmailHistoryData
  ```json
  [
    {
      "siteId": 10000,
      "ticketId": 29407,
      "subject": "Grad admission decision letter disappeared – OKAY (AREAS TO CHANGE ARE HIGHLIGHTED",       
      "body": [
        "From: Terry Jin
          Sent: 05/18/2023 08:39:13
          To: terryjinhz@outlook.com
          Cc: terryjincn@gmail.com
          Subject: Grad admission decision letter disappeared – OKAY (AREAS TO CHANGE ARE HIGHLIGHTED
          Hello!

          I’m an incoming grad student in music major, my girlfriend and I both got admitted by UH school of music, however, her admission decision letter disappeared from her applyweb page, believe or not( at least I can’t believe it happened and the school showing no care about it) We both signed the scholarship offer letter and and it’s about the ddl to reply other schools, I hope can stay with her, anyone may think this is a problem? Any information would be greatly appreciated!

          Thanks
          Agent Terry from Comm100",
        "From: Terry Jin
          Sent: 05/19/2023 08:39:13
          To: terryjinhz@outlook.com
          Cc: terryjincn@gmail.com
          Subject: RE:Grad admission decision letter disappeared – OKAY (AREAS TO CHANGE ARE HIGHLIGHTED
          Hi!
          We are happy to assist.
          If you are given an AccessUH Account, you can log in and see the decision status there.
          For the letter, if you call the Graduate Admissions office they should get it back for you.
          They're a much more responsive department.

          Thanks
          Agent Terry from Comm100"],
      "createTime":"2023/06/01 16:31:17",
    }
  ]
  ``` 
BotData
```json
  [
    {
      "siteId": 10000,
      "botid": "f19e8b8b-9233-4491-8466-934d3ac2b279", 
      "intentName": "Greeting",
      "questions": [
        "hi",
        "hello"
      ],
      "answer": "Hi, how can I help you?"  -- sendmessage/sendimage/sendvedio
    }
  ]
  ``` 
KB Data or QA Data
```json
  [
    {
      "siteId": 10000,
      "title": "How to Apply for Financial Aid",
      "similarQuestions": [],
      "content": "At the University of Houston, we realize the important role financial aid plays in funding your education. In order to have access to this valuable resource in a timely fashion, it is important for you to complete a Free Application for Federal Student Aid (FAFSA) as soon as possible after Oct. 1 (prior to the academic year) to ensure you receive your awards in time to pay tuition and fees. You must complete and submit the FAFSA, along with any requested documentation, by the priority deadline of Jan. 15 (prior to the academic year) to receive the maximum consideration for limited financial aid resources. The University of Houston’s Federal School Code is 003652."
    },
    {
      "siteId": 10000,
      "title": "What will cause my appeal to be rejected or denied?",
      "similarQuestions": [],
      "content": "If your appeal is not completed, properly signed, and if no corroborating documents are included, your appeal is considered incomplete. Students who miss the deadline or fail to turn in additional requested documents in a timely fashion will be denied. We encourage students to submit a thoughtful and well-worded typed statement, as this reflects on your commitment towards improving academic performance."
    }
  ]
  ``` 

测试example:
Email:
```json
  {
    "siteId": 10000, 
    "sessionId": "56A2EF45-7D46-EB11-8100-00155D081D0B",
    "query": "From: Amy
Sent: 05/18/2023 08:39:13
To: terryjinhz@outlook.com
Cc: terryjincn@gmail.com
Subject: RE:RE: Tuition
Will it affect the classes I enrolled in for summer/fall?",
    "context": {
      "ticketId": 29407,
      "subject": "Tuition", 
      "history": [
        "From: Terry Jin
Sent: 05/18/2023 08:39:13
To: Amy@outlook.com
Cc: terryjincn@gmail.com
Subject: RE: Tuition
Hi, 
The fee is $25 if you don’t pay your deferred plan. And a financial hold will be placed on your account.


Thanks
Agent Terry from Comm100",
"From: Amy
Sent: 05/18/2023 08:39:13
To: terryjinhz@outlook.com
Cc: terryjincn@gmail.com
Subject: Tuition
Hi, would you please tell me what happens if I don’t pay my deferred plan by Monday? What’s the fee? Will it not let me register for classes?"

      ]
    }    
  } 
  ```
Chat:
```json
  {
    "siteId": 10000, 
    "sessionId": "56A2EF45-7D46-EB11-8100-00155D081D0B",
    "query": "User:I have a denied transfer admission.But I met assured admission req? What is wrong?",
    "context": {
      "subject": "", 
      "history": [
        "AI:Hi, welcome. What can I do for you?",
        "User:Hello sir",
        "AI:Yes?"
      ]
    }    
  } 
  ```
Other
  ```json
  {
    "siteId": 10000, 
    "sessionId": "56A2EF45-7D46-EB11-8100-00155D081D0B",
    "query": "Hi, 
I’m a freshman here. I wonder what are the requirements for applying the Federal Financial Aid?
I really want to apply the aids but never have done that before. Sorry.",
    "context": {
      "subject": "", 
      "history": []
    }    
  } 
  ```
