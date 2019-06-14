# coding: utf-8
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

import json
from config import CONFIG
from fbmq import Attachment, Template, QuickReply, NotificationType
from fbpage import page

USER_SEQ = {}


@page.handle_optin
def received_authentication(event):
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_auth = event.timestamp

    pass_through_param = event.optin.get("ref")

    print("Received authentication for user %s and page %s with pass "
          "through param '%s' at %s" % (sender_id, recipient_id, pass_through_param, time_of_auth))

    page.send(sender_id, "Authentication successful")


@page.handle_echo
def received_echo(event):
    message = event.message
    message_id = message.get("mid")
    app_id = message.get("app_id")
    metadata = message.get("metadata")
    print("page id : %s , %s" % (page.page_id, page.page_name))
    print("Received echo for message %s and app %s with metadata %s" % (message_id, app_id, metadata))


@page.handle_message
def received_message(event):
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_message = event.timestamp
    message = event.message
    print("Received message for user %s and page %s at %s with message:"
          % (sender_id, recipient_id, time_of_message))
    print(message)

    seq = message.get("seq", 0)
    message_id = message.get("mid")
    app_id = message.get("app_id")
    metadata = message.get("metadata")

    message_text = message.get("text")
    message_attachments = message.get("attachments")
    quick_reply = message.get("quick_reply")

    seq_id = sender_id + ':' + recipient_id
    if USER_SEQ.get(seq_id, -1) >= seq:
        print("Ignore duplicated request")
        return None
    else:
        USER_SEQ[seq_id] = seq

    if quick_reply:
        quick_reply_payload = quick_reply.get('payload')
        print("quick reply for message %s with payload %s" % (message_id, quick_reply_payload))

        page.send(sender_id, "Quick reply tapped")

    if message_text:
        send_message(sender_id, message_text)
    elif message_attachments:
        page.send(sender_id, "Message with attachment received")


@page.handle_delivery
def received_delivery_confirmation(event):
    delivery = event.delivery
    message_ids = delivery.get("mids")
    watermark = delivery.get("watermark")

    if message_ids:
        for message_id in message_ids:
            print("Received delivery confirmation for message ID: %s" % message_id)

    print("All message before %s were delivered." % watermark)


@page.handle_postback
def received_postback(event):
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_postback = event.timestamp

    payload = event.postback_payload

    print("Received postback for user %s and page %s with payload '%s' at %s"
          % (sender_id, recipient_id, payload, time_of_postback))

    page.send(sender_id, "Postback called")


@page.handle_read
def received_message_read(event):
    watermark = event.read.get("watermark")
    seq = event.read.get("seq")

    print("Received message read event for watermark %s and sequence number %s" % (watermark, seq))


@page.handle_account_linking
def received_account_link(event):
    sender_id = event.sender_id
    status = event.account_linking.get("status")
    auth_code = event.account_linking.get("authorization_code")

    print("Received account link event with for user %s with status %s and auth code %s "
          % (sender_id, status, auth_code))


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


