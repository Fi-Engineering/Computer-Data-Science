# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 15:20:03 2020

@author: Owner

Project VI: Poisson Image Editing

version 2 using this source:
    https://github.com/willemmanuel/poisson-image-editing/blob/master/poisson.py


"""
# imports from learnerTemplate:
import scipy
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import scipy.sparse as sparse
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve
import scipy.signal as signal


# VVVVVVVVVVVVVVVVVVVVVVVVVVV PROVIDED FUNCTIONS: VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV


def PoissonMixing(sourceImg, targetImg, mask, offsetX, offsetY):
    """
    Wrapper function to put all steps together
    Args:
    - sourceImg, targetImg: source and target image
    - mask: masked area in the source image
    - offsetX, offsetY: offset of the mask in the target image
    Returns:
    - ResultImg: result image
    """
    # step 1: index replacement pixels
    indexes = getIndexes(mask, targetImg.shape[0], targetImg.shape[1], offsetX,
                         offsetY)
    # step 2: compute the Laplacian matrix A
    A = getCoefficientMatrix(indexes)

    # step 3: for each color channel, compute the solution vector b
    red, green, blue = [
        getSolutionVectMixing(indexes, sourceImg[:, :, i], targetImg[:, :, i],
                        offsetX, offsetY).T for i in range(3)
    ]

    # step 4: solve for the equation Ax = b to get the new pixels in the replacement area
    new_red, new_green, new_blue = [
        solveEqu(A, channel)
        for channel in [red, green, blue]
    ]

    # step 5: reconstruct the image with new color channel
    resultImg = reconstructImg(indexes, new_red, new_green, new_blue,
                               targetImg)
    return resultImg


def seamlessCloningPoisson(sourceImg, targetImg, mask, offsetX, offsetY):
    """
    Wrapper function to put all steps together
    Args:
    - sourceImg, targetImg: source and targe image
    - mask: masked area in the source image
    - offsetX, offsetY: offset of the mask in the target image
    Returns:
    - ResultImg: result image
    """
    # step 1: index replacement pixels
    indexes = getIndexes(mask, targetImg.shape[0], targetImg.shape[1], offsetX,
                         offsetY)
    # step 2: compute the Laplacian matrix A
    A = getCoefficientMatrix(indexes)

    # step 3: for each color channel, compute the solution vector b
    red, green, blue = [
        getSolutionVect(indexes, sourceImg[:, :, i], targetImg[:, :, i],
                        offsetX, offsetY).T for i in range(3)
    ]

    # step 4: solve for the equation Ax = b to get the new pixels in the replacement area
    new_red, new_green, new_blue = [
        solveEqu(A, channel)
        for channel in [red, green, blue]
    ]

    # step 5: reconstruct the image with new color channel
    resultImg = reconstructImg(indexes, new_red, new_green, new_blue,
                               targetImg)
    return resultImg


def PoissonTextureFlattening(targetImg, mask, edges):
    """
    Wrapper function to put all steps together
    Args:
    - targetImg: target image
    - mask: masked area in the source image
    - offsetX, offsetY: offset of the mask in the target image
    Returns:
    - ResultImg: result image
    """
    # step 1: index replacement pixels
    indexes = getIndexes(mask, targetImg.shape[0], targetImg.shape[1])
    # step 2: compute the Laplacian matrix A
    A = getCoefficientMatrix(indexes)

    # step 3: for each color channel, compute the solution vector b
    red, green, blue = [
        getSolutionVectTexture(indexes, targetImg[:, :, i], mask, edges).T for i in range(3)
    ]

    # step 4: solve for the equation Ax = b to get the new pixels in the replacement area
    new_red, new_green, new_blue = [
        solveEqu(A, channel)
        for channel in [red, green, blue]
    ]

    # step 5: reconstruct the image with new color channel
    resultImg = reconstructImg(indexes, new_red, new_green, new_blue,
                               targetImg)
    return resultImg

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^ END PROVIDED FUNCTIONS ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


# VVVVVVVVVVVVVVVVVVVVVVVVVVV REQUIRED CODING VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV


#   getIndexes(dummy_mask, dummy_mask.shape[0], dummy_mask.shape[1])
def getIndexes(mask, targetH, targetW, offsetX=0, offsetY=0):
    """ Creates indexes in the target image, each replacement pixel in the
    target image would get index starting from 1, other pixels get 0 in the indexes.

    Args:
    mask: SrcH * SrcW, logical mask of source image
    targetH, targetW: int, height and width of target image
    offsetX, offsetY: int, offset of replacement pixel area from source to target

    Return:
    indexes: targetH * targetW, indexes of target image
    """
    # IMPLEMENT HERE
    # you might find numpy.meshgrid and numpy.arange useful
    print('\n inside getIndexes:\n')
    
    """
    print('\n len(mask): ', len(mask))
    print('\nmask:')
    print(mask, '\n')
    
    print('targetH', targetH)
    print('targetW', targetW)
    print()
    print('offsetX: ', offsetX)
    print('offsetY: ', offsetY, '\n')
    """
    
    indexes = []
    row = []
    ndx = 1
    for r in range(targetH):
    #for r in range(targetH + offsetY):    
        for c in range(targetW):
        #for c in range(targetW + offsetW):    
            if(mask[r, c]==False):
                row.append(0)
            else:
                row.append(ndx)
                ndx += 1
        indexes.append(row)
        row = []
    
    indexes = np.array(indexes).reshape((targetH, targetW))
    return indexes


# helpers for getCoefficientMatrix(indexes):
def getSur(index):
    #print('inside getSur, index = ', index)
    i, j = index  # too many values to unpack, expected 2
    #print('i, j: ', i, j)
    return [(i+1,j),(i-1,j),(i,j+1),(i,j-1)] 

# indices of omega values, where mask = 1:
def maskIndices(mask):
    nonzero = np.nonzero(mask)
    print('nonzero: ')
    print(nonzero, '\n')
    nz0 = np.array(nonzero[0])
    nz1 = np.array(nonzero[1])
    
    maskInxs = np.dstack((nz0, nz1))
    maskInxs = maskInxs.reshape((-1,2))
 
    #print(' maskInxs')
    #print( maskInxs, '\n')
    return  maskInxs    
    
    
def getCoefficientMatrix(indexes, mask):
  """
  constructs the coefficient matrix(A in Ax=b)
  
  Args: 
  indexes: targetH * targetW, indexes of target image starting from 1, 0 if not in target area 
  
  returns:
  coeffA: N * N(N is max index), a matrix corresponds to laplacian kernel, 4 on the diagonal and -1 for each neighbor
  """
  # IMPLEMENT HERE
  # the coefficient matrix is by nature sparse. consider using scipy.sparse.csr_matrixr


  coeffA = []
  
  coeffDim = 0
  for i in range(len(indexes)):
      for j in range(len(indexes[i])):
          if(indexes[i][j]>0):
              coeffDim += 1
                            
  #print('coeffDim: ', coeffDim, '\n')
  
  coeffA = csr_matrix((coeffDim, coeffDim), dtype=np.int8).toarray()
        
  # note: if all values are 0, the csr_matrix structure displays nothing  
  #print('initial coeffA: ')
  #print(coeffA, '\n')
  
  n = len(mask)
  print('len(mask)', len(mask), '\n')
    
  print('indices of omega, where mask = 1')
  maskNdx = maskIndices(mask)
  print('maskNdx: ')
  print(maskNdx, '\n')
  #coeffA = lil_matrix((n, n)) 
  #print('A: ')
  #print(coeffA, '\n')
      
  # find indices ndxNpy that translate to A[i,j]:
  
  maskNdxList = maskNdx.tolist()
  print('maskNdxList ')
  print(maskNdxList , '\n')
   
  for i in range(len(maskNdx)):    
        print('>>>>>>>>>>>>>>>>>>> start main loop, i= ', i, ' maskNdx[i]: ', maskNdx[i], '\n')        
        coeffA[i,i] = 4 # Fill diagonal with 4s
               
        for x in getSur(maskNdxList[i]):    
                print('x in getSur: ', x)
                print('x[0], x[1]: ', x[0], x[1])
                x = list(x)
               
                if(x not in maskNdxList):    
                    print('x not in indexes')
                    continue
           
                j = maskNdxList.index(x)
                #print('j: ', j)
                coeffA[i][j] = -1
              
  print('\nA: ')
  print(coeffA, '\n')
  
  """
  print('sparse to dense: ')
  Adense = coeffA.todense()  # AttributeError: 'numpy.ndarray' object has no attribute 'todense'
  print(Adense, '\n')
  print('sparse to array: ')
  Atoarray = coeffA.toarray()
  print(Atoarray, '\n')
  """
    
  go = int(input('at end of getCoefficientMatrix; to continue enter 3: ')) 
      
     
  return coeffA

#   getSolutionVect(indexes, dummy_src_img, dummy_target_img, 0, 0)
#def getSolutionVect(indexes, source, target, offsetX, offsetY):
def getSolutionVect(indexes, source, target, offsetX, offsetY):    
    """
    constructs the target solution vector(b in Ax=b) 
    
    Args:
    indexes:  targetH * targetW, indexes of replacement area
    source, target: source and target image
    offsetX, offsetY: offset of source image origin in the target image

    Returns:
    solution vector b (for single channel)
    """
    
    # IMPLEMENT HERE
    # 1. get Laplacian part of b from source image
    # 2. get pixel part of b from target image
    # 3. add two parts together to get b
    
    # using material from walkthrough:
        
# vvvvvvvvvvvvvvvvvvvv Laplacian part of b: vvvvvvvvvvvvvvvvvvv
        
    lap = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
    
    print('source: ')
    print(source, '\n')
    go = int(input('after source; to continue enter 3: '))
    print()
    
    print('target: ')
    print(target, '\n')
    go = int(input('after target; to continue enter 3: '))
    print()
    
    
    srcLap = signal.convolve(source, lap, 'same')
    print('srcLap: ')
    print(srcLap, '\n')
    
    offsetX, offsetY = 0, 0
    Y, X = np.nonzero(indexes)
    print('Y: ')
    print(Y, '\n')
    print('X: ')
    print(X, '\n')
    
    Y_src, X_src = Y - offsetY, X - offsetX
    print('Y_src')
    print(Y_src, '\n')
    print('X_src')
    print(X_src, '\n')
    
    lapFinal = srcLap[Y_src, X_src]
    print('srcLap: ')
    print(lapFinal, '\n')
    
    go = int(input('after srcLap; to continue enter 3: '))
    
# ^^^^^^^^^^^^^^^^^^^^^^ end laplacian part of b ^^^^^^^^^^^^^^^    

# vvvvvvvvvvvvvvvvvvvvvvv piexl part of b vvvvvvvvvvvvvvvvvvvvvvv    
    offsetX, offsetY = 0, 0
    Y, X = np.nonzero(indexes)
    print('Y: ')
    print(Y, '\n')
    print('X: ')
    print(X, '\n')
    N = np.count_nonzero(indexes)
    print('N: ')
    print(N, '\n')
    go = int(input('after Y, X, N; to continue enter 3: '))
    print()
    
    leftNdx = np.zeros(N, dtype=np.int32)
    print('leftNdx')
    print(leftNdx, '\n')
    leftVal = np.zeros(N, dtype=np.float32)
    print('leftVal')
    print(leftVal , '\n')
    valid = X - 1 >= 0
    print('valid')
    print(valid , '\n')
    leftNdx[valid] = indexes[Y[valid], (X - 1)[valid]] # same as before
    print('leftNdx[valid]')
    print(leftNdx[valid], '\n')
    
    good = np.logical_and(valid, leftNdx == 0)
    print('good')
    print(good, '\n')
    
    leftVal[good] = target[Y[good], (X - 1)[good]]
    print('leftVal[good]]')
    print(leftVal[good], '\n')
   
    # copied verbatim from Project_6_walkthrough: doesn't work as written:
    b = lapFinal + + leftVal + right_val + up_val + down_val
    # how to compute right_val, up_val, down_val are missing; no clues apparent
    
    go = int(input('after lapResult; to continue enter 3: '))
    print()
       
    return b
    
    


def solveEqu(A, b):
  """
  solve the equation Ax = b to get replacement pixels x in the replacement area
  Note: A is a sparse matrix, so we need to use coresponding function to solve it

  Args:
  - A: Laplacian coefficient matrix
  - b: target solution vector
  
  Returns:
  - x: solution of Ax = b
  """
  # IMPLEMENT HERE
  # you may find scipy.sparse.linalg.spsolve
  
  coeffDim = len(A)
  
  A = csr_matrix((coeffDim, coeffDim), dtype=np.int8).toarray()
  
  f = scipy.sparse.linalg.spsolve(A, b) # ValueError: matrix - rhs dimension mismatch ((16, 16) - 1)
  
  return f



def reconstructImg(indexes, red, green, blue, targetImg):
    """
    reconstruct the target image with new red, green, blue channel values in th
    e indexes area

    red, green, blue: 1 x N, three chanels for replacement pixels
    """
    # 1. get nonzero component in indexes

    # 2. stack three channels together with numpy dstack

    # 3. copy new pixels in the indexes area to the target image 
    # use numpy copy to make a copy of targetImg, otherwise the original targetImg might change, too



def getSolutionVectMixing(indexes, source, target, offsetX, offsetY):
    """
    constructs the target solution vector(b in Ax=b) 
    
    Args:
    indexes:  targetH * targetW, indexes of replacement area
    source, target: source and target image
    offsetX, offsetY: offset of source image origin in the target image

    Returns:
    solution vector b (for single channel)
    """
    # IMPLEMENT HERE
    # almost the same as getSolutionVect, need to change the Laplacian part of b


def getSolutionVectTexture(indexes, target, mask, edges):
    """
    constructs the target solution vector(b in Ax=b) 
    
    Args:
    indexes:  targetH * targetW, indexes of replacement area
    source, target: source and target image
    offsetX, offsetY: offset of source image origin in the target image

    Returns:
    solution vector b (for single channel)
    """
    # IMPLEMENT HERE
    # almost the same as getSolutionVect, need to change the Laplacian part of b

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^ END REQUIRED CODING ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# functions from other sources:
    
def preview(source, target, mask):
    return (target * (1.0 - mask)) + (source * (mask))    


def main():
    
#    added imports:
    from skimage.color import rgb2gray
    from skimage import feature
    
     # displays all values in each numpy array:
    import sys     
    np.set_printoptions(threshold=sys.maxsize)
    
    print('\n')
    print('Project 6: Poisson Image Editing\nInside Main Function\n')
    
    

# VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV READ INPUT FILES VVVVVVVVVVVVVVVVVVVVVVVVVVV
    # read the first set of input files:
    # archived for later use    
    
    """
    src_path = 'source_3.jpg'
    src = np.array(Image.open(src_path).convert('RGB'), 'f') / 255
    target_path  ='target_3.jpg'
    target = np.array(Image.open(target_path).convert('RGB'), 'f') / 255
    offsetX = 40
    offsetY = 20
    mask_path = 'mask_3.bmp'
    mask = np.array(Image.open(mask_path)) > 0
    #mask = Image.open(mask_path)
    print('mask: ')
    print(mask, '\n')
    go = int(input('inside main; to continue enter 3: ')) 
    #result = seamlessCloningPoisson(src, target, mask, offsetX, offsetY)
    #plt.imshow(result)
    #plt.imshow(mask)
    #plt.show()
    #plt.close()
    #cloned = Image.fromarray((np.clip(result, 0, 1) * 255).astype(np.uint8))
    #cloned.save('cloned.png')
    #files.download('cloned.png')
    
    # from Will Emmanuel; fails with current input 
    #print('preview: ')
    #print(preview(src, target, mask), '\n')
    """
    
# new lines as of 201021:    
   
    dummy_mask = np.zeros((8, 8), dtype=bool)
    dummy_mask[2:6, 2:6] = 1
    print('\ndummy_mask: ')
    print(dummy_mask , '\n')
    print('dummy_mask.shape[0]: ', dummy_mask.shape[0])
    print('dummy_mask.shape[1]: ', dummy_mask.shape[1], '\n')
  
   
    # from Will Emmanuel: https://github.com/willemmanuel/poisson-image-editing/blob/master/main.py
    # Normalize mask to range [0,1]
    #mask = np.atleast_3d(mask_img).astype(np.float) / 255.
    #mask = np.atleast_3d(mask).astype(np.float) / 255.
    mask = np.atleast_3d(dummy_mask).astype(np.float) / 255.
    #print('Emmanuel mask:')
    #print(mask, '\n')
    # Make mask binary
   # mask[mask != 1] = 0
    mask[mask >0] = 1
    mask[mask != 1] = 0
    
    # Trim to one channel
    mask = mask[:,:,0]
    print('Emmanuel mask:')
    print(mask, '\n')
    dummy_mask = mask
    go = int(input('inside main; to continue enter 3: '))       
    
   
    dummy_target_img = np.arange(64).reshape(8, 8)
    print('\ndummy_target_img.shape: ', dummy_target_img.shape, '\n')
    print('dummy_target_img: ')
    print(dummy_target_img, '\n')
    
    
    dummy_src_img = np.load('dummy_src_img.npy') # generated by np.random.randint(0, 256, size=(8, 8))
    print('dummy_src_img :')
    print(dummy_src_img , '\n')
    
    go = int(input('inside main; to continue enter 3: '))  
  
    indexes = getIndexes(dummy_mask, dummy_mask.shape[0], dummy_mask.shape[1])
    print('\nindexes from getIndexes: ')
    #for r in range(dummy_mask.shape[0]):
    #    for c in range(dummy_mask.shape[1]):
    #        print(indexes[r][c], ' ', end='')
    #    print()
    print(indexes, '\n')    
    
    # compare with index.npy:
    ndxNpy = np.load('index.npy')
    print('ndxNpy: ')
    print(ndxNpy, '\n')
    
    go = int(input('after indexes; to continue enter 3: '))  
    print()
    
    Anpy = np.load('A.npy')
    print('Anpy: ')
    print(Anpy, '\n') 
    
    #A = getCoefficientMatrix(indexes)
    A = getCoefficientMatrix(indexes, dummy_mask) # WillEmmanuel
    print('coeffA:')
    print(A, '\n')
    # compare with A.npy
    
    go = int(input('after Anpy; to continue enter 3: ')) 
    print()
         
    b = getSolutionVect(indexes, dummy_src_img, dummy_target_img, 0, 0)
    
    print('b: ')
    print(b, '\n')
    
    # compare with b.npy
    bNpy = np.load('b.npy')
    print('len(bNpy: ', len(bNpy), '\n')
    print(bNpy, '\n')
    
    go = int(input('after bNpy; to continue enter 3: '))  
 
    f = solveEqu(A, bNpy)
    print('result: ')
    print(f, '\n')
    
    
    go = int(input('end first new lines of 201021; to continue enter 3: '))  

    # archived for later use:
    """    
    src_path = 'source_2.jpg'
    src = Image.open(src_path).convert('RGB')    
    src = np.array(src, 'f') / 255
    
    target_path  = 'target_2.jpg'
    target = Image.open(target_path).convert('RGB')
    target = np.array(target, 'f') / 255
    offsetX = 10
    offsetY = 130

    mask_path = 'mask_2.bmp'
    mask = Image.open(mask_path)
    mask = np.array(mask) > 0
    
    result = PoissonMixing(src, target, mask, offsetX, offsetY)
    plt.imshow(result)
    plt.show()
    mixed = Image.fromarray((np.clip(result, 0, 1) * 255).astype(np.uint8))
    mixed.save('mixed.png')
    #files.download('mixed.png')     
    """

#   new lines as of 201021:
    """
    target_path  ='bean.jpg'
    target = np.array(Image.open(target_path).convert('RGB'), 'f') / 255
    edges = feature.canny(rgb2gray(target))
    plt.imshow(edges)
    plt.show()
    plt.close()
    mask_path = 'mask_bean.bmp'
    mask = np.array(Image.open(mask_path)) > 0
    resultFlat = PoissonTextureFlattening(target, mask, edges)
    plt.imshow(resultFlat)
    plt.show()
    plt.close()
    #flatten = Image.fromarray((np.clip(result, 0, 1) * 255).astype(np.uint8))
    
    #flatten.save('flatten.png')
    #files.download('flatten.png')
    """
    
    print('\nprocess terminated without exception\n')
    print('\n\n')


main()







