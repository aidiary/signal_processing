#coding:utf-8
import numpy as np
from pylab import *

N = 512

hammingWindow = np.hamming(N)
hanningWindow = np.hanning(N)
bartlettWindow = np.bartlett(N)
blackmanWindow = np.blackman(N)
kaiserWindow = np.kaiser(N, 5)

subplot(231)
plot(hammingWindow)
title("Hamming Window")
axis((0, N, 0, 1))

subplot(232)
plot(hanningWindow)
title("Hanning Window")
axis((0, N, 0, 1))

subplot(233)
plot(bartlettWindow)
title("Bartlett Window")
axis((0, N, 0, 1))

subplot(234)
plot(blackmanWindow)
title("Blackman Window")
axis((0, N, 0, 1))

subplot(235)
plot(kaiserWindow)
title("Kaiser Window")
axis((0, N, 0, 1))

show()
