
# %%
import logging
import os
from pathlib import Path
import subprocess
import yaml
from util.helper_functions import copy_files, convert_files_to_markdown_read_write


# %% read relevant config parameters
with open(Path('./config.yaml'), 'r', encoding='utf-8') as file:
    cfg = yaml.safe_load(file)

outdir_host = Path(cfg['paths']['outdir_host'])
vuegen_report_type = cfg['vuegen']['report_type']


# %% define variables

#create directory and subdirectory for the vuegen report structure: here tracy's outfiles will be saved
outdir_vuegen = outdir_host / 'vuegen_report' / 'report_structure'
outdir_vuegen.mkdir(parents=True, exist_ok=True)

#sub-directory and sub-sub-directory names where files will be copied to
subdir_names = ['01_Mutation_tables_decompose', 
                '02_alignments_decompose', 
                '03_alignments_align', 
                '04_sequence_assembly_assemble'
                ]

subdir_names_alignments_decompose_02 = ['align1', 'align2', 'align3']

subdir_names_seq_assemble_04 = ['alignments', 'consensus_sequences']


#mutation table output to be copied
src_dir_mut_comb = Path(f'{outdir_host}/results_combined.csv')
dest_dir_mut_comb = outdir_vuegen / subdir_names[0] / 'results_combined.csv'

#files to copy from decompose dir
src_dir_decompose = Path(f'{outdir_host}/decompose')
dest_dir_decompose = Path(outdir_vuegen / subdir_names[1])

#files to copy from align dir
src_dir_align = Path(f'./{outdir_host}/align')    #source dir
dest_dir_align = Path(outdir_vuegen / subdir_names[2])    #destination dir
file_ext_align = ('.txt') #file extensions

#files to copy from assembly dir
src_dir_assemble = Path(f'{outdir_host}/assemble')
dest_dir_assemble = Path(outdir_vuegen / subdir_names[3])


# %% create vuegen directory and relevant sub-folders

#vuegen directory
for subdir_name in subdir_names:
    os.makedirs(outdir_vuegen / subdir_name, exist_ok=True)

#sub-directories of the 02_alignments_decompose directory
for subdir in subdir_names_alignments_decompose_02:
    os.makedirs(dest_dir_decompose / subdir, exist_ok=True)

#sub-directories of the 04_sequence_assembly_assemble directory
for subdir_assemble in subdir_names_seq_assemble_04:
    os.makedirs(dest_dir_assemble / subdir_assemble, exist_ok=True)


# %% copy results files into vuegen folder and convert .align* files to markdown (.md)

##copy mutation summary file (from decompose process)
copy_files(src_file=src_dir_mut_comb, 
           dest_file=dest_dir_mut_comb)

##copy files from decompose dir as markdowns
for i in subdir_names_alignments_decompose_02:
    convert_files_to_markdown_read_write(
                src_dir_path=src_dir_decompose, 
                src_file_ext=f'.{i}', 
                dest_dir_path=dest_dir_decompose / i
                )

##copy files from align dir as markdowns
convert_files_to_markdown_read_write(
                src_dir_path=src_dir_align, 
                src_file_ext=file_ext_align, 
                dest_dir_path=dest_dir_align
                )

##copy files from assemble dir as markdowns
#alignments
convert_files_to_markdown_read_write(
        src_dir_path=src_dir_assemble, 
        src_file_ext='.align.fa', 
        dest_dir_path=dest_dir_assemble / subdir_names_seq_assemble_04[0]
        )

#consensus sequences
convert_files_to_markdown_read_write(
        src_dir_path=src_dir_assemble, 
        src_file_ext='.cons.fa', 
        dest_dir_path=dest_dir_assemble / subdir_names_seq_assemble_04[1]
        )

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
            vuegen_report_type
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
