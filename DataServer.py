import sched
import threading
from time import monotonic, sleep, clock, strftime

import numpy as np


class DataServer:
    def __init__(self, parent):
        self.setParent(parent)
        self.sche = sched.scheduler()
        self.sche.enter(0, 1, self.onSched)
        self.thread = threading.Thread(target=self.sche.run)
        self.connected = False
        self.startTime = 0
        self.sampleRate = 500
        self.samplePeriod = 0.002
        self.signal = np.empty(0)
        self.signalList = []
        self.mark = np.empty(0)
        self.markList = []
        self.timestamp = np.empty(0)
        self.timestampList = []
        self.setReady()
        self.setProcess()
        self.setFinish()
        self.setStimBeginTS()

    def setParent(self, parent):
        self.parent = parent
        self.parent.setDataServer(self)

    def onSched(self):
        now = monotonic()
        self.sche.enterabs(now+self.T, 1, self.onSched)
        try:
            self.onDataRead()
        except Exception as e:
            print(e.strerror)
        self.endTime = clock()
        self.onProcess(self)
        self.timestamp = np.concatenate(
            (self.timestamp, np.arange(self.endTime)))

    def configure(self, frez=16):
        self.T = 1.0/frez

    def start(self):
        self.onConnect()
        if(self.connected):
            print('Data Server Ready')
        self.onReady(self)
        self.startTime = clock()
        self.thread.start()

    def stop(self):
        for i in self.sche.queue:
            self.sche.cancel(i)
        self.onFinish(self)
        if self.connected:
            self.onDisconnect()
        print('Data Server Disconnected')
        self.thread.join()

    def onConnect(self):
        pass

    def onDataRead(self):
        pass

    def onDisconnect(self):
        pass

    def onStim(self, code, duration=0, timestamp=None):
        if timestamp is None:
            timestamp = clock()
        self.markList.append([timestamp, code, duration])

    def setReady(self, func=lambda x: None):
        self.onReady = func

    def setProcess(self, func=lambda x: None):
        self.onProcess = func

    def setFinish(self, func=lambda x: None):
        self.onFinish = func

    def setSampleRate(self, rate):
        self.sampleRate = rate
        self.samplePeriod = 1.0/rate

    def setSamplePeriod(self, period):
        self.samplePeriod = period
        self.sampleRate = int(1.0/period)

    def setStimBeginTS(self):
        self.stimBeginTS = clock()

    def saveData(self):
        self.mark = np.array(self.markList)
        self.mark[:, 0] -= self.startTime
        self.signal = np.array(self.signalList)
        np.savez(strftime("NSsignal_%Y_%m_%d_%H_%M_%S"),
                 signal=self.signal, mark=self.mark, timestamp=self.timestamp)
