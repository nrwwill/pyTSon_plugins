import ts3defines, ts3lib
from pytson import getPluginPath
from pluginhost import PluginHost
from ts3plugin import ts3plugin
from os import path
from json import loads
from datetime import datetime
from pytsonui import setupUi
from getvalues import getValues, ValueType
from PythonQt.QtGui import QDialog, QComboBox
from PythonQt.QtCore import Qt, QUrl
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from bluscream import saveCfg, timestamp, msgBox
from configparser import ConfigParser
from traceback import format_exc

class easyMod(ts3plugin):
    name = "Easy Moderation"
    apiVersion = 22
    requestAutoload = False
    version = "1.0"
    author = "Bluscream"
    description = ""
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = [
        ("restrict_last_joined_server", "Restrict the last user that joined your server."),
        ("restrict_last_joined_channel", "Restrict the last user that joined your channel."),
        ("ban_last_joined_server", "Bans the last user that joined your server."),
        ("ban_last_joined_channel", "Bans the last user that joined your channel.")
    ]
    last_joined_server = 0
    last_joined_channel = 0
    sgids = [17,21]
    requested = 0

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(),self.name,self.author))

    def onHotkeyEvent(self, keyword):
        schid = ts3lib.getCurrentServerConnectionHandlerID()
        if keyword == "restrict_last_joined_server":
            self.requested = self.last_joined_server
            ts3lib.requestClientVariables(schid, self.last_joined_server)
            # self.restrictClient(schid, self.last_joined_server)
        elif keyword == "restrict_last_joined_channel":
            self.requested = self.last_joined_channel
            ts3lib.requestClientVariables(schid, self.last_joined_channel)
            # self.restrictClient(schid, self.last_joined_channel)
        elif keyword == "ban_last_joined_server":
            self.banClient(schid, self.last_joined_server)
        elif keyword == "ban_last_joined_channel":
            self.banClient(schid, self.last_joined_channel)

    def onUpdateClientEvent(self, schid, clid, invokerID, invokerName, invokerUniqueIdentifier):
        if clid != self.requested: return
        (err, cldbid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_DATABASE_ID)
        print("cldbid:",cldbid)
        (err, sgids) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientPropertiesRare.CLIENT_SERVERGROUPS)
        print("sgids:",sgids)
        if set(self.sgids).issubset(sgids):
            for sgid in self.sgids: ts3lib.requestServerGroupDelClient(schid, sgid, cldbid)
        else:
            for sgid in self.sgids: ts3lib.requestServerGroupAddClient(schid, sgid, cldbid)
        self.requested = 0

    def banClient(self, schid, clid):
        (err, uid) = ts3lib.getClientVariable(schid, clid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        ts3lib.banadd(schid, "", "", uid, 2678400, "Ban Evading / Bannumgehung")

    def onClientMoveEvent(self, schid, clid, oldChannelID, newChannelID, visibility, moveMessage):
        if schid != ts3lib.getCurrentServerConnectionHandlerID(): return
        if oldChannelID == 0: self.last_joined_server = clid
        (err, ownID) = ts3lib.getClientID(schid)
        (err, ownCID) = ts3lib.getChannelOfClient(schid, ownID)
        if newChannelID == ownCID: self.last_joined_channel = clid