#!/usr/bin/env python

import sys
import time
import socket
import threading

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

class Prflr:
    def __init__(self, api_key, source):
        self.addr = ('prflr.org', 4000)
        self.source = source[:32]
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.key = api_key[:32]
        self.timers = {}
        self.lock = threading.RLock()

    def begin(self, timer):
        thread_id = threading.current_thread().ident
        with self.lock:
            if not self.timers.get(thread_id):
                self.timers[thread_id] = {}
            self.timers[thread_id][timer] = time.time()

    def end(self, timer, info=''):
        thread_id = threading.current_thread().ident
        timers = self.timers.get(thread_id)
        if not timers:
            return False
        prev_time = timers.get(timer)
        if not prev_time:
            return False
        spent = round((time.time() - prev_time) * 1000, 3)
        self.send(timer, spent, info, thread_id)
        with self.lock:
            timers.pop(timer)
        return True

    def send(self, timer, time, info, thread_id):
        msg = '|'.join([str(thread_id)[:32],
                        self.source,
                        timer[:48],
                        str(time)[:16],
                        info[:32],
                        self.key])
        if PY3:
            self.socket.sendto(bytes(msg, 'utf-8'), self.addr)
        else:
            self.socket.sendto(msg, self.addr)
