import requests
from django.http import JsonResponse
import json
def shopmessage(mobile):
    print('okk',mobile)
    url = "https://www.fast2sms.com/dev/bulkV2"
    urls="4566777"
    payload = "sender_id=ARNDM&message=161987&variables_values=User|"+(urls)+"&route=dlt&numbers="+str(mobile)
    headers = {
          'authorization': "NksBYWlf6KEqMCtxdwJXvSDpQ4ZPjV1AhLeru3zinm8ybo9RHGkJ3VZcs6lI80DaRxriq2tufdMpvO59",
           'Content-Type': "application/x-www-form-urlencoded",
          'Cache-Control': "no-cache",
                       }
    requests.request("POST", url, headers=headers, data=payload)
    return JsonResponse({'urls':urls})
