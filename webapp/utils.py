from django.core.mail import EmailMessage
import requests
from django.http import JsonResponse
import json
from django.urls import reverse
from businessapp.models import *
from urllib.parse import quote
import threading


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()
    @staticmethod
    def send_email1(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()
    @staticmethod
    def shopmessage(mobile,inquiryid):
      
   
      inquirys=Inquiry_from.objects.filter(id=inquiryid).first()
      name=inquirys.name
      ph=inquirys.ph
      print('okk667',mobile)
      url = "https://www.fast2sms.com/dev/bulkV2"
      payload = "sender_id=ARNDM&message=164498&variables_values="+str(name)+"|"+str(ph)+"&route=dlt&numbers="+str(mobile)
      headers = {
          'authorization': "NksBYWlf6KEqMCtxdwJXvSDpQ4ZPjV1AhLeru3zinm8ybo9RHGkJ3VZcs6lI80DaRxriq2tufdMpvO59",
           'Content-Type': "application/x-www-form-urlencoded",
          'Cache-Control': "no-cache",
                       }
      requests.request("POST", url, headers=headers, data=payload)
      return JsonResponse({'name':name})

    @staticmethod
    def inquirymessage(mobile,location,category,inquiryid):

      # original_url=f"https://www.aroundme.co.in/{location}/{category}/"
      # print('-----url',original_url)
      # short_url_obj, created = ShortenedURL.objects.get_or_create(original_url=original_url)
      # short_urls=short_url_obj.short_url
      urls=f"https://arnm.in/{location}/{category}/"
      print('urls',urls)
      # urls=f"https://www.aroundme.co.in/{short_urls}"
    
      inquirys=Inquiry_from.objects.get(id=inquiryid)
      name=inquirys.name
  
      print('okk667',mobile)
      
      url = "https://www.fast2sms.com/dev/bulkV2"
      payload = {
         "sender_id": "ARNDM",
          "message": "164499",
         "variables_values": f"{name}|{category}|{urls}",
         "route": "dlt",
         "numbers": str(mobile),
       }
      headers = {
          'authorization': "NksBYWlf6KEqMCtxdwJXvSDpQ4ZPjV1AhLeru3zinm8ybo9RHGkJ3VZcs6lI80DaRxriq2tufdMpvO59",
           'Content-Type': "application/x-www-form-urlencoded",
          'Cache-Control': "no-cache",
                       }
      requests.request("POST", url, headers=headers, data=payload)
      return JsonResponse({'urls':urls})
