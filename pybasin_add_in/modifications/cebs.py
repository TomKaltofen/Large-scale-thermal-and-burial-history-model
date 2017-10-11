# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 16:13:08 2016

@author: Tom

Functions for pybasin model

"""

#http://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value/12141511#12141511
from bisect import bisect_left

def takeClosestTom(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest POSITION to myNumber.

    If two numbers are equally close, return the smallest numbers position.
    """
    pos = bisect_left(myList, myNumber)
    #print ''
    if pos == 0:
        #print 'Point is at start.'
        return pos
    if pos == len(myList):
        #print 'Point is at end.'
        return pos-1
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before: 
       #print 'Point is before point to compare with: ' + str(after)
       return pos
    else:
       #print 'Point is before point to compare with: ' + str(before)
       return pos-1

def derive_mean_from_age(age):
    '''mean'''
    return (age[0]+age[1])/2

def present_temp_in_given_depth(z_nodes,model_scenario_number,T_nodes,model_results_df):

    #depth of present day temperatures to be saved      
    temp_depth = []
    for t_range in range(0,8000,50):
        temp_depth.append(t_range)
        
        
                 
    #temp_depth = 1000,3000,4000,,6000,8000
    
    for t_depth in temp_depth:

        #looks for closest position to depth
        t_pos = takeClosestTom(z_nodes[-1], t_depth)
        t_name = 'temp' + str(t_depth)
        
        #if depth exists(index in bound), present day temperature is taken
        if (t_pos != (len(z_nodes[-1])-1)) and (t_pos != len(z_nodes[-1])):
            try:
                model_results_df.ix[model_scenario_number,t_name] = \
                    T_nodes[-1][t_pos]
            except IndexError:
                model_results_df.ix[model_scenario_number,t_name] = \
                    'None'
        else:
            model_results_df.ix[model_scenario_number,t_name] = \
                    'None'
                    
    return model_results_df

def vr_top_bot(model_results_df, node_strat, vr_nodes,geohist_df,model_scenario_number):
    # get vr of bot and top node of lithology    
    
    string_of_strata = 4    

    #wanted_top_and_bot_lith = ['tert','ucr_','lcr_','mtr_']   
    wanted_top_and_bot_lith = geohist_df.index.values.tolist()
    
    # go through node strat, on first and last encounter, take vr
    for wanted_nodes in wanted_top_and_bot_lith:
        first = []
        last =  []
        
        # get position of vr_nodes compared to node_strat
        for idx, val in enumerate(node_strat):
            # if searched strata
            if val[0:string_of_strata] == wanted_nodes:
                if first == []:
                    first = idx
                else:
                    last = idx
            
            # case first != last 
            if (first != last) and (last != []) and (last != 0):
                if vr_nodes[-1][first] >= 4.5:
                    vr_nodes[-1][first] = 4.5
                if vr_nodes[-1][last] >= 4.5:
                    vr_nodes[-1][last] = 4.5
                    
                model_results_df.ix[model_scenario_number,wanted_nodes +'first'] = \
                    vr_nodes[-1][first]
                model_results_df.ix[model_scenario_number,wanted_nodes +'last'] = \
                     vr_nodes[-1][last]
                     
    return model_results_df
    
