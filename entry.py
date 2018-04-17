import wx
import wx.adv as wxadv

from Graz import *
from lslDataServer import *
from MainWindow import *

app = wx.App()
win = MainWindow()
# window = Graz()
win.Show()
# s = MIStimulator(window)
# s.setTcpTagging() # Enable Stimulations TCP Tagging
print('Ready')
# ds = lslDataServer(win)
# ds.configure()
# ds.start()
# window.displayGif('tmp.gif')
# window.startStim()
# print('Total Time: ', s.T, 's')
app.MainLoop()
