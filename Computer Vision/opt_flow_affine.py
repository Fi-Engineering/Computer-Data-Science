import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import convolve
import cv2

img = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                ] )
img_next = np.array([
                     [0,   0,    0,   0,   0,   0,   0,   0,  0],
                     [0, 0.25, 0.5, 0.5, 0.5, 0.5, 0.5, 0.25, 0],
                     [0, 0.5,   1,   1,    1,   1,   1, 0.5,  0],
                     [0, 0.5,   1,   1,    1,   1,   1, 0.5,  0],
                     [0, 0.5,   1,   1,    1,   1,   1, 0.5,  0],
                     [0, 0.5,   1,   1,    1,   1,   1, 0.5,  0],
                     [0, 0.5,   1,   1,    1,   1,   1, 0.5,  0],
                     [0, 0.25, 0.5, 0.5, 0.5, 0.5, 0.5, 0.25, 0],
                     [0,   0,   0,   0,    0,   0,   0,   0,  0],
                     ] )

x, y = np.meshgrid(np.arange(img.shape[1]), np.arange(img.shape[0]))
x = x - img.shape[1] // 2
y = y - img.shape[0] // 2

fx = np.array([[1, 0, -1]])
fy = fx.T

# comment these two lines when using Gaussian blur
# Ix = convolve(img_next, fx, mode='same')
# Iy = convolve(img_next, fy, mode='same')

# uncomment following lines to use Gaussian blur 
G = cv2.getGaussianKernel(11, 30)
G = G @ G.T
Gx = convolve(G, fx, mode='same')
Gy = convolve(G, fy, mode='same')
Ix = convolve(img_next, Gx, mode='same')
Iy = convolve(img_next, Gy, mode='same')


It = img_next - img
A = np.c_[(Ix * x).ravel(), (Ix * y).ravel(), Ix.ravel(),
           (Iy * x).ravel(), (Iy * y).ravel(), Iy.ravel()]
b = (-It).ravel()

res = np.linalg.solve(A.T @ A, A.T @ b)

# recover coefficients
A_ = np.array([[res[0]+1, res[1]], [res[3], res[4]+1]])
b_ = np.array([res[2], res[5]])
print('A:', A_)
print('b:', b_)