def vr_middle(model_results_df, node_strat, vr_nodes,geohist_df,model_scenario_number, z_nodes):         
     
     string_of_strata = 4 
     
     df_index = geohist_df.index.values.tolist()
     mean_depth_list = []
     mean_lithology_list = []
              
     # Testing if first run is a hiatus and setting vars accordingly
     # case hiatus  
     if ("~" in df_index[0]):
         bot = 0
         top = 0
         mean_depth = 0
         # case normal 
     else:
         top = int(geohist_df.loc[df_index[0],'depth_top'])
         bot = int(geohist_df.loc[df_index[0],'depth_bottom'])
         mean_depth = 0
   
     for litho in df_index:
                    # for comparing strings in index of input lithology
                    comp = litho[0:string_of_strata]
                    
                    # case first run
                    if litho == df_index[0]:
                        # case hiatus
                        if (bot == 0):
                            lith_save = comp
                        # case normal
                        elif bot > 0:  
                            mean_depth = int(derive_mean_from_age([int(top),int(bot)]))
                            lith_save = comp
                            
                    # case last run
                    elif litho in df_index[-1]:
                        # case hiatus as last, not possible
                        if ("~" in litho):
                            mean_depth_list.append(mean_depth)
                            mean_lithology_list.append(comp)
                        # case != after hiatus
                        elif ("~" in lith_save) and (lith_save != comp):
                            top = int(geohist_df.loc[litho,'depth_top'])
                            bot = int(geohist_df.loc[litho,'depth_bottom'])
                            mean_depth = int(derive_mean_from_age([(top),(bot)]))
                            mean_depth_list.append(mean_depth)
                            mean_lithology_list.append(comp)
                        # != 
                        elif (lith_save != comp):
                            mean_depth_list.append(mean_depth)
                            mean_lithology_list.append(comp)
                            top = int(geohist_df.loc[litho,'depth_top'])
                            bot = int(geohist_df.loc[litho,'depth_bottom'])
                            mean_depth = int(derive_mean_from_age([(top),(bot)]))
                            mean_depth_list.append(mean_depth)
                            mean_lithology_list.append(comp)
                        # ==
                        else:
                            bot = int(geohist_df.loc[litho,'depth_bottom'])
                            mean_depth = int(derive_mean_from_age([(top),(bot)]))
                            mean_depth_list.append(mean_depth)
                            mean_lithology_list.append(comp)
                            
                    # case 2nd run
                    else:
                        # case hiatus
                        if ("~" in comp) and (mean_depth > 0):
                            mean_depth_list.append(mean_depth)
                            mean_lithology_list.append(lith_save)
                            lith_save = comp
                        # case != after hiatus
                        elif ("~" in lith_save) and (lith_save != comp):
                            top = int(geohist_df.loc[litho,'depth_top'])
                            bot = int(geohist_df.loc[litho,'depth_bottom'])
                            mean_depth = int(derive_mean_from_age([(top),(bot)]))
                            lith_save = comp
                        # != 
                        elif (lith_save != comp):
                            mean_depth_list.append(mean_depth)
                            mean_lithology_list.append(lith_save)
                            top = int(geohist_df.loc[litho,'depth_top'])
                            bot = int(geohist_df.loc[litho,'depth_bottom'])
                            mean_depth = int(derive_mean_from_age([(top),(bot)]))
                            lith_save = comp                           
                        # ==
                        else:
                            bot = int(geohist_df.loc[litho,'depth_bottom'])
                            mean_depth = int(derive_mean_from_age([(top),(bot)]))
                                             
                # extracts position of depth z_nodes with an nearest too bisectLeft
     z_node_pos = []
     for i in range(len(mean_depth_list)):
                    lith_name = mean_lithology_list[i][0:string_of_strata]
                    z_node_pos = takeClosestTom(z_nodes[-1], mean_depth_list[i])                 
                    try:         
                        if vr_nodes[-1][z_node_pos] >= 4.5:
                            vr_nodes[-1][z_node_pos] = 4.5
                        model_results_df.ix[model_scenario_number,lith_name] = \
                                  vr_nodes[-1][z_node_pos]
                    except IndexError:
                        model_results_df.ix[model_scenario_number,lith_name] = \
                                  'NaN' 
             
     return model_results_df
 
def thickness(model_results_df, node_strat, geohist_df,model_scenario_number,z_nodes):    

    print max(geohist_df['present-day_thickness'])
    print max(geohist_df['initial_thickness'])

    string_of_strata = 4 
    

    df_index = geohist_df.index.values.tolist()
       
    # initial day thickness

    for litho in df_index:
                           
          comp = litho[0:string_of_strata]
    
          if ("~" in litho):
              pass
          else:
              try:
                  val = model_results_df.ix[model_scenario_number,'ini_' + str(comp)]
                  model_results_df.ix[model_scenario_number,'ini_' + str(comp)] = int(val + geohist_df.ix[litho,'initial_thickness'])                        
              except:
                  try:
                      model_results_df.ix[model_scenario_number,'ini_' + str(comp)] = int(geohist_df.ix[litho,'initial_thickness'])
                  except:
                      pass
    
                  
    # present day thickness
    
    val = []
    for litho in df_index:
                           
          comp = litho[0:string_of_strata]
    
          if ("~" in litho):
              pass
          else:
              try:
                  val = model_results_df.ix[model_scenario_number,'pre_' + str(comp)]
                  model_results_df.ix[model_scenario_number,'pre_' + str(comp)] = int(val + geohist_df.ix[litho,'present-day_thickness'])                    
              except:
                  try:
                      model_results_df.ix[model_scenario_number,'pre_' + str(comp)] = int(geohist_df.ix[litho,'present-day_thickness'])
                  except:
                      pass

          
    return model_results_df
    
