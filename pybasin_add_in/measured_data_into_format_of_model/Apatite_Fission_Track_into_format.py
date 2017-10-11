# -*- coding: utf-8 -*-
"""
Created on Mon Sep 05 16:02:01 2016

@author: Tom
"""
## input: 'zk_apa.csv', 'apatite_complete.xls'
## output 'parallel_run_wells.csv', 'aft_samples.csv'
##
# brings zk_apa.csv and apatite_complete.xls into format for reading in pybasin

import pandas as pd
import os

# read result of wells.py
df_wellnumber = pd.read_csv('zk_apa.csv')
#print df_wellnumber
#df_wellnumber = pd.read_csv('zk_apa.csv')

# read complete strata 

df_depth = pd.read_excel('apatite.xls')
#print df_depth
#df_depth = pd.read_excel('apatite.xls')
df_depth.set_index('wellnumber',inplace=True)

# get back all single well data 
list_wellnumbers = []
list_wellname = []

# go through wellnumbers
print df_wellnumber

for index, row in df_wellnumber.iterrows():
    
    # go through df_depth and get all with same coordinates
    
    ex = df_depth.get_value(row[1], col='EX', takeable=False)
    ny = df_depth.get_value(row[1], col='NY', takeable=False)    
    
    # get name of this well
    wellname = row.ix[0]
     
    # append to list when coordiantes are the same 
    for ind, rows in df_depth.iterrows():        
        if ex == df_depth.loc[ind,'EX']:
            if ny == df_depth.loc[ind,'NY']:               
                list_wellnumbers.append(ind)
                list_wellname.append(wellname)
        print list_wellname #next well is faulty, delete from zk_apa.csv manually
      
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
out = 'wellnumber_into_apatite/aft_samples.csv'

if os.path.isfile(out) is True:
    os.remove(out)

txtfile = open(out,'a+')
txtfile.writelines("well,sample,depth,n_grains,AFT_age,AFT_age_stderr_plus,AFT_age_stderr_min,P_X2,data_type,length_mean,length_std,n_lengths,kinetic_parameter,kinetic_param_min,kinetic_param_max,ref,EX,NY,wellnumber\n")

sample_x = 1

print df_join
# fills file with lines from df_join
for index, row in df_join.iterrows():    
    #if type(df_join.ix[index,'depth']) is (float or int):   
            well = str(df_join.ix[index,'wellname'])
            sample = str(sample_x)
            sample_x += 1
            depth = str(df_join.ix[index,'depth'])
            n_grains = str(df_join.ix[index,'n_grains'])
            AFT_age = str(df_join.ix[index,'AFT_age']) 
            AFT_age_stderr_plus = str(df_join.ix[index,'AFT_age_stderr_plus'])
            AFT_age_stderr_min = str(df_join.ix[index,'AFT_age_stderr_min'])
            P_X2 = ''
            data_type = str(df_join.ix[index,'data_type'])
            length_mean = str(df_join.ix[index,'length_mean'])
            length_std = str(df_join.ix[index,'length_std'])
            n_lengths = str(df_join.ix[index,'n_lengths'])
            kinetic_parameter = str(df_join.ix[index,'kinetic_parameter'])
            kinetic_param_min = str(df_join.ix[index,'kinetic_param_min'])
            kinetic_param_max = str(df_join.ix[index,'kinetic_param_max'])
            ref = str(df_join.ix[index,'ref'])
            
            #new
            ex1 = str(df_join.ix[index,'EX'])
            ny1 = str(df_join.ix[index,'NY'])
            wellnumb = str(df_join.ix[index,'wellnumber'])
            
            new_line = well+','+sample+','+depth+','+n_grains+','+AFT_age+','+AFT_age_stderr_plus+','+AFT_age_stderr_min+','+P_X2+','+data_type+','+length_mean+','+length_std+','+n_lengths+','+kinetic_parameter+','+kinetic_param_min+','+kinetic_param_max+','+ref+','+ex1+','+ny1+','+wellnumb
           # new_line = (well + sample + 'depth' + ',,' + AFT_age + ',,,,,,,,,,,')  
            
            txtfile.writelines(new_line + "\n")
txtfile.close()

# output parallel_well as wells, which are having equal properties are deleted (drop_duplicate)
well_output = 'wellnumber_into_apatite/parallel_run_wells.csv'
df_par = df_join
df_par = df_par.loc[:,['wellname']] 
df_par = df_par.drop_duplicates()
df_par = df_par.rename(columns = {'wellname':'well'}, inplace = False)
df_par.to_csv(path_or_buf=well_output,sep=',',index=None,mode='a', header=True)

print 'done'
