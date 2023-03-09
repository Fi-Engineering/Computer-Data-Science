"""
    results:
        Theoretical probability : 0.41603404967903984
        Simulated probability   : 0.4156294715428503
        Simulated probability : 0.4156294715428503
        
"""

import random

#alpha: selfish miners mining power (percentage),
#gamma: the ratio of honest miners choose to mine on the selfish miners pool's block
#N: number of simulations run
def Simulate(alpha, gamma, N, seed):
    
    # DO NOT CHANGE. This is used to test your function despite randomness
    random.seed(seed)
  
    #the same as the state of the state machine in the slides 
    state=0 # given
    # the length of the blockchain
    ChainLength=0 # given
    # the revenue of the selfish mining pool
    SelfishRevenue=0 # given 
                     # 
    
    # You might need to define new variable to keep track of the number of hidden blocks:
    hiddenBlocks = 0
                    # 
                    # 

    #A round begin when the state=0
    for i in range(N):
        r=random.random()
        
        if state==0: # no branches
           
            if r<=alpha:               
                state = 1 # given 
            else:                               
                ChainLength += 1 # given                               
                state = 0 # given
                

        elif state==1:
            
            if r<=alpha:
                
                state = 2
                hiddenBlocks = 2
               
                                
            else:                       
                state = -1
                
                
        elif state==-1:
            
            if r<=alpha:
                SelfishRevenue += 2
                state = 0
                ChainLength += 2 # 
               

            elif r<=alpha+(1-alpha)*gamma:
                
                SelfishRevenue += 1
                state = 0
                
                ChainLength += 2

            else:
                state = 0
                SelfishRevenue += 0
                ChainLength += 2

        elif state==2:
           
            if r<=alpha:
                state += 1
                hiddenBlocks += 1 # 

            else:
                
                state = 0
                
                ChainLength += hiddenBlocks
                SelfishRevenue += hiddenBlocks 
                

        elif state>2:
            if r<=alpha:
                
                hiddenBlocks += 1
                state += 1                              
                                         
            else:
                                               
                state -= 1
                

    return float(SelfishRevenue)/ChainLength


""" 
  Uncomment out the following lines to try out your code
  DON'T include it in your final submission though.
"""

"""
#let's run the code with the follwing parameters!
alpha=0.35
gamma=0.5
Nsimu=10**7
seed = 100

print('\n\nmining simulation results\n\n')
#This is the theoretical probability computed in the original paper
print("Theoretical probability :",(alpha*(1-alpha)**2*(4*alpha+gamma*(1-2*alpha))-alpha**3)/(1-alpha*(1+(2-alpha)*alpha)))

print("Simulated probability :",Simulate(alpha,gamma,Nsimu, seed))

print('\n\nprocess terminated without exception\n\n')
"""
