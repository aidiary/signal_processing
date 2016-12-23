#coding:utf-8
import sys
import wave
import numpy as np
import scipy.fftpack
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt

wf = wave.open("data/tamsu02.wav" , "r" )
fs = wf.getframerate()  # サンプリング周波数
x = wf.readframes(wf.getnframes())
x = np.frombuffer(x, dtype= "int16") / 32768.0  # -1 - +1に正規化
wf.close()

fig = plt.figure()
sp1 = fig.add_subplot(211)
sp2 = fig.add_subplot(212)

print len(x)

start = 0    # サンプリングする開始位置
N = 512      # FFTのサンプル数
SHIFT = 128  # 窓関数をずらすサンプル数

hammingWindow = np.hamming(N)
freqList = np.fft.fftfreq(N, d=1.0/fs)  # 周波数軸の値を計算

def update(idleevent):
    global start

    windowedData = hammingWindow * x[start:start+N]  # 切り出した波形データ（窓関数あり）
    X = np.fft.fft(windowedData)  # FFT

    amplitudeSpectrum = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in X]  # 振幅スペクトル

    # 波形を更新
    sp1.cla()  # クリア
    sp1.plot(range(start, start+N), x[start:start+N])
    sp1.axis([start, start+N, -0.3, 0.3])
    sp1.set_xlabel("time [sample]")
    sp1.set_ylabel("amplitude")

    # 振幅スペクトルを描画
    sp2.cla()
    sp2.plot(freqList, amplitudeSpectrum, marker= 'o', linestyle='-')
    sp2.axis([0, fs/2, 0, 20])
    sp2.set_xlabel("frequency [Hz]")
    sp2.set_ylabel("amplitude spectrum")

    fig.canvas.draw_idle()
    start += SHIFT  # 窓関数をかける範囲をずらす
    if start + N > len(x):
        sys.exit()

import wx
wx.EVT_IDLE(wx.GetApp(), update)
plt.show()

