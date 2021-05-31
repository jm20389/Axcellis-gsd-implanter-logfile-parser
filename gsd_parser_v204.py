#!/usr/bin/env python
# coding: utf-8

# # GSD LOGIFILE PARSER
# ## Python parser to collect IDL data from GSD Ion implanters

# ## 0. Program set-up

# ### 0.1 Load required modules

# In[21]:


import pandas as pd
import re
import os
import sys
import time
from tqdm import tqdm


# ### 0.2 Look for configuration files
# 
# Attempts to load the configuration files "gsd_config_01.txt" & "gsd_config_02.txt", if present in the .py application directory. This is to select the variables (columns) that will be captured during the parsing. Should these files not be present, a default set of variables will be loaded.

# In[2]:


try:
     with open('gsd_config_01.txt') as gsd_config_01:
         gsd_config_01 = gsd_config_01.read()
         print('gsd_config_01.txt file was found. Loading custom capture settings.')
         variables = gsd_config_01.split('\n')
         variables = [i.strip() for i in variables]

except:
    
    print('No config file was found. Loading default capture settings.')
               
    variables = ['Date',
    'Time',
    'Machine ID',
    'SW Version', 
    'Wafer size',   
    'Beam Height',      
    'Beam Height Offset',   
    'Estimated time',
    'Actual time',                             
    'Interruptions',      
    'Particle count',        
    'Snapshot count',   
    'Process Recipe',
    'Dose',
    'Trim Factor',
    'Recipe Energy',
    'Recipe Beam Current',
    'Implant Species',
    'Ion charge',
    'E.S. Pressure Comp.',
    'B.L. Pressure Comp.',
    'Implant Start Prs.',
    'Implant Stop Prs.',
    'Implant Min. Prs.',
    'Tilt angle',
    'Twist angle',
    'Flat/Notch angle',
    'Percent complete',
    'Recovery time']



try:
     with open('gsd_config_02.txt') as gsd_config_02:
         gsd_config_02 = gsd_config_02.read()
         print('gsd_config_02.txt file was found. Loading custom capture settings.')
         variables_table = gsd_config_02.split('\n')
         variables_table = [i.strip() for i in variables_table]

except:
    
    print('No config file was found. Loading default capture settings.')
               

    variables_table = ['Total energy       (keV)',
    'AMU',
    'Beam current       (A)',
    'Beam current noise (A)',
    'Preset Scans',
    'Source Pressure    (Torr)',
    'Beamline Pressure  (Torr)',
    'Chamber Pressure   (Torr)',
    'Linac Pressure     (Torr)',
    'Gauge Ratio IG2/IG3',
    'Arc Current        (Amps)',
    'Arc Voltage        (Volts)',
    'Filament Current   (Amps)',
    'Cathode Voltage    (Volts)',
    'Cathode Current    (Amps)',
    'Extraction Current (mA)',
    'Extraction Voltage (kV)',
    'Vap #1 Oven Temp   (DegC)',
    'Vap #1 Heater Temp (DegC)',
    'Vap #2 Oven Temp   (DegC)',
    'Vap #2 Heater Temp (DegC)',
    'Gas #1 MFC         (sccm)',
    'Gas #2 MFC         (sccm)',
    'Gas #3 MFC         (sccm)',
    'Gas #4 MFC         (sccm)',
    'Extr Gap Axis',
    'Extr Suppress I    (mA)',
    'Extr Suppress V    (kV)',
    'Extr Suppress I-2  (mA)',
    'Extr Suppress V-2  (kV)',
    'Source Injection Gas',
    'Source Injection Gas Flow',
    'Variable Rslv Aperture (mm)',
    'Source Magnet I    (Amps)',
    'Analyzer Magnet I  (Amps)',
    'AMU Hall Probe     (Gauss)',
    'Pl.Sh. Gas Flow MFC(sccm)',
    'Pl.Sh. Extr Voltage(V)',
    'Pl.Sh. Extr Current(mA)',
    'Pl.Sh. Arc Voltage (V)',
    'Pl.Sh. Arc Current (A)',
    'Pl.Sh. Fil Voltage (V)',
    'Pl.Sh. Fil Current (A)',
    'Pl.Sh. Fil Power   (W)',
    'Pl.Sh. Bias Aper Voltage(kV)',
    'Pl.Sh. Bias Aper Current(mA)',
    'Disk Current       (mA)',
    'Charge Mon Pos Peak(volts)',
    'Charge Mon Neg Peak(volts)',
    'Tilt Angle         (degrees)',
    'Twist Angle        (degrees)',
    'HYT Particle Counts',
    'HYT Stray Light',
    'HYT Laser Current  (mA)',
    'Beam Height (mm)',
    'Beam Height Offset (mm)',
    'Gas Bottle 1 pres   (kPa)',
    'Gas Deliver 2 pres  (kPa)',
    'Gas Deliver 3 pres  (kPa)',
    'Gas Deliver 4 pres  (kPa)',
    'FOM K-factor     (1/Torr)',
    'FOM Intercept        (mA)',
    'FOM Max Pressure   (Torr)',
    'FOM Min Pressure   (Torr)',
    'FOM Total Points',
    'Estimated Time     (HHMMSS)',
    'Actual Time        (HHMMSS)',
    'Actual/Estimated Time',
    'Interruptions']


