import socket
import time
import numpy as np
import  struct
class NSdata:
    def __init__(self):
        self.ip = 'localhost'
        self.port = 9889
        self.NSocket = socket.socket()
    def StartData(self):
        self.NSocket.connect((self.ip, self.port))
        #send command to get basic information
        self.SendCommandToNS(3,5)
        time.sleep(0.04)
        #get basic information
        self.BasicInfo = self.NSocket.recv(100)
        ID = str(self.BasicInfo[0:4], encoding='utf-8')
        Code = int.from_bytes(self.BasicInfo[4:6],byteorder='big')
        req = int.from_bytes(self.BasicInfo[6:8],byteorder='big')
        size = int.from_bytes(self.BasicInfo[8:12],byteorder='big')
        if(Code == 1 and req == 3 and size == 28and len(self.BasicInfo) == 40):
            self.Bsize = int.from_bytes(self.BasicInfo[12:16],byteorder='little')
            self.BEegChannelNum= int.from_bytes(self.BasicInfo[16:20],byteorder='little')
            self.BEventChannelNum = int.from_bytes(self.BasicInfo[20:24],byteorder='little')
            self.BlockPnts = int.from_bytes(self.BasicInfo[24:28],byteorder='little')
            self.BSampleRate = int.from_bytes(self.BasicInfo[28:32],byteorder='little')
            self.BDataSize = int.from_bytes(self.BasicInfo[32:36],byteorder='little')
            self.BResolution = struct.unpack('<f',self.BasicInfo[36:40])
            self.FirstData = 0
        self.SendCommandToNS(2,1)
        self.SendCommandToNS(3,3)
        while (1):
            data_head = self.NSocket.recv(12)
            if (len(data_head) != 0):
                break
        chId = str(data_head[0:4], encoding='utf-8')
        #print(chId)
        Code = int.from_bytes(data_head[4:6], byteorder='big')
       # print(Code)
        Request = int.from_bytes(data_head[6:8], byteorder='big')
       # print(Request)
        size = int.from_bytes(data_head[8:12], byteorder='big')
        #print(size)
    def SendCommandToNS(self,ctrcode,reqnum):
        a = 'CTRL'
        Cmd = a.encode(encoding="utf-8")
        temp = (ctrcode).to_bytes(2, 'big')
        Cmd = Cmd + temp
        temp = (reqnum).to_bytes(2, 'big')
        Cmd = Cmd + temp
        temp = (0).to_bytes(4, 'big')
        Cmd = Cmd + temp
        self.NSocket.sendall(Cmd)
    def ReadNSdata(self,):
        while(1):
            data_head = self.NSocket.recv(12)
            if(len(data_head) != 0):
                break
        chId = str(data_head[0:4], encoding='utf-8')
        print(chId)
        Code = int.from_bytes(data_head[4:6],byteorder='big')
        print(Code)
        Request = int.from_bytes(data_head[6:8],byteorder='big')
        print(Request)
        size = int.from_bytes(data_head[8:12],byteorder='big')
        print(size)
        total = 0
        while(total < size):
            a = self.NSocket.recv(size -total)
            if (self.FirstData == 0):
                self.FirstData = 1
                self.Data = a
            else:
                self.Data = self.Data + a
            total = total + len(a)

    def TransToRealData(self):
        self.temp1 = np.empty(len(self.Data) // self.BDataSize)
        temp2 = np.empty(len(self.Data) // self.BDataSize)
        #self.temp1 = struct.unpack('<i',self.Data)
        n = 0
        i = 0
        if(self.BDataSize == 2):
            while (n < len(self.Data)):
                self.temp1[i] =struct.unpack('<h',self.Data[n:n+2])[0]
                temp2[i] = self.temp1[i]* self.BResolution[0] / 1000000
                i = i + 1
                n = n + self.BDataSize
        elif(self.BDataSize == 4):
            while (n <  len(self.Data)):
                #self.temp1[i] = int.from_bytes(self.Data[n:n + self.BDataSize], 'big')
                self.temp1[i] = struct.unpack('<i',self.Data[n:n+4])[0]
                temp2[i] = self.temp1[i] * self.BResolution[0]
                i = i + 1
                n = n + self.BDataSize

        self.Real_Data = np.reshape(temp2,((len(self.Data) // self.BDataSize//(self.BEegChannelNum + self.BEventChannelNum)),(self.BEegChannelNum + self.BEventChannelNum)))

    def StopTransport(self):
        self.SendCommandToNS(3, 4)
        self.SendCommandToNS(2, 2)
        self.SendCommandToNS(1, 2)

obj = NSdata()
obj.StartData()
n =2000
i = 0
while(i < n):
    obj.ReadNSdata()
    i =i + 1
obj.StopTransport()
obj.TransToRealData()
np.savetxt('data1.csv', obj.Real_Data, delimiter=',')









