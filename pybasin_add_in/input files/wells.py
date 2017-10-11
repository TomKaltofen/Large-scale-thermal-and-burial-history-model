"""
Created on Aug 09 23:37:21 2016

@author: Tom

This script extracts single wells from thickness rasters into pybasin format.

All rasters have to be in '.asc' format.
Addtionally, all rasters have to be in a meter coordinate system, not degree.

For ignoring areas, add it to the 'salt.asc'.

comp = VR

"""

import os
import pandas as pd

### timer
import timeit
start = timeit.default_timer()

# arcmap packages
import arcpy
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial") 
arcpy.CheckOutExtension("3D")

#import functions
import wells_params
import wells_functions

# creates raster file and sorts them from input
list_of_rasters = wells_functions.read_input_rasters()

# helps when rasters not sorted to read in
help = wells_functions.helping(list_of_rasters)

# list of rasters, which is ordered by user in wells_params.order_of_rasters
list_of_rasters = wells_params.order_of_rasters(list_of_rasters)

# creates wells without content, but with complete well_name coloum
wells_functions.create_empty_wells()

# extracts values to points with arcpy function
print 'Combine raster data to one shapefile'
s = timeit.default_timer()
ExtractMultiValuesToPoints(wells_params.output_shapefile,list_of_rasters,"NONE") # no interpolation
s2 = timeit.default_timer()
print "Time rasters to shapefile " + str(s2 - s) + ' min'

# creates table from shapefile
print 'Shapefile -> Table'
liste_of_all_fields = arcpy.ListFields(wells_params.output_shapefile) 

# create variables and searchcursor / cursor runs through table from first to last row 
table=[]          # var for table
table_last =[]    # var for last subset table, which is not saved on harddisk
rowcounty = 0     # counts subset of data, necessary for larger datasets
rowcount = 0      # one row is one well -> count wells
data = arcpy.SearchCursor(wells_params.output_shapefile)

# sets up the coloum names for df
cols_names = [] 
for liste in liste_of_all_fields:
    cols_names.append(liste.name)

#################################################################
# creates txtfiles for connection of observed well data to modeled wells

# prep comp wells / comp is VR
print wells_params.comp_output
txtfile = open(wells_params.comp_output,'a+')
txtfile.writelines("Well,wellnumber\n")

# prep apatite wells
print wells_params.apatite_output
txtfile_apatite = open(wells_params.apatite_output,'a+')
txtfile_apatite.writelines("Well,wellnumber\n")

# prep zechstein heatflow wells
print wells_params.ze_hf_output
hf_zechstein = open(wells_params.ze_hf_output,'a+')
hf_zechstein.writelines("Well,heatflow\n")

# prep temperature wells
print wells_params.temp_output
txtfile_temp = open(wells_params.temp_output,'a+')
txtfile_temp.writelines("Well,wellnumber\n")

# prep porosity wells
print wells_params.porosity_output
txtfile_porosity = open(wells_params.porosity_output,'a+')
txtfile_porosity.writelines("Well,wellnumber\n")

#################################################################
# adds informations to textfile and splits data into smaller data subsets to increase performance
try:
    for row in data:
    
            # delete wells if in file 
            if not row.getValue(wells_params.salt) == wells_params.saltnr: # salt
    
                # if VR data, then add line to VR file   //vr is comp
                if row.getValue(wells_params.comp_wells) >= 0:
                   txtfile.writelines(str(row.getValue('Well')) + ',' + str(row.getValue(wells_params.comp_wells)) + "\n")
    
                # apatite data
                if row.getValue(wells_params.apatite) >= 0:
                   txtfile_apatite.writelines(str(row.getValue('Well')) + ',' + str(row.getValue(wells_params.apatite)) + "\n")
                
                # temp data
                if row.getValue(wells_params.temperature) >= 0:
                   txtfile_temp.writelines(str(row.getValue('Well')) + ',' + str(row.getValue(wells_params.temperature)) + "\n")
                   
                # porosity data
                if row.getValue(wells_params.porosity) >= 0:
                   txtfile_porosity.writelines(str(row.getValue('Well')) + ',' + str(row.getValue(wells_params.porosity)) + "\n")
                                 
                # zechstein heatflow
                if row.getValue(wells_params.ze_hf) > 0:
                   hf_zechstein.writelines(str(row.getValue('Well')) + ',' + str(int(row.getValue(wells_params.ze_hf))) + "\n") 
                               
                rowcount += 1
                
                # i) clear data for subset of data; ii) add subset to table 
                add_to_table =[]
                for field in liste_of_all_fields:
                    add_to_table.append(row.getValue(field.name))
                table.append(add_to_table)
    
                # for copying larger tables
                rowcounty += 1
                
                # saves table to hard disk, else it is saved into table_last
                if rowcounty == wells_params.group_data:
                    
                        # resets counter for naming
                        print 'Rowcounty' + str(rowcounty)
                        rowcounty = 0
    
                        # save to hard disk
                        df = pd.DataFrame(data=table,columns=cols_names)
                        df.to_pickle(wells_params.pickle + '/' + str(rowcount)+'.pk1')
    
                        # resets table
                        table = []
                else:
                        # saves last rows
                        table_last = table

