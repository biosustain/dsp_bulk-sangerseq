# source: https://chatgpt.com/share/6842f7c0-29dc-8003-9574-048726a5893a

#%%
import subprocess
import os
import glob


# %% USER SETTINGS

# Folder path where data is saved (.ab1 files) and outfiles will be saved
data_path = '/Users/sebschu/Documents/senDS_cfb/code/dsp_bulk-sangerseq/data/sanger_seq'

outdir_path = '/Users/sebschu/Documents/senDS_cfb/code/dsp_bulk-sangerseq/outdir/sanger_seq'

# reference to align to
ref_name = 'reference.fa'

# outfile path -- Double-check with docker command
outfile_path = 'results/bulk_test'

# trimming options
trim_left = 50
trim_right= 200

# Docker image version
image_version = 'latest'

# %% download Docker image

#pull docker image to local machine
try:
    subprocess.run(['docker', 'pull', f'geargenomics/tracy:{image_version}'], check=True)
    
except subprocess.CalledProcessError as e:
        print(f'Error pulling image geargenomics/tracy:{image_version}: {e}')

# specify name of local docker image to be used
docker_image = f'geargenomics/tracy:{image_version}'

#%%
# Create list of file paths and loop over each path name and run a container for each
file_paths = [file_path for file_path in glob.glob(os.path.join(data_path, '*.ab1'))]
print(file_paths)

#%%
for file_path in file_paths:
    container_name = f'container_{file_path.split('/')[-1]}'
    docker_cmd = [
        'docker', 'run',
        #'--rm',                                  # Remove the container
        '-v', f'{data_path}:/home/sanger_seq/data', # Mount data volume
        '-v', f'{outdir_path}:/home/sanger_seq/outdir', # Mount outdir volume
        '--name', container_name, 
        '-i', #-i lets the conainer actively run
        '--platform', 'linux/amd64',             # platform (precede image!)
        docker_image,
        'tracy', '--help'
        #f'tracy decompose -v -r reference.fa -o test_6Aug --trimLeft {trim_left} --trimRight {trim_right} ' # command to run inside the docker container
    ]

    print('Running:', ' '.join(docker_cmd))
    
    try:
        subprocess.run(docker_cmd, check=True)
    
    except subprocess.CalledProcessError as e:
        print(f'Error running container for {file_path}: {e}')

# %%
