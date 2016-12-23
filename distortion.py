#coding:utf-8
import wave
import pyaudio
import struct
from pylab import *

def play(data, fs, bit):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=int(fs),
                    output=True)
    # 再生
    chunk = 1024
    sp = 0
    buffer = data[sp:sp+chunk]
    while stream.is_active():
        stream.write(buffer)
        sp += chunk
        buffer = data[sp:sp+chunk]
        if buffer == '': stream.stop_stream()
    stream.close()
    p.terminate()

def distortion(data, gain, level):
    length = len(data)
    newdata = [0.0] * length
    for n in range(length):
        newdata[n] = data[n] * gain  # 増幅
        # クリッピング
        if newdata[n] > 1.0:
            newdata[n] = 1.0
        elif newdata[n] < -1.0:
            newdata[n] = -1.0
        # 音量を調整
        newdata[n] *= level
    return newdata

def save(data, fs, bit, filename):
    """波形データをWAVEファイルへ出力"""
    wf = wave.open(filename, "w")
    wf.setnchannels(1)
    wf.setsampwidth(bit / 8)
    wf.setframerate(fs)
    wf.writeframes(data)
    wf.close()

if __name__ == "__main__":
    # 音声をロード
    wf = wave.open("data/sine.wav")
    fs = wf.getframerate()
    length = wf.getnframes()
    data = wf.readframes(length)

    # デフォルトの音声を再生、ファイルにも保存
    play(data, fs, 16)
    save(data, fs, 16, "original.wav")

    # エフェクトをかけやすいようにバイナリデータを[-1, +1]に正規化
    data = frombuffer(data, dtype="int16") / 32768.0

    # オリジナル波形の一部をプロット
    subplot(211)
    plot(data[0:200])
    xlabel("time [sample]")
    ylabel("amplitude")
    ylim([-1.0, 1.0])

    # ここでサウンドエフェクト
    newdata = distortion(data, 200, 0.3)

    # サウンドエフェクトをかけた波形の一部をプロット
    subplot(212)
    plot(newdata[0:200])
    xlabel("time [sample]")
    ylabel("amplitude")
    ylim([-1.0, 1.0])

    # 正規化前のバイナリデータに戻す
    newdata = [int(x * 32767.0) for x in newdata]
    newdata = struct.pack("h" * len(newdata), *newdata)

    # サウンドエフェクトをかけた音声を再生
    play(newdata, fs, 16)
    save(newdata, fs, 16, "distortion.wav")

    show()
