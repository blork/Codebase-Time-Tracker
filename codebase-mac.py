from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper
import time
import sys
import json
import math
import urllib2
import base64
import BaseHTTPServer

project = "2011-eltcwas"
base_url = "http://api3.codebasehq.com"
sessions_url = base_url + "/" + project + "/time_sessions"
username = ""
key = ""

xml_template = """
<time-session>
  <summary>{0}</summary>
  <minutes type="integer">{1}</minutes>
</time-session>
"""

status_images = {'idle': 'clock.png'}


class Alert(object):

    def __init__(self, messageText):
        super(Alert, self).__init__()
        self.messageText = messageText
        self.informativeText = ""
        self.buttons = []
        self.accessory = None
        self.alertstyle = NSInformationalAlertStyle

    def displayAlert(self):
        alert = NSAlert.alloc().init()
        alert.setMessageText_(self.messageText)
        alert.setInformativeText_(self.informativeText)
        alert.setAlertStyle_(self.alertstyle)

        if self.accessory is not None:
            alert.setAccessoryView_(self.accessory)

        for button in self.buttons:
            alert.addButtonWithTitle_(button)

        NSApp.activateIgnoringOtherApps_(True)
        self.buttonPressed = alert.runModal()


def ask(message="Default Message", info_text="", buttons=["OK"]):
    ap = Alert(message)
    ap.informativeText = info_text
    ap.buttons = buttons
    input = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 0, 200, 24))
    input.setStringValue_("")
    ap.accessory = input
    ap.displayAlert()
    return ap.accessory.stringValue()


def alert(message="Default Message", info_text="", buttons=["OK"]):
    ap = Alert(message)
    ap.informativeText = info_text
    ap.buttons = buttons
    ap.alertstyle = NSCriticalAlertStyle
    ap.displayAlert()
    return ap.buttonPressed


class Timer(NSObject):
    images = {}
    statusbar = None
    state = 'idle'
    newitem = None
    stopitem = None
    start_time = time.time()
    task_name = ""

    def applicationDidFinishLaunching_(self, notification):
        statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
        for i in status_images.keys():
            self.images[i] = NSImage.alloc().initByReferencingFile_(status_images[i])
        self.statusitem.setImage_(self.images['idle'])
        self.statusitem.setHighlightMode_(1)
        self.statusitem.setToolTip_('New Task')

        self.menu = NSMenu.alloc().init()
        self.newitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('New Task...', 'task:', '')
        self.menu.insertItem_atIndex_(self.newitem, 0)
        menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
        self.menu.insertItem_atIndex_(menuitem, 1)
        self.stopitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Finish Task', 'finish:', '')

        self.statusitem.setMenu_(self.menu)

    def task_(self, notification):
        self.task_name = ask("New Task", "Enter a task description:", ["OK"])
        if self.task_name == "":
            return
        self.timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(
             NSDate.date(),
             1.0,
             self,
             'display:',
             None,
             True
        )
        NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer, NSDefaultRunLoopMode)
        self.timer.fire()

        self.start_time = time.time()
        self.menu.removeItem_(self.newitem)
        self.menu.insertItem_atIndex_(self.stopitem, 0)

    def display_(self, notification):
        seconds = time.time() - self.start_time
        minutes = seconds // 60
        seconds %= 60
        elapsed = "%02i:%02i" % (minutes, seconds)
        self.statusitem.setTitle_("{0}: {1}".format(self.task_name, elapsed))

    def upload(self):
        time_spent = int(math.ceil((time.time() - self.start_time) / 60))

        xml = xml_template.format(self.task_name, time_spent)

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
            message = "Try again later."
            if hasattr(e, 'code'):
                message = BaseHTTPServer.BaseHTTPRequestHandler.responses[e.code][1], ["OK"]
            alert("There was an error uploading to Codebase", message)

    def finish_(self, notification):
        self.upload()
        self.menu.removeItem_(self.stopitem)
        self.menu.insertItem_atIndex_(self.newitem, 0)
        self.timer.invalidate()
        self.statusitem.setTitle_("")


if __name__ == "__main__":
    print sys.path[0]
    try:
        userdata = json.load(open("userdata.json"))
        username = userdata["username"]
        key = userdata["key"]
        if username == "" or key == "":
            raise
    except Exception as e:
        username = ask("New Account", "Enter your Codebase API Username:", ["OK"])
        key = ask("New Account", "Enter your Codebase API Key:", ["OK"])
        json.dump({"username": username, "key": key}, open("userdata.json", "w+"))

    app = NSApplication.sharedApplication()
    delegate = Timer.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()
