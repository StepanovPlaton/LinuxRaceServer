#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import socket, threading
from time import sleep

class Player:
    def __init__(self, Connect, Name, Address="Unknown", Position=(0, 0, 0), Rotation=(0, 0, 0), WheelAngle=0):
        self.Position = Position
        self.Rotation = Rotation
        self.WheelAngle = WheelAngle
        self.Name = Name
        self.Connect = Connect
        self.Address = Address

    def GetPlayerData(self):
        return self.Name + ";" + str(self.Position[0]) + ";" + str(self.Position[1]) + ";" + str(self.Position[2]) + ";" + \
                str(self.Rotation[0]) + ";" + str(self.Rotation[1]) + ";" + str(self.Rotation[2]) + ";" + str(self.WheelAngle)

    def SetPlayerData(self, Position=(0, 0, 0), Rotation=(0, 0, 0), WheelAngle=0):
        self.Position = Position
        self.Rotation = Rotation
        self.WheelAngle = WheelAngle

class SocketServerClass:
    def __init__(self, DataBaseAPI, Port, Start=True, DebugPrints=True):
        self.DataBase = DataBaseAPI("127.0.0.1", "user", "password", "Players")
        self.Port = Port
        self.Socket = socket.socket()
        self.Socket.settimeout(2)
        self.DebugPrints = DebugPrints
        if(self.DebugPrints): print("Socket init - OK")
        self.Players = []
        if(Start): self.StartServer()

    def StartServer(self, ListenClients=10):
        self.Socket.bind(('', self.Port))
        self.Socket.listen(ListenClients)
        self.StartDemon(self.WaitConnect)
        if(self.DebugPrints): print("Server start - OK")

    def StartDemon(self, Target, Arguments=()):
        self.Demon = threading.Thread(target=Target, args=Arguments)
        self.Demon.daemon = True
        self.Demon.start()

    def FindPlayerByName(self, Name):
        for i in range(len(self.Players)):
            if(self.Players[i].Name == Name): return i
        return None

    def WaitConnect(self):
        while True:
            try: Connect, Address = self.Socket.accept()
            except BaseException: continue
            if(self.DebugPrints): print("Connect", Address)
            try: data = str(Connect.recv(1024)).replace("'", "")[1:]
            except BaseException:
                if(self.DebugPrints): print("Connect", Address, "is silent!")
            else:
                try:
                    print("Connect", Address, "say -", data)
                    if(data[0] == "("):
                        if(data.find(")") != -1):
                            Name = data[1:data.find(")")]
                            if(self.DebugPrints): print("Connect", Address, "wats to name himself -", Name)
                            if(self.FindPlayerByName(Name) is None):
                                if(self.DebugPrints): print("Name", Name, "is free")
                                Connect.send(b"+) Name is free, login ok!")
                                self.Players.append(Player(Connect, Name, Address))
                                self.StartDemon(self.ReadingPlayerData, (Name,))
                            else:
                                if(self.DebugPrints): print("Name", Name, "is taken!")
                                Connect.send(b"-) Name is taken, login fail!")
                except BaseException as e: print(e.format_exc())

    def ReadingPlayerData(self, Name):
        PlayerID = self.FindPlayerByName(Name)
        while True:
            try:
                data = str(self.Players[PlayerID].Connect.recv(1024)).replace("'", "").replace(",", ".")[1:]
                if(data[0] == '!' and data[len(data)-1] == '~'):
                    PlayerParameters = data[1:len(data)-1].split(";")
                    self.Players[PlayerID].SetPlayerData((float(PlayerParameters[0]), float(PlayerParameters[1]), float(PlayerParameters[2])),
                                                          (float(PlayerParameters[3]), float(PlayerParameters[4]), float(PlayerParameters[5])), float(PlayerParameters[6]))
                self.Players[PlayerID].Connect.send(self.GetDataAllPlayers())
            except BaseException:
                print("Package from", Name, "is wrong or connection close")
                return

    def GetDataAllPlayers(self):
        data = "!"
        for i in self.Players: data += i.GetPlayerData() + "~"
        return data.encode()

    def GetDataBasePlayers(self):
        data = self.DataBase.Execute()
