
# %%
import logging
import os
from pathlib import Path
import subprocess
import yaml
from util.helper_functions import copy_files, copy_files_extension,  convert_files_to_markdown_read_write


# %% read relevant onfig parameters
with open('./config.yaml', 'r', encoding='utf-8') as file:
    cfg = yaml.safe_load(file)

outdir_host = cfg['paths']['outdir_host']


# %% define variables
outdir_vuegen = os.path.join(outdir_host, 'vuegen_report')

#sub-directory names where files will be copied to
subdir_names = ['01_Mutation_tables_decompose', 
                '02_alignments_decompose', 
                '03_traces'
                ]
subdir_names_alignments_decompose_02 = ['align1', 'align2', 'align3']

#mutation table output to be copied
src_dir_mut_comb = 'outdir/results_combined.csv'
dest_dir_mut_comb = f'./outdir/vuegen_report/{subdir_names[0]}/results_combined.csv'

#files to copy from decompose dir
src_dir_decompose = 'outdir/decompose'
dest_dir_decompose = f'./outdir/vuegen_report/{subdir_names[1]}'

#files to copy from align dir
src_dir_align = './outdir/align'    #source dir
dest_dir_align = f'./outdir/vuegen_report/{subdir_names[2]}'    #destination dir
file_ext_align = ('.json', '.html') #file extensions

#files to copy from assembly process

#TO BE ADDED 


# %% create vuegen folder and relevant sub-folders
for subdir_name in subdir_names:
    os.makedirs(Path(os.path.join(outdir_vuegen, subdir_name)), exist_ok=True)


for subdir in subdir_names_alignments_decompose_02:
    os.makedirs(Path(os.path.join(dest_dir_decompose, subdir)), exist_ok=True)


# %% copy results files into vuegen folder and convert .align* files to markdown (.md)

#copy mutation summary file
copy_files(src_file=src_dir_mut_comb, 
           dest_file=dest_dir_mut_comb)

#copy files from decompose dir
for i in subdir_names_alignments_decompose_02:
    convert_files_to_markdown_read_write(
                src_dir_path=src_dir_decompose, 
                src_file_ext=f'.{i}', dest_dir_path=f'{dest_dir_decompose}/{i}'
                )

#copy files from align dir
# Todo: read aling files and then create markdown file from it 
copy_files_extension(src_dir=src_dir_align, 
                     dest_dir=dest_dir_align, 
                     file_ext=file_ext_align)


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



# %%
