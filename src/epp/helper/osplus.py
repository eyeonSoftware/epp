#!/usr/bin/env python
#coding=utf-8
#? py

'''
os.py
####################################

Additional helper functions for os / file system.

:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''
# Python pre 3.0 uses _winreg instead of winreg
try:
    import _winreg as winreg
except:
    import winreg 

import __main__
import os
import sys
import unicodedata
import win32api
import win32clipboard as w 
from win32con import CF_TEXT
#from win32com.shell import shell, shellcon

import win32con
from win32gui import SendMessageTimeout


# -------------------------------------------------------------------------------------
def unitostr(string):
    """docstring for fname"""
    return unicodedata.normalize('NFKD', string).encode('ascii','ignore')

# -------------------------------------------------------------------------------------
def unitostr_decorator(function):
    return lambda: unitostr(function())

# -------------------------------------------------------------------------------------
def get_env_system(varname, default=None):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment') as key:
            return winreg.QueryValueEx(key, varname)[0]
    except:
        return default

# -------------------------------------------------------------------------------------
def get_env_local(varname, default=None):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as key:
            return winreg.QueryValueEx(key, varname)[0]
    except:
        return default

# -------------------------------------------------------------------------------------
def getusername():
    # TODO: Plattform
    username = win32api.GetUserName()
    # To fix the case see if we find a profile
    try:
        prof_username = os.environ["userprofile"].split(os.path.sep)[-1]
        if prof_username.lower() == username.lower():
            username = prof_username
    except:
        pass


    return username

# -------------------------------------------------------------------------------------
def get_clipboard(): 
    w.OpenClipboard() 
    try:
        d=w.GetClipboardData(CF_TEXT) 
        w.CloseClipboard() 
        return d 
    except:
        return None
 
# -------------------------------------------------------------------------------------
def set_clipboard(aString, aType=CF_TEXT): 
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardData(aType,aString) 
    w.CloseClipboard()

# -------------------------------------------------------------------------------------
"""
def getmydocuments():
    try:
        mydocs = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, 0, 0)
    except:
        mydocs = ""

    return mydocs
"""


# -------------------------------------------------------------------------------------
def get_env(name):

    ret = get_env_local(name)
    if ret is None:
        ret = get_env_system(name)

    return ret

# -------------------------------------------------------------------------------------
def set_env(name, value):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
    winreg.CloseKey(key)
    SendMessageTimeout( win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment', win32con.SMTO_ABORTIFHUNG, 100)

# -------------------------------------------------------------------------------------
def remove(paths, value):
    while value in paths:
        paths.remove(value)


# -------------------------------------------------------------------------------------
def unique(paths):
    unique = []
    for value in paths:
        if value not in unique:
            unique.append(value)
    return unique


# -------------------------------------------------------------------------------------
def prepend_env(name, values):
    for value in values:
        paths = get_env(name).split(';')
        remove(paths, '')
        paths = unique(paths)
        remove(paths, value)
        paths.insert(0, value)
        set_env(name, ';'.join(paths))


# -------------------------------------------------------------------------------------
def prepend_env_pathext(values):
    prepend_env('PathExt_User', values)
    pathext = ';'.join([
        get_env('PathExt_User'),
        get_env('PathExt', user=False)
    ])
    set_env('PathExt', pathext)

# -------------------------------------------------------------------------------------
def app_path(*filepath):
    """
    Returns the absolute path from relative url to the app
    
    filepath -- relative path to the app like "filename.txt" or "config/test.dat"
    """
    # determine if application is a script file or frozen exe
    if hasattr(sys, 'frozen'):
        application_path = os.path.dirname(sys.executable)
    elif "__file__" in dir(__main__):
        application_path = os.path.dirname(__main__.__file__)
    else:
        return None

    return os.path.join(os.path.abspath(application_path), *filepath)


