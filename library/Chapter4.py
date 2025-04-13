import numpy as np
import cv2

L=256


def Spectrum(imgin):
    M,N = imgin.shape
    #Buoc 1, 2: mo rong anh kich thuoc p, q
    P = cv2.getOptimalDFTSize(M)
    Q = cv2.getOptimalDFTSize(N)
    fp = np.zeros((P,Q),np.float32)
    fp[:M,:N] = 1.0*imgin/(L-1)

    #Buoc 3: Nhan fp voi (-1)^(x+y)
    for x in range(0,M):
        for y in range(0,N):
            if(x+y) % 2 == 1:
                fp[x,y] = -fp[x,y]

    #Buoc 4: tinh DFT
    F = cv2.dft(fp,flags=cv2.DFT_COMPLEX_OUTPUT)

    #Tinh pho(spectrum)
    Spectrum = np.sqrt(F[:,:,0]**2+F[:,:,1]**2)
    Spectrum = np.clip(Spectrum,0,L-1)
    imgout = Spectrum.astype(np.uint8)

    return imgout

