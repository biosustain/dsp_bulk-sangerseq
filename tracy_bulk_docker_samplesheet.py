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


# %% Create sample-reference pairs

#read samplesheet
samplesheet = pd.read_csv(cfg['paths']['samplesheet'])
print(samplesheet)

#create sample-reference pairs as a list of tuples
sample_ref_df = samplesheet[['ab1_1', 'reference']]
print(sample_ref_df)

sample_ref_pairs = list(sample_ref_df.itertuples(index=False))
print(sample_ref_pairs)

print(sample_ref_pairs[0].ab1_1)
print(sample_ref_pairs[0].reference)



# %% Download Docker image
try:
    subprocess.run(['docker', 'pull', f'{cfg['docker']['image']}:{cfg['docker']['version']}'], check=True)
    
except subprocess.CalledProcessError as e:
        print(f'Error pulling image {cfg['docker']['image']}:{cfg['docker']['version']}: {e}')


# %% Perform sequencing analysis

# Create list of file paths and loop over each path name and run a container for each
file_paths = [file_path for file_path in glob.glob(os.path.join(cfg['paths']['data_host'], '*.ab1'))]
print(file_paths)

# run analysis (one container per sequencing analysis)
for file_path in file_paths:
    
    file_name = file_path.split('/')[-1]
    container_name = file_name.split('.')[0]

    docker_cmd = [
        'docker', 'run',
        # Remove the container
        '--rm',                                  
        # Mount data volume (ro: read-only)
        '-v', f'{cfg['paths']['data_host']}:{cfg['paths']['data_docker']}:ro',
        # Mount outdir volume
        '-v', f'{cfg['paths']['outdir_host']}:{cfg['paths']['outdir_docker']}', 
        # container name
        '--name', container_name, 
        # -i option lets the conainer actively run
        '-i',                               
        # platform (precede image!)
        '--platform', 'linux/amd64',             
        # docker image and version to use
        f'{cfg['docker']['image']}:{cfg['docker']['version']}',
        
        # tracy decompose command for variant calling
        'tracy', 'decompose', '-v',
        # reference to align to
        '-r', f'{cfg['paths']['data_docker']}/{cfg['tracy']['ref_name']}',
        # outdirectory and outfile name
        '-o', f'{cfg['paths']['outdir_docker']}/{container_name}',
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
        print(f'Error running container for {file_path}: {e}')

