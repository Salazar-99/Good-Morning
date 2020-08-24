import os
import re
import praw
import requests
import random
import json
from dotenv import load_dotenv
from twilio.rest import Client

#Load environment variables
load_dotenv()

#Get names
names = os.getenv('NAMES').split(" ")

#Get twilio credentials
TWILIO_NUM = os.getenv('TWILIO_NUM')
TWILIO_SID = os.getenv('TWILIO_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
RECIPIENT = os.getenv('RECIPIENT')

#Get Reddit credentials
CLIENT_ID = os.getenv('CLIENT_ID')
SECRET_KEY = os.getenv('SECRET_KEY')
USER_AGENT = os.getenv('USER_AGENT')

#Get dictionary credentials
DICTIONARY_KEY = os.getenv('DICTIONARY_KEY')
word_base_url = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/'
word_key_url = '?key=' + DICTIONARY_KEY

#Function for sending message
def send_text(body, image_url):
    client = Client(TWILIO_SID, AUTH_TOKEN)
    message = client.messages.create(body=body, 
                                     from_=TWILIO_NUM,
                                     media_url=[image_url], 
                                     to=RECIPIENT)

#Function for creating message content
def create_body(names, title, word, definition, sentence):
    name = random.choice(names)
    content = f"Good morning {name}! \n\n" + f"The caption for today's image is: '{title}' \n\n" + f"Your word of the day is: \n" + f"'{word}' - {definition} \n\n" + f"Here is a usage example: \n{sentence}"
    return content

#Function for saving an image
def fetch_image():
    reddit = praw.Reddit(client_id=CLIENT_ID, 
                    client_secret=SECRET_KEY, 
                    user_agent=USER_AGENT)
    posts = reddit.subreddit('Awwducational').hot(limit=10)
    for post in posts:
        #Check if the post is a jpeg image
        if is_jpg(post.url):
            image_url = post.url
            #Check if the image is within the size limit
            if check_size(image_url):
                title = post.title
                break
    return image_url, title

#Function to check if a string ends in '.jpg'
def is_jpg(url):
    if re.search(r".jpg$", url) is not None:
        return True
    else:
        return False

#Function for checking image size
def check_size(image_url):
    response = requests.get(image_url)
    size = int(response.headers['Content-Length'])
    #Size limit of 600 kB
    if size > 600000:
        return False
    else: 
        return True

def fetch_word():
    #Get random word
    with open('words.json') as f:
        words = json.load(f)
    #Try words until we find one with a valid definition and sentence example
    while True:
        try:
            #Select random word
            word = random.choice(words)
            #Get definition/sentence data
            api_url = word_base_url + word + word_key_url
            response = requests.get(api_url)
            data = json.loads(response.content.decode('utf-8'))[0]
            #Dig through the JSON response to find relevant info
            definition = data['shortdef'][0]
            raw_sentence = data['def'][0]['sseq'][0][0][1]['sdsense']['dt'][1][1][0]['t']
            #Remove text modifiers from raw sentence string
            sentence = re.sub('{.*?}', '', raw_sentence)
            break
        except (KeyError, TypeError, IndexError):
            print(f"The word '{word}' had invalid dictionary data.")
    return word, definition, sentence

#Entry point for AWS Lambda
def lambda_handler(event, context):
    image_url, title = fetch_image()
    word, definition, sentence = fetch_word()
    body = create_body(names, title, word, definition, sentence)
    send_text(body, image_url)


