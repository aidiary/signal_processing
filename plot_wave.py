#coding:utf-8
import wave
from numpy import *
from pylab import *

def printWaveInfo(wf):
    """WAVEファイルの情報を取得"""
    print "チャンネル数:", wf.getnchannels()
    print "サンプル幅:", wf.getsampwidth()
    print "サンプリング周波数:", wf.getframerate()
    print "フレーム数:", wf.getnframes()
    print "パラメータ:", wf.getparams()
    print "長さ（秒）:", wf.getnframes() / wf.getframerate()

if __name__ == '__main__':
    wf = wave.open("o.wav", "r")
    printWaveInfo(wf)

    buffer = wf.readframes(wf.getnframes())
    print len(buffer)  # バイト数 = 1フレーム2バイト x フレーム数

    # bufferはバイナリなので2バイトずつ整数にまとめる
    data = frombuffer(buffer, dtype="int16")

    # そのままプロット
    plot(data[15000:15500])
    show()
