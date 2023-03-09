# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 06:33:28 2021

@author: Alex I
   
    ESE 542 Project 1:
    



"""

import os
import sys

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

import csv

#%matplotlib inline

import distutils
from distutils import util


def go():
    x = input('to continue enter 3: ')
    if(x == "3"):
       # print('\ncontinuing\n')
        pass
    else:
        print('\nProcess terminated by user\n')
        sys.exit(0)



def main():
    
    
    
    print('\nESE 542 Project  1: \n')
    
    # 2. Load the College dataset using pandas:
    
    collegeDF = pd.read_csv('College.csv')
    
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    
    # 3. Use the head() function to view the data:
    print('df head:')    
    print(collegeDF.head(), '\n')
    go()
    
    # 4. Use Name field as new index of the dataframe: 
    collegeDF.set_index ("Names", inplace = True )
    
    # 5. Use the head() function again:
    print('df head:')    
    print(collegeDF.head(), '\n')
    go()
    
    # 6. Use the info() function to check and produce a numerical summary of your variables.
    print('df.info()')
    print(collegeDF.info(), '\n')
    go()
    
    # 7. Examine if there are any duplicate rows and drop them if needed.
    collegeDF.drop_duplicates(keep = False, inplace = True)
    print('after dropping duplicate rows, df head:')    
    print(collegeDF.head(), '\n')
    print('after dropping duplicate rows, df.info()')
    print(collegeDF.info(), '\n')
    go()
    
    # 8. Replace any missing values in the `Apps' column with 0:
    print('detect missing data in "Apps" column:')
    print(collegeDF.isnull(), '\n')
    # replacing any missing data in Apps column with 0:
    collegeDF['Apps'] = collegeDF['Apps'].fillna(0)
    print()
    go()
    
    #9. Find the college with the least out-of-state tuition and name this variable
        # college_least_tuition.
    college_least_tuitionVal = collegeDF['Outstate'].min()
    print('college_least_tuition, minimum value of column "Outstate": ',college_least_tuitionVal, '\n')
   
    x  = collegeDF.loc[collegeDF['Outstate'] == college_least_tuitionVal]
    print(x)
    print('type: ', type(x))
    indx = x.index
    print('indx: ', indx[0])
    college_least_tuition = indx[0]
    print('college_least_tuition: ',college_least_tuition ,'\n')
    go()
 
    #10. From the original dataframe, select the `PhD' column and name this new dataframe phd_column.
        #Find the length of this dataframe and assign this value to the variable phd_column_length.
    
   # phd_column = pd.dataframe(collegeDF["PhD"])
    phd_column = collegeDF[["PhD"]].copy()
    print('phd_column type: ', type(phd_column), '\n')
    
    phd_column_length = len(phd_column.index)
    print('phd_column_length: ', phd_column_length, '\n')
    
    go()

    # 11. From the original dataframe, select both the `Private' and `Top10perc' columns, and slice them
        # such that only the rows with index 15 and 16 remain. Name this dataframe private_top10.
        # From this dataframe, nd the length of the ltered `Private' column and name this variable private_column_length.
    
    private_top10 =  collegeDF[['Private', 'Top10perc']].copy()
    print('private_top10.head(): ',  private_top10.head(), '\n' )
    private_top10 =  private_top10[15:17 ]
    print('private_top10.head(): ',  private_top10.head(), '\n' )
    private_column_length = len(private_top10.index)
    print('private_column_length: ',private_column_length,'\n')
    go()
    
    # 12. From the original dataframe, select the row that only contains data about the "University of Pennsylvania". Name this dataframe penn.
    
    ndxs = collegeDF.index
    print('ndxs: ')
    print(ndxs, '\n')
    # find index number by index label
    # find list index by value
    ndx = list(ndxs).index("University of Pennsylvania")
    print('ndx: ', ndx, '\n')
    
    #df.loc[[2]] # get index by label
    penn = collegeDF.iloc[[ndx]]
    print('penn: ')
    print(penn, '\n')
    go()

    # 13. From the original dataframe, select the rows that contain all colleges with the substring
    # Penn" in their names. The "P" should be capitalized. Name this dataframe many_penns.

    subString = "Penn"
    subList = [stng for stng in list(ndxs) if subString in stng] 
    #print('subList: ')
    #print(subList, '\n')
    # use subList to find indexes of the selected rows to put into a new df:
        
    #many_penns = collegeDF[subList]
    # df = df.loc[df1.index]
    many_penns = collegeDF.loc[subList]
          
    print('many_penns: ')
    print(many_penns, '\n')    
    go()
    
    
    
    print('\n')
    print('\n')
    print('\n')
    print('\n')
    
    
    
    print('\n')
    print('Process terminated without exception. \n')
    print('\n')


main()



