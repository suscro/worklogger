#!/usr/bin/python3

import gi
import threading
import os
import datetime

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk
from gi.repository import AppIndicator3 as AppIndicator
from os.path import expanduser

STORAGE_DIR = ".worklog"

STOPPED_ICON = Gtk.STOCK_STOP
STARTED_ICON = Gtk.STOCK_OK

HOME = expanduser("~")
STORAGE_PATH = "/".join((HOME, STORAGE_DIR))

class Worklogger:

    def __init__(self):
        self.indicator = Indicator(self.start, self.stop, self.quit)
        self.logger = Logger()
        self.timer = Timer(self.logger.ping)

    def run(self):
        ask = AskWindow()
        ask.ask()
        if ask.shouldStart():
            self.start()
        else:
            self.stop()

        self.indicator.show()

    def start(self):
        self.indicator.start()
        self.timer.start()

    def stop(self):
        self.indicator.stop()
        self.timer.stop()

    def quit(self):
        self.stop()
        Gtk.main_quit()

class Indicator:

    def __init__(self, start_callback, stop_callback, quit_callback):
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.quit_callback = quit_callback

        self.item = ReplacableMenuItem('Start', self._start)

        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self._quit)

        self.menu = Gtk.Menu()
        self.menu.append(self.item)
        self.menu.append(item_quit)
        self.menu.show_all()

        self.indicator = AppIndicator.Indicator.new('Worklogger', STOPPED_ICON, AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(AppIndicator.IndicatorStatus.PASSIVE)
        self.indicator.set_menu(self.menu)
        self.indicator.set_title("Worklogger")

    def show(self):
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

    def start(self):
        self.item.replace('Stop', self._stop)
        self.indicator.set_icon(STARTED_ICON)

    def stop(self):
        self.item.replace('Start', self._start)
        self.indicator.set_icon(STOPPED_ICON)

    def _start(self, source):
        self.start_callback()

    def _stop(self, source):
        self.stop_callback()

    def _quit(self, source):
        self.quit_callback()

class ReplacableMenuItem(Gtk.MenuItem):

    def __init__(self, label, callback):
        Gtk.MenuItem.__init__(self, label)
        self.handler = self.connect('activate', callback)

    def replace(self, label, callback):
        self.disconnect(self.handler)
        self.set_label(label)
        self.handler = self.connect('activate', callback)

class Timer:

    def __init__(self, callback):
        self.event = threading.Event()
        self.callback = callback
        self.thread = None

    def start(self):
        if self.thread is not None:
            self.stop()

        self.thread = threading.Thread(target = self.run)
        self.thread.start()

    def stop(self):
        if self.thread is not None:
            self.event.set()
            self.thread.join()

        self.event.clear()
        self.thread = None

    def run(self):
        run = True
        while run:
            run = not self.event.wait(3)
            self.callback()

class Logger:

    def __init__(self):
        self.last = None

    def ping(self):
        now = datetime.datetime.now().replace(second = 0, microsecond = 0)
        if (self.last is None) or (self.last != now):
            self.last = now
            self.log()

    def log(self):
        dir_name = "/".join((STORAGE_PATH, str(self.last.year), str(self.last.month))) + "/"
        self.make_path(dir_name)

        log_file = open(dir_name + str(self.last.day), "a+")
        log_file.write(self.last.strftime("%H:%M\n"))
        log_file.close()

    def make_path(self, dir_name):
        folder = os.path.dirname(dir_name)
        if not os.path.exists(folder):
            os.makedirs(folder)

class AskWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Kul Worklog")
        self.response = False
        self.dialog = AskDialog(self)

    def ask(self):
        self.dialog.show_all()
        self.response = self.dialog.run()
        self.dialog.destroy()
        self.destroy()

    def shouldStart(self):
        return self.response == Gtk.ResponseType.OK

class AskDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Kul Worklog", parent, 0,
                            (Gtk.STOCK_NO, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_YES, Gtk.ResponseType.OK))

        self.set_default_size(250, 100)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_urgency_hint(True)
        self.set_keep_above(True)

        label = Gtk.Label("Rozpocząć pracę?")

        box = self.get_content_area()
        box.add(label)

if __name__ == "__main__":
    worklogger = Worklogger()
    worklogger.run()
    Gtk.main()
