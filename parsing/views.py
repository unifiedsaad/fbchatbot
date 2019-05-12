import json, requests, random, re
from pprint import pprint
from wit import Wit

from django.views import generic
from django.http.response import HttpResponse


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

import json
from config import CONFIG
from fbmq import Attachment, Template, QuickReply, NotificationType
from fbpage import page


#  ------------------------ Fill this with your page access token! -------------------------------
PAGE_ACCESS_TOKEN = "EAACURkd8Ul0BAJLiZBi5evLzkIYLnTgyNZC29UBv8B4saqLWDeGlZC4rTic0MYCHjjICBRTZCWOCXVEke6JDqxxAWckrHonnNV8YKNSiA0FCgoFtVqQxl5gm4ZB3fvuuSL281jee7upALO4E5DI0yg8VdvW6lhJZC0GarbWeNvUispx1iMuNBZA"
VERIFY_TOKEN = "1234567890"

client = Wit('HLNPTWYGOJS7FV7PLUWS3PZY7ARIBTZF')


def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val


# Helper function
def post_facebook_message(fbid, recevied_message):
    # Remove all punctuations, lower case the text and split it based on space
    tokens = re.sub(r"[^a-zA-Z0-9\s]", ' ', recevied_message).lower().split()
    joke_text = ''

    resp = client.message(tokens)

    entities = resp['entities']

    greetings = first_entity_value(entities, 'greetings')
    developer = first_entity_value(entities, 'developer')
    chatbot = first_entity_value(entities, 'chatbot')
    department = first_entity_value(entities, 'department_info')
    hod = first_entity_value(entities, 'head_info')
    bye = first_entity_value(entities, 'farewell')
    intent = first_entity_value(entities, 'intent')
    print(intent)


    if greetings:
        joke_text = "hey, how you doing"
    elif developer:
        joke_text = "Why you asking about my creator, anyway i am gonnna tell you. He is Saad Mirza ;)"

    elif chatbot:
        joke_text = "I am University Enquiring Chatbot, you can ask me anything About University. Feel Free to ping me anytime."
    elif department :
        joke_text = "Here department goes"
    elif hod:
        joke_text = " here is the hod info goes "
    elif intent == "department_info":
        joke_text = " here department info from intent"
    elif intent == "head_info":
        joke_text = " he is asking about head dude"
    elif bye:
        joke_text = "Nice Talking to you, Bye"


    else:
        joke_text = "try again"

    send_message(fbid, joke_text)
    send_typing_off(fbid)



class MessengerProfile(generic.View):
    def get(self, request, *args, **kwargs):
        page.show_persistent_menu([Template.ButtonPostBack('MENU1', 'MENU_PAYLOAD/1'),
                                   Template.ButtonPostBack('MENU2', 'MENU_PAYLOAD/2')])

        @page.callback(['MENU_PAYLOAD/(.+)'])
        def click_persistent_menu(payload, event):
            click_menu = payload.split('/')[1]
            print("you clicked %s menu" % click_menu)



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
                    send_typing_on(message['sender']['id'])
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.
                    post_facebook_message(message['sender']['id'], message['message']['text'])
        return HttpResponse()




def send_message(recipient_id, text):
    # If we receive a text message, check to see if it matches any special
    # keywords and send back the corresponding example. Otherwise, just echo
    # the text we received.
    special_keywords = {
        "image": send_image,
        "gif": send_gif,
        "audio": send_audio,
        "video": send_video,
        "file": send_file,
        "button": send_button,
        "generic": send_generic,
        "receipt": send_receipt,
        "quick reply": send_quick_reply,
        "read receipt": send_read_receipt,
        "typing on": send_typing_on,
        "typing off": send_typing_off,
        "account linking": send_account_linking
    }

    if text in special_keywords:
        special_keywords[text](recipient_id)
    else:
        page.send(recipient_id, text, callback=send_text_callback, notification_type=NotificationType.REGULAR)


def send_text_callback(payload, response):
    print("SEND CALLBACK")




def send_image(recipient):
    page.send(recipient, Attachment.Image(CONFIG['SERVER_URL'] + "/assets/rift.png"))


def send_gif(recipient):
    page.send(recipient, Attachment.Image(CONFIG['SERVER_URL'] + "/assets/instagram_logo.gif"))


def send_audio(recipient):
    page.send(recipient, Attachment.Audio(CONFIG['SERVER_URL'] + "/assets/sample.mp3"))


def send_video(recipient):
    page.send(recipient, Attachment.Video(CONFIG['SERVER_URL'] + "/assets/allofus480.mov"))


