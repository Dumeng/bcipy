import wx


class MIStimCfgDlg(wx.Dialog):
    def __init__(self, parent=None):
        super(MIStimCfgDlg, self).__init__(
            parent, title="Stimulator Configure", size=(480, 640))
        self.Centre()
        self.initUI()
        self.Fit()

        self.stimConfig = {
            "firstClass": "OVTK_GDF_Left",
            "firstClassNum": 10,
            "secondClass": "OVTK_GDF_Right",
            "secondClassNum": 10,
            "baseline": 10,
            "waitCue": 2,
            "dispCue": 4,
            "feedback": 4
        }
        self.updateConfig(self.stimConfig)

        self.Bind(wx.EVT_CLOSE, self.onClose)

    def initUI(self):
        self.DestroyChildren()
        panel = wx.Panel(self)

        gs = wx.FlexGridSizer(cols=2, vgap=10, hgap=10)
        bs = wx.BoxSizer(wx.HORIZONTAL)
        ms = wx.BoxSizer(wx.VERTICAL)
        stimSet = ['OVTK_GDF_Left', 'OVTK_GDF_Right',
                   'OVTK_GDF_Down', 'OVTK_GDF_Up']
        imgWildcard = "Image File (.gif, .bmp, .jpg, .png)" + \
            "|*.gif;*.bmp;*.jpg;*.png"

        self.firstClassCtrl = wx.Choice(
            panel, name="First Class", choices=stimSet)
        label = wx.StaticText(panel)
        label.SetLabel("First Class Stimulation")
        gs.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        gs.Add(self.firstClassCtrl, 0, wx.ALL, 5)

        self.firstClassNumCtrl = wx.SpinCtrl(panel, min=0, max=20)
        label = wx.StaticText(panel)
        label.SetLabel("First Class Stimulation Number")
        gs.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        gs.Add(self.firstClassNumCtrl, 0, wx.ALL, 5)

        self.customFirstClassCtrl = wx.FilePickerCtrl(
            panel, wildcard=imgWildcard)
        label = wx.StaticText(panel)
        label.SetLabel("First Class Custom Cue")
        gs.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        gs.Add(self.customFirstClassCtrl, 0, wx.ALL, 5)

        self.secondClassCtrl = wx.Choice(
            panel, name="Second Class", choices=stimSet)
        label = wx.StaticText(panel)
        label.SetLabel("Second Class Stimulation")
        gs.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        gs.Add(self.secondClassCtrl, 0, wx.ALL, 5)

        self.secondClassNumCtrl = wx.SpinCtrl(panel, min=0, max=20)
        label = wx.StaticText(panel)
        label.SetLabel("Second Class Stimulation Number")
        gs.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        gs.Add(self.secondClassNumCtrl, 0, wx.ALL, 5)

        self.customFirstClassCtrl = wx.FilePickerCtrl(
            panel, wildcard=imgWildcard)
        label = wx.StaticText(panel)
        label.SetLabel("First Class Custom Cue")
        gs.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        gs.Add(self.customFirstClassCtrl, 0, wx.ALL, 5)

        self.baselineCtrl = wx.SpinCtrl(panel, min=0, max=20)
        label = wx.StaticText(panel)
        label.SetLabel("Baseline Duration (sec)")
        gs.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        gs.Add(self.baselineCtrl, 0, wx.ALL, 5)

        self.waitCueCtrl = wx.SpinCtrl(panel, min=0, max=10)
        label = wx.StaticText(panel)
        label.SetLabel("Waiting For Cue Duration (sec)")
        gs.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        gs.Add(self.waitCueCtrl, 0, wx.ALL, 5)

        self.dispCueCtrl = wx.SpinCtrl(panel, min=0, max=20)
        label = wx.StaticText(panel)
        label.SetLabel("Display Cue Duration (sec)")
        gs.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        gs.Add(self.dispCueCtrl, 0, wx.ALL, 5)

        self.feedbackCtrl = wx.SpinCtrl(panel, min=0, max=20)
        label = wx.StaticText(panel)
        label.SetLabel("Feedback Duration (sec)")
        gs.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        gs.Add(self.feedbackCtrl, 0, wx.ALL, 5)

        self.defaultBtn = wx.Button(
            panel, label="Default", size=wx.Size(72, 36))
        self.saveBtn = wx.Button(
            panel, label="Save", size=wx.Size(72, 36))
        self.cancelBtn = wx.Button(
            panel, label="Cancel", size=wx.Size(72, 36))
        bs.Add(self.saveBtn, 0, wx.ALL, 20)
        bs.Add(self.defaultBtn, 0, wx.ALL, 20)
        bs.Add(self.cancelBtn, 0, wx.ALL, 20)

        ms.Add(gs)
        ms.Add(bs)
        panel.SetSizerAndFit(ms)
        panel.Center()
        self.Fit()
        print(self.Size, self.GetBestSize())

        self.defaultBtn.Bind(wx.EVT_BUTTON, self.OnDefault)
        self.saveBtn.Bind(wx.EVT_BUTTON, self.OnSave)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.OnCancel)

    def updateConfig(self, config):
        self.firstClassCtrl.SetSelection(
            self.firstClassCtrl.FindString(config['firstClass']))
        self.firstClassNumCtrl.SetValue(config['firstClassNum'])
        self.secondClassCtrl.SetSelection(
            self.secondClassCtrl.FindString(config['secondClass']))
        self.secondClassNumCtrl.SetValue(config['secondClassNum'])
        self.baselineCtrl.SetValue(config['baseline'])
        self.waitCueCtrl.SetValue(config['waitCue'])
        self.dispCueCtrl.SetValue(config['dispCue'])
        self.feedbackCtrl.SetValue(config['feedback'])

    def OnSave(self, event):
        self.stimConfig = {
            "firstClass": self.firstClassCtrl.GetString(
                self.firstClassCtrl.GetCurrentSelection()),
            "firstClassNum": self.firstClassNumCtrl.GetValue(),
            "secondClass": self.secondClassCtrl.GetString(
                self.secondClassCtrl.GetCurrentSelection()),
            "secondClassNum": self.secondClassNumCtrl.GetValue(),
            "baseline": self.baselineCtrl.GetValue(),
            "waitCue": self.waitCueCtrl.GetValue(),
            "dispCue": self.dispCueCtrl.GetValue(),
            "feedback": self.feedbackCtrl.GetValue()
        }
        self.EndModal(wx.APPLY)

    def OnCancel(self, event):
        self.updateConfig(self.stimConfig)
        self.EndModal(wx.CANCEL)

    def OnDefault(self, event):
        stimConfig = {
            "firstClass": "OVTK_GDF_Left",
            "firstClassNum": 10,
            "secondClass": "OVTK_GDF_Right",
            "secondClassNum": 10,
            "baseline": 10,
            "waitCue": 2,
            "dispCue": 4,
            "feedback": 4
        }
        self.updateConfig(stimConfig)

    def onClose(self, event):
        self.updateConfig(self.stimConfig)
        self.EndModal(wx.CANCEL)
