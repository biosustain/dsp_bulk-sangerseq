# Script to perform post-processing of results from script 'tracy_bulk_docker.py'
# relevant results from json output files is extracted and consolidated into a concise results reporting table

# %%
import json
import pandas as pd
import yaml
import glob
import os


# %% Read yaml configuration file
with open('./config.yaml', 'r') as file:
     cfg = yaml.safe_load(file)


# %% add all json files from host directory to a list for simple bulk processing
file_paths = [file_path for file_path in glob.glob(os.path.join(cfg['paths']['outdir_host'], '*.json'))]

print(file_paths)


# %% extract data from each json file
for file_path in file_paths:
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        print(data)
        
# %%
