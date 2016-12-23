#coding:utf-8
import wave
import numpy as np
import scipy.fftpack
from pylab import *

if __name__ == "__main__":
    wf = wave.open("data/combined.wav", "r")
    fs = wf.getframerate()  # サンプリング周波数
    x = wf.readframes(wf.getnframes())
    x = frombuffer(x, dtype="int16") / 32768.0  # 0-1に正規化

    start = 0   # サンプリングする開始位置
    N = 512     # FFTのサンプル数

    hammingWindow = np.hamming(N)    # ハミング窓
    hanningWindow = np.hanning(N)    # ハニング窓
    blackmanWindow = np.blackman(N)  # ブラックマン窓
    bartlettWindow = np.bartlett(N)  # バートレット窓

    originalData = x[start:start+N]                  # 切り出した波形データ（窓関数なし）
    windowedData = hammingWindow * x[start:start+N]  # 切り出した波形データ（窓関数あり）

    originalDFT = np.fft.fft(originalData)
    windowedDFT = np.fft.fft(windowedData)
    freqList = np.fft.fftfreq(N, d=1.0/fs)

    originalAmp = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in originalDFT]
    windowedAmp = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in windowedDFT]

    # 波形を描画（窓関数なし）
    subplot(221)  # 2行2列のグラフの1番目の位置にプロット
    plot(range(start, start+N), originalData)
    axis([start, start+N, -1.0, 1.0])
    xlabel("time [sample]")
    ylabel("amplitude")

    # 波形を描画（窓関数あり）
    subplot(222)  # 2行2列のグラフの2番目の位置にプロット
    plot(range(start, start+N), windowedData)
    axis([start, start+N, -1.0, 1.0])
    xlabel("time [sample]")
    ylabel("amplitude")

    # 振幅スペクトルを描画（窓関数なし）
    subplot(223)
    plot(freqList, originalAmp, marker='o', linestyle='-')
    axis([0, fs/2, 0, 100])
    xlabel("frequency [Hz]")
    ylabel("amplitude spectrum")

    # 振幅スペクトルを描画（窓関数あり）
    subplot(224)
    plot(freqList, windowedAmp, marker='o', linestyle='-')
    axis([0, fs/2, 0, 100])
    xlabel("frequency [Hz]")
    ylabel("amplitude spectrum")

    show()
