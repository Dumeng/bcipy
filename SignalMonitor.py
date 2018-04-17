import wx
import wx.lib.plot as wxplot
import numpy as np
import time
import threading


class SignalMonitor(wx.Frame):
    def __init__(self, parent, Nch=2, length=5, frez=200):
        super(SignalMonitor, self). __init__(
            parent, title='Signal Monitor', size=(640, 480))
        self.step = 1.0/frez
        self.duration = 0.04
        self.t = np.arange(0, length, self.step)
        self.running = False
        datas = np.array(
            [self.t, 3*np.sin(2*np.pi*self.t)]).T
        datac = np.array(
            [self.t, 3*np.cos(2*np.pi*self.t)+7]).T

        self.model = [[wxplot.PolySpline(datas, width=3), datas],
                      [wxplot.PolySpline(datac, width=3), datac]]
        self.g = wxplot.PlotGraphics([i[0] for i in self.model])
        self.canvas = wxplot.PlotCanvas(self)
        self.canvas.Draw(self.g)
        self.canvas.enableAxesValues = (True, False)
        self.dataThread = threading.Thread(target=self.dataSend)

    def run(self):
        self.Show()
        self.running = True
        self.dataThread.start()

    def dataSend(self):
        while(self.running):
            self.t += self.duration
            self.model[0][1][:, 1] = 3*np.sin(1.5*np.pi*self.t)
            self.model[1][1][:, 1] = 3*np.cos(2.5*np.pi*self.t)+7
            self.updatePlot()

    def updatePlot(self):
        for ch in self.model:
            ch[1][:, 0] += self.step
            ch[0].points = ch[1]
        self.canvas.ScrollRight(self.step)
        self.canvas.Redraw()
        # self.canvas.Update()

    def stop(self):
        self.running = False
        self.Hide()
