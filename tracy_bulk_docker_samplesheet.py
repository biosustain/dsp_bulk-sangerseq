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
from pathlib import Path
import itertools


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
            SeqIO.write(record, f'{cfg['paths']['data_host']}/{record.id}.fa', 'fasta')

#%%
# run analysis (one container per sequencing analysis)
for sample_ref_pair in sample_ref_pairs:
    
    file_name = Path(sample_ref_pair.ab1_file).name
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


# %% Run tracy assemble against the reference in docker container (for the analysis of overlapping reads)

#group data by group in sample sheet
grouped_input = samplesheet.groupby(by='group')
print(grouped_input)

new = grouped_input.apply(lambda x: list(x.itertuples(index=False))).reset_index()
print(new)

#rename column
new.columns = ['group', 'samples']
print(new)

#select samples column and convert to a list of lists
new_select = new['samples']
print(new_select)

#export for easier visualisation
new_select.to_csv('./outdir/new_select_assembly_groups.csv')

assembly_groups = new_select.values.tolist()    #yields a list of lists
print(assembly_groups)

#%%
#run tracy assemble in docker container

for group in assembly_groups:

    #generate fa list of paths to files that get assembled (paths in docker container)
    file_paths_list = [f'{cfg['paths']['data_docker']}/{file_path.ab1_file.split('/')[-1]}' for file_path in group]
    print(file_paths_list)

    #join sample ids that get assembled
    sample_id_joined = '_'.join([sample.sample_id for sample in group])
    print(sample_id_joined)

    #append file extension (.fa) for docker command
    refs_temp = [reference.reference_id + '.fa' for reference in group]
    print(refs_temp)    #has duplicated reference files

    reference_name = ''.join((set(refs_temp)))   #delete identical reference files in list because tracy assemble command only accepts one reference file
    print(reference_name)

    docker_cmd_assemble = [
        'docker', 'run',
        # Remove the container
        '--rm',                                  
        # Mount data volume (ro: read-only)
        '-v', f'{cfg['paths']['data_host']}:{cfg['paths']['data_docker']}:ro',
        # Mount outdir volume
        '-v', f'{cfg['paths']['outdir_host']}:{cfg['paths']['outdir_docker']}', 
        # container name
        '--name', f'assemble_{sample_id_joined}', 
        # -i option lets the conainer actively run
        '-i',                               
        # platform (precede image!)
        '--platform', cfg['docker']['platform'],             
        # docker image and version to use
        f'{cfg['docker']['image']}:{cfg['docker']['version']}',
        
        # tracy assmble command for assembling traces againbst the reference
        'tracy', 'assemble',
        # reference to align to
        '-r', f'{cfg['paths']['data_docker']}/{reference_name}',
        # outdirectory and outfile name
        '-o', f'{cfg['paths']['outdir_docker']}/{sample_id_joined}',
        # sequence trimming options (only trimming stringency can be specified but not fixed values using trimLeft and trimRight; default according to tracy assemble --help: 4 --> set here explicitly ([0:9], 0: disable trimming))
        '-t', '4',
        # .ab1 files to assemble (passed here as a list; see also below) 
        file_paths_list     
    ]

    #flatten docker_assemble_cmd because the file_path_list variable is a list(inspired by https://stackoverflow.com/questions/22569094/how-to-flatten-a-list-with-various-data-types-int-tuple)
    docker_cmd_assemble_flattened = list(itertools.chain(*(i if isinstance(i, list) else (i,) for i in docker_cmd_assemble)))

    print('Running assemble:', ' '.join(docker_cmd_assemble_flattened))
    
    try:
        subprocess.run(docker_cmd_assemble_flattened, check=True)
    
    except subprocess.CalledProcessError as e:
        print(f'Error running container for TO BE FILLED: {e}')




# %% Run tracy decompose using the assembled traces against the reference for variant calling
#TO BE IMPLEMENTED if necessary
