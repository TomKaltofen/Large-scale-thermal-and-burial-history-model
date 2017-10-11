"""
Created on Aug 09 23:37:21 2016

@author: Tom

This file holds functions for correcting input raster data.
"""

import arcpy
import wells_params
import pandas as pd
import arcpy.sa
import numpy as np

def monotonic(x):
    # returns true when list increases
    dx = np.diff(x)
    return np.all(dx <= 0) or np.all(dx >= 0) 

def append_csv(df):
    '''Adds wells to df
    
    to do: combine functions create_csv and append_csv
    '''
    output_dir = wells_params.output_dir
    
    # output of wells
    well_output = output_dir + '/parallel_run_wells.csv'
    stratigraphy_output = output_dir + '/well_stratigraphy.csv'
     
     
    # writes parallel_run_wells.csv     
    # renames and puts 'well' into column
    df2 = df.reset_index(level=0,inplace=False)
    df2 = df2.rename(columns = {'Well':'well'}, inplace = False)
 
    # produce output    
    df3 = df2.loc[:,['well']] 
    df3.to_csv(path_or_buf=well_output,sep=',',index=None,mode='a', header=False)
    
    #with open(well_output, 'a+') as f:
    #    df.to_csv(f, header=False)
    
    # writes well_stratigraphy.csv 
    df4 = df2   
    df4 = df4.set_index('well',drop=True)
    
    txtfile = open(stratigraphy_output,'a+')
    
    for index, row in df4.iterrows():
        iterator = 0
        for ind, value in row.iteritems():
            
          # every bottom coloum have both values
          if not iterator % 2:
              top = value
          else:
              bot = value
              
              #add row to knew df  
              if top != bot:
                  new_line = str(index)+','+str(top)+','+str(bot)+','+ str(row.index[iterator][0:wells_params.length_of_input_name])              
                  txtfile.writelines(new_line + "\n")                        
          iterator += 1
        
    txtfile.close()
    
def create_csv(df):
    '''Adds wells to df
    
    to do: combine functions create_csv and append_csv
    '''
    output_dir = wells_params.output_dir
    
    # output of wells
    well_output = output_dir + '/parallel_run_wells.csv'
    stratigraphy_output = output_dir + '/well_stratigraphy.csv'
     
     
    # writes parallel_run_wells.csv     
    # renames and puts 'well' into column
    df2 = df.reset_index(level=0,inplace=False)
    df2 = df2.rename(columns = {'Well':'well'}, inplace = False)
 
    # produce output    
    df3 = df2.loc[:,['well']] 
    df3.to_csv(path_or_buf=well_output,sep=',',index=None)
    
    # writes well_stratigraphy.csv 
    df4 = df2   
    df4 = df4.set_index('well',drop=True)
    
    txtfile = open(stratigraphy_output,'a+')
    txtfile.writelines("well,depth_top,depth_bottom,strat_unit\n")
    
    for index, row in df4.iterrows():
        iterator = 0
        for ind, value in row.iteritems():
            
          # every bottom coloum have both values
          if not iterator % 2:
              top = value
          else:
              bot = value
              
              #add row to knew df  
              if top != bot:
                  new_line = str(index)+','+str(top)+','+str(bot)+','+ str(row.index[iterator][0:wells_params.length_of_input_name])              
                  txtfile.writelines(new_line + "\n")                        
          iterator += 1
        
    txtfile.close()
    
