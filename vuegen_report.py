
# %%
import logging
import os
from pathlib import Path
import shutil
import subprocess
import yaml


# %% read crelevant onfig parameters
with open('./config.yaml', 'r', encoding='utf-8') as file:
    cfg = yaml.safe_load(file)

outdir_host = cfg['paths']['outdir_host']

# %% define variables
outdir_vuegen = Path(os.path.join(outdir_host, 'vuegen_report'))

# %% create vuegen folder and relevant sub-folders

subdir_names = ['mut_table_summary_01', 'alignments_02', 'traces_03']
for subdir_name in subdir_names:
    Path(os.makedirs(os.path.join(outdir_vuegen, subdir_name)))


# %% copy results files into vuegen folder




# %% create vuegen report
# vuegen and streamlit bash command:
# vuegen --directory ./outdir/zresults_vuegen/ --report_type streamlit
# streamlit run streamlit_report/sections/report_manager.py

#create streamlit report
try:
    subprocess.run(
        [
            'vuegen',
            '--directory',
            outdir_vuegen,
            '--report_type',
            'streamlit'
        ],
        check=True,
    )
except subprocess.CalledProcessError as e:
    logging.error(
        'Error generating vuegen report %s:%s: %s',
        e,
    )


#open report in streamlit app --> change this to on demand
try:
    subprocess.run(
        [
            'streamlit',
            'run',
            Path('streamlit_report/sections/report_manager.py')
        ],
        check=True,
    )
except subprocess.CalledProcessError as e:
    logging.error(
        'Error opening vuegen report with streamlit app %s:%s: %s',
        e,
    )


