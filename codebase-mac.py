import objc, re, os
import Cocoa
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
import Tkinter
import tkSimpleDialog
import time

status_images = {'idle':'clock.png'}

class Alert(object):
    
    def __init__(self, messageText):
        super(Alert, self).__init__()
        self.messageText = messageText
        self.informativeText = ""
        self.buttons = []
        self.input = None

    def displayAlert(self):
        alert = NSAlert.alloc().init()
        alert.setMessageText_(self.messageText)
        alert.setInformativeText_(self.informativeText)
        alert.setAlertStyle_(NSInformationalAlertStyle)

        self.input = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 0, 200, 24))
        self.input.setStringValue_("default")
        alert.setAccessoryView_(self.input)

        for button in self.buttons:
            alert.addButtonWithTitle_(button)
        NSApp.activateIgnoringOtherApps_(True)
        self.buttonPressed = alert.runModal()
    
def alert(message="Default Message", info_text="", buttons=["OK"]):    
    ap = Alert(message)
    ap.informativeText = info_text
    ap.buttons = buttons
    ap.displayAlert()
    return ap.input.stringValue()

class Timer(NSObject):
    images = {}
    statusbar = None
    state = 'idle'
    newitem = None
    stopitem = None
    start_time = time.time()

    def applicationDidFinishLaunching_(self, notification):
        statusbar = NSStatusBar.systemStatusBar()
        # Create the statusbar item
        self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
        # Load all images
        for i in status_images.keys():
          self.images[i] = NSImage.alloc().initByReferencingFile_(status_images[i])
        # Set initial image
        self.statusitem.setImage_(self.images['idle'])
        # Let it highlight upon clicking
        self.statusitem.setHighlightMode_(1)
        # Set a tooltip
        self.statusitem.setToolTip_('New Task')

        # Build a very simple menu
        self.menu = NSMenu.alloc().init()
        # Sync event is bound to sync_ method
        self.newitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('New Task...', 'task:', '')
        self.menu.insertItem_atIndex_(self.newitem, 0)
        # Default event
        menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
        self.menu.insertItem_atIndex_(menuitem, 1)
        # Bind it to the status item
        self.statusitem.setMenu_(self.menu)

    def task_(self, notification):
        print alert("New Task", "Enter a task description.", ["OK"])
        self.timer =  NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(
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
        self.stopitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Finish Task', 'finish:', '')
        self.menu.insertItem_atIndex_(self.stopitem, 0)

    def finish_(self, notification):
        self.menu.removeItem_(self.stopitem)
        self.menu.insertItem_atIndex_(self.newitem, 0)
        self.timer.invalidate()
        self.statusitem.setTitle_("")

    def display_(self, notification):
        seconds = time.time() - self.start_time
        minutes = seconds // 60
        seconds %= 60
        elapsed = "%02i:%02i" % (minutes, seconds)
        self.statusitem.setTitle_("Task Name: {0}".format(elapsed))



if __name__ == "__main__":

    app = NSApplication.sharedApplication()
    delegate = Timer.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()
    del root