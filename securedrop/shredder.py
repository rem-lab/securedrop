# -*- coding: utf-8 -*-
#
# SecureDrop whistleblower submission system
# Copyright (C) 2017 Loic Dachary <loic@dachary.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import inotify_simple
import logging
import os
import sh
import subprocess
import threading

log = logging.getLogger(__name__)


class Shredder(object):

    def __init__(self, dir):
        self.dir = dir
        self.thread = None

    def start(self):
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

        if self.thread:
            return False
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()
        return True

    def stop(self):
        if not self.thread:
            return False
        self.stop_event.set()
        open(os.path.join(self.dir, '_REMOVE_ME_'), 'w').close()
        self.thread.join()
        self.thread = None
        return True

    def rm(self, path):
        base = os.path.basename(path)
        dest = os.path.join(self.dir, base)
        log.debug("mv {} {}".format(path, dest))
        os.rename(path, dest)

    def shred(self):
        log.debug("shred {}".format(self.dir))
        for f in os.listdir(self.dir):
            try:
                sh.sh("srm -v -r {}".format(os.path.join(self.dir, f)))
            except subprocess.CalledProcessError:
                log.error("error ignored, proceeding")

    def loop(self):
        i = inotify_simple.INotify()
        i.add_watch(
            self.dir,
            inotify_simple.flags.CREATE | inotify_simple.flags.MOVED_TO)
        while True:
            self.shred()
            if self.stop_event.is_set():
                break
            log.debug("inotify waiting ...")
            events = i.read()
            log.debug("... inotify woke up {}".format(events))
        i.close()
