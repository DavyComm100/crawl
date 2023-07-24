1. 后台运行：nohup python3 CrawlWebsite.py > spider_log.txt &
1. 后台运行：nohup python3 spider_liveperson_google_improve.py > liveperson_log.txt &
   (1). ps aux | grep python
   (2). kill -9 -主进程号 举例：kill -9 -1265
查看output： vi spider_log.txt

安装步骤：
1. 安装软件 pip and chrome kit
apt-get update
apt-get install python3-pip
sudo apt install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget

2. 安装依赖
pip install -r requirements.txt