def thermal_conductivity(model_results_df, node_strat, geohist_df,model_scenario_number,k_nodes):
    # gets thermal conductivity of bottom of lithology

    string_of_strata = 4            
                 
    #wanted_thermal_conductivity = ['q_d_']  
    wanted_thermal_conductivity = geohist_df.index.values.tolist()
                              
    for wanted_nodes in wanted_thermal_conductivity:
        first = []
        last = []
        for idx, val in enumerate(node_strat):
            if val[0:string_of_strata] == wanted_nodes: 
                if first == []:
                    first = idx
                else:
                    last = idx
                
            if last != [] and last != 0:    
                model_results_df.ix[model_scenario_number,wanted_nodes+'_K'] = \
                         k_nodes[-1][last-1]
        
    return model_results_df   
    
def porosity(model_results_df, node_strat, geohist_df,model_scenario_number,porosity_nodes):
    # gets thermal conductivity of bottom of lithology

    string_of_strata = 4    
           
    # wanted_porosity = ['ucr_']  
    wanted_porosity = geohist_df.index.values.tolist()
                          
    for wanted_nodes in wanted_porosity:
        first = []
        last = []
        for idx, val in enumerate(node_strat):
            if val[0:string_of_strata] == wanted_nodes: 
                if first == []:
                     first = idx
                else:
                    last = idx         
                    
            if last != [] and last != 0:                         
                model_results_df.ix[model_scenario_number,'p_' + wanted_nodes] = \
                    porosity_nodes[-1][last-1]    
            
    return model_results_df        
            
def basal_heat_flow_scenarios(well_hf,basal_heat_flow_scenarios):
    import pybasin_params
    import pandas as pd
    import math
    
    # checks if heat flow is in given csv, else take csv from model_scenarios
    
    input_direction = pybasin_params.input_dir + '/cebs/ze_hf_wells.csv'    
    df_basal_heat_flow_scenarios = pd.read_csv(input_direction, index_col = 'Well')  
    
    basal_heat_flow = df_basal_heat_flow_scenarios.ix[well_hf,'heatflow'][0] *1e-3   
 
    if math.isnan(basal_heat_flow):
        return basal_heat_flow_scenarios
    else:
        basal_heat_flow = [basal_heat_flow]
        return basal_heat_flow

def make_model_data_fig(make_model_data_fig,simulate_VR,simulate_AFT,simulate_AHe):
        if make_model_data_fig == False:
            import pybasin_params
            import pandas as pd
            import sys
            
            input_VR = pybasin_params.input_dir + '/cebs/comp_wells.csv'
            input_AFT = pybasin_params.input_dir + '/cebs/zk_apa.csv'
            
            #not included yet
            input_AHE = pybasin_params.input_dir + '/cebs/comp_wells.csv'
            
            input_T = pybasin_params.input_dir + '/cebs/zk_poro.csv'
            input_P = pybasin_params.input_dir + '/cebs/zk_temp.csv'
            
            if len(sys.argv) > 1:
                well_in_file = sys.argv[1:]
            well_in_file = str(well_in_file[0])
            
            try:
                df_VR = pd.read_csv(input_VR, index_col = 'Well')
                myliste = list(df_VR.index.values)                                                            
                for welli in myliste:
                    if well_in_file == welli:
                        make_model_data_fig = True
                        break                
            except:
                pass
            
            if not make_model_data_fig == True:
                try:
                    df_VR = pd.read_csv(input_AFT, index_col = 'Well')
                    myliste = list(df_VR.index.values)                                                            
                    for welli in myliste:
                        if well_in_file == welli:
                            make_model_data_fig = True
                            break      
                except:
                    pass
            
            #not included yet
            if not make_model_data_fig == True:
                try:
                    df_VR = pd.read_csv(input_AHE, index_col = 'Well')
                    myliste = list(df_VR.index.values)                                                            
                    for welli in myliste:
                        if well_in_file == welli:
                            make_model_data_fig = True
                            break
                except:
                    pass
                
            if not make_model_data_fig == True:
                try:
                    df_VR = pd.read_csv(input_T, index_col = 'Well')
                    myliste = list(df_VR.index.values)                                                            
                    for welli in myliste:
                        if well_in_file == welli:
                            make_model_data_fig = True
                            break
                except:
                    pass
                
            #not included yet
            if not make_model_data_fig == True:
                try:
                    df_VR = pd.read_csv(input_P, index_col = 'Well')
                    myliste = list(df_VR.index.values)                                                            
                    for welli in myliste:
                        if well_in_file == welli:
                            make_model_data_fig = True
                            break
                except:
                    pass
                
            return make_model_data_fig
  
        else:
            return make_model_data_fig
            
            