def strata_options(df):
    '''Stratigraphic choices
    '''
    df2 = df  
    
    # counts how many wells have below min_strat
    delete_list = []
    
    # runs this function
    if wells_params.min_strat_units != 0:
           
        # vars
        min_strat = wells_params.min_strat_units
       
        for index, row in df.iterrows():
            
            # for counting position in rows
            iterator = 0   
            
            # counting strats
            counter = 0
            
            for ind, value in row.iteritems():                
                
                
                if iterator % 2:              
                    if df.ix[index,iterator] != df.ix[index,iterator-1]:
                        
                        counter += 1
                        
                if counter == min_strat:
                    break
                
                # not reached minimum strats
                if ind == row.index[-1]:
                   delete_list.append(index)
                               
                iterator += 1
    
    # runs this function
    if wells_params.condition_list != ['0']:

        # sets condition
        cond = wells_params.condition_list        
        condition_count = len(cond)
        
        for index, row in df.iterrows():
            
            # counts how often condition matches
            condition_counter = 0

            # sets last_value to 0 (top)
            last_value = 0
            
            for ind, value in row.iteritems():  

                for ele in cond:
                    
                    # sets to coloum names
                    ele = str(ele) + '_b'
                    
                    # if equal, set true
                    if str(ind) == ele:
                        
                        #checks, if no hiatus
                        if value != last_value:
                            
                            # counts valid strata
                            condition_counter += 1
                            
                if condition_count == condition_counter:
                    break            
                            
                # not including strats
                if ind == row.index[-1]:
                        delete_list.append(index)
                            
                last_value = value
              
    df2 = df.drop(delete_list, axis=0, inplace=False)    
    print str(len(delete_list)) + ' wells dont have minimum strats.'
    
    return df2       



