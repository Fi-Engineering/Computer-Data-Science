import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import convolve
import cv2

img = np.array([[0,0,1,1,1,0,0]])
img_next = np.array([[0,1,1,1,1,1,0]])

x = np.meshgrid(np.arange(img.shape[1]))[0]
x = x - img.shape[1] // 2
fx = np.array([[1, 0, -1]])
G = cv2.getGaussianKernel(13,4)

Ix = convolve(img_next, fx, mode='same')
Ix = convolve(Ix, G.T, mode='same')
I_t = img_next - img
A = np.c_[(Ix * x).ravel(), Ix.ravel()]
b = (-I_t).ravel()

res = np.linalg.solve(A.T @ A, A.T @ b)
print('A:', res[0]+1)
print('b:', res[1])

