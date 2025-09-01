# source: https://chatgpt.com/share/6842f7c0-29dc-8003-9574-048726a5893a
# Script uses a samplesheet as a way to couple each sample with a single reference file rto align to

#%%
import subprocess
import os
import glob
import yaml
import pandas as pd


# %% Read yaml configuration file
with open('./config.yaml', 'r') as file:
     cfg = yaml.safe_load(file)


# %% Download Docker image
try:
    subprocess.run(['docker', 'pull', f'{cfg['docker']['image']}:{cfg['docker']['version']}'], check=True)
    
except subprocess.CalledProcessError as e:
        print(f'Error pulling image {cfg['docker']['image']}:{cfg['docker']['version']}: {e}')


# %% Perform sequencing analysis

#create sample-reference pairs

#read samplesheet
samplesheet = pd.read_csv(cfg['paths']['samplesheet'])
print(samplesheet)

#create sample-reference pairs as a list of tuples
sample_ref_df = samplesheet[['sample_id', 'ab1_1', 'reference']]
print(sample_ref_df)

sample_ref_pairs = list(sample_ref_df.itertuples(index=False))
print(sample_ref_pairs)

print(sample_ref_pairs[0].ab1_1)
print(sample_ref_pairs[0].reference)

#%%
# run analysis (one container per sequencing analysis)
for sample_ref_pair in sample_ref_pairs:
    
    file_name = sample_ref_pair.ab1_1.split('/')[-1]
    sample_id = sample_ref_pair.sample_id
    reference_name = sample_ref_pair.reference.split('/')[-1]

    docker_cmd = [
        'docker', 'run',
        # Remove the container
        '--rm',                                  
        # Mount data volume (ro: read-only)
        '-v', f'{cfg['paths']['data_host']}:{cfg['paths']['data_docker']}:ro',
        # Mount outdir volume
        '-v', f'{cfg['paths']['outdir_host']}:{cfg['paths']['outdir_docker']}', 
        # container name
        '--name', sample_id, 
        # -i option lets the conainer actively run
        '-i',                               
        # platform (precede image!)
        '--platform', 'linux/amd64',             
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

    print('Running:', ' '.join(docker_cmd))
    
    try:
        subprocess.run(docker_cmd, check=True)
    
    except subprocess.CalledProcessError as e:
        print(f'Error running container for {sample_ref_pair.ab1_1}: {e}')
