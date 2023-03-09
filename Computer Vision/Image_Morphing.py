def generate_warp(size_H, size_W, Tri, A_Inter_inv_set, A_im_set, image):

    # Generate x,y meshgrid # comment provided in starter code:

    """
    print('\n shape of input parameters: ')
    print('A_Inter_inv_set shape: ', A_Inter_inv_set.shape)
    go = int(input('to continue enter 3: '))
    print('A_im_set shape:', A_im_set.shape)
    print('A_im_set: ', A_im_set)
    go = int(input('to continue enter 3: '))
    print('image:')
    print('image shape:', image.shape)
    print('image first element: ', image[0][0][0])    
    print('\n end input shapes\n')
    go = int(input('to continue enter 3: '))
    """
    
#VVVVVVVV #PURPOSE: GENERATE ALL PIXEL COORDS FROM (0,0) TO (W-1, H-1): VVVVVVVVVVVVV:
    # creates empty meshgrid using dimenions of the image:
    
    #print('\nbegin function generate_warp\n')    
    
    #print('height, image.shape[0]: ', image.shape[0])
   # print('width, image.shape[1] ', image.shape[1],'\n')
    
    
    x, y = np.meshgrid(range(size_W), range(size_H))
    #x, y = np.meshgrid(range(size_H), range(size_W))
    
    """
    print('x: ')
    print(x, '\n')
    print('len(x): ', len(x))
    go = int(input('x array of meshgrid computed; to continue enter 3: '))
    
    print('y: ')
    print(y, '\n')
    print('len(y): ', len(y))
    go = int(input('y array of meshgrid computed; to continue enter 3: '))
    """
    
    # Flatten the meshgrid
    
    
    xf = np.ravel(x)
    yf = np.ravel(y)
    #print('xf: ')
    #print(xf, '\n')
    #go = int(input('flatGrid calculated, display xf; to continue enter 3: '))
    
    #print('yf: ')
    #print(yf, '\n')    
    #go = int(input('flatGrid calculated, display yf; to continue enter 3: '))
    
    coordVals = np.array(list(zip(xf, yf)))
    #print('This is the output from the list(zip) code using xf, yf: \n ')
    #print(coordVals, '\n')
    #print('coordVals.shape: ', coordVals.shape)             
    #go = int(input('coordVals calculated; to continue enter 3: '))
    
#^^^^^^^^^^ END: GENERATE ALL PIXEL COORDS FROM (0,0) TO (W-1, H-1): ^^^^^^^^^^:    
 
    
# VVVVVVVVV PURPOSE: GENERATE TRI.SIMPLICES: VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV:    
 
    simplices = Tri.find_simplex(coordVals)
    #print('simplices: ')
    #print(simplices, '\n')
    #print('len(simplices): ', len(simplices))   
    
    # plot results:
    #delaunay_plot_2d(Tri)
    #plt.show()
    #plt.close()
    #go = int(input('simplices calculated; to continue enter 3: '))    
    
