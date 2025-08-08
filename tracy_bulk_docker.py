# source: https://chatgpt.com/share/6842f7c0-29dc-8003-9574-048726a5893a

#%%
import subprocess
import os
import glob
import yaml


# %% Read yaml configuration file
with open('./config.yaml', 'r') as file:
     cfg = yaml.safe_load(file)


# %% Download Docker image
try:
    subprocess.run(['docker', 'pull', f'{cfg['docker']['image']}:{cfg['docker']['version']}'], check=True)
    
except subprocess.CalledProcessError as e:
        print(f'Error pulling image {cfg['docker']['image']}:{cfg['docker']['version']}: {e}')


# %% Perform sequencing analysis

# Create list of file paths and loop over each path name and run a container for each
file_paths = [file_path for file_path in glob.glob(os.path.join(cfg['paths']['data_host'], '*.ab1'))]
print(file_paths)

# specify name of local docker image to be used
docker_image = f'{cfg['docker']['image']}:{cfg['docker']['version']}'

# run analysis (one container per sequencing analysis)
for file_path in file_paths:
    container_name = file_path.split('/')[-1]
    docker_cmd = [
        'docker', 'run',
        #'--rm',                                  # Remove the container
        '-v', f'{cfg['paths']['data_host']}:{cfg['paths']['data_docker']}:ro', # Mount data volume
        '-v', f'{cfg['paths']['outdir_host']}:{cfg['paths']['outdir_docker']}', # Mount outdir volume
        '--name', container_name, 
        '-i',                               #-i lets the conainer actively run
        '--platform', 'linux/amd64',             # platform (precede image!)
        docker_image,
        'tracy', 'decompose', '-v',         #tracy decompose cmd variant calling
        '-r', '/home/sanger_seq/data/reference.fa', #reference to align to
        '-o', '/home/sanger_seq/outdir/test_6Aug_new',     #outdirectory and outfile name
        '--trimLeft', f'{cfg['tracy']['trim_left']}',
        '--trimRight', f'{cfg['tracy']['trim_right']}', 
        '/home/sanger_seq/data/EF73244592_EF73244592.ab1'   #.ab1 file to use
    ]

    print('Running:', ' '.join(docker_cmd))
    
    try:
        subprocess.run(docker_cmd, check=True)
    
    except subprocess.CalledProcessError as e:
        print(f'Error running container for {file_path}: {e}')