# ## 1. User interface
# The following sequence will trigger a list of user input requests, this is to collect the location of the IDL files and the desired output fine name.

# ### 1.1 Define user input request functions

# In[3]:


def TriggerPresentation():
    
    '''
    Clears the console and prints a program header/presentation.
    
    '''

    presentation = '''
     __ __ _        _  __ _____    __    _  _  _  __ __ _ 
    /__(_ | \   |  / \/__|_  | |  |_    |_)|_||_)(_ |_ |_)
    \_|__)|_/   |__\_/\_||  _|_|__|__   |  | || \__)|__| |
                                                  
    '''

    os.system('cls' if os.name == 'nt' else 'clear')  

    print(presentation)
    
    return None


# In[4]:


def AskForDirectory():
    
    '''
    Triggers a user input collection event and validates whether it is a valid directory.
    Then returns the collected directory path and the list of files contained in that directory.
    
    '''
    user_filepath = None

    while user_filepath not in ['none', '']:  
        
        user_filepath = input('Please enter a file directory containing GSD logfiles or press ENTER to select current working directory: \nEXAMPLE: ---> C:\\Users\\Documents\\John\\gsd_files\n')
    
        if user_filepath.lower() == 'none' or user_filepath == None or user_filepath == '' :
            gsd_files = os.listdir()
        
        else:  
            try:
                user_filepath.replace('\\', r'\\')
                gsd_files = os.listdir(user_filepath)
        
                break
            
            except:
                print('Current directory not accepted\nPlease enter a valid directory or \'None\' to select current working directory. ')
                time.sleep(1)
                continue
    
    # To ensure input directory ends with '\', in order to concatenate with single files later on:
    
    if user_filepath != '' and user_filepath[-1] != '\\' :
        user_filepath = user_filepath + '\\'
    
    else:
        pass
    
    
    return gsd_files, user_filepath
    


# In[5]:


def GsdFilesCleanup(gsd_files, user_filepath):
    
    '''
    Given a list of file names, splits the list filtering into valid and non valid files.
    
    '''
    
    # REMOVE sub-directories out: Keeps only files with extension (IDL files MUST have an extension)
    gsd_files = [file for file in gsd_files if list(file)[0] != '.']
    gsd_files = [file for file in gsd_files if '.' in list(file)]
    

    
    # Filters non valid_extensions out:
    non_valid_ext = ['csv', 'txt', 'py', 'exe', 'ipynb']
    
    valid_files = [file for file in gsd_files if (str(file).split('.')[1] not in non_valid_ext)]
    non_valid_files = [file for file in gsd_files if (str(file).split('.')[1] in non_valid_ext)]
    
    
    if len(valid_files) > 0:
        for file in valid_files:
            print(file)  
        print('\n',len(valid_files), ' IDL files have been found.', '\n')
        
    else:
        print('\n','No valid IDL files found in directory.', '\n')


    if len(non_valid_files) > 0:
        
        for file in non_valid_files:
            print(file)
            
        print('\n',len(non_valid_files), ' non-IDL files dismissed: ', '\n')
    
    
    return valid_files, non_valid_files
    
     


# In[6]:


def AskForOutputFile(non_valid_files):

    '''
    Asks for an output file name that will later be user to generate a csv with generated dataframe.
    Validates that the input name does not exists in the current directory.
    
    Args:
    
        List of non-idl files contained in the target directory
        
    Returns
    
        Validated output file name, with a .csv extension
    
    '''
    
    non_valid_chars = list(r'?!.%@\#%&{}\'"<>*/$:+=|')
    validation = False
    
    while not validation:
    
        user_output = input('\nPlease enter an output .csv file name (without extensions):\nEXAMPLE: ---> \'output2\' will produce \'output2.csv\'\n')
        
        if user_output+'.csv' in non_valid_files:
            print('\nOutput file already exists in current directory. ')
            validation = False
        
        elif len(set(list(user_output)).intersection(non_valid_chars))>0:
            print('\nOutput file contains invalid characters. ')
            validation = False
            
        else:
            validation = True

    
        time.sleep(1)


    print('\nOutput file name accepted\n')
    
    return str(user_output)+'.csv'


