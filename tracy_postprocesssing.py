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


# %%
