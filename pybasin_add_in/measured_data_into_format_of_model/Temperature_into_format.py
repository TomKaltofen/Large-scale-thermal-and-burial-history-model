# -*- coding: utf-8 -*-
"""
Created on Mon Sep 05 16:02:01 2016

@author: Tom

input: 'zk_temp.csv', 'temp_complete.xls'
output 'parallel_run_wells.csv', 'vitrinite_reflectance.csv'

"""

import pandas as pd
import os

# read result of wells.py
df_wellnumber = pd.read_csv(outi+'/zk_temp.csv')

# read complete strata 
df_depth = pd.read_excel('wellnumber_into_temp/temp_complete.xls')
df_depth.set_index('wellnumber',inplace=True)

# get back all single well data 
list_wellnumbers = []
list_wellname = []
# go through wellnumbers
for index, row in df_wellnumber.iterrows():
        
    # go through df_depth and get all with same coordinates
    ex = df_depth.get_value(row[1], col='EX', takeable=False)
    print ex
    ny = df_depth.get_value(row[1], col='NY', takeable=False)    
    
    # get name of this well
    wellname = row.ix[0]
    
    # append to list when coordiantes are the same 
    for ind, rows in df_depth.iterrows():        
        if ex == df_depth.loc[ind,'EX']:
            if ny == df_depth.loc[ind,'NY']:               
                list_wellnumbers.append(ind)
                list_wellname.append(wellname)
      
print 'Created list for appending.'
# make df from wellnumbers and wellname again         
df_of_well_name_and_well_number = pd.DataFrame({'wellname' : list_wellname, \
 'wellnumber' : list_wellnumbers})
df_of_well_name_and_well_number.set_index('wellnumber',inplace=True)

# takes from complete list only those with same coordinates
df = df_depth.ix[list_wellnumbers]

# merges and then drops duplicates
df_join = df_of_well_name_and_well_number.merge(df,left_index='wellnumber',right_index='wellnumber',copy=False)
df_join = df_join.reset_index(level=0,inplace=False)
df_join = df_join.drop_duplicates(subset='wellnumber',keep='first')

# preparing output file
out = 'wellnumber_into_temp/temperature_data.csv'

if os.path.isfile(out) is True:
    os.remove(out)

txtfile = open(out,'a+')
txtfile.writelines("well,depth,temperature,temperature_unc_1sigma,data_type,wellnumb,EX,NY\n")

# fills file with lines from df_join
for index, row in df_join.iterrows():    
    if type(df_join.ix[index,'temperature']) is (float or int):     
            well = str(df_join.ix[index,'wellname'])
            depth = str(df_join.ix[index,'depth'])
            temperature = str(df_join.ix[index,'temperature'])
            temperature_unc_1sigma = str(df_join.ix[index,'temperature_unc_1sigma'])
            data_type = str(df_join.ix[index,'data_type'])
            
            #new
            wellnumb = str(df_join.ix[index,'wellnumber'])
            ex1 = str(df_join.ix[index,'EX'])
            ny1 = str(df_join.ix[index,'NY'])

            new_line = well+','+depth+','+temperature+','+temperature_unc_1sigma+','+data_type+','+wellnumb+','+ex1+','+ny1
        
            txtfile.writelines(new_line + "\n")
txtfile.close()

# output parallel_well as wells, which are having equal properties are deleted (drop_duplicate)
well_output = 'wellnumber_into_temp/parallel_run_wells.csv'
df_par = df_join
df_par = df_par.loc[:,['wellname']] 
df_par = df_par.drop_duplicates()
df_par = df_par.rename(columns = {'wellname':'well'}, inplace = False)
df_par.to_csv(path_or_buf=well_output,sep=',',index=None,mode='a', header=True)

print 'done'
