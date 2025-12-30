# ToBi
A Telegram bot that allows users to locate the nearest bidet-equipped toilets.

### Demo
Here is the latest demo of the bot in action.

<a href="https://youtube.com/shorts/YmVhxuHcuZc" target="_blank" rel="noopener noreferrer">
  <img src="https://img.youtube.com/vi/YmVhxuHcuZc/maxresdefault.jpg" alt="BidetBuddyBot Demo">
</a>

### Update (28/12/25)
<p>The bot is now live! Do check it out at @BidetBuddyBot.</p>
<p>Do note that the first response after you select start may be delayed due to the server being deployed on a free tier on <a href="https://render.com/" target="_blank" rel="noopener noreferrer">Render</a>. The server is in sleep mode after a period of inactivity and thus will need some time to spin back up after you select start thus causing a slight delay.</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments
Powered by data from toiletswithbidetsg and community contributors. (Latest data from 29/11/2025)

* [toiletswithbidetsg](https://linktr.ee/toiletswithbidetsg)

<!-- GETTING STARTED -->
## Getting Started Locally

### Prerequisites
Install required packages
```sh
  pip install -r requirements.txt
```

<!-- RUNNING BOT -->
## Running the bot
```sh
cd toilet-bot
python -m uvicorn bot:app --reload
```
