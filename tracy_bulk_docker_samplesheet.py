# source: https://chatgpt.com/share/6842f7c0-29dc-8003-9574-048726a5893a
# Script uses a samplesheet as a way to couple each sample with a single reference file rto align to

#%%
import subprocess
import os
import glob
import yaml
import pandas as pd
from Bio import SeqIO
import tempfile


# %% Read yaml configuration file
with open('./config.yaml', 'r') as file:
     cfg = yaml.safe_load(file)


# %% Download Docker image
try:
    subprocess.run(['docker', 'pull', '--platform', f'{cfg['docker']['platform']}', f'{cfg['docker']['image']}:{cfg['docker']['version']}'], check=True)
    
except subprocess.CalledProcessError as e:
        print(f'Error pulling image {cfg['docker']['image']}:{cfg['docker']['version']}: {e}')


# %% Perform sequencing analysis

#create sample-reference pairs

#read samplesheet
samplesheet = pd.read_csv(cfg['paths']['samplesheet'])
print(samplesheet)

#create sample-reference pairs as a list of tuples
sample_ref_df = samplesheet[['sample_id', 'ab1_file', 'group', 'reference_id']]
print(sample_ref_df)

sample_ref_pairs = list(sample_ref_df.itertuples(index=False))
print(sample_ref_pairs)

print(sample_ref_pairs[0].ab1_file)
print(sample_ref_pairs[0].reference_id)


#%% read relevant entries from multifasta and create temporary file for each fasta entry

#get unqiue reference ids and save as list
ref_names_set = {sample_ref_pair.reference_id for sample_ref_pair in sample_ref_pairs}  #use a set to get unique values

ref_names_list = list(ref_names_set)
print(ref_names_list)


#%% Parse multifasta file with reference ids and save each fasta entry (header plus sequence) in a fasta file in the host data folder (docker command will read the reference form there)

# get relevant single fasta entries from multifasta file and store in a list
with open(cfg['paths']['reference_fasta']) as handle:
    for record in SeqIO.parse(handle, 'fasta'):
        if record.id in ref_names_list:
            fasta_entry = f'>{record.id}\n{record.seq}'
            
            #Save each fasta entry in a fasta file
            with open(f'{cfg['paths']['data_host']}/{record.id}.fa', 'w') as file:
                file.write(fasta_entry)

#%%
# run analysis (one container per sequencing analysis)
for sample_ref_pair in sample_ref_pairs:
    
    file_name = sample_ref_pair.ab1_file.split('/')[-1]
    sample_id = sample_ref_pair.sample_id
    reference_name = sample_ref_pair.reference_id + '.fa'   #append file extension (.fa) for docker command
    print(reference_name)

    docker_cmd = [
        'docker', 'run',
        # Remove the container
        '--rm',                                  
        # Mount data volume (ro: read-only)
        '-v', f'{cfg['paths']['data_host']}:{cfg['paths']['data_docker']}:ro',
        # Mount outdir volume
        '-v', f'{cfg['paths']['outdir_host']}:{cfg['paths']['outdir_docker']}', 
        # container name
        '--name', f'decompose_{sample_id}', 
        # -i option lets the conainer actively run
        '-i',                               
        # platform (precede image!)
        '--platform', cfg['docker']['platform'],             
        # docker image and version to use
        f'{cfg['docker']['image']}:{cfg['docker']['version']}',
        
        # tracy decompose command for variant calling
        'tracy', 'decompose', '-v',
        # reference to align to
        '-r', f'{cfg['paths']['data_docker']}/{reference_name}',
        # outdirectory and outfile name
        '-o', f'{cfg['paths']['outdir_docker']}/{sample_id}',
        # sequence trimming options
        '--trimLeft', f'{cfg['tracy']['trim_left']}',
        '--trimRight', f'{cfg['tracy']['trim_right']}', 
        # .ab1 file to use
        f'{cfg['paths']['data_docker']}/{file_name}'
    ]

    print('Running decompose:', ' '.join(docker_cmd))
    
    try:
        subprocess.run(docker_cmd, check=True)
    
    except subprocess.CalledProcessError as e:
        print(f'Error running container for {sample_ref_pair.ab1_file}: {e}')

    docker_cmd = [
        'docker', 'run',
        # Remove the container
        '--rm',                                  
        # Mount data volume (ro: read-only)
        '-v', f'{cfg['paths']['data_host']}:{cfg['paths']['data_docker']}:ro',
        # Mount outdir volume
        '-v', f'{cfg['paths']['outdir_host']}/align:{cfg['paths']['outdir_docker']}', 
        # container name
        '--name', f'align_{sample_id}', 
        # -i option lets the conainer actively run
        '-i',                               
        # platform (precede image!)
        '--platform', cfg['docker']['platform'],             
        # docker image and version to use
        f'{cfg['docker']['image']}:{cfg['docker']['version']}',
        
        # tracy align command for variant calling
        'tracy', 'align',
        # reference to align to
        '-r', f'{cfg['paths']['data_docker']}/{reference_name}',
        # outdirectory and outfile name
        '-o', f'{cfg['paths']['outdir_docker']}/{sample_id}',
        # sequence trimming options
        '--trimLeft', f'{cfg['tracy']['trim_left']}',
        '--trimRight', f'{cfg['tracy']['trim_right']}', 
        # .ab1 file to use
        f'{cfg['paths']['data_docker']}/{file_name}'
    ]

    print('Running align:', ' '.join(docker_cmd))
    
    try:
        subprocess.run(docker_cmd, check=True)
    
    except subprocess.CalledProcessError as e:
        print(f'Error running container for {sample_ref_pair.ab1_file}: {e}')

# %%
