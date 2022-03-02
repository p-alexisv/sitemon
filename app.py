#!/usr/local/bin/python3

import requests
import time
import os
from datetime import datetime
from prometheus_client import start_http_server, Gauge

def getstat(u):
    up = 0
    response_ms = -1
    code = -1
    try:
        con = requests.get(u)
    except Exception as inst:
        log("Exception: >%s<! %s" % (u, inst))
    else:
        code = con.status_code
        if code == 200:
            up = 1
        else:
            up = 0
        elapsed = con.elapsed
        response_ms = elapsed.microseconds * .001
    return up, response_ms, code

def log(l):
    try:
        l = str(l)
    except:
        return -1
    dtnow = datetime.now().astimezone().strftime("%c %z")
    print("%s %s" % (dtnow, l))
    return 0

def getsettings():
    listenport = ""
    urls = []
    interval = 60
    # Get TCP port number, from SITEMON_METRICSPORT envar
    listenport = int(os.environ["SITEMON_METRICSPORT"])
    if (listenport < 1024 or listenport > 49151):
        raise ValueError('Invalid port number')
    urls = os.environ["SITEMON_URLS"].split(",")
    if (len(urls) < 1 or urls[0] == ""):
        raise ValueError('Invalid URLs')
    try:
        interval = int(os.environ["SITEMON_INTERVAL"])
    except:
        pass
    return listenport, urls, interval

def main():
    # Get settings
    listenport, urls, interval = getsettings()
    log("Settings: { port : %s, urls : %s, interval : %s }" % (listenport, urls, interval))
    # Start up the server to expose the metrics.
    start_http_server(listenport)
    log("http_server started.")
    # Create the metrics
    g_up = Gauge('sample_external_url_up', 'External URL is up', ['url'])
    g_response = Gauge('sample_external_url_response_ms', 'External URL response time in milliseconds', ['url'])
    log("metrics created.")
    # loop forever
    while True:
        for u in urls:
            up, response_ms, code = getstat(u)
            log("URL:%s Up:%s ResponseTime:%s HTTPCode:%s" % (u, up, response_ms, code))
            g_up.labels(url=u).set(up)
            g_response.labels(url=u).set(response_ms)
        time.sleep(interval)
    return 0
            
if __name__ == "__main__":
    main()