def simulate_AFT(simulate_AFT):
            if simulate_AFT == False:
                import pybasin_params
                import pandas as pd
                import sys
                
                input_AFT = pybasin_params.input_dir + '/cebs/zk_apa.csv'
                
                if len(sys.argv) > 1:
                    well_in_file = sys.argv[1:]
                    
                well_in_file = str(well_in_file[0])
                
                try:
                    df_AFT = pd.read_csv(input_AFT, index_col = 'Well')
                    myliste = list(df_AFT.index.values)
                    for welli in myliste:
                        if well_in_file == welli:
                            simulate_AFT = True
                            break      
                except:
                    pass
                
                return simulate_AFT
            else:
                return simulate_AFT
         
def poros():
                
    poros = 'input_data/ce/porosity.csv'
    
    import pandas as pd
    
    if poros is not None:
       poros_df = pd.read_csv(poros, index_col = 'well')
    else: 
       poros_df = False
       
    return poros_df

            
def strat_trans(strat):        

    liste = []   
    color = [] 
    for ele in strat:

        if 'q_d_' == ele:
            liste.append('Qua')
            color.append('#FFF2C7')     
        if 'tert' == ele:           
             liste.append('Ter')
             color.append('#FDF291')
        if 'ucr_' == ele:
             color.append('#E6C091')
             liste.append('UCr')
             
        if 'lcr_' == ele:
             color.append('#8CCD60') 
             liste.append('LCr')
             
        if 'uju_' == ele:
             color.append('#D9F160')
             liste.append('UJu')
             
        if 'mju_' == ele:
             color.append('#B3F1F7')
             liste.append('MJu')
             
        if 'lju_' == ele:
             color.append('#4EB3D3')
             liste.append('LJu')
             
        if 'utr_' == ele:
            color.append('#E3B9DB')
            liste.append('UTr') 
            
        if 'mtr_' == ele:
             color.append('#BC75B7')
             liste.append('MTr')
             
        if 'ltr_' == ele:
             color.append('#A4469F')
             liste.append('LTr')
             
        if 'ze_d' == ele:
             color.append('#FCC0B2')
             liste.append('Ze')
             
             
        if 'ro_d' == ele:
            color.append('#E36350')
            liste.append('Rot')
            
    return liste, color
    
def color(number):
    if number == 0:
        color = '#FFF2C7'
    if number == 1:
        color = '#FDF291'
    if number == 2:
        color = '#E6C091'
    if number == 3:
        color = '#8CCD60'
        
    if number == 4:
        color = '#D9F160'
        
    if number == 5:
        color = '#B3F1F7'
        
    if number == 6:
        color = '#4EB3D3'
        
    if number == 7:
        color = '#E3B9DB'
        
    if number == 8:
        color = '#BC75B7'
        
    if number == 9:
        color = '#A4469F'
    if number == 10:
        color = '#FCC0B2'
        
    if number == 11:
        color = '#E36350'
    return color           
            
            
            
            
            
            
            
            
            