# In[7]:


def ProceedConfirmation():

    proceed_answer = 'a'
    
    while proceed_answer != 'y' or proceed_answer != 'n':
        proceed_answer = input('Proceed with extraction? (y/n): ')
        
        try:
            proceed_answer.lower()
        except:
            print('Invalid answer. Please answer yes or no (y/n): ')
            continue
    
        if proceed_answer in ['y', 'Y']:
            break
        elif proceed_answer in ['n', 'N']:
            print('Extraction aborted')
            time.sleep(1)
            sys.exit()
        else:
            print('Please answer yes or no (y/n)')
            continue
    
    return None


# ## 2. Parser functions

# ### 2.1 Define IDL file parser function

# In[8]:


def gsd_extract(gsd_file, user_filepath):

    
    '''
    GSD IDL Text file parser that converts a IDL text file into a python dictionary.
    
    
    Args:
        gsd_file: The NAME of the IDL text file we wish to parse.
    
    Returns:
    
        run_dict: A python dictionary containing the captured information.
    
    '''
    run_dict = {}
    
    filepath = user_filepath + gsd_file
    
    with open(filepath, mode ='r') as gsd_run:
    
        gsd_run = gsd_run.read()
        
        
        # IDL NUMBER COLLECTION
        
        run_dict['IDL'] = float(gsd_file)



        # CAPTURE HEADER INFO: MATERIAL TRACKING INFO
        
        material_tracking_chunk_regex = r'(Material Tracking.*)Parameter [ ]*#1 Avg'
        material_tracking_chunk = re.findall(material_tracking_chunk_regex , gsd_run, re.DOTALL )
                              
        # DOESN'T LOOK FOR DUMMIES
        
        mtc_regex = r'(Material I.D.)[^\n]*(Cassette Slots) \n[ \-]*\n([+\w\d\. \-]+)[ ]+Port [\d] :[ ]+([\d ]+)\n'        
        
        mtc_match = re.findall(mtc_regex , material_tracking_chunk[0], re.DOTALL )
        mtc_match = mtc_match[0] # match is a list containing a tuple, only want the inside tuple
                
        # Write captures into dictionary
        run_dict[mtc_match[0]] = mtc_match[2]
        run_dict[mtc_match[1]] = mtc_match[3]
        
        
        # DUMMIES 
        
        mtc_dummies_regex = r'(DUMMY WAFERS)[ ]+:[ ]*([\d ]*)\n'
        
        try:
            mtc_match_dummies = re.findall(mtc_dummies_regex, material_tracking_chunk[0], re.DOTALL)
            run_dict['DUMMY WAFERS'] = mtc_match_dummies[0][1]
        except:
            run_dict['DUMMY WAFERS'] = 'NO DUMMIES'


        
        # RUN TYPE
        
        run_type_regex = r'[ ]+([\w ]+)[ ]Implant Summary'
        try:
            run_type_match = re.findall(run_type_regex , gsd_run, re.DOTALL )[0]
        except:
            run_type_match = ''
        
        if run_type_match == 'Aborted':
            run_dict['RUN TYPE'] = 'ABORTED'
        elif run_type_match == 'Abt Rec':
            run_dict['RUN TYPE'] = 'RECOVERY'
        else:
            run_dict['RUN TYPE'] = 'NORMAL'
        
        
        
        # VARIABLES

        single_variable_chunk_regex = r'(Implant Summary.*Flat/Notch angle[^\n]*\n)'
        single_variable_chunk = re.findall(single_variable_chunk_regex , gsd_run, re.DOTALL )
        
        for i in variables:
              
            regex_string = str(i).strip() + '[ ]*' + ':' + r'[ ]*([\d\w\.e+:_\-]*)'
            match = re.findall(regex_string, single_variable_chunk[0], re.DOTALL)
            
            try:
                run_dict[i.strip()] = match[0]
            except:
                run_dict[i.strip()] = 'NO MATCH'
            
        
        
        # VARIABLES TABLE    
        
        variables_table_chunk_regex = r'(Parameter.*Interruptions[^\n]*\n)'
        variables_table_chunk = re.findall(variables_table_chunk_regex , gsd_run, re.DOTALL )    
        
        
        for i in variables_table:
            
            regex_string_table = str(i).strip().replace('(', '\(').replace(')', '\)') + r'[ ]*([\-+:\.\d\w]*)[ ]*([\-+:\.\d\w]*)[ ]*([\-+:\.\d\w]*)[ ]*([\-+:\.\d\w]*)'
            
            match = re.findall(regex_string_table, variables_table_chunk[0], re.DOTALL)
            
            
            # The above code is intended to generate match lists of 2 elements
            # Accidental captures could create duplicates (generate match lists of 4 elements instead of 2)
            # Below elif block considers accidental duplicated capture case and selects first of each [0] and [2]
            
            
            # Expected case (first match[0] contains 25 and 50%, match[1] contains 75 and 100%)
            if len(match) == 2:
                run_dict[i.strip() + ' 25% mean'] = match[0][0]
                run_dict[i.strip() + ' 25% std'] = match[0][1]
                    
                run_dict[i.strip() + ' 50% mean'] = match[0][2]
                run_dict[i.strip() + ' 50% std'] = match[0][3]
                    
                run_dict[i.strip() + ' 75% mean'] = match[1][0]
                run_dict[i.strip() + ' 75% std'] = match[1][1]
                    
                run_dict[i.strip() + ' 100% mean'] = match[1][2]
                run_dict[i.strip() + ' 100% std'] = match[1][3]
                
            # Elif block dismisses duplicated captures (selects [0] and [2] hence avoiding duplicates in [1] and [3])   
            elif len(match) == 4:
                run_dict[i.strip() + ' 25% mean'] = match[0][0]
                run_dict[i.strip() + ' 25% std'] = match[0][1]
                    
                run_dict[i.strip() + ' 50% mean'] = match[0][2]
                run_dict[i.strip() + ' 50% std'] = match[0][3]
                    
                run_dict[i.strip() + ' 75% mean'] = match[2][0]
                run_dict[i.strip() + ' 75% std'] = match[2][1]
                    
                run_dict[i.strip() + ' 100% mean'] = match[2][2]
                run_dict[i.strip() + ' 100% std'] = match[2][3]
            
                
    return run_dict


