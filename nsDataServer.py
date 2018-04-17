import socket
import struct
import time

import numpy as np

from DataServer import *


class nsDataServer(DataServer):
    def __init__(self, parent):
        super(nsDataServer, self).__init__(parent)
        self.ip = 'localhost'
        self.port = 9889
        self.NSocket = socket.socket()
        self.NSocket.settimeout(15)

    def onConnect(self):
        try:
            self.NSocket.connect((self.ip, self.port))
        except Exception as e:
            print(e.strerror)
            print("Data Server Connection Failed")
            self.connected = False
            return
        else:
            print("Data Server Connection Completed")
            self.NSocket.settimeout(None)
            self.connected = True
        self.SendCommandToNS(3, 5)
        time.sleep(0.1)
        # get basic information
        self.BasicInfo = self.NSocket.recv(100)
        ID = str(self.BasicInfo[0:4], encoding='utf-8')
        Code = int.from_bytes(self.BasicInfo[4:6], byteorder='big')
        req = int.from_bytes(self.BasicInfo[6:8], byteorder='big')
        size = int.from_bytes(self.BasicInfo[8:12], byteorder='big')
        if(Code == 1 and
           req == 3 and
           size == 28 and
           len(self.BasicInfo) == 40):
            (self.Bsize, self.BEegChannelNum, self.BEventChannelNum,
             self.BlockPnts, self.BSampleRate, self.BDataSize,
             self.BResolution) = struct.unpack_from('<iiiiiif',
                                                    self.BasicInfo, 12)
            # self.Bsize = int.from_bytes(
            #     self.BasicInfo[12:16], byteorder='little')
            # self.BEegChannelNum = int.from_bytes(
            #     self.BasicInfo[16:20], byteorder='little')
            # self.BEventChannelNum = int.from_bytes(
            #     self.BasicInfo[20:24], byteorder='little')
            # self.BlockPnts = int.from_bytes(
            #     self.BasicInfo[24:28], byteorder='little')
            # self.BSampleRate = int.from_bytes(
            #     self.BasicInfo[28:32], byteorder='little')
            # self.BDataSize = int.from_bytes(
            #     self.BasicInfo[32:36], byteorder='little')
            # self.BResolution = struct.unpack(
            #     '<f', self.BasicInfo[36:40])[0]

            self.pattern = '<h' if self.BDataSize == 2 else '<i'
            self.channelNum = self.BEegChannelNum + self.BEventChannelNum
            self.T = self.BlockPnts / self.BSampleRate
            self.sampleRate = self.BSampleRate
        self.SendCommandToNS(2, 1)
        self.SendCommandToNS(3, 3)
        data_head = self.NSocket.recv(12)
        chId = str(data_head[0:4], encoding='utf-8')
        Code = int.from_bytes(data_head[4:6], byteorder='big')
        Request = int.from_bytes(data_head[6:8], byteorder='big')
        size = int.from_bytes(data_head[8:12], byteorder='big')

    def onDataRead(self):
        if(not self.connected):
            return
        try:
            timeout = True
            for i in range(5):
                data_head = self.NSocket.recv(12)
                if (len(data_head) == 12):
                    timeout = False
                    break
                time.sleep(0.002)
            if timeout:
                raise TimeoutError(1, 'Data Read Time Out')
        except Exception as e:
            print(e.strerror)
            return
        chId = str(data_head[0:4], encoding='utf-8')
        Code = int.from_bytes(data_head[4:6], byteorder='big')
        Request = int.from_bytes(data_head[6:8], byteorder='big')
        size = int.from_bytes(data_head[8:12], byteorder='big')
        print("Receive Data Size:", size)
        data = bytearray()
        while(len(data) < size):
            data += self.NSocket.recv(size - len(data))
        data = [i[0]*self.BResolution
                for i in struct.iter_unpack(self.pattern, data)]
        self.signalList += [data[i: i+self.channelNum]
                            for i in range(0, len(data), self.channelNum)]

    def onDisconnect(self):
        if not self.connected:
            return
        self.SendCommandToNS(3, 4)
        self.SendCommandToNS(2, 2)
        self.SendCommandToNS(1, 2)
        time.sleep(0.1)
        self.NSocket.close()
        self.connected = True
        self.timestamp = np.arange(len(self.signalList))*self.samplePeriod

    def SendCommandToNS(self, ctrcode, reqnum):
        a = 'CTRL'
        Cmd = a.encode(encoding="utf-8")
        Cmd += (ctrcode).to_bytes(2, 'big')
        Cmd += (reqnum).to_bytes(2, 'big')
        Cmd += (0).to_bytes(4, 'big')
        self.NSocket.sendall(Cmd)

    def getSignal(self):
        return np.array(self.signal)
