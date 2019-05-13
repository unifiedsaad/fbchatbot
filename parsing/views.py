import json, requests, random, re
from pprint import pprint
from django.http import JsonResponse
from wit import Wit

from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

import json
from config import CONFIG
from fbmq import Attachment, Template, QuickReply, NotificationType
from fbpage import page

#  ------------------------ Fill this with your page access token! -------------------------------
PAGE_ACCESS_TOKEN = "EAACURkd8Ul0BAFepv7EL9S65bCWe2ZCSzAWjCdEcWD0fbONiZB9qRREitKK1WbWEOQnPNFmTOmzVu1IvKMgrhGmlpMIZBrsAZC7oGEJ4lVr29eZAZC66uIZCv1hPl3n2Q0T85MF0owTAIFbwZB6kZBGXYmGM3mHwBTnnaEbpACzZAqRDeOguh2q8l2"
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
    print(entities)
    greetings = first_entity_value(entities, 'greetings')
    person = first_entity_value(entities, 'notable_person')
    chatbot = first_entity_value(entities, 'chatbot')
    developer = first_entity_value(entities, 'developer')
    department = first_entity_value(entities, 'department_info')
    hod = first_entity_value(entities, 'head_info')
    contact = first_entity_value(entities, 'contact')
    bye = first_entity_value(entities, 'farewell')
    salam = first_entity_value(entities, 'salam')
    faculty = first_entity_value(entities, 'faculty')
    intent = first_entity_value(entities, 'intent')

    if chatbot:
        joke_text = "I am University Enquiring Chatbot, you can ask me anything About University. Feel Free to ping me anytime."
    elif bye:
        joke_text = "Nice Talking to you, Bye"

    elif person:
        joke_text = "person here "+person['name']
    elif salam:
        joke_text = "Walaikum us Salam, how can i help you."
    elif intent == "farewell":
        joke_text = "Nice Talking to you, Bye"
    elif greetings:
        joke_text = "hey, how can i help you"
    elif developer:
        joke_text = "Why you asking about my creator, anyway i am gonnna tell you. He is Saad Mirza ;)"
    elif intent == "department_info":
        joke_text = "Here you go....."
        send_generic(fbid, 'dep')
    elif intent == "head_info":
        joke_text = "Here you go....."
        send_generic(fbid, 'hod')
    elif intent == "faculty":
        joke_text = "asking about faculty profile"
    elif intent == "greeting":
        joke_text = "hey, how can i help you"
    elif contact:
        joke_text = "person searching "+contact
    elif department:
        joke_text = "Here you go...."
        send_generic(fbid, 'dep')
    elif hod:
        joke_text = " here is the hod info goes "
    elif faculty:
        joke_text = "asking about faculty"
    else:
        joke_text = "try again"

    send_message(fbid, joke_text)

    send_typing_off(fbid)


class MessengerProfile(generic.View):
    def get(self, request, *args, **kwargs):
        page.show_persistent_menu([Template.ButtonWeb('University of Sargodha', 'https://uos.edu.pk/'),
                                   Template.ButtonWeb('ORIC', 'https://oric.uos.edu.pk'),
                                   Template.ButtonWeb('File a Complaint', 'https://uos.edu.pk/complaint')])

        page.show_starting_button("Get Started")
        page.greeting("University Enquiring Chatbot is here to answer your queries About University")
        return HttpResponse('yaayyyyy')


