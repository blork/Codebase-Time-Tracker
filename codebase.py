#!/usr/bin/env python
import urllib2
import base64
import BaseHTTPServer
import time
import sys
import math
import json

project = "2011-eltcwas"
base_url = "http://api3.codebasehq.com"
sessions_url = base_url + "/" + project + "/time_sessions"


xml_template = """
<time-session>
  <summary>{0}</summary>
  <minutes type="integer">{1}</minutes>
</time-session>
"""


def main():
    try:
        userdata = json.load(open("userdata.json"))
        username = userdata["username"]
        key = userdata["key"]
        if username == "" or key == "":
            raise
    except:
        sys.exit("Misconfigured. Edit userdata.json.")

    while True:
        task_name = raw_input("Enter a task summary: ")

        start = time.time()
        raw_input("Press any key when complete.")

        time_spent = int(math.ceil((time.time() - start) / 60))

        print "You spend {0} minutes on that task.".format(time_spent)
        upload = True if raw_input("Upload to Codebase? Y/N ").lower() == "y" else False

        if upload:
            xml = xml_template.format(task_name, time_spent)

            req = urllib2.Request(url=sessions_url, data=xml)

            base64string = base64.encodestring('%s:%s' % (username, key)).replace('\n', '')
            authheader = "Basic %s" % base64string

            req.add_header("Authorization", authheader)
            req.add_header("Content-type", "application/xml")
            req.add_header("Accept", "application/xml")

            try:
                urllib2.urlopen(req)
                print "Uploaded."
            except IOError, e:
                if hasattr(e, 'code'):
                    print "There was an error."
                    print BaseHTTPServer.BaseHTTPRequestHandler.responses[e.code]


if __name__ == "__main__":
    main()
