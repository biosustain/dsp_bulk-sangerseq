# Script to perform post-processing of results from script 'tracy_bulk_docker.py'
# relevant results from json output files are extracted and consolidated into a concise results reporting table
# Electropherogram traces are plotted

# %%
import json
import pandas as pd
import yaml
import glob
import os
from Bio import SeqIO
from collections import defaultdict
import matplotlib.pyplot as plt
import plotly.express as px



# %% Read yaml configuration file
with open('./config.yaml', 'r') as file:
     cfg = yaml.safe_load(file)


# %% add all json files from host directory to a list for simple bulk processing
file_paths = [file_path for file_path in glob.glob(os.path.join(cfg['paths']['outdir_host'], '*.json'))]

print(file_paths)


# %% extract data from each json file
result_df_dict = {}
for file_path in file_paths:
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        #print(data['meta']['arguments']['input'])
        #print(data['variants']['columns'])
        #print(data['variants']['rows'])

        # generate sample name
        sample_name = data['meta']['arguments']['input'].split('.')[0]
        #print(sample_name)

        # generate dataframe with results
        result_df = pd.DataFrame(data['variants']['rows'], columns=data['variants']['columns'])

        # add each df to a dictionary
        result_df_dict[sample_name] = result_df

print(result_df_dict['EF73244592_EF73244592'])

#%%
# export each df of the dictionary
for sample_name, result_df in result_df_dict.items():
    result_df.to_csv(f'{cfg['paths']['outdir_host']}/{sample_name}.csv')


# %% Plot electropherogram traces
# see Biopython documentation: https://biopython.org/wiki/ABI_traces
# and the reference therein: http://www.appliedbiosystem.com/support/software_community/ABIF_File_Format.pdf 


# Create list of file paths
ab1_paths = [ab1_path for ab1_path in glob.glob(os.path.join(cfg['paths']['data_host'], '*.ab1'))]
print(ab1_paths)

#%%
# Loop over each path name to plot the Sanger sequencing trace
for ab1_path in ab1_paths:
    file_name_ab1 = ab1_path.split('/')[-1]
    sample_name_ab1 = file_name_ab1.split('.')[0]
      
    record = SeqIO.read(ab1_path, 'abi')
    print(record)
    print(list(record.annotations.keys()))
    print(list(record.annotations['abif_raw'].keys()))

    channels = ['DATA9', 'DATA10', 'DATA11', 'DATA12']
    trace = defaultdict(list)
    for c in channels:
        trace[c] = record.annotations['abif_raw'][c]

    print(trace['DATA9'])

    #plot Sanger traces with matplotlib
    plt.plot(trace['DATA9'], color='blue')
    plt.plot(trace['DATA10'], color='red')
    plt.plot(trace['DATA11'], color='green')    
    plt.plot(trace['DATA12'], color='yellow')
    plt.show()

    # plot Sanger traces with plotly-express
    fig = px.line(y=[trace['DATA9'], trace['DATA10'], trace['DATA11'], trace['DATA12']], title=sample_name_ab1)

    fig.write_html(f'{cfg['paths']['outdir_host']}/{sample_name_ab1}.html')
    fig.show()

# %%
