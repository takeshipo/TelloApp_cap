#!/usr/bin/python3
# -*- coding: utf-8 -*-

#-------------標準ライブラリ--------------------
import sys
import traceback
import cv2
import socket
# import numpy
import time

#----------kivyフレームワーク-------------------
import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from threading import Thread
# from flask import Response
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivy.clock import Clock

#メインクラス
class TestApp(App,Thread):

    #属性の定義
    text = StringProperty('')
    cnt = NumericProperty()
    flag_fow = NumericProperty()
    flag_bak = NumericProperty()
    flag_rig = NumericProperty()
    flag_lef = NumericProperty()

    #TestAppの最初に実行される処理
    def __init__(self, **kwargs):
        super(TestApp, self).__init__(**kwargs)
        self.text = 'default'
        self.flag_fow = 0
        self.flag_bak = 0
        self.flag_rig = 0
        self.flag_lef = 0
        self.call_cnt = 0
        self.initConnection()

    # 通信の設定
    def initConnection(self):
        print('-' * 20)
        host = ''
        port = 9000
        locaddr = (host, port)
        self.tello = ('192.168.10.1', 8889)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(locaddr)

        # 受信スレッド起動
        recvThread = Thread(target=self.recvSocket)
        recvThread.setDaemon(True)
        recvThread.start()

        # 最初にcommandコマンドを送信
        try:
            sent = self.sock.sendto('command'.encode(encoding="utf-8"), self.tello)
        except:
            pass
        
        #各スレッドの受付け
        fowThread = Thread(target=self.fowBtnClicked)
        # fowThread.start()
        bckThread = Thread(target=self.backBtnClicked)
        # bckThread.start()
        rigThread = Thread(target=self.rightBtnClicked)
        # rigThread.start()
        lefThread = Thread(target=self.leftBtnClicked)
        # lefThread.start()

        streamThread = Thread(target=self.Streaming)
        streamThread.start()

        print('iniConnection FIN')
        print('-'*20)

    #前進処理
    def fowBtnClicked(self):
        # while (True):
        try:
            cnt = 0
            while(self.flag_fow):
                sent = self.sock.sendto('forward 100'.encode(encoding="utf-8"), self.tello)
                time.sleep(0.1)
                cnt += 1
                if cnt > 1:
                    print("fow")
                    self.flag_fow = 0
        except :
            pass

    #前後左右をの振り分け
    def toggleFlag(self,flag_name,stat):
        print('toggleFlag',flag_name,stat)
        if 'flag_fow' == flag_name:
            self.flag_fow = stat
            self.fowBtnClicked()
        if 'flag_bak' == flag_name:
            self.flag_bak = stat
            self.backBtnClicked()
        if 'flag_rig' == flag_name:
            self.flag_rig = stat
            self.rightBtnClicked()
        if 'flag_lef' == flag_name:
            self.flag_lef = stat
            self.leftBtnClicked()
        pass

    #後退処理
    def backBtnClicked(self):
        # while True:
        try:
            cnt = 0
            while (self.flag_bak):
                sent = self.sock.sendto('back 100'.encode(encoding="utf-8"), self.tello)
                time.sleep(0.1)
                cnt += 1
                if cnt > 1:
                    print("bak")
                    self.flag_bak = 0
        except :
            pass

    #左進処理
    def leftBtnClicked(self):
        # while True:
        try:
            cnt = 0
            while (self.flag_lef):
                sent = self.sock.sendto('left 100'.encode(encoding="utf-8"), self.tello)
                time.sleep(0.1)
                cnt += 1
                if cnt > 1:
                    print("left")
                    self.flag_lef = 0
        except :
            pass

    #右進処理
    def rightBtnClicked(self):
        # while True:
        try:
            cnt = 0
            while (self.flag_rig):
                sent = self.sock.sendto('right 100'.encode(encoding="utf-8"), self.tello)
                time.sleep(0.1)
                cnt += 1
                if cnt > 1:
                    print("right")
                    self.flag_rig = 0
        except :
            pass

    # Telloからのレスポンス受信
    def recvSocket(self):
        while True:
            try:
                data, server = self.sock.recvfrom(1518)
                self.label.setText(data.decode(encoding="utf-8"))
            except:
                pass

    # takeoffコマンド送信
    def takeoffBtnClicked(self):
        try:
            sent = self.sock.sendto('takeoff'.encode(encoding="utf-8"), self.tello)
        except:
            pass

    # landコマンド送信
    def landBtnClicked(self):
        try:
            sent = self.sock.sendto('land'.encode(encoding="utf-8"), self.tello)
        except:
            pass

    #停止処理
    def stopBtnClicked(self):
        try:
            self.flag_fow = 0
            self.flag_bak = 0
            self.flag_rig = 0
            self.flag_lef = 0
            print(Thread.active_count())
        except:
            pass
    
    #flip処理
    def flipBtnClicked(self):
        try:
            sent = self.sock.sendto('flip f'.encode(encoding="utf-8"), self.tello)
        except:
            pass


    # Telloからのレスポンス受信
    def recvSocket(self):
        while True:
            try:
                data, server = self.sock.recvfrom(1518)
                self.label.setText(data.decode(encoding="utf-8"))
            except:
                pass

    #動画出力処理
    def Streaming(self):
        try:
            sent = self.sock.sendto('streamon'.encode(encoding="utf-8"), self.tello)
            cap = \
                cv2.VideoCapture('udp://0.0.0.0:11111')
            
            while True:
                ret,frame=cap.read()
                cv2.imshow('TelloEDU',frame)
                key = cv2.waitKey(1)
                if key == 27:
                    break
        except Exception:
            print(Exception)
        
        finally:
            cap.release()
            cv2.destroyAllWindows()

            sent = self.sock.sendto('streamoff'.encode(encoding="utf-8"), self.tello)
            print('-------------END-------------------')
    
    #
    def releseBtn(self):
        self.flag = 0

#メイン「スクリーンの起動」
if __name__ == '__main__':
    TestApp().run()
    print("fin_run")