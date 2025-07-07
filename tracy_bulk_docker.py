# source: https://chatgpt.com/share/6842f7c0-29dc-8003-9574-048726a5893a

#%%
import subprocess
import os
import glob


# %% USER SETTINGS

# Folder path where data is saved (.ab1 files)
folder_path = ['/Users/sebschu/Documents/senDS_cfb/code/tracy/data/sanger_seq']

# reference to align to
ref_name = 'fake_template.fa'

# outfile path
outfile_path = 'results/variant_trim'

# trimming options
trim_left = 50
trim_right= 200

# Docker image
docker_image = 'geargenomics/tracy:latest'  #replace with url for download if possible

#%%
# Create list of file paths and loop over each path name and run a container for each
file_paths = [file_path for file_path in glob.glob(os.path.join(folder_path, '*.ab1'))]

for file_path in file_paths:
    container_name = f'container_{file_path.split('/')[-1]}'
    docker_cmd = [
        'docker', 'run',
        '--rm',                                  # Remove the container
        '-v', f'{folder_path}/data:/home/sanger_seq/data:ro', # Mount data volume
        '-v', f'{folder_path}/results:/home/sanger_seq/results' # Mount results volume
        '--name', container_name,                # Optional: name the container
        '--platform', 'linux/amd64',             # platform (precede image!)
        docker_image,
        f'tracy decompose -v -r {ref_name} -o {outfile_path} --trimLeft {trim_left} --trimRight {trim_right} ', # command to run inside the docker container
    ]

    print('Running:', ' '.join(docker_cmd))
    
    try:
        subprocess.run(' '.join(docker_cmd), check=True)
    
    except subprocess.CalledProcessError as e:
        print(f'Error running container for {file_path}: {e}')

# %%
