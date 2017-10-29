from django.shortcuts import render
import json, requests, random, re
from pprint import pprint
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

PAGE_ACCESS_TOKEN = "EAAZAZCa7zdnK8BAFgf0VR99X2qRzOHh4zZAFHB5lNpXXs8gcCGJv82wulWmOZCVajm9xVn65p4vIcERMkJgyAyvRo1ceF00sOJgjvJAvQL8qf8vjRNkLQpthjqo98LNuZBn1BQQK7kwMWJsUB1LzlfRZBrI7zUfbIB6iZAMY26s0wZDZD"
VERIFY_TOKEN = "2318934571"

balance = 150

def set_global_balance(amount=0):
    global balance
    balance -= amount

texts = {
         'balance': ["""Your balance is {} pounds""".format(balance)],
         'send':    ["""Who do you want to send money to?"""],
         'details':   ["""Your """,
                    """Yo' Mama is so dumb, she locked her keys inside her motorcycle."""],
         'radu': ["How much?"],
         'maria': ["How much?"],
         'roland': ["How much?"],
         }

def post_facebook_message(fbid, recevied_message):

    # Remove all punctuations, lower case the text and split it based on space
    tokens = re.sub(r"[^a-zA-Z0-9\s]",' ',recevied_message).lower().split()
    joke_text = ''
    for token in tokens:
        if token in texts:
            joke_text = random.choice(texts[token])
            break
        elif token.isdigit():
            set_global_balance(int(filter(str.isdigit, str(token))))
            joke_text = "The money was sent. Your balance is now {} pounds".format(balance)
    if not joke_text:
        joke_text = "I didn't understand! Send 'balance', 'send', or 'details'!"

    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":joke_text}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())


class BankyView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other eventsl
                if 'message' in message:
                    # Print the message to the terminal
                    pprint(message)
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.
                    post_facebook_message(message['sender']['id'], message['message']['text'])
        return HttpResponse()
