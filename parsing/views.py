import json, requests, random, re
from pprint import pprint
from wit import Wit

from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

#  ------------------------ Fill this with your page access token! -------------------------------
PAGE_ACCESS_TOKEN = "EAACURkd8Ul0BAINJIQkYiGhRy9yQyn6yWOyzsGioC4XIxbgA168ZB76kztvPAWFVssC2AfvixRuU6F7UVG8UKLGRsVAF75xGH9utEz9aZAtbEapgoe3ZBqz7wWTEy12KFsRzBwGiE7ZCpp3FkH6IyagYvAJtduCc3R68rUwJjGEgQZBWhpwV9"
VERIFY_TOKEN = "1234567890"

client = Wit('HLNPTWYGOJS7FV7PLUWS3PZY7ARIBTZF')



# Helper function
def post_facebook_message(fbid, recevied_message):
    # Remove all punctuations, lower case the text and split it based on space
    tokens = re.sub(r"[^a-zA-Z0-9\s]", ' ', recevied_message).lower().split()
    joke_text = ''

    resp = client.message(tokens)
    entities = resp['entities']
    if(entities.intent['value']):
        print(entities.intent['value'])
    else:
        print(entities)
        print("it's the second one ")


    if (resp['entities'] == "greetings" ):
        joke_text = "Hey , how you doing man"
    else:
        joke_text = "try again"

    post_message_url = 'https://graph.facebook.com/v3.2/me/messages?access_token=%s' % PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": joke_text}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)



# Create your views here.
class JokesBotView(generic.View):
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
                # This might be delivery, optin, postback for other events
                if 'message' in message:
                    # Print the message to the terminal

                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.
                    post_facebook_message(message['sender']['id'], message['message']['text'])
        return HttpResponse()
