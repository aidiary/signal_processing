#coding:utf-8
import wave
import numpy as np
import scipy.signal
import scipy.fftpack
import scipy.fftpack.realtransforms
from pylab import *

def wavread(filename):
    wf = wave.open(filename, "r")
    fs = wf.getframerate()
    x = wf.readframes(wf.getnframes())
    x = np.frombuffer(x, dtype="int16") / 32768.0  # (-1, 1)に正規化
    wf.close()
    return x, float(fs)

def hz2mel(f):
    """Hzをmelに変換"""
    return 1127.01048 * np.log(f / 700.0 + 1.0)

def mel2hz(m):
    """melをhzに変換"""
    return 700.0 * (np.exp(m / 1127.01048) - 1.0)

def melFilterBank(fs, nfft, numChannels):
    """メルフィルタバンクを作成"""
    # ナイキスト周波数（Hz）
    fmax = fs / 2
    # ナイキスト周波数（mel）
    melmax = hz2mel(fmax)
    # 周波数インデックスの最大数
    nmax = nfft / 2
    # 周波数解像度（周波数インデックス1あたりのHz幅）
    df = fs / nfft
    # メル尺度における各フィルタの中心周波数を求める
    dmel = melmax / (numChannels + 1)
    melcenters = np.arange(1, numChannels + 1) * dmel
    # 各フィルタの中心周波数をHzに変換
    fcenters = mel2hz(melcenters)
    # 各フィルタの中心周波数を周波数インデックスに変換
    indexcenter = np.round(fcenters / df)
    # 各フィルタの開始位置のインデックス
    indexstart = np.hstack(([0], indexcenter[0:numChannels - 1]))
    # 各フィルタの終了位置のインデックス
    indexstop = np.hstack((indexcenter[1:numChannels], [nmax]))

    filterbank = np.zeros((numChannels, nmax))
    for c in np.arange(0, numChannels):
        # 三角フィルタの左の直線の傾きから点を求める
        increment= 1.0 / (indexcenter[c] - indexstart[c])
        for i in np.arange(indexstart[c], indexcenter[c]):
            filterbank[c, i] = (i - indexstart[c]) * increment
        # 三角フィルタの右の直線の傾きから点を求める
        decrement = 1.0 / (indexstop[c] - indexcenter[c])
        for i in np.arange(indexcenter[c], indexstop[c]):
            filterbank[c, i] = 1.0 - ((i - indexcenter[c]) * decrement)

    return filterbank, fcenters

def preEmphasis(signal, p):
    """プリエンファシスフィルタ"""
    # 係数 (1.0, -p) のFIRフィルタを作成
    return scipy.signal.lfilter([1.0, -p], 1, signal)

def mfcc(signal, nfft, fs, nceps):
    """信号のMFCCパラメータを求める
    signal: 音声信号
    nfft  : FFTのサンプル数
    nceps : MFCCの次元"""
    # プリエンファシスフィルタをかける
    p = 0.97         # プリエンファシス係数
    signal = preEmphasis(signal, p)

    # ハミング窓をかける
    hammingWindow = np.hamming(len(signal))
    signal = signal * hammingWindow

    # 振幅スペクトルを求める
    spec = np.abs(np.fft.fft(signal, nfft))[:nfft/2]
    fscale = np.fft.fftfreq(nfft, d = 1.0 / fs)[:nfft/2]
#    plot(fscale, spec)
#    xlabel("frequency [Hz]")
#    ylabel("amplitude spectrum")
#    savefig("spectrum.png")
#    show()

    # メルフィルタバンクを作成
    numChannels = 20  # メルフィルタバンクのチャネル数
    df = fs / nfft   # 周波数解像度（周波数インデックス1あたりのHz幅）
    filterbank, fcenters = melFilterBank(fs, nfft, numChannels)
#    for c in np.arange(0, numChannels):
#        plot(np.arange(0, nfft / 2) * df, filterbank[c])
#    savefig("melfilterbank.png")
#    show()

    # 定義通りに書いた場合
    # 振幅スペクトルに対してフィルタバンクの各フィルタをかけ、振幅の和の対数をとる
#    mspec = []
#    for c in np.arange(0, numChannels):
#        mspec.append(np.log10(sum(spec * filterbank[c])))
#    mspec = np.array(mspec)

    # 行列で書くと簡単になる！
    # 振幅スペクトルにメルフィルタバンクを適用
    mspec = np.log10(np.dot(spec, filterbank.T))

    # 元の振幅スペクトルとフィルタバンクをかけて圧縮したスペクトルを表示
#    subplot(211)
#    plot(fscale, np.log10(spec))
#    xlabel("frequency")
#    xlim(0, 25000)
#
#    subplot(212)
#    plot(fcenters, mspec, "o-")
#    xlabel("frequency")
#    xlim(0, 25000)
#    savefig("result_melfilter.png")
#    show()

    # 離散コサイン変換
    ceps = scipy.fftpack.realtransforms.dct(mspec, type=2, norm="ortho", axis=-1)

    # 低次成分からnceps個の係数を返す
    return ceps[:nceps]

if __name__ == "__main__":
    # 音声をロード
    wav, fs = wavread("a.wav")
    t = np.arange(0.0, len(wav) / fs, 1/fs)

    # 音声波形の中心部分を切り出す
    center = len(wav) / 2  # 中心のサンプル番号
    cuttime = 0.04         # 切り出す長さ [s]
    wavdata = wav[center - cuttime/2*fs : center + cuttime/2*fs]

    nfft = 2048  # FFTのサンプル数
    nceps = 12   # MFCCの次元数
    ceps = mfcc(wavdata, nfft, fs, nceps)
    print "mfcc:", ceps
