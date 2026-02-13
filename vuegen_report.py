
# %%
import logging
import os
from pathlib import Path
import subprocess
import yaml
from util.helper_functions import copy_files, copy_files_extension


# %% read relevant onfig parameters
with open('./config.yaml', 'r', encoding='utf-8') as file:
    cfg = yaml.safe_load(file)

outdir_host = cfg['paths']['outdir_host']


# %% define variables
outdir_vuegen = os.path.join(outdir_host, 'vuegen_report')

#sub-directory names where files will be copied to
subdir_names = ['mut_table_summary_01', 'alignments_02', 'traces_03']

#mutation table output to be copied
src_dir_mut_comb = 'outdir/results_combined.csv'
dest_dir_mut_comb = f'./outdir/vuegen_report/{subdir_names[0]}/results_combined.csv'

#files to copy from decompose dir
src_dir_decompose = 'outdir/decompose'
dest_dir_decompose = f'./outdir/vuegen_report/{subdir_names[1]}'
file_ext_decompose = ('.align1', '.align2', '.align3')

#files to copy from align dir
src_dir_align = './outdir/align'    #source dir
dest_dir_align = f'./outdir/vuegen_report/{subdir_names[2]}'    #destination dir
file_ext_align = ('.json', '.html') #file extensions

#files to copy from assembly process

#TO BE ADDED 


# %% create vuegen folder and relevant sub-folders
for subdir_name in subdir_names:
    os.makedirs(Path(os.path.join(outdir_vuegen, subdir_name)), exist_ok=True)


# %% copy results files into vuegen folder

#copy mutation sumamry file
copy_files(src_file=src_dir_mut_comb, 
           dest_file=dest_dir_mut_comb)

#copy files from decompose dir
copy_files_extension(src_dir=src_dir_decompose, 
                     dest_dir=dest_dir_decompose, 
                     file_ext=file_ext_decompose)

#copy files from align dir
copy_files_extension(src_dir=src_dir_align, 
                     dest_dir=dest_dir_align, 
                     file_ext=file_ext_align)




#%%
#try:
    #copy summary mutation file

    #copy Sanger traces (.json, and .htmk)
#    src_dir = './outdir/align'
#    dest_dir = './outdir/vuegen_report/traces_03'
    
#    for filename in os.listdir(src_dir):
#        if filename.endswith(('.json', '.html')):
#            shutil.copy2(src_dir + filename, dest_dir)
#    print("File copied successfully.")

#except:
#    print('Error occured while copying files.')



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


