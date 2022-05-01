from zipfile import ZipFile
import os
import winshell
from win32com.client import Dispatch

# Create a ZipFile Object and load sample.zip in it
with ZipFile('gui.zip', 'r') as zipObj:
    zipObj.extractall()

desktop = winshell.desktop()
path = os.path.join(desktop, "Sdarobot.lnk")
target = os.path.abspath("gui/gui.exe")
wDir = target[:-7]
icon = os.path.abspath("gui/icon.ico")
shell = Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(path)
shortcut.Targetpath = target
shortcut.WorkingDirectory = wDir
shortcut.IconLocation = icon
shortcut.save()
