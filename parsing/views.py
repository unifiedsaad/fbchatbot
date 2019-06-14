import json, requests, random, re

from django.http import JsonResponse
from wit import Wit
import urllib.parse
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


PAGE_ACCESS_TOKEN = "EAACURkd8Ul0BAFepv7EL9S65bCWe2ZCSzAWjCdEcWD0fbONiZB9qRREitKK1WbWEOQnPNFmTOmzVu1IvKMgrhGmlpMIZBrsAZC7oGEJ4lVr29eZAZC66uIZCv1hPl3n2Q0T85MF0owTAIFbwZB6kZBGXYmGM3mHwBTnnaEbpACzZAqRDeOguh2q8l2"
VERIFY_TOKEN = "1234567890"

client = Wit('BA7KJ6C3ATHG7WPYGEO36U3FL4IL4BTQ')


def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val



def post_facebook_message(fbid, recevied_message):
    resp = client.message(recevied_message)
    entities = resp['entities']
    print("***************************************")
    print(entities)
    print("***************************************")
    message = handleIntents(entities, fbid)
    if message:
        send_message(fbid, message)
    else:
        send_message(fbid, 'Sorry i am unable to answer this question ')

        print("can't send message, becausee it's blankkkkkkkkkkkkkkkkkkkkkkkkkkkk")


def handleIntents(receivedent, user):
    try:

        if first_entity_value(receivedent, 'intent'):
            return Intents_parser(receivedent, user)
        if first_entity_value(receivedent, 'greetings'):
            return "Hey, How can i help you"

    except Exception as e:
        print("not found dude")


def Intents_parser(receivedent, user):
    if receivedent['intent'][0]['value'] == "department_info":
        return department_info(receivedent, user)
    elif receivedent['intent'][0]['value'] == "faculty_profile":
        if first_entity_value(receivedent, 'department_name'):
            send_generic_faculty(user, receivedent['faculty_name'][0]['value'],
                                 receivedent['department_name'][0][
                                     'value'])
            return "Here you go"
        else:
            send_generic_faculty(user, receivedent['faculty_name'][0]['value'])
            return "Here you go"
    elif receivedent['intent'][0]['value'] == "admission_info":
        page.send(user, Template.Buttons('Admissions', [
            Template.ButtonWeb("Private Admissions", "https://uos.edu.pk/examination/Admissions_Schedule"),
            Template.ButtonWeb("Regular Admissions", "https://admissions.uos.edu.pk/importantdates")
        ]))
        return "Here you can Find All Admisison Related Info"
    elif receivedent['intent'][0]['value'] == "merit_info":
        page.send(user, Template.Buttons('Merit Info', [
            Template.ButtonWeb("Merit Lists", "https://uos.edu.pk/examination/merits")
        ]))
        return "Here you can Find All info Related To Merit"
    elif receivedent['intent'][0]['value'] == "junk":
        return "Sorry i don't understand your question."
    else:
        return "Sorry I don't Understand your Question"


