import random
import sched
import socket
import threading

import wx
import wx.adv as wxadv
import wx.lib.newevent

from StimulationsCodes import *

StimEvent, EVT_STIM = wx.lib.newevent.NewEvent()


class Graz(wx.Frame):
    def __init__(self, parent=None):
        super(Graz, self).__init__(parent, title="Graz", size=(1280, 720))
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE & ~(
            wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.SetBackgroundColour(wx.BLACK)
        self.Centre()
        self.Bind(EVT_STIM, self.onStim)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.setStimulator()
        self.setDataServer(self.Parent.dataServer)

        self.dc = wx.ClientDC(self)
        self.SetSize(self.GetSize()*2-self.dc.GetSize())
        self.radio = self.dc.GetSize()[1]/480
        self.centerPoint = wx.Point((self.dc.GetSize()/2).Get())
        self.gifCtrl = wxadv.AnimationCtrl(self)
        self.threadStim = threading.Thread(target=self.Close)

        leftArrow = [wx.Point(i) for i in
                     [(20, 50), (-80, 50), (-80, -50), (20, -50),
                      (20, -100), (120, 0), (20, 100)]]
        rightArrow = [-i for i in leftArrow]
        upArrow = [wx.Point(i.Get()[:: -1]) for i in rightArrow]
        downArrow = [-i for i in upArrow]
        self.arrow = {
            'left': leftArrow,
            'right': rightArrow,
            'up': upArrow,
            'down': downArrow
        }
        self.onStimActions = {
            'OVTK_GDF_Left': (self.drawArrow, 'left'),
            'OVTK_GDF_Right': (self.drawArrow, 'right'),
            'OVTK_GDF_Up': (self.drawArrow, 'up'),
            'OVTK_GDF_Down': (self.drawArrow, 'down'),
            'OVTK_GDF_Cross_On_Screen': (self.drawCross, None),
            'OVTK_GDF_Feedback_Continuous': (self.drawCross, None),
            'OVTK_GDF_End_Of_Trial': (self.clear, None),
            'OVTK_StimulationId_ExperimentStop': (self.displayText,
                                                  '结束'),
            'OVTK_StimulationId_ExperimentStart': (self.displayText,
                                                   '即将开始'),
            'OVTK_StimulationId_BaselineStart': (self.displayText,
                                                 '请放松'),
            'OVTK_StimulationId_BaselineStop': (self.displayText,
                                                '')
        }

    def clear(self):
        self.dc.Clear()
        self.gifCtrl.SetAnimation(wxadv.NullAnimation)
        self.gifCtrl.Hide()

    def drawArrow(self, direction):
        self.dc.SetPen(wx.Pen(wx.RED))
        self.dc.SetBrush(wx.Brush(wx.RED))
        self.dc.DrawPolygon([self.centerPoint+wx.Size(i.x, i.y)*self.radio
                             for i in self.arrow.get(direction, [])])

    def drawCross(self):
        self.clear()
        self.dc.SetPen(wx.Pen(wx.GREEN))
        w = 240 * self.radio
        h = 180 * self.radio
        self.dc.DrawLine(
            self.centerPoint.x, self.centerPoint.y+h,
            self.centerPoint.x, self.centerPoint.y-h)
        self.dc.DrawLine(
            self.centerPoint.x+w, self.centerPoint.y,
            self.centerPoint.x-w, self.centerPoint.y)

    def displayText(self, string=''):
        self.clear()
        self.dc.SetTextForeground(wx.WHITE)
        self.dc.SetFont(wx.Font(wx.FontInfo(48).Bold().FaceName('微软雅黑')))
        self.dc.DrawText(string,
                         self.centerPoint-self.dc.GetTextExtent(string)/2)

    def displayCue(self, path=''):
        img = wx.Bitmap(path, wx.BITMAP_TYPE_BMP)
        self.dc.DrawBitmap(img, self.centerPoint-img.GetSize()/2)

    def displayGif(self, path=''):
        self.gifCtrl.LoadFile(path)
        self.gifCtrl.SetPosition(self.centerPoint-self.gifCtrl.GetSize()/2)
        self.gifCtrl.Show()
        self.gifCtrl.Play()

    def setStimulator(self, stimulator=None):
        self.stimulator = stimulator
        if(self.stimulator):
            self.threadStim = threading.Thread(target=self.stimulator.start)

    def setDataServer(self, dataServer=None):
        self.dataServer = dataServer

    def startStim(self):
        if(self.stimulator):
            print("Graz Begin")
            self.setDataServer(self.Parent.dataServer)
            self.threadStim.start()
            self.clear()

    def onStim(self, evt):
        if(evt.stim == "q_end"):
            self.Close()
            return
        if(evt.stim == "q_begin"):
            self.dataServer.setStimBeginTS()
            return
        print(evt.stim)
        if(self.dataServer):
            code = OpenViBE_stimulation.get(evt.stim, -1)
            if(code != -1):
                self.dataServer.onStim(code)
        action = self.onStimActions.get(evt.stim, None)
        if(action):
            if(action[1]):
                action[0](action[1])
            else:
                action[0]()

    def onClose(self, evet):
        evet.Skip()
        self.Parent.grazFinish()
        self.destroyStimulator()

    def destroyStimulator(self):
        print('Graz is closing')
        if(self.stimulator):
            self.stimulator.stop()
            del(self.stimulator)
            self.setStimulator()
            print('Stimulator Deleted')
        if(self.threadStim.isAlive()):
            self.threadStim.join()
            print("Thread Terminated")


class Stimulator:
    def __init__(self, parent):
        parent.setStimulator(self)
        self.parent = parent
        self.sequence = []
        self.T = 0
        self.length = -1
        self.tagging = False
        self.sche = sched.scheduler()

    def addStim(self, stim, interval=0, during=0):
        self.sequence.append((self.T, stim, interval, during))
        self.T += interval

    def insertStim(self, stim, t=0, during=0):
        self.sequence.append((self.T, stim, interval, during))
        self.T = t

    def waitStim(self, interval=0):
        self.T += interval

    def start(self):
        self.sequence.sort(key=lambda i: i[0])
        if(self.tagging):
            self.tcp.connect((self.host, self.port))
        for i in self.sequence:
            self.sche.enter(i[0], 1, self.emit, argument=(i[1],))
        self.emit('q_begin')
        self.sche.run(True)
        self.emit('q_end')
        if(self.tagging):
            self.tcp.close()

    def emit(self, stim):
        wx.PostEvent(self.parent, StimEvent(stim=stim))
        if(self.tagging):
            b = []
            value = OpenViBE_stimulation[stim]
            self.tcp.sendall(
                bytes([0]*8)+value.to_bytes(8, 'little')+bytes([0]*8))

    def setTcpTagging(self, host='127.0.0.1', port=15361):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tagging = True
        self.host = host
        self.port = port

    def stop(self):
        for i in self.sche.queue:
            self.sche.cancel(i)


def MIStimulator(parent,
                 first_class='OVTK_GDF_Left',
                 first_class_number=5,
                 second_class='OVTK_GDF_Right',
                 second_class_number=5,
                 baseline_duration=1,
                 wait_for_cue_duration=1,
                 display_cue_duration=1,
                 feedback_duration=1
                 ):
    s = Stimulator(parent)

    tasks = []
    tasks += [first_class]*first_class_number
    tasks += [second_class]*second_class_number
    random.shuffle(tasks)

    s.addStim('OVTK_StimulationId_ExperimentStart', 5)
    s.addStim('OVTK_StimulationId_BaselineStart', baseline_duration)
    s.addStim('OVTK_StimulationId_BaselineStop', 5)
    for task in tasks:
        s.addStim('OVTK_GDF_Start_Of_Trial', 0)
        s.addStim('OVTK_GDF_Cross_On_Screen', wait_for_cue_duration)
        s.addStim(task, display_cue_duration)
        s.addStim('OVTK_GDF_Feedback_Continuous', feedback_duration)
        s.addStim('OVTK_GDF_End_Of_Trial', 2)
    s.addStim('OVTK_GDF_End_Of_Session', 5)
    s.addStim('OVTK_StimulationId_Train', 1)
    s.addStim('OVTK_StimulationId_ExperimentStop')

    return s
