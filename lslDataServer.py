import numpy as np
from pylsl import StreamInlet, resolve_stream

from DataServer import *


class lslDataServer(DataServer):
    def __init__(self, parent):
        super(lslDataServer, self).__init__(parent)

    def onConnect(self):
        eegStream = resolve_stream('type', 'signal')[0]
        self.signal = np.ndarray((eegStream.channel_count(), 0))
        self.eegInlet = StreamInlet(eegStream)

    def onDataRead(self):
        sample, timestamp = self.eegInlet.pull_chunk()
        if(len(sample) == 0):
            return
        npsample = np.array(sample).transpose()
        print(self.signal.shape, npsample.shape)
        self.signal = np.concatenate((self.signal, npsample), axis=1)
        self.timestamp.extend(timestamp)
        print("got %s at time %s" % (len(sample), len(timestamp)))

    def onDisconnect(self):
        for stream in self.eegInlets:
            stream.close_stream()