def department_info(receivedent, user):
    if first_entity_value(receivedent, 'department_info_type'):
        if receivedent['department_info_type'][0]['value'] == "general":
            if first_entity_value(receivedent, 'timing_type'):
                return Timing_type(receivedent)
            else:
                if first_entity_value(receivedent, 'department_name'):
                    send_generic(user, 'dep', receivedent['department_name'][0][
                        'value'])
                    return "sorry i cant ans this"
                else:

                    return "Please Mention Department Correct Name to Find Details"

        elif receivedent['department_info_type'][0]['value'] == "hod":
            if first_entity_value(receivedent, 'department_name'):
                send_generic(user, 'hod', receivedent['department_name'][0][
                    'value'])
                return "Here you can see Detail of the department HOD" + receivedent['department_name'][0][
                    'value']
            else:

                return "Please Mention Department Name for HOD"

        elif receivedent['department_info_type'][0]['value'] == "contact_details":
            if first_entity_value(receivedent, 'department_name'):
                send_generic(user, 'dep', receivedent['department_name'][0][
                    'value'])
                return "Here You can Find Details of the department contact"
            else:

                return "Please Mention Department Correct Name to Find Details"

        elif receivedent['department_info_type'][0]['value'] == "Faculty":
            if first_entity_value(receivedent, 'department_name'):
                if first_entity_value(receivedent, 'faculty_name'):
                    send_generic_faculty(user, receivedent['faculty_name'][0]['value'],
                                         receivedent['department_name'][0][
                                             'value'])
                    return "Here you go"
                else:
                    send_generic(user, 'dep', receivedent['department_name'][0][
                        'value'])
                    return "Here you Can Find All the Faculty Members of " + receivedent['department_name'][0][
                        'value']

            else:
                send_generic_faculty(user, receivedent['faculty_name'][0]['value'])
                return "Here you go"

        elif receivedent['department_info_type'][0]['value'] == "programs":
            print("reached in program section")
            if first_entity_value(receivedent, 'department_name'):
                print('reached in department section')
                if first_entity_value(receivedent, 'program_name'):
                    print("reached in name section")
                    send_generic_program(user, receivedent['program_name'][0][
                        'value'])
                    return "Here you Can See Detail of " + receivedent['program_name'][0]['value']
                else:
                    print('reached in else section')
                    send_generic_program_dep(user, receivedent['department_name'][0][
                        'value'])
                    return "Here are the List of Programs"
            else:
                if first_entity_value(receivedent, 'program_name'):
                    send_generic_program(user, receivedent['program_name'][0][
                        'value'])
                    return "Here you Can See Detail of " + receivedent['program_name'][0]['value']
                else:

                    return "we are unable to Parse this query, Please Enter Correct Department and Program Name"
        elif receivedent['department_info_type'][0]['value'] == "contact_details":
            if first_entity_value(receivedent, 'department_name'):
                send_generic(user, 'dep', receivedent['department_name'][0][
                    'value'])
                return "Here You can Find Contact Details"
            else:

                return "Please Mention Department Correct Name to Find Details"

        elif receivedent['department_info_type'][0]['value'] == "admission":
            return "The admission will start in " + receivedent['department_name'][0][
                'value'] + "in September"

        else:
            if first_entity_value(receivedent, 'department_name'):
                send_generic(user, 'dep', receivedent['department_name'][0][
                    'value'])
                return "Here You can Find Details here department info type not mention that's why "
            else:

                return "Please Mention Department Correct Name to Find Details"
    else:
        if first_entity_value(receivedent, 'department_name'):
            send_generic(user, 'dep', receivedent['department_name'][0][
                'value'])
            return "Here You can Find Details where department info type is not mentioned"


def Timing_type(receivedent):
    if receivedent['timing_type'][0]['value'] == "open":
        return "Opening Time of " + receivedent['department_name'][0][
            'value'] + " is 9:00 AM "
    elif receivedent['timing_type'][0]['value'] == "close":

        return "Closing Time of " + receivedent['department_name'][0][
            'value'] + "is 5:00 PM "
    else:
        return "Nohting from timing type module "