# ^^^^^^^ END: GENERATE TRI.SIMPLICES: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^:    

    
    # compute alpha, beta, gamma for all the color layers(3)
    
    brcCoor = A_Inter_inv_set[simplices]
    
   # print('barycentric coords based on inverse matrix: ')
   # print('size of barycentric coords ', len(brcCoor))
   # print('barycentric coords.shape: ', brcCoor.shape, '\n') 
    #print(brcCoor, '\n')
    #for i in range(10):
    #    print(brcCoor[i])
    #print('\n')
    
    brc = A_im_set[simplices]
   # print('barycentric coords based on A_im_set: ')
    #print('size of barycentric coords ', len(brc))
   # print('barycentric coords.shape: ', brc.shape, '\n') 
    #print(brc, '\n')
    #for i in range(10):
    #    print(brc[i])
    #print('\n')
    
    #go = int(input('barycentric coords calculated; to continue enter 3: '))    
    #print('\n')
    
    lineLimit = 10
    
    alphas = []
    lineCount = 0
    for a in range(len(brcCoor)):
    #for a in range(lineLimit):    
        alphas.append((brcCoor[a, 0, 0]*coordVals[a,0]) + (brcCoor[a, 0, 1]*coordVals[a, 1]) + brcCoor[a, 0, 2])
        #print('alphas[a]: ', alphas[a])
        #lineCount += 1
        #if(lineCount==10):
        #    break;
    #print('alphas size: ', len(alphas))
    alphas = np.array(alphas)
    #print('alphas shape: ', alphas.shape)    
    #go = int(input('alpha list calculated; to continue enter 3: '))   
   # print('\n')

    betas = []
    lineCount = 0
    
    # Beta = Ay*Px + By*Py + Cy 
    
    for b in range(len(brcCoor)):
    #for b in range(lineLimit):    
        betas.append((brcCoor[b, 1, 0]*coordVals[b, 0]) + (brcCoor[b, 1, 1]*coordVals[b, 1]) + brcCoor[b, 1, 2] )
          
        #print(betas[b])
        #lineCount += 1
        #if(lineCount==lineLimit):
           # break;
    #print('betas size: ', len(betas))
    betas = np.array(betas)
   # print(' betas shape: ', betas.shape)
   # go = int(input('betas list calculated; to continue enter 3: '))  
    #print('\n')
    
    gammas = []
    lineCount = 0
    for g in range(len(brcCoor)):
    #for g in range(lineLimit):    
        #gammas.append(coordVals[g, 0] + coordVals[g, 1] + 1)   #   '+1' ???????????????????????????????????????????????? 
            
        gammas.append(1 - (alphas[g] + betas[g])) # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< cx made 201019 @ 0859 hrs Pacific
                                                  # after resarching computation of barycentric coords, found that this
                                                  # forumula is commonly used. It certainly appears to work
       # print('coorVals[g, 0]: ', coordVals[g, 0])
       # print('coorVals[g, 1]: ', coordVals[g, 1])
       # print('gammas[g]: ', gammas[g])
        #lineCount += 1
        #if(lineCount==lineLimit):
        #    break;
    #print('gammas size: ', len(gammas))
    gammas = np.array(gammas)
    #print(' gammas shape: ', gammas.shape)
    #go = int(input('gammas list calculated; to continue enter 3: '))  
    #print('\n')
    
    # Find all x and y co-ordinates:
    px = []
    py = []
    chkVal = []
    for p in range(len(brcCoor)):
    #for p in range(lineLimit):    
        #           Ax               alphas           Bx            betas          Cx              gammas
        px.append((brc[p, 0, 0]*alphas[p]) +  (brc[p, 0, 1]*betas[p])  +  brc[p, 0, 2]*gammas[p] )
        #print('px[p] ', px[p])
        
        #           Ay       *        alphas   +        By     *       betas   +       Cx   *           gammas
        py.append((brc[p, 1, 0]*alphas[p]) +  (brc[p, 1, 1]*betas[p])  +  (brc[p, 1, 2]*gammas[p]))
        #print('py[p] ', py[p])
        
        #  1   =       alpha   +    beta  +    gammas
        chkVal.append(alphas[p] + betas[p] + gammas[p])
        #print('chkVal ', chkVal[p])
    
    px = np.array(px)
    py = np.array(py)
    chkVal = np.array(chkVal)
    

    # Generate Warped Images (Use function interp2) for each of 3 layers
    generated_pic = np.zeros((size_H, size_W, 3), dtype=np.uint8)
    
    #4_________________________________________________________________________

  # Generate Warped Images (Use function interp2) for each of 3 layers
  #generated_pic = np.zeros((size_H, size_W, 3), dtype=np.uint8)
  #for i in range(len(brcCoor)):  
    channel_1 = interp2(image[:,:,0], px, py)
    channel_2 = interp2(image[:,:,1], px, py)
    channel_3 = interp2(image[:,:,2], px, py)
    generated_pic[:,:,0] = channel_1.reshape((size_H, size_W))
    generated_pic[:,:,1] = channel_2.reshape((size_H, size_W))
    generated_pic[:,:,2] = channel_3.reshape((size_H, size_W))


    return generated_pic    