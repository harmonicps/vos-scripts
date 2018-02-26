#!/usr/bin/env python

import requests
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

session = requests.Session()

urls = ["https://vos-ms.herokuapp.com",
        "https://www.salesforce.com",
        "https://www.google.com"]



for url in urls:
    t = 1
    print "Testing URL %s" %url
    for n in range(10):
        try:
            req = session.get(url)
        except requests.exceptions.ConnectionError:
            req.status_code = "Connection Error"
        #if not req.status_code == 200:
        print " %d retry code %s" %(t,req.status_code)
        req.connection.close()
        time.sleep(1)
        t+=1