class Testing(generic.View):
    def get(self, request, *args, **kwargs):
        tokens = re.sub(r"[^a-zA-Z0-9\s]", ' ', 'tell me about Ms Samreen Razzaq').lower().split()
        joke_text = ''

        resp = client.message(tokens)
        entities = resp['entities']
        person = first_entity_value(entities, 'contact')
        print(person)
        response = requests.get('https://uos.edu.pk/about/bot_faculty/' + 'Mr. Amir')
        result = response.json()
        if result:
            print("happy")
        else:
            result = "not happy"
        d = {
            'entties': entities,
            'person': person,
            'result' : result
        }
        return JsonResponse(d)


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

                if 'quick_reply' in message:
                    # Print the message to the terminal
                    if (message['message']['quick_reply']['payload'] == "Dep_info"):
                        send_generic(message['sender']['id'], 'dep')
                    else:
                        send_button(message['sender']['id'])

                elif 'postback' in message:
                    if (message['postback']['payload'] == "Get Started"):
                        greeating = "Hey, i am University Enquiring Chatbot.... Ask me anything about University"
                        send_message(message['sender']['id'], greeating)
                        send_quick_reply(message['sender']['id'])
                elif 'message' in message:
                    messagepoint = message['message']
                    if 'quick_reply' in messagepoint:

                        if (messagepoint['quick_reply']['payload'] == "Dep_info"):
                            send_generic(message['sender']['id'], 'dep')
                        elif messagepoint['quick_reply']['payload'] == "head_info":
                            send_generic(message['sender']['id'], 'hod')
                        elif messagepoint['quick_reply']['payload'] == "faculty_info":
                            send_button(message['sender']['id'])
                    else:
                        if 'text' in messagepoint:
                            if (message['message']['text'] == "restart"):
                                send_quick_reply(message['sender']['id'])
                            else:
                                send_typing_on(message['sender']['id'])
                                # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                                # are sent as attachments and must be handled0p'{{ accordingly.
                                post_facebook_message(message['sender']['id'], message['message']['text'])
                        else:
                            send_message(message['sender']['id'], 'Hey there is problem')

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


@page.callback(['MENU_PAYLOAD/(.+)'])
def click_persistent_menu(payload, event):
    print('menu clicked')


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


def send_generic(recipient, type, data=True):
    if (type == "dep"):
        page.send(recipient, Template.Generic([
            Template.GenericElement("CS & IT",
                                    subtitle="Department of Computer Science & Information Technology",
                                    item_url="https://uos.edu.pk/department/profile/2",
                                    image_url="https://uos.edu.pk/uploads/departments/banner/IT.jpg",
                                    buttons=[
                                        Template.ButtonWeb("Academic Programs",
                                                           "https://uos.edu.pk/department/academic_programs/2"),
                                        Template.ButtonWeb("Faculty",
                                                           "https://uos.edu.pk/department/faculty_list/2"),
                                        Template.ButtonPhoneNumber("Contact", "+16505551234")
                                    ])

        ]))
    elif type == "hod":
        page.send(recipient, Template.Generic([
            Template.GenericElement("Mr. Saad Razzaq",
                                    subtitle="Assistant Professor / Incharge",
                                    item_url="https://uos.edu.pk/faculty/profile/muhammadsaadrazzaq",
                                    image_url="https://uos.edu.pk/uploads/faculty/profiles/Saad_Razzaq.JPG",
                                    buttons=[
                                        Template.ButtonWeb("Open Profile",
                                                           "https://uos.edu.pk/faculty/profile/muhammadsaadrazzaq"),
                                        Template.ButtonPhoneNumber("Contact", "+92489230879")
                                    ])

        ]))
    elif type == "faculty":
        response = requests.get('https://uos.edu.pk/about/bot_faculty/'+data)
        result = response.json()
        if result:
            page.send(recipient, Template.Generic([
                Template.GenericElement(result[0]['name'],
                                        subtitle=result[0]['designation'],
                                        item_url="https://uos.edu.pk/faculty/profile/"+result[0]['username'],
                                        image_url="https://uos.edu.pk/uploads/faculty/profiles/"+result[0]['picture'],
                                        buttons=[
                                            Template.ButtonWeb("Open Profile",
                                                               "https://uos.edu.pk/faculty/profile/"+result[0]['username']),
                                            Template.ButtonPhoneNumber("Contact", result[0]['mobile_no'])
                                        ])

            ]))
        else:
            send_message(recipient, 'No User found in our Database')
            send_typing_off(recipient)


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
    '''
    page.send(recipient, "What's your favorite movie genre?",
                quick_replies=[{'title': 'Action', 'payload': 'PICK_ACTION'},
                               {'title': 'Comedy', 'payload': 'PICK_COMEDY'}, ],
                metadata="DEVELOPER_DEFINED_METADATA")
    '''
    page.send(recipient, "Here are some suggestion, if you wanna choose",
              quick_replies=[QuickReply(title="CS Department", payload="Dep_info"),
                             QuickReply(title="CS HOD", payload="head_info"),
                             QuickReply(title="CS Faculty", payload="faculty_info"),
                             QuickReply(title="CS Programs", payload="program_info")],
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