class MessengerProfile(generic.View):
    def get(self, request, *args, **kwargs):
        page.show_persistent_menu([Template.ButtonWeb('University of Sargodha', 'https://uos.edu.pk/'),
                                   Template.ButtonWeb('ORIC', 'https://oric.uos.edu.pk'),
                                   Template.ButtonWeb('File a Complaint', 'https://uos.edu.pk/complaint')])

        page.show_starting_button("Start Asking Your Queries")
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
            'result': result
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

            if "notification_type" in incoming_message:
                print("that was notification")
            else:
                for message in entry['messaging']:
                    # Check to make sure the received call is a message call
                    # This might be delivery, optin, postback for other events

                    if 'quick_reply' in message:
                        # Print the message to the terminal
                        if (message['message']['quick_reply']['payload'] == "Dep_info"):
                            send_generic(message['sender']['id'], 'dep', 'CS & IT')
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
                                send_generic(message['sender']['id'], 'dep', 'CS & IT')
                            elif messagepoint['quick_reply']['payload'] == "head_info":
                                send_generic(message['sender']['id'], 'hod', 'CS & IT')
                            elif messagepoint['quick_reply']['payload'] == "faculty_info":
                                send_message(message['sender']['id'],
                                             'Here You Can Find Faculty Profiles Of CS & IT')
                                send_generic(message['sender']['id'], 'dep', 'CS & IT')
                            elif messagepoint['quick_reply']['payload'] == "program_info":
                                send_generic_program_dep(message['sender']['id'], 'CS & IT')
                                send_quick_reply_program(message['sender']['id'])
                            elif messagepoint['quick_reply']['payload'] == "bscs":
                                send_message(message['sender']['id'], 'BSCS Details goes here')
                                send_generic_program(message['sender']['id'], 'BS Computer Science')
                            elif messagepoint['quick_reply']['payload'] == "bsse":
                                send_message(message['sender']['id'], 'BSSE Details goes here')
                                send_generic_program(message['sender']['id'], 'BS Software Engineering')
                            elif messagepoint['quick_reply']['payload'] == "bsit":
                                send_message(message['sender']['id'], 'BSIT Details goes here')
                                send_generic_program(message['sender']['id'], 'BS Information Technology')
                            elif messagepoint['quick_reply']['payload'] == "mscs":
                                send_message(message['sender']['id'], 'MSCS Details goes here')
                                send_generic_program(message['sender']['id'], 'MS Computer Science')

                        elif 'attachment' in message:
                            print('that was attachement')

                        elif 'is_echo' in messagepoint:
                            print("hey that was the bug ")

                        else:
                            if 'text' in messagepoint:
                                if (message['message']['text'] == "help" or message['message']['text'] == "Help" ):
                                    send_quick_reply(message['sender']['id'])
                                else:

                                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                                    # are sent as attachments and must be handled0p'{{ accordingly.
                                    post_facebook_message(message['sender']['id'], message['message']['text'])
                            else:
                                send_message(message['sender']['id'], 'Hey there is problem')

        return HttpResponse()

