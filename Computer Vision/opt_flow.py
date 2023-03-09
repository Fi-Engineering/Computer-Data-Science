import numpy as np
import matplotlib.pyplot as plt
import cv2
import scipy.signal
def findGradient(img, ksize=5, sigma=1):
    G = cv2.getGaussianKernel(ksize, sigma)
    G = G @ G.T
    fx = np.array([[1, -1]])
    fy = fx.T
    Gx = scipy.signal.convolve2d(G, fx, 'same', 'symm')[:, 1:]
    Gy = scipy.signal.convolve2d(G, fy, 'same', 'symm')[1:, :]
    Ix = scipy.signal.convolve2d(img, Gx, 'same', 'symm')
    Iy = scipy.signal.convolve2d(img, Gy, 'same', 'symm')
    return Ix, Iy


img1 = np.array([[0, 0, 0, 0, 0],
                [0, 1, 2, 0, 0],
                [0, 3, 4, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0]])
img2 = np.array([[0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 1, 2, 0],
                [0, 0, 3, 4, 0],
                [0, 0, 0, 0, 0]])

Jx, Jy = findGradient(img2, 7, 1.3) 
It = img2 - img1
A = np.hstack((Jx.reshape(-1, 1), Jy.reshape(-1, 1)))
b = -It.reshape(-1, 1)
res = np.linalg.solve(A.T @ A, A.T @ b)
print(res)