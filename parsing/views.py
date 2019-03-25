from django.shortcuts import render
from django.http import HttpResponse
from wit import Wit

# Create your views here.

def parse(self):
    access_token = '2NH6NQG7FNEFPKHEBPKTWLPD4LJFECXX';
    client = Wit(access_token)
    resp = client.message('Who is Waseem')
    print(resp)
    return HttpResponse(str('Hey Thanks for Contacting Sargodha Computers.'))