## Good-Morning
I wrote this script to automate the process of sending my SO a good morning text message every day. The message includes the image and caption of the top post on reddit.com/r/Awwducational for the day as well as a word of the day, it's definition, and a usage example.

### How it works
---
The script begins by instantiating a Reddit agent via the PRAW API provided by Reddit. It then fetches the top 10 images from r/Awwducational and searches through them (top to bottom) to find the first JPEG file. This is done to avoid returning non-image, 'meta' posts that are common on the site. Once an image post is found the URL and caption are saved for later use.

Next, the script selects a random word from the ```words.json``` file and queries the Merriam-Webster API for the word's definition and a usage example. This functionality is nested in a try-except statement because not all of the words in the ```words.json``` file return a valid API response. In this context, valid, means that when the response is parsed we can find a definition and usage example in their expected location. The format of the Merriam-Webster API response has a deep hierarchical nature and thus accessing the data we are interested in requires a very long, static access syntax. If this search 'misses' we simply try a new word.

Finally, the script combines the aforementioned elements and creates the body of the text message. The message is then sent with the Twilio API.

### Deployment on AWS Lambda
---
I am currently hosting this script on AWS Lambda and triggering it via a cronjob hosted on AWS EventBridge. In order to host this on AWS Lambda one needs to package up the ```lib/python3.x/site-packages``` as well as the ```words.json``` and ```good-morning.py``` files into a zip folder. The entire zip folder is then uploaded to AWS Lambda. The AWS EventBridge is configured to run a cronjob with a crontab of the form ```0 12 * * ? *``` which translates to every day at 7am CST. Recall that AWS cronjobs utilize the UTC timezone.

### Possible Improvements
---
Currently, most 'valid' words are not very interesting. A better approach may be to scrape my own set of 'interesting' words and their definitions and draw from that rather than querying the Merriam-Webster API. Additionally, every once in a while the top post on r/Awwwducational is the same for longer than a day which causes the script to send the same image/caption twice in a row. This may be remedied by adding a conditional to check the time since the post was created and rejecting posts which were posted longer than a day before the scripts execution.