def thickness_input(df):
    '''   
    Calculation according to stratigraphic choices in regard to minimum 
    thickness, and stratigraphic orientation.
    
    Solves first forward, if not possible, backwards,
    else well gets dropped.
    '''    
    
    #list for dropping
    delete_list = []
    
    del_s = wells_params.delete_singe_litho_below_meter

    cha_s = wells_params.change_single_litho_below_meter
    
    for index, row in df.iterrows():
        
        iterator = 0
        bot = 0
        top = 0
        
        # solution 1
        solution = 3
        # solution 2
        solution2 = 3         
        
        # solution 1 forward
        for ind, value in row.iteritems(): 
            
            # 
            runs = len(row)
             
            # not run top except
            if not iterator % 2:
            # take value of t
                top = value
            # run bot and do logic                             
            else:
                bot = value
                diff = bot - top

                # run as long the row is
                # try to solve first for positiv
                # and then for negativ              
                # do it first for low values 
                
                if (diff < del_s) and (diff > 0):
                    
                    # get position of the problem
                    position = iterator                   
                                        
                    # goes in forward direction to find a space for putting strata
                    # p_pos + 2 for not checking own spot, runs+1 because of iterate, in 2 steps
                    for x in range(position,runs,2):
                        
                        # gets values from actual df
                        loc_top = df.ix[index,(x-1)]
                        loc_bot = df.ix[index,(x)]
                        loc_diff = loc_bot-loc_top
                        solution = 0
                        
                        if loc_diff > del_s:                            
                             # found place for solution
                             # decrease bot                                                         
                             if not position+2 > runs:  

                                 df.ix[index,position] = (df.ix[index,position]) - (diff)
                                 
                             # increase when not found a hiatus
                             for i in range(position+2,runs,2):
                                 if not df.ix[index,i] == df.ix[index,i-1]:
                                     # not hiatus -> top takes value of lowered bot
                                     df.ix[index,i-1] = df.ix[index,position]
                                     # solution is found, break to next diff vs given number check
                                     solution = 1
                                     break
                                 else:
                                     # hiatus
                                     # takes value of lowered bot
                                     df.ix[index,i] = df.ix[index,position]
                                     # takes value of lowered bot
                                     df.ix[index,i-1] = df.ix[index,position]
                        if solution == 1:
                            break
            iterator += 1
               
        
            
        bot = 0
        top = 0         
        iterator = 0
        # solution 1 backward
        for ind, value in row.iteritems(): 
 
            runs = len(row)
            if not iterator % 2:
                top = value                            
            else:
                bot = value
                diff = bot - top
                
                if (diff < del_s) and (diff > 0) and (solution != 1):
                    
                    # get position of the problem
                    position = iterator 
                    m_pos = runs-(runs-position)

                    # goes in forward direction to find a space for putting strata
                    # p_pos + 2 for not checking own spot, runs+1 because of iterate, in 2 steps
                    for x in range(m_pos,0,-2):
                     
                        # gets values from actual df
                        loc_top = df.ix[index,(x-1)]
                        loc_bot = df.ix[index,(x)]
                        loc_diff = loc_bot-loc_top
                        solution = 0
                        
                        if loc_diff > del_s: 
                            
                           # found place for solution
                           # decrease top                                                         
                             if not m_pos-2 < 0:                             
                                 df.ix[index,position-1] = (df.ix[index,position-1]) + (diff)
                             
                            # increase when not found a hiatus
                             for i in range(m_pos-2,0,-2):
                                if not df.ix[index,i] == df.ix[index,i-1]:
                                     # not hiatus -> bot takes value of lowered top
                                     df.ix[index,i] = df.ix[index,position-1]
                                     
                                     # solution is found, break to next diff vs given number check
                                     solution = 1
                                     break
                                else:
                                     # hiatus
                                     # takes value of lowered bot
                                     df.ix[index,i] = df.ix[index,position-1]
                                     # takes value of lowered bot
                                     df.ix[index,i-1] = df.ix[index,position-1]
                        if solution == 1:
                            break
            iterator += 1
        
        bot = 0
        top = 0        
        iterator = 0
        # solution 2 forward
        for ind, value in row.iteritems(): 
            
            # 
            runs = len(row)
            
            # not run top except
            if not iterator % 2:
            # take value of t
                top = value
            # run bot and do logic                             
            else:
                bot = value
                diff = bot - top
                
                if(diff < cha_s) and (diff >= del_s):   
                                        
                    # get position of the problem
                    position = iterator 
                                                       
                    # goes in forward direction to find a space for putting strata
                    # p_pos + 2 for not checking own spot, runs+1 because of iterate, in 2 steps
                    for x in range(position,runs,2):
                        # gets values from actual df
                        loc_top = df.ix[index,(x-1)]
                        loc_bot = df.ix[index,(x)]
                        loc_diff = loc_bot-loc_top
                        solution2 = 0
                        if loc_diff < cha_s:
                            
                             # found place for solution
                             # increase bot with certain amout
                             plus = (cha_s - diff)
                             
                             if not position+2 > runs:
                                 df.ix[index,position] = (df.ix[index,position]) + plus
                   
                             # increase when not found a hiatus
                             for i in range(position+2,runs,2):
                                 if not ((df.ix[index,i] == df.ix[index,i-1]) or ((abs(df.ix[index,i]-df.ix[index,i-1]))<abs(2*plus))):
                                     # not hiatus
                                     df.ix[index,i-1] = df.ix[index,position]
                                     # solution is found, break to next diff vs given number check
                                     solution2 = 2
                                     break
                                 else:
                                     # hiatus
                                     # takes value of lowered bot
                                     df.ix[index,i] = df.ix[index,position]
                                     # takes value of lowered bot
                                     df.ix[index,i-1] = df.ix[index,position]
                        if solution2 == 2:
                            break                            
            iterator += 1
        
        
        iterator = 0    
        bot = 0
        top = 0                 
        # solution 2 backward
        for ind, value in row.iteritems(): 
            
            runs = len(row)            
            if not iterator % 2:
                top = value                           
            else:
                bot = value
                diff = bot - top
                  
                if (diff < cha_s) and (diff >= del_s) and (solution2 != 2): #and (diff > del_s):]
                    
                    # 'Negative run.'
                    # get position of the problem
                    position = iterator 
                    m_pos = runs-(runs-position)

                    # goes in forward direction to find a space for putting strata
                    # p_pos + 2 for not checking own spot, runs+1 because of iterate, in 2 steps
                    for x in range(m_pos,0,-2):

                        # gets values from actual df
                        loc_top = df.ix[index,(x-1)]
                        loc_bot = df.ix[index,(x)]
                        loc_diff = loc_bot-loc_top
                        solution2 = 0
                        plus = (cha_s - diff)                      
                        
                        if loc_diff < cha_s:                              
                           # decrease top     
                                                                          
                             if not m_pos-2 < 0:                             
                                 df.ix[index,position-1] = (df.ix[index,position-1]) - (plus)
                             
                            # increase when not found a hiatus
                             for i in range(m_pos-2,0,-2):
                                if not ((df.ix[index,i] == df.ix[index,i-1]) or ((abs(df.ix[index,i]-df.ix[index,i-1]))<abs(2*plus))):
                                    
                                     # not hiatus -> bot takes value of lowered top
                                     df.ix[index,i] = df.ix[index,position-1]
                                     
                                     # solution is found, break to next diff vs given number check
                                     solution2 = 2
                                     break
                                else:
                                     # hiatus
                                     # takes value of lowered bot
                                     df.ix[index,i] = df.ix[index,position-1]
                                     # takes value of lowered bot
                                     df.ix[index,i-1] = df.ix[index,position-1]
                        if solution2 == 2:
                            break                
                
            iterator += 1   

        # no correct solution was found
        if (solution == 0):              
            if (solution2 == 0):
                    delete_list.append(index)
    
        # deletes row, if data mangling went to far :), only happening when to many small layers
        elif monotonic(row) == False:
                delete_list.append(index)     
                  
    df2 = df.drop(delete_list, axis=0, inplace=False)

    print str(len(delete_list)) + ' wells with thickness problems cannot be fixed e.g. negative thickness.'
    
    return df2    
  