# closes txtfiles
finally:
        txtfile.close()
        hf_zechstein.close()
        txtfile_apatite.close()
        txtfile_porosity.close()
        txtfile_temp.close()

print 'Wells created: ' + str(rowcount)

# runs each subset of dataset, first from hard disk, then from table_last
for runnings in range(0,rowcount,wells_params.group_data):

    print 'Run ' + str(runnings/wells_params.group_data) + ' of ' + str(rowcount/wells_params.group_data) + ' runs.'
    # rows for each df
    first_row = runnings
    last_row = runnings + wells_params.group_data

    # creates df of subset of data, which is run 
    # run [-1] -> run of table_last
    if runnings/wells_params.group_data == rowcount/wells_params.group_data:
            df = pd.DataFrame(data=table_last,columns=cols_names)
            table_last = []
            df = df.drop(wells_params.salt,1)       # salt
            df = df.drop(wells_params.comp_wells,1) # comp_well
            df = df.drop(wells_params.ze_hf,1)      # ze_hf
            df = df.drop(wells_params.apatite,1)    # apatite
            df = df.drop(wells_params.temperature,1)    # apatite
            df = df.drop(wells_params.porosity,1)    # porosity
    # run [:-2] -> run of data from hard disk
    else:
            df = pd.read_pickle(wells_params.pickle + '/' + str(runnings+wells_params.group_data)+'.pk1')
            df = df.drop(wells_params.comp_wells,1) # comp_well
            df = df.drop(wells_params.salt,1)       # salt
            df = df.drop(wells_params.ze_hf,1)      # ze_hf
            df = df.drop(wells_params.apatite,1)    # apatite
            df = df.drop(wells_params.temperature,1)    # apatite
            df = df.drop(wells_params.porosity,1)    # porosity

    # data correction after extraction inclusive etopo
    df = wells_functions.correct_data(df)

    # adds top and bot layers
    df = wells_functions.add_t_b(df)

    # recalculates last thickness and deletes well if below threshhold
    df = wells_functions.thickness(df)

    # looks into low thickness values and resets them according to input
    df = wells_functions.thickness_input(df)
    
    # strata options
    df = wells_functions.strata_options(df)

    # creates necessary csv
    if runnings == 0:
         wells_functions.create_csv(df)
    # and appends [1:] runs
    else:
        wells_functions.append_csv(df)

    # creates shapefiles
    path_of_shape = wells_functions.df2shape(df,'POINT',(runnings/wells_params.group_data))

    # appends shapefiles to first one
    if runnings != 0:
        arcpy.Append_management(path_of_shape,target_path)
    else:
        target_path = path_of_shape

#########################################################################
### next part of program is for checking, if observed well data are still included in the to simulate file

### loads complete dataset 
well_output = wells_params.output_dir + '/parallel_run_wells.csv'
df_large = pd.read_csv(well_output)
dfList = df_large['well'].tolist()

### loads data from textfile
# comp / vr
well_output = wells_params.output_dir + '/comp_wells.csv'
df_small = pd.read_csv(well_output)
# drops non existing
droplist = []
for index, row in df_small.iterrows():
    if row[0] not in dfList:
        droplist.append(row[0])
# puts back into file        
df_small = df_small.set_index('Well')
df = df_small.drop(droplist, axis=0, inplace=False)
df.to_csv(path_or_buf=well_output,sep=',',index=True,mode='w', header=True)

# apatite
well_output = wells_params.apatite_output
df_small = pd.read_csv(well_output)
droplist = []
for index, row in df_small.iterrows():
    if row[0] not in dfList:
        droplist.append(row[0])   
df_small = df_small.set_index('Well')
df = df_small.drop(droplist, axis=0, inplace=False)
df.to_csv(path_or_buf=well_output,sep=',',index=True,mode='w', header=True)


# heat flow, temperature, porosity
hf_temp_porosity = [wells_params.output_dir + '/ze_hf_wells.csv',wells_params.temp_output,wells_params.porosity_output]
for each in hf_temp_porosity:
    df_zechstein = pd.read_csv(well_output)
    droplist = []
    for index, row in df_zechstein.iterrows():
        if row[0] not in dfList:
             droplist.append(row[0])    
df_zechstein = df_zechstein.set_index('Well')
df = df_zechstein.drop(droplist, axis=0, inplace=False)
df.to_csv(path_or_buf=well_output,sep=',',index=True,mode='w', header=True)
      
print 'Output shapefile is under: ' + target_path
                          
arcpy.CheckInExtension("Spatial") 
arcpy.CheckInExtension("3D")
stop = timeit.default_timer()
print "Total time: " + str(stop - start)

#### create data for comparison 

folder_test = []
if os.path.exists('wellnumber_into_vr') is True:
    folder_test.append('wellnumber_into_vr')
if os.path.exists('wellnumber_into_apatite') is True:
    folder_test.append('wellnumber_into_apatite')
#if os.path.exists('wellnumber_into_temp') is True:
#    folder_test.append('wellnumber_into_temp')
#if os.path.exists('wellnumber_into_porosity') is True:
#    folder_test.append('wellnumber_into_porosity')

outi=wells_params.output_dir
for element in folder_test:
    print 'element'
    name_of_py = element + '/into_format.py'  
    exec(open(name_of_py).read(), globals())  
    print name_of_py + ' done'






