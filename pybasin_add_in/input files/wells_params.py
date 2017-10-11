"""
Created on Aug 09 23:37:21 2016

@author: Tom

Model setup for creating well data

edit this file to change the model parameters for wells.py
"""

import arcpy
import os
import random


##################################input parameters
##################################
def order_of_rasters(a):
    #  comp/vr, salt, ,apatite, etopo
    a = a[6],a[9],a[10],a[1],a[11],a[4],a[2],a[12],a[5],a[3],a[13],a[7],a[8],a[0],a[14],a[15],a[16],a[17],a[18]
    # mit comp_wells and salt
    #a = a[6],a[9],a[10],a[1],a[11],a[4],a[2],a[12],a[5],a[3],a[13],a[7],a[8],a[0]
    # mit salt
    #a = a[5],a[8],a[9],a[0],a[10],a[3],a[1],a[11],a[4],a[2],a[12],a[6],a[7]
    # ohne salt
    #a = a[5],a[7],a[8],a[0],a[9],a[3],a[1],a[10],a[4],a[2],a[11],a[6]
    # q_d_,ter,ucr,lcr
    #a = a[1],a[2],a[3],a[0]
   
    return a

input_dir = 'input'
output_dir = 'output'
output_of_raster = 'raster_output'
output_shapefile = 'wells.shp'

###################################### strata options
# how many strata must be there
# choose 0 if not necessary
min_strat_units = 2      

# which strata must be included
# choose ['0'] if not necessary
condition_list = ['0'] 

# length of name
length_of_input_name = 4

raster_for_extent =  'q_d_.asc'

# salt -> put salt.asc into input folder
# name of raster (zzz forces last coloum...)
salt = 'salt'
# value of salt in raster
saltnr = 1

# determines, how big the chunks of data are getting
# not more than 100 000
group_data = 50000

cellsize = 50000

raster_for_extent = input_dir + '/' + raster_for_extent
dir_specifier = str(cellsize / 1000) 

############### thickness

# delete well, when m thickness
delete_total_litho_below_meter = 250

delete_singe_litho_below_meter = 5

change_single_litho_below_meter = 20

#dir_specifier = str(random.randint(0,1000))
output_dir = output_dir + dir_specifier

##################################
##################################

# location of files and creating of such

if os.path.exists(input_dir) is False:
    print 'Input folder is not existing.'
    
if os.path.exists(output_dir) is False:
    print 'Output folder is not existing and gets created.'
    os.makedirs(output_dir)
else: 
    output_dir = output_dir + str(random.randint(0,1000))
    print 'Output folder already existing and new output folder gets created,'
    print 'with the name ' + output_dir + '.'
    
if os.path.exists(output_dir + '/' + output_of_raster) is False:
    os.makedirs(output_dir + '/' + output_of_raster)   
    
pickle = output_dir + '/' + 'pickle'
if os.path.exists(pickle) is False:
    print 'Pickle folder is not existing and gets created.'
    os.makedirs(pickle)
    
# produces arcpy environement
arcpy.env.workspace = os.getcwd()
wkspc = arcpy.env.workspace

# creates empty shapefile
output_shapefile = output_dir + '/' + output_shapefile
if os.path.isfile(output_shapefile) is False:
    arcpy.CreateFeatureclass_management(wkspc, output_shapefile, "POINT")
else: 
    print 'No shapefile created.'
    
# compare wells
# name of raster (zzz forces last coloum...)
comp_wells = 'comp'
# comp_output
comp_output = output_dir + '/comp_wells.csv'

# heatflow zechstein
ze_hf = 'ze_hf'
# comp_output
ze_hf_output = output_dir + '/ze_hf_wells.csv'

# apatite
apatite = 'zk_apa'
apatite_output = output_dir + '/zk_apa.csv'

# temperature
temperature = 'zk_temp'
temp_output = output_dir + '/zk_temp.csv'

# porosity
porosity = 'zk_poro'
porosity_output = output_dir + '/zk_poro.csv'