def send_receipt(recipient):
    receipt_id = "order1357"
    element = Template.ReceiptElement(title="University of Sargodha",
                                      subtitle="University of Sargodha",
                                      quantity=1,
                                      price=599.00,
                                      currency="USD",
                                      image_url=CONFIG['SERVER_URL'] + "/"
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
    page.send(recipient, Template.Buttons("hello", [
        Template.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
        Template.ButtonPostBack("trigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
        Template.ButtonPhoneNumber("Call Phone Number", "+16505551234")
    ]))


@page.callback(['DEVELOPED_DEFINED_PAYLOAD'])
def callback_clicked_button(payload, event):
    print(payload, event)


def send_generic(recipient, type, data=""):
    data = urllib.parse.quote_plus(data)
    if (type == "dep"):
        if (data):

            response = requests.get('https://uos.edu.pk/about/bot_department/' + data)
            result = response.json()

            if result:
                page.send(recipient, Template.Generic([
                    Template.GenericElement(result[0]['name'],
                                            subtitle="Department of " + result[0]['name'],
                                            item_url="https://uos.edu.pk/department/profile/" + result[0]['id'],
                                            image_url="https://uos.edu.pk/uploads/departments/banner/" + result[0][
                                                'banner'],
                                            buttons=[
                                                Template.ButtonWeb("Academic Programs",
                                                                   "https://uos.edu.pk/department/academic_programs/" +
                                                                   result[0]['id']),
                                                Template.ButtonWeb("Faculty",
                                                                   "https://uos.edu.pk/department/faculty_list/" +
                                                                   result[0]['id']),
                                                Template.ButtonPhoneNumber("Phone", '+92 48 9230879')
                                            ])

                ]))
    elif type == "hod":
        if (data):
            print(data)
            response = requests.get('https://uos.edu.pk/about/bot_hod/' + data)
            result = response.json()
            print(result)
            print("result section there")
            if result:
                page.send(recipient, Template.Generic([
                    Template.GenericElement(result[0]['name'],
                                            subtitle=result[0]['designation'],
                                            item_url="https://uos.edu.pk/faculty/profile/" + result[0]['username'],
                                            image_url="https://uos.edu.pk/uploads/faculty/profiles/" + result[0][
                                                'picture'],
                                            buttons=[
                                                Template.ButtonWeb("Open Profile",
                                                                   "https://uos.edu.pk/faculty/profile/" + result[0][
                                                                       'username']),
                                                Template.ButtonPhoneNumber("Contact", '+92 48 9230879')
                                            ])

                ]))


def send_generic_faculty(recipient, data, dep=""):
    data = urllib.parse.quote_plus(data)
    dep = urllib.parse.quote_plus(dep)
    if (dep):
        response = requests.get('https://uos.edu.pk/about/bot_faculty/' + data + "/" + dep)
        result = response.json()
        if result:
            page.send(recipient, Template.Generic([
                Template.GenericElement(result[0]['name'],
                                        subtitle=result[0]['designation'],
                                        item_url="https://uos.edu.pk/faculty/profile/" + result[0]['username'],
                                        image_url="https://uos.edu.pk/uploads/faculty/profiles/" + result[0]['picture'],
                                        buttons=[
                                            Template.ButtonWeb("Open Profile",
                                                               "https://uos.edu.pk/faculty/profile/" + result[0][
                                                                   'username']),
                                            Template.ButtonPhoneNumber("Contact", '+92 48 9230879')
                                        ])

            ]))
        else:
            send_message(recipient, 'Sorry, but i am unable to Find' + data + " in " + dep)
            send_typing_off(recipient)
    else:
        response = requests.get('https://uos.edu.pk/about/bot_faculty/' + data)
        result = response.json()

        if result:
            page.send(recipient, Template.Generic([
                Template.GenericElement(result[0]['name'],
                                        subtitle=result[0]['designation'],
                                        item_url="https://uos.edu.pk/faculty/profile/" + result[0]['username'],
                                        image_url="https://uos.edu.pk/uploads/faculty/profiles/" + result[0]['picture'],
                                        buttons=[
                                            Template.ButtonWeb("Open Profile",
                                                               "https://uos.edu.pk/faculty/profile/" + result[0][
                                                                   'username']),
                                            Template.ButtonPhoneNumber("Contact", '+92 48 9230879')
                                        ])

            ]))
        else:
            send_message(recipient, 'Sorry, but i am unable to Find' + data)
            send_typing_off(recipient)


def send_generic_program(recipient, data):
    data = urllib.parse.quote_plus(data)
    response = requests.get('https://uos.edu.pk/about/bot_program/' + data)
    result = response.json()
    if result:
        send_message(recipient, 'Duration : ' + result[0]['duration'])
        send_message(recipient, 'Credit Hours ' + result[0]['credit_hour'])
        send_message(recipient, 'Eligibility ' + result[0]['requirement'])
        page.send(recipient, Template.Buttons(result[0]['name'], [
            Template.ButtonWeb("See More Detail", "https://uos.edu.pk/department/academic_programs/" +
                               result[0]['dpartment']),
            Template.ButtonWeb("Prospectus Jump", "https://uos.edu.pk/uploads/faculties/covers/" +
                               result[0]['scheme_file']),
            Template.ButtonWeb("Scheme of Study", "https://uos.edu.pk/uploads/faculties/schemes/" +
                               result[0]['detail_scheme'])
        ]))
    else:
        send_message(recipient, 'Sorry, but i am unable to Find' + data)
        send_typing_off(recipient)


def send_generic_program_dep(recipient, data):
    data = urllib.parse.quote_plus(data)
    print(data)
    response = requests.get('https://uos.edu.pk/about/bot_department/' + data)
    result = response.json()
    print(result)
    if result:
        print(result[0]['name'])
        page.send(recipient, Template.Buttons(result[0]['name'], [
            Template.ButtonWeb("See All Programs", "https://uos.edu.pk/department/academic_programs/" +
                               result[0]['id'])

        ]))
    else:
        send_message(recipient, 'Sorry, but i am unable to Find' + data)
        send_typing_off(recipient)





def send_quick_reply(recipient):
    page.send(recipient, "Here are some suggestion, if you wanna choose",
              quick_replies=[QuickReply(title="CS Department", payload="Dep_info"),
                             QuickReply(title="CS HOD", payload="head_info"),
                             QuickReply(title="CS Faculty", payload="faculty_info"),
                             QuickReply(title="CS Programs", payload="program_info")],
              metadata="DEVELOPER_DEFINED_METADATA")


def send_quick_reply_program(recipient):
    page.send(recipient, "Here are some suggestion, if you wanna choose",
              quick_replies=[QuickReply(title="BSCS", payload="bscs"),
                             QuickReply(title="BSIT", payload="bsit"),
                             QuickReply(title="BSSE", payload="bsse"),
                             QuickReply(title="MSCS", payload="mscs")],
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


def discipline_details(recipient, message):
    send_message(recipient, 'Program Detail goes here ' + message)



