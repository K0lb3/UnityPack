from ctypes import *
import os

PATH=os.path.dirname(os.path.realpath(__file__))
print(os.path.join(PATH,'format.dll'))
# give location of dll
vgmFormat = CDLL(os.path.join(PATH,'format.dll'))
vgmUtil = WinDLL.LoadLibrary(os.path.join(PATH,'vgmtutil.dll'))

#
testFile = os.path.join(PATH,'BGM_0001.awb')