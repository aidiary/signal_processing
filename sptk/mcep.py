#coding:utf-8
import os
import sys
import subprocess
import pylab

# メルケプストラム分析合成の手順
# 実行にはsox、gnuplot、SPTKが必要
# 使い方: python mcep.py [raw_file] [order of mel cepstrum]

def execute(cmd):
    subprocess.call(cmd, shell=True)
    print cmd

def draw_figure(dat_file, xlabel="", ylabel="", style="b-", lw=1):
    fp = open(dat_file, "r")
    x = []
    y = []
    for line in fp:
        line = line.rstrip()
        dat = line.split()
        x.append(float(dat[0]))
        y.append(float(dat[1]))
    pylab.plot(x, y, style, linewidth=lw)
    pylab.xlabel(xlabel)
    pylab.ylabel(ylabel)
    pylab.xlim(min(x), max(x))
    fp.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: python mcep.py [raw_file] [order of mel cepstrum]"
        exit()

    raw_file = sys.argv[1]    # RAWファイル
    order = int(sys.argv[2])  # メルケプストラムの次数

    # 16000Hzの場合は0.42で固定
    alpha = 0.42

    prefix = raw_file.replace(".raw", "")

    # RAWファイルをWAVEファイルに変換
    # 音声を確認できるように
    cmd = "sox -e signed-integer -c 1 -b 16 -r 16000 %s.raw %s.wav" % (prefix, prefix)
    execute(cmd)

    # ピッチ抽出
    cmd = "x2x +sf %s.raw | pitch -a 1 > %s.pitch" % (prefix, prefix)
    execute(cmd)

    # ピッチの描画
    cmd = "dmp +f %s.pitch > pitch.txt" % prefix
    execute(cmd)
    draw_figure("pitch.txt", "frame", "pitch")
    pylab.savefig("pitch.png")
    pylab.clf()
    os.remove("pitch.txt")

    # 音源の生成
    cmd = "excite -p 80 data.pitch | sopr -m 1000 | x2x +fs > source.raw"
    execute(cmd)
    cmd = "sox -e signed-integer -c 1 -b 16 -r 16000 source.raw source.wav"
    execute(cmd)
    cmd = "dmp +s source.raw > source.txt"
    execute(cmd)

    # 音源の描画
    draw_figure("source.txt", "sample", "amplitude")
    pylab.savefig("source.png")
    pylab.clf()
    os.remove("source.txt")

    # メルケプストラム分析
    cmd = "x2x +sf < %s.raw | frame -l 400 -p 80 | window -l 400 -L 512 | mcep -l 512 -m %d -a %f > %s.mcep" % (prefix, order, alpha, prefix)
    execute(cmd)

    # 65フレームのの対数スペクトルを描画
    cmd = "x2x +sf < %s.raw | frame -l 400 -p 80 | bcut +f -l 400 -s 65 -e 65 | window -l 400 -L 512 | spec -l 512 | dmp +f > spec.txt" % prefix
    execute(cmd)
    draw_figure("spec.txt", style="b-")

    # フレーム65のメルケプストラムのスペクトル包絡を描画
    cmd = "bcut +f -n %d -s 65 -e 65 < %s.mcep | mgc2sp -m %d -a %f -g 0 -l 512 | dmp +f > mcep.txt" % (order, prefix, order, alpha)
    execute(cmd)
    draw_figure("mcep.txt", "frequency bin", "log magnitude [dB]", style="r-", lw=2)
    pylab.savefig("mcep.png")

    os.remove("spec.txt")
    os.remove("mcep.txt")

    # 分析合成音の作成
    cmd = "excite -p 80 %s.pitch | mlsadf -m %d -a %f -p 80 %s.mcep | x2x +fs > %s.mcep.raw" % (prefix, order, alpha, prefix, prefix)
    execute(cmd)

    # WAVEファイルに変換
    cmd = "sox -e signed-integer -c 1 -b 16 -r 16000 %s.mcep.raw %s.mcep.wav" % (prefix, prefix)
    execute(cmd)