def thickness(df):
    ''' Check of large (potential) errors in input dataset
    '''    
    
    # delete all wells below total meter
    total = wells_params.delete_total_litho_below_meter

    # counts how many wells have below 50 m
    delete_list = []
    
    # not writing in reading df
    df2 = df
    
    for index, row in df.iterrows():
  
                    # getting last top and bot
                    last_bot = df.ix[index,row.index[-1]]
                    
                    # case delete_total_litho_below_meter                   
                    if last_bot < total:
                            delete_list.append(index)
                            
    for index, row in df.iterrows():
        if monotonic(row) == False:
            delete_list.append(index)
                                    
    df2 = df2.drop(delete_list, axis=0, inplace=False)
 
    print str(len(delete_list)) + ' wells got deleted, which have low very thickness or are not monotonic. '
      
    return df2
    

def add_t_b(df):
    ''' Adds top and bottom to df
    '''
    
    # not writing in reading df
    # and adding coloums for bottom and top
    cols = df.columns.values.tolist()
    df2 = df  
    for col in cols:        
        df2[col + '_t'] = 0
        df2[col + '_b'] = 0      
    df2 = df.drop(cols,inplace=False,axis=1)

    for index, row in df.iterrows():
        iterator = 0
        for ind, value in row.iteritems():
            iterator += 1
            # case run[0]
            # case T:  
               # pass, because is 0 anyway
            # case B:
            if ind == row.index[0]:
                df2.ix[index,1] = value
                case_T = value
            # case run[1:]            
            else:  
                # hiatus or wrong input data
                if value > 0 and value >= case_T:
                    try:
                     # case T: takes the value before   
                        df2.ix[index,(iterator*2)-2] = case_T
                    # case B: takes other value                   
                        df2.ix[index,((iterator*2)-1)] = value
                        case_T = value  
                    except:
                        pass
                elif value == 0: 
                    try:
                    # case hiatus 
                        df2.ix[index,((iterator*2)-1)] = case_T
                        df2.ix[index,(iterator*2)-2] = case_T
                    except:
                        pass

    return df2

def correct_data(df):
    '''Checks if coordinate transformations produced errors and,
    deletes if necessary
    '''
    
    delete_counter = len(df.index)    
    
    # drops unwanted cols
    df2 = df.drop('FID', axis=1, inplace=False)
    df3=df2.drop('Id', axis=1, inplace=False)
    df4=df3.drop('Shape', axis=1, inplace=False)
    df=df4
    # replaces negatives, 999, 9999 with 0, usually no NaN, or NONE should be in there at all anyway
    df = df.replace([9999,'NaN','NONE'],[0,0,0])
    df = df.replace([9999],[0])
        
    # corrects etopo 
    # cols[-1] should be etopo
    cols = list(df)
    for col in cols[1:]:
        if col == cols[-1]:
            df2 = df.drop(cols[-1],axis=1, inplace=False)
            df = df2
            break
        else:
           df[col] = df[col] + df[cols[-1]]        
       
    # deletes < 0 
    num = df._get_numeric_data()
    num [num < 0] = 0

    # drops all rows with only 0
    df = df.set_index('Well',drop=True,inplace=False)
    df = df[(df.T != 0).any()]    
    
    #int for nicer looks
    df = df.astype(int)  
    
    # deletes bad q_d_ input
    df = df[df.q_d_ != 9999]
        
    delete_counter = delete_counter - len(df.index) 
    print str(delete_counter) +' got deleted after basic operations.'


    return df
    
