#!/usr/bin/python3

"""
   Copyright 2019 Suscro

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import gi
import threading
import os
import datetime

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk
from gi.repository import AppIndicator3 as AppIndicator
from os.path import expanduser
from datetime import timedelta

STORAGE_DIR = ".worklog"

STOPPED_ICON = Gtk.STOCK_STOP
STARTED_ICON = Gtk.STOCK_OK

HOME = expanduser("~")
STORAGE_PATH = "/".join((HOME, STORAGE_DIR))

class Worklogger:

    def __init__(self):
        self.indicator = Indicator(self.start, self.stop, self.quit)
        self.logger = Logger()
        self.timer = Timer(self.ping)

    def run(self):
        ask = AskWindow()
        ask.ask()
        if ask.shouldStart():
            self.start()
        else:
            self.stop()

        self.logger.start()
        self._update()
        self.indicator.show()

    def start(self):
        self.logger.start()
        self.indicator.start()
        self.timer.start()

    def ping(self):
        self.logger.ping()
        self._update()

    def _update(self):
        self.indicator.label(str(timedelta(minutes=self.logger.workedToday()))[:-3])

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

    def label(self, label):
        self.indicator.set_label(label, label)

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
        self.workedMinutes = 0

    def start(self):
        now = datetime.datetime.now()
        dir_name = self._dir_name(now)
        file_name = self._file_name(dir_name, now)
        if not os.path.exists(file_name):
            self.workedMinutes = 0
        else:
            day_file = open(file_name, 'r')
            lines = set()
            last = None
            for line in day_file:
                lines.add(line)
                last = line
            self.workedMinutes = len(lines)
            if not last is None:
                self.last = datetime.datetime(now.year, now.month, now.day, int(last[0:2]), int(last[3:5]))

    def workedToday(self):
        return self.workedMinutes

    def ping(self):
        now = datetime.datetime.now().replace(second = 0, microsecond = 0)
        if (self.last is None) or (self.last != now):
            self.last = now
            self.workedMinutes = self.workedMinutes + 1
            self._log()

    def _log(self):
        dir_name = self._dir_name(self.last)

        log_file = open(self._file_name(dir_name, self.last), "a+")
        log_file.write(self.last.strftime("%H:%M\n"))
        log_file.close()

    def _file_name(self, dir_name, date):
        return dir_name + str(date.day)

    def _dir_name(self, date):
        dir_name = "/".join((STORAGE_PATH, str(date.year), str(date.month))) + "/"
        self._make_path(dir_name)
        return dir_name

    def _make_path(self, dir_name):
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