# ### 2.2 Gather all files to be extracted

# In[9]:


def GsdCollectionBuilder(valid_files):

    run_collection = []
    failed_extract = []

    for filename in tqdm(valid_files):
        
        try:
            run_collection.append(gsd_extract(filename, user_filepath))

        except:
            failed_extract.append(i)
    
    print('\nEXTRACTION COMPLETED\n')
    print('\nGenerating output files ...\n')
    
    return run_collection, failed_extract
    


# In[10]:


def GsdDataFrameBuilder(run_collection):
  
    d = {}

    if len(run_collection)>0:

        for k in run_collection[0].keys():
          d[k] = list(d[k] for d in run_collection)
    
        return pd.DataFrame(data=d)

    else:
        print('\n None of the IDL files could be extracted. \n')
        
        return None
    
    
    


# In[11]:


def FinalSummary(failed_extract):
    
    if len(failed_extract) > 0:
        print('\nThe parser failed to extract ', str(len(failed_extract)), ' files.')
        print('FAILED to extract the following IDL files: ', '\n')
    
        for i in failed_extract:
            print(i)
        
        failed_output_name = user_output + '_FAILED' + '.txt'
    
        with open(failed_output_name, "w") as failed_output:
            failed_output.write(str(failed_extract))
            
    else:
        print('\nAll IDL files were successfully extracted.\n')
    
    return None


# In[12]:


def ExitSequence():
    
    exit_opt = True
    
    while exit_opt:
        
        exit_ans = input('\nProgram completed. Type \'end\' to exit: ')
        exit_ans = exit_ans.lower()
    
        if exit_ans == 'end':
            exit_opt = False
        else:
            exit_opt = True  
    
    return None


# ## 4. Main program sequence

# In[ ]:


TriggerPresentation()


# User interface - collect user info

gsd_files, user_filepath = AskForDirectory()

valid_files, non_valid_files = GsdFilesCleanup(gsd_files, user_filepath)

output_file = AskForOutputFile(non_valid_files)

ProceedConfirmation()


# Start parsing

run_collection, failed_extract = GsdCollectionBuilder(valid_files)

gsd_df = GsdDataFrameBuilder(run_collection)
gsd_df.to_csv(user_filepath + output_file, mode = 'a')

FinalSummary(failed_extract)

ExitSequence()

