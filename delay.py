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
    print "長さ（秒）:", float(wf.getnframes()) / wf.getframerate()

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
    wf = wave.open("data/yukkuri.wav", "r")
    printWaveInfo(wf)

    fs = wf.getframerate()      # サンプリング周波数
    length = wf.getnframes()    # 総フレーム数
    data = wf.readframes(length)
    play(data, fs, 16)  # デフォルトの音声を再生

    data = frombuffer(data, dtype="int16") / 32768.0  # -1 - +1に正規化
    a = 0.7      # 減衰率
    repeat = 3   # リピート回数

    alldata = ''
    for d in range(1000, 3000, 500):  # 遅延時間d(sample) を変えながら音を鳴らす
        newdata = [0.0] * length
        for n in range(length):
            newdata[n] = data[n]
            # 元のデータに残響を加える
            for i in range(1, repeat + 1):
                m = int(n - i * d)
                if m >= 0:
                    newdata[n] += (a ** i) * data[m]  # i*dだけ前のデータを減衰させた振幅を加える

        # -32768 - +32767へバイナリ化してから再生
        newdata = [int(x * 32767.0) for x in newdata]
        newdata = struct.pack("h" * len(newdata), *newdata)
        play(newdata, fs, 16)
        alldata += newdata  # ファイル保存用

    # 音声をWAVEファイルに保存
    save(alldata, fs, 16, 'yukkuri_reverve.wav')
