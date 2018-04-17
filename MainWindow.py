import wx

from Graz import *
from nsDataServer import *
from lslDataServer import *
from MIStimCfgDlg import *
from SignalMonitor import *


class MainWindow(wx.Frame):
    def __init__(self):
        super(MainWindow, self).__init__(None, title="Main", size=(480, 640))
        self.initUI()

        self.stimCfgDlg = MIStimCfgDlg(self)
        self.dataServer = None
        self.monitor = SignalMonitor(self)

    def initUI(self):
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE & ~(
            wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        panel = wx.Panel(self)
        vs = wx.BoxSizer(wx.VERTICAL)

        bs = wx.BoxSizer(wx.HORIZONTAL)
        self.MIBtn = wx.Button(
            panel, label="Graz Configure", size=wx.Size(72, 36))
        self.MIBtn.Bind(wx.EVT_BUTTON, self.onMIBtn)
        self.BeginBtn = wx.Button(
            panel, label="Launch", size=wx.Size(72, 36))
        self.BeginBtn.Bind(wx.EVT_BUTTON, self.onBeginBtn)
        self.QuitBtn = wx.Button(
            panel, label="Quit", size=wx.Size(72, 36))
        self.QuitBtn.Bind(wx.EVT_BUTTON, self.onQuitBtn)

        bs.Add(self.MIBtn)
        bs.Add(self.BeginBtn)
        bs.Add(self.QuitBtn)
        vs.Add(bs)

        bs = wx.BoxSizer(wx.HORIZONTAL)
        self.StartBtn = wx.Button(
            panel, label="Start", size=wx.Size(72, 36))
        self.StartBtn.Bind(wx.EVT_BUTTON, lambda x: self.monitor.run())
        self.StopBtn = wx.Button(
            panel, label="Stop", size=wx.Size(72, 36))
        self.StopBtn.Bind(wx.EVT_BUTTON, lambda x: self.monitor.stop())
        bs.Add(self.StartBtn)
        bs.Add(self.StopBtn)
        vs.Add(bs)
        panel.SetSizer(vs)

    def onMIBtn(self, event):
        self.stimCfgDlg.ShowModal()

    def onBeginBtn(self, event):
        if self.graz:
            del(self.graz)
        self.dataServer = nsDataServer(self)
        self.graz = Graz(self)
        config = self.stimCfgDlg.stimConfig
        self.stim = MIStimulator(self.graz,
                                 first_class=config['firstClass'],
                                 first_class_number=config['firstClassNum'],
                                 second_class=config['secondClass'],
                                 second_class_number=config['secondClassNum'],
                                 baseline_duration=config['baseline'],
                                 wait_for_cue_duration=config['waitCue'],
                                 display_cue_duration=config['dispCue'],
                                 feedback_duration=config['feedback'])
        msg = "Graz Stimulator is Ready!\n" + \
            "Total Time of the Session is: " + \
            str(self.stim.T)+"s\n"+"Start Now?"
        style = wx.OK | wx.CANCEL | wx.CENTRE
        msgbox = wx.MessageDialog(self, msg, "Experiment is Ready", style)
        if(msgbox.ShowModal() == wx.ID_OK):
            self.graz.Show()
            if self.dataServer:
                self.dataServer.configure()
                if(not self.dataServer.connected):
                    self.dataServer.start()
            self.graz.startStim()
        else:
            return

    def onQuitBtn(self, event):
        self.Close()

    def setDataServer(self, dataServer=None):
        self.dataServer = dataServer

    def grazFinish(self):
        if self.dataServer:
            self.dataServer.stop()
            print('Saving Signal...')
            self.dataServer.saveData()
            print('Signal Saved')
