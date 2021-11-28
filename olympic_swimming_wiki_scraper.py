# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 19:56:42 2021
@author: Zoren Liu

Final table fields:
    
    year                [string]    2000, 2016, etc
    Event               [string]    freetyle/butterfly/relay etc
    Distance            [string]    100m/4 x 100m
    Stage               [string]    Heats, Finals    
    Rank                [integer]   1,2,3..
    Lane                [integer]   1-8
    Nation              [string]
    Swimmer             [string]
    Individual time     [datetime] if relay event, then it is the individual's leg time
    Total time          [datetime] if individual event, then Total time = Individual time
    Notes               [string]

"""
import pandas as pd
from datetime import datetime

#%% Function 1

def extract_olympic_events(olympic_year_range, swim_events):
    """"Function to build a dictionary of Olympic swimming events by year"""
    
    # Initialise dictionary
    olympic_events = dict()
    
    # Convert a Series to a List
    swim_events = swim_events.T.values.tolist()[0]
    swim_events.append('Qualification')
    
    # Iterate through by Olympic year
    for year in olympic_year_range:
        
        print("Olympic events for year", year)
        
        # Build URL to acess Wikipedia page, we only want the 2nd table
        URL = "https://en.wikipedia.org/wiki/Swimming_at_the_" + str(year) + "_Summer_Olympics"
        wiki_tables = pd.read_html(URL,header=0)[1]
        # wiki_tables = [table for table in wiki_tables if any(wiki_tables[1].columns.str.contains(str(year) + " Summer Olympics"))]
        
        # Drop rows with all NaNs and drop last row which is not wanted information
        tmp_table = wiki_tables.dropna(how='all')[:-1].reset_index(drop=True)
        
        # An exception for year 2020 as the table is in a slightly different format
        if year == 2020:
            tmp_table.drop(tmp_table.columns[2], axis=1, inplace=True)
            tmp_table.columns = ["Distance", "Men", "Women"]
        else:
            tmp_table.columns = ["Distance", "Men", "Women"]
        
        # Create new column 'Event' to record swimming event category
        tmp_table['Event'] = pd.Series([tmp_table.iloc[0,0]]*tmp_table.shape[0])
        
        # Initialise a list of index to drop
        drop_list = []
        
        # Iterate through each row of dataframe to record swimming event category
        for index, row in tmp_table.iterrows():
            if row["Distance"] in swim_events:
                tmp_table["Event"][index:] = row["Distance"]
                drop_list.append(index)
          
        # Save dataframe to dictionary and reset index
        olympic_events[str(year)] = tmp_table.drop(tmp_table.index[drop_list])
        olympic_events[str(year)].reset_index(drop=True, inplace=True)
        
    return olympic_events

#%% Function 2

def str2time(str_time):
    """Function to convert string object to datetime object, and back into standardise string object"""
    
    str_time = str(str_time) # Convert input to string for parsing
    
    # Strange occurances where time string has a space 
    # https://en.wikipedia.org/wiki/Swimming_at_the_2016_Summer_Olympics_%E2%80%93_Women%27s_4_%C3%97_100_metre_freestyle_relay
    # Inge Dekker (54.75)
    
    str_time = str_time.replace(' ', '')
    
    # String can be MM:SS.ff or SS.ff
    # MM:SS.ff - M - minute, S - second, f - micro-second
    
    # Special occurance where format is MM:SS:ff, convert to MM:SS.ff
    # https://en.wikipedia.org/wiki/Swimming_at_the_2016_Summer_Olympics_%E2%80%93_Women%27s_200_metre_individual_medley
    if str_time.count(':') > 1:
        str_time = str_time.replace(':', '_', 1).replace(':', '.').replace('_', ':')
    
    # Special occurance where format is MM.SS.ff, convert to MM:SS.ff
    # https://en.wikipedia.org/wiki/Swimming_at_the_1980_Summer_Olympics_%E2%80%93_Women%27s_200_metre_butterfly
    if str_time.count('.') > 1:
        str_time = str_time.replace('.', ':', 1)

    if ':' in str_time: # Minute string
        return datetime.strptime(str_time, '%M:%S.%f').strftime('%M:%S.%f')
    elif (':' not in str_time) and ('.' not in str_time): # Second string
        return datetime.strptime(str_time, '%S').strftime('%M:%S.%f')
    else: # Second with micro-second string
        return datetime.strptime(str_time, '%S.%f').strftime('%M:%S.%f')

#%% Function 3

