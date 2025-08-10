# Script to perform post-processing of results from script 'tracy_bulk_docker.py'
# relevant results from json output files is extracted and consolidated into a concise results reporting table

# %%
import json
import pandas as pd


# %% read all json files