def send_file(recipient):
    page.send(recipient, Attachment.File(CONFIG['SERVER_URL'] + "/assets/test.txt"))


def send_button(recipient):
    """
    Shortcuts are supported
    page.send(recipient, Template.Buttons("hello", [
        {'type': 'web_url', 'title': 'Open Web URL', 'value': 'https://www.oculus.com/en-us/rift/'},
        {'type': 'postback', 'title': 'tigger Postback', 'value': 'DEVELOPED_DEFINED_PAYLOAD'},
        {'type': 'phone_number', 'title': 'Call Phone Number', 'value': '+16505551234'},
    ]))
    """
    page.send(recipient, Template.Buttons("hello", [
        Template.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
        Template.ButtonPostBack("trigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
        Template.ButtonPhoneNumber("Call Phone Number", "+16505551234")
    ]))


@page.callback(['DEVELOPED_DEFINED_PAYLOAD'])
def callback_clicked_button(payload, event):
    print(payload, event)


def send_generic(recipient):
    page.send(recipient, Template.Generic([
        Template.GenericElement("rift",
                                subtitle="Next-generation virtual reality",
                                item_url="https://www.oculus.com/en-us/rift/",
                                image_url=CONFIG['SERVER_URL'] + "/assets/rift.png",
                                buttons=[
                                    Template.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
                                    Template.ButtonPostBack("tigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
                                    Template.ButtonPhoneNumber("Call Phone Number", "+16505551234")
                                ]),
        Template.GenericElement("touch",
                                subtitle="Your Hands, Now in VR",
                                item_url="https://www.oculus.com/en-us/touch/",
                                image_url=CONFIG['SERVER_URL'] + "/assets/touch.png",
                                buttons=[
                                    {'type': 'web_url', 'title': 'Open Web URL',
                                     'value': 'https://www.oculus.com/en-us/rift/'},
                                    {'type': 'postback', 'title': 'tigger Postback',
                                     'value': 'DEVELOPED_DEFINED_PAYLOAD'},
                                    {'type': 'phone_number', 'title': 'Call Phone Number', 'value': '+16505551234'},
                                ])
    ]))


def send_receipt(recipient):
    receipt_id = "order1357"
    element = Template.ReceiptElement(title="Oculus Rift",
                                      subtitle="Includes: headset, sensor, remote",
                                      quantity=1,
                                      price=599.00,
                                      currency="USD",
                                      image_url=CONFIG['SERVER_URL'] + "/assets/riftsq.png"
                                      )

    address = Template.ReceiptAddress(street_1="1 Hacker Way",
                                      street_2="",
                                      city="Menlo Park",
                                      postal_code="94025",
                                      state="CA",
                                      country="US")

    summary = Template.ReceiptSummary(subtotal=698.99,
                                      shipping_cost=20.00,
                                      total_tax=57.67,
                                      total_cost=626.66)

    adjustment = Template.ReceiptAdjustment(name="New Customer Discount", amount=-50)

    page.send(recipient, Template.Receipt(recipient_name='Peter Chang',
                                          order_number=receipt_id,
                                          currency='USD',
                                          payment_method='Visa 1234',
                                          timestamp="1428444852",
                                          elements=[element],
                                          address=address,
                                          summary=summary,
                                          adjustments=[adjustment]))


def send_quick_reply(recipient):
    """
    shortcuts are supported
    page.send(recipient, "What's your favorite movie genre?",
                quick_replies=[{'title': 'Action', 'payload': 'PICK_ACTION'},
                               {'title': 'Comedy', 'payload': 'PICK_COMEDY'}, ],
                metadata="DEVELOPER_DEFINED_METADATA")
    """
    page.send(recipient, "What's your favorite movie genre?",
              quick_replies=[QuickReply(title="Action", payload="PICK_ACTION"),
                             QuickReply(title="Comedy", payload="PICK_COMEDY")],
              metadata="DEVELOPER_DEFINED_METADATA")


@page.callback(['PICK_ACTION'])
def callback_picked_genre(payload, event):
    print(payload, event)


def send_read_receipt(recipient):
    page.mark_seen(recipient)


def send_typing_on(recipient):
    page.typing_on(recipient)


def send_typing_off(recipient):
    page.typing_off(recipient)


def send_account_linking(recipient):
    page.send(recipient, Template.AccountLink(text="Welcome. Link your account.",
                                              account_link_url=CONFIG['SERVER_URL'] + "/authorize",
                                              account_unlink_button=True))


def send_text_message(recipient, text):
    page.send(recipient, text, metadata="DEVELOPER_DEFINED_METADATA")
