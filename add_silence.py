#coding:utf-8
import wave
import pyaudio
import struct
from pylab import *

def printWaveInfo(wf):
    """WAVEファイルの情報を取得"""
    print "チャンネル数:", wf.getnchannels()
    print "サンプル幅:", wf.getsampwidth()
    print "サンプリング周波数:", wf.getframerate()
    print "フレーム数:", wf.getnframes()
    print "パラメータ:", wf.getparams()
    print "長さ（秒）:", wf.getnframes() / wf.getframerate()

def play (data, fs, bit):
    # ストリームを開く
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=int(fs),
                    output= True)
    # チャンク単位でストリームに出力し音声を再生
    chunk = 1024
    sp = 0  # 再生位置ポインタ
    buffer = data[sp:sp+chunk]
    while buffer != '':
        stream.write(buffer)
        sp = sp + chunk
        buffer = data[sp:sp+chunk]
    stream.close()
    p.terminate()

def save(data, fs, bit, filename):
    """波形データをWAVEファイルへ出力"""
    wf = wave.open(filename, "w")
    wf.setnchannels(1)
    wf.setsampwidth(bit / 8)
    wf.setframerate(fs)
    wf.writeframes(data)
    wf.close()

if __name__ == "__main__":
    wf = wave.open("data/yahho.wav", "r")
    printWaveInfo(wf)

    fs = wf.getframerate()
    length = wf.getnframes()
    data = wf.readframes(length)
    data = frombuffer(data, dtype="int16") / 32768.0  # -1 - +1に正規化
    data = list(data)

    # 3秒間の無音を追加
    for n in range(fs * 3):
        data.append(0.0)

    data = [int(x * 32767.0) for x in data]
    data = struct.pack("h" * len(data), *data)
    save(data, fs, 16, 'yahho2.wav')