def Shp2dataframe(path):
    '''shape to df transformation'''
     
    # gets the field/coloum names of the input shapefile
    liste_of_all_fields = arcpy.ListFields(path)
      
    # sets up a cursor, which puts always whole row into the table
    table=[]
    rowcount = 0
    data = arcpy.SearchCursor(path)
    for row in data:
        rowcount += 1
        add_to_table =[]
        for field in liste_of_all_fields:
            add_to_table.append(row.getValue(field.name))
        table.append(add_to_table)
        
    # sets up the coloum names for output df
    cols_names = [] 
    for liste in liste_of_all_fields:
         cols_names.append(liste.name)
                
    return pd.DataFrame(table,columns=cols_names)
    
def read_input_rasters():
    '''set up of input environment'''
    
    from shutil import copyfile
    
    #creates list of rasters
    arcpy.env.workspace = wells_params.wkspc + '/' + wells_params.input_dir
    list_of_rasters = arcpy.ListRasters("*.asc", "All")
    arcpy.env.workspace = wells_params.wkspc
    
    #copies raster into outputfolder and create variable with list of rasters
    ras = []                                #
    for raster in list_of_rasters:   
        name = wells_params.output_dir + '/' + wells_params.output_of_raster         
        name = name + '/' + str(raster)         
        raster = wells_params.input_dir + '/' + raster   
        copyfile(raster,name) 
        ras.append(name)
                     
    list_of_rasters = ras    
    
    del ras, name    
    return list_of_rasters
    
def helping(a):       
    ''' help function for setting up and testing the input .asc files'''
    
    count = 0
    for b in a:
        print b + " " + str(count)
        count += 1
        
def create_empty_wells():
    ''' set up of empty wells with correct properties'''    
    
  
    #gets extent of given raster # wells_params.raster_for_extent
    
    arcpy.env.workspace = wells_params.wkspc + '/' + wells_params.input_dir
    rast = arcpy.Raster(wells_params.raster_for_extent)
    extent = rast.extent
    xmin = int(extent.XMin)
    xmax = int(extent.XMax)
    ymin = int(extent.YMin)
    ymax = int(extent.YMax )

    k=0                               #counter for wellnames
    row_values = []                   #stores later the row of every well
    name = 'Well'                     #field name for wells
    
    # creates wells in every cell depending on extent
    for i in range(xmin,xmax,wells_params.cellsize):
        for j in range(ymin,ymax,wells_params.cellsize):
            #coordinates of wellpoints
            pos = [i,j]
            well_name = "Well"+str(k)
            k += 1
            row_values.append([well_name, pos])

    ####iterate through table and produce empty rows 
    arcpy.AddField_management(wells_params.output_shapefile,name,"TEXT") #keine Kommastellen 
    cursor = arcpy.da.InsertCursor(wells_params.output_shapefile,[name,'SHAPE@XY'])
    for row in row_values:
        cursor.insertRow(row)
    del cursor, row, row_values

def df2shape(df,geoType,run_number):
    '''
    Pandas df back to shape

    '''
    #os.makedirs(output_dir + '/' + output)
    
    outpath = wells_params.output_shapefile[:-4] + str(run_number) + '.shp'
    out_path = outpath.replace(outpath.split('/')[-1],'')
    out_name = outpath.split('/')[-1]
    geometry_type = geoType
    template = ''
    
    arcpy.env.overwriteOutput = True
    feature_class = arcpy.CreateFeatureclass_management(
        out_path, out_name, geometry_type, template)

    df = df.reset_index(level=0,inplace=False)
    desc = arcpy.Describe(outpath)
    
    if template=='':
        fields = set(list(df.columns)+['Shape','FID'])
        originfieldnames = [field.name for field in desc.fields]
        originfieldnames.append('Well')
        for fieldname in fields:            
            if fieldname not in originfieldnames:            
                arcpy.AddField_management(outpath,fieldname,'FLOAT')
            arcpy.AddField_management(outpath,'Well','STRING')
                  
    for row in df.index:
        cursor = arcpy.da.InsertCursor(outpath,[field for field in df.columns])
        cursor.insertRow([df[field][row] for field in df.columns])
    try:
        del cursor
    except:
        pass
    
    return outpath