def mod_relay_table(df):
    """Function to modify relay tables to split all swimmers into different rows"""
    
    df_len = len(df)    # Get number of entries
    df = df.loc[df.index.repeat(4)].reset_index(drop = True) # Repeast each row four times
    
    # Get column index numbers
    name_loc = df.columns.get_loc("Name")
    split_loc = df.columns.get_loc("Split Time")
    
    # Iterate through original number of rows offset by four (number of repeated rows)
    for n in range(df_len):
        
        # Split string to a list of four sets of name to time and save as a dataframe
        results_str = df['Name'][4*n]
        
        # Format special occurances of 'NR' in string "(MM.ff NR)" or "(MM.ff) NR"
        # https://en.wikipedia.org/wiki/Swimming_at_the_2016_Summer_Olympics_%E2%80%93_Men%27s_4_%C3%97_100_metre_freestyle_relay
        # https://en.wikipedia.org/wiki/Swimming_at_the_2016_Summer_Olympics_%E2%80%93_Women%27s_4_%C3%97_100_metre_freestyle_relay
        results_str = results_str.replace('NR', '')

        # Format special occurances of 'WJ' in string "(MM.ff WJ)"
        # https://en.wikipedia.org/wiki/Swimming_at_the_2020_Summer_Olympics_%E2%80%93_Women%27s_4_%C3%97_200_metre_freestyle_relay
        results_str = results_str.replace('WJ', '')
        
        results_str = results_str.split(')')[:-1]
        results_str = [n.split('(') for n in results_str]  
        tmp_df = pd.DataFrame(results_str)
        
        # Replace dataframe entries by names and split times
        df.iloc[4*n:4*n+4, name_loc] = tmp_df.iloc[:,0]
        
        df.iloc[4*n:4*n+4, split_loc] = tmp_df.iloc[:,1]
    
    df['Split Time'] = df['Split Time'].apply(str2time)
    
    return df

#%% Function 4

def extract_wiki_tables(year, gender, distance, event):
    """Function to extract Olympic results from Wikipedia pages"""
    
    # Build Wikipedia URL from function arguments    
    URL = "https://en.wikipedia.org/wiki/Swimming_at_the_"+year+"_Summer_Olympics_%E2%80%93_"+gender+"%27s_"+distance+"_"+event
    
    # Read Wikipedia tables as DataFrame
    wiki_tables = pd.read_html(URL,header=0)
    
    # Select only tables with results, which all contain a column called 'Rank'
    wiki_tables = [table for table in wiki_tables if 'Rank' in table.columns]
       
    # Different results tables have different column names for the same datatype, hence need to standardise
    for n in range(len(wiki_tables)):
        
        if "Nationality" in wiki_tables[n].columns:
            wiki_tables[n] = wiki_tables[n].rename(columns = {'Nationality': 'Nation'})
        if "Swimmer" in wiki_tables[n].columns:
            wiki_tables[n] = wiki_tables[n].rename(columns = {'Swimmer': 'Name'})
        if "Swimmers" in wiki_tables[n].columns:
            wiki_tables[n] = wiki_tables[n].rename(columns = {'Swimmers': 'Name'})
        if "Names" in wiki_tables[n].columns:
            wiki_tables[n] = wiki_tables[n].rename(columns = {'Names': 'Name'})            
        if "Notes" not in wiki_tables[n].columns:
            wiki_tables[n]["Notes"] = "None"
        if "Time" in wiki_tables[n].columns:
            wiki_tables[n] = wiki_tables[n].rename(columns = {'Time': 'Total Time'})
            wiki_tables[n]['Total Time'] = wiki_tables[n]['Total Time'].astype(str)
        wiki_tables[n]['Notes'].fillna(value='None', inplace=True)
        
        wiki_tables[n].drop(wiki_tables[n].index[wiki_tables[n]['Notes'].str.contains('DSQ|DNS')], inplace=True)
        wiki_tables[n].drop(wiki_tables[n].index[wiki_tables[n]['Total Time'].str.contains('DSQ|DNS')], inplace=True)
            
        wiki_tables[n]['Split Time'] = "None"

    # Separate tables containing pre-final results, including heats and semi-finals
    pre_final_tables = wiki_tables[:-1]
    
    # Separate table containing final results
    final_tables = wiki_tables[-1]
    
    # Cleaning pre-final tables
    for n in range(len(pre_final_tables)):
        
        # Clean heats results tables
        if "Heat" in pre_final_tables[n].columns:
            pre_final_tables[n] = pre_final_tables[n].rename(columns = {'Heat': 'Stage'})
            pre_final_tables[n]['Stage'] = pre_final_tables[n]['Stage'].apply(lambda x: 'Heat')
        
        # Clean semi-final results tables
        else:
            pre_final_tables[n]['Stage'] = 'Semifinal'
        
        # Drop results null results, which can be due to not qualified or disqualified (DSQ)
        pre_final_tables[n] = pre_final_tables[n][pre_final_tables[n]["Rank"].notnull()]
    
    # Cleaning final results tables, including replacing medal icons with integer ranks, and dropping null results due to DSQ
    final_tables['Stage'] = 'Final'
    final_tables['Rank'] = final_tables['Rank'].fillna({0:1, 1:2, 2:3})
    
    # Concatenate all results tables into a single DataFrame for output
    results_table = pd.concat(pre_final_tables + [final_tables], ignore_index=True)
    
    # Cleaning the strings to be recorded in dataframe table        
    results_table['Event'] = event.replace('_', ' ').capitalize()
    if '%C3%97' in distance: distance = distance.replace('%C3%97', '×')
    results_table['Distance'] = distance.replace('_', ' ')
    
    # print(results_table.shape)
        
    # Rearrange columns
    results_table = results_table[['Event',
                                   'Distance',
                                   'Stage',
                                   'Rank',
                                   'Name',
                                   'Split Time',
                                   'Total Time',
                                   'Nation',
                                   'Notes'
                                   ]]
    
    # Modify relay events to split all swimmers into separate rows
    if "relay" in event:
        results_table = mod_relay_table(results_table)
    
    # Standardise time string object into datetime string objects
    results_table['Total Time'] = results_table['Total Time'].apply(str2time)
    
    return results_table

#%% Function 5

def extract_olympic_results(olympic_events):
    """
    Function to build a dictionary of Olympic swimming events results
    Input given by olympic_events dictionary    
    """
    
    # Initialise Olympic results dictionary, which will save Olympic year as
    # key, and the results as value, which is a nested dictionary for 'Men'
    # and 'Women' results
    olympic_results = dict()
    
    # Iterate through each Olympic year
    for year in olympic_events.keys():
        
        print("Olympic results for year", year)
        
        tmp_df = olympic_events[year]   # Extract swimming events for that year
        olympic_results[year] = {}      # Initialise results for that year
        
        #Iterate through each row of dataframe to access swimming event category
        for index, row in tmp_df.iterrows():
            
            # Build the strings to be used as arguments for "extract_wiki_tables" function
            distance = row['Distance'].replace(' ', '_').replace('k', 'kilo').replace('m', 'metre')
            event = row['Event'].lower().replace(' ', '_')
            if '×' in distance: distance = distance.replace('×', '_%C3%97_')
            
            print(year, distance, event)
            
            # At this stage we do not want marathon results
            if event == 'marathon': continue
        
            # Only build gender results if there are events that year for that gender
            # Concatenate all results in current year into a single dataframe table
            
            for gender in ['Men', 'Women']:
                
                if isinstance(row[gender], str):
                    if gender not in olympic_results[year].keys():
                        olympic_results[year][gender] = extract_wiki_tables(year, gender, distance, event)
                    else:
                        olympic_results[year][gender] = pd.concat([olympic_results[year][gender], extract_wiki_tables(year, gender, distance, event)]).reset_index(drop=True)
                        
    return olympic_results

#%% Function 6

def set_olympic_years(start_year, end_year):
    """Function to set start and end Olympic years from input start and end years"""
    
    olympic_start_year_index = [n%4 for n in range(start_year, start_year+4)].index(0)
    olympic_start_year = start_year + olympic_start_year_index

    olympic_end_year_index = [n%4 for n in range(end_year, end_year-4, -1)].index(0)
    olympic_end_year = end_year - olympic_end_year_index
    
    print('Olympic year range: ', olympic_start_year, ' to ', olympic_end_year)
    
    return range(olympic_start_year, olympic_end_year+1, 4)

#%% Extract Olympic results

# Define the year range in which the Olympic data is to be extracted
start_year = 1980
end_year = 2020

swim_events = ['Freestyle',
               'Backstroke',
               'Breaststroke',
               'Butterfly',
               'Individual medley',
               'Freestyle relay',
               'Medley relay',
               'Marathon'
               ]

swim_events = pd.DataFrame(swim_events)

olympic_year_range = set_olympic_years(start_year, end_year)
olympic_events = extract_olympic_events(olympic_year_range, swim_events)
olympic_results = extract_olympic_results(olympic_events)

#%% Export data to csv

for year in olympic_results.keys():
    
    for gender in ['Men', 'Women']:
        
        file_name = year + '_Olympics_' + gender + '.csv'
        olympic_results[year][gender].to_csv(file_name, encoding='utf-8-sig')

