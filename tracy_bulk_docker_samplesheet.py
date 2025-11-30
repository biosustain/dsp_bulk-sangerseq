# source: https://chatgpt.com/share/6842f7c0-29dc-8003-9574-048726a5893a
# Script uses a samplesheet as a way to couple each sample with a single
# reference file to align to

# %%
import subprocess
import logging
import yaml
import pandas as pd
from Bio import SeqIO
from os import path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# %% Read yaml configuration file
with open('./config.yaml', 'r', encoding='utf-8') as file:
    cfg = yaml.safe_load(file)

datadir_host = cfg['paths']['data_host']
datadir_docker = cfg['paths']['data_docker']

outdir_host = cfg['paths']['outdir_host']
outdir_docker = cfg['paths']['outdir_docker']


# %% Download Docker image
try:
    subprocess.run(
        [
            'docker',
            'pull',
            '--platform',
            f'{cfg['docker']['platform']}',
            f'{cfg['docker']['image']}:{cfg['docker']['version']}',
        ],
        check=True,
    )
except subprocess.CalledProcessError as e:
    logging.error(
        'Error pulling image %s:%s: %s',
        cfg['docker']['image'],
        cfg['docker']['version'],
        e,
    )


# %% Perform sequencing analysis

# create sample-reference pairs

# read samplesheet
samplesheet_data_rel_dir = path.relpath(
    path.dirname(cfg['paths']['samplesheet']),
    start=datadir_host
)
samplesheet = pd.read_csv(
    cfg['paths']['samplesheet'],
    # Convert ab1_file to data dir relative paths
    converters={'ab1_file': lambda x: path.join(samplesheet_data_rel_dir, x)},
)
logging.info('Samplesheet loaded:\n%s', samplesheet)

# create sample-reference pairs as a list of tuples
sample_ref_df = samplesheet[
    ['sample_id', 'ab1_file', 'group', 'reference_id']
]
logging.debug('Sample-reference dataframe:\n%s', sample_ref_df)

sample_ref_pairs = list(sample_ref_df.itertuples(index=False))
logging.debug('Sample-reference pairs: %s', sample_ref_pairs)

logging.debug('First ab1 file: %s', sample_ref_pairs[0].ab1_file)
logging.debug('First reference: %s', sample_ref_pairs[0].reference_id)


# %% read relevant entries from multifasta
# and create temporary file for each fasta entry

# get unique reference ids and save as list
ref_names_set = {
    sample_ref_pair.reference_id
    for sample_ref_pair in sample_ref_pairs
}  # use a set to get unique values

ref_names_list = list(ref_names_set)
logging.info('Unique reference IDs: %s', ref_names_list)


# %% Parse multifasta file with reference ids and save each fasta entry
# (header plus sequence) in a fasta file in the host data folder
# (docker command will read the reference from there)

# get relevant single fasta entries from multifasta file and store in a list
with open(cfg['paths']['reference_fasta'], encoding='utf-8') as handle:
    for record in SeqIO.parse(handle, 'fasta'):
        if record.id in ref_names_list:
            SeqIO.write(
                record,
                path.join(datadir_host, f'{record.id}.fa'),
                'fasta'
            )

# %%
# run analysis (one container per sequencing analysis)
for sample_ref_pair in sample_ref_pairs:
    ab1_abs_path = path.join(
        datadir_docker, str(sample_ref_pair.ab1_file)
    )
    sample_id = sample_ref_pair.sample_id
    reference_name = (
        f'{sample_ref_pair.reference_id}.fa'
    )  # append file extension (.fa) for docker command
    logging.debug('Reference name: %s', reference_name)
    reference_path = path.join(
        datadir_docker, reference_name
    )

    docker_cmd = [
        'docker',
        'run',
        # Remove the container
        '--rm',
        # Mount data volume (ro: read-only)
        '-v',
        f'{datadir_host}:{datadir_docker}:ro',
        # Mount outdir volume
        '-v',
        f'{outdir_host}:{outdir_docker}',
        # container name
        '--name',
        f'decompose_{sample_id}',
        # -i option lets the container actively run
        '-i',
        # platform (precede image!)
        '--platform',
        cfg['docker']['platform'],
        # docker image and version to use
        f'{cfg['docker']['image']}:{cfg['docker']['version']}',
        # tracy decompose command for variant calling
        'tracy',
        'decompose',
        '-v',
        # reference to align to
        '-r',
        reference_path,
        # outdirectory and outfile name
        '-o',
        path.join(outdir_docker, str(sample_id)),
        # sequence trimming options
        '--trimLeft',
        f'{cfg['tracy']['trim_left']}',
        '--trimRight',
        f'{cfg['tracy']['trim_right']}',
        # .ab1 file to use
        ab1_abs_path,
    ]

    logging.info('Running decompose: %s', ' '.join(docker_cmd))

    try:
        subprocess.run(docker_cmd, check=True)

    except subprocess.CalledProcessError as e:
        logging.error(
            'Error running container for %s: %s',
            str(sample_ref_pair.ab1_file), e
        )

    docker_cmd = [
        'docker',
        'run',
        # Remove the container
        '--rm',
        # Mount data volume (ro: read-only)
        '-v',
        f'{datadir_host}:{datadir_docker}:ro',
        # Mount outdir volume
        '-v',
        f'{path.join(outdir_host, 'align')}:{outdir_docker}',
        # container name
        '--name',
        f'align_{sample_id}',
        # -i option lets the container actively run
        '-i',
        # platform (precede image!)
        '--platform',
        cfg['docker']['platform'],
        # docker image and version to use
        f'{cfg['docker']['image']}:{cfg['docker']['version']}',
        # tracy align command for variant calling
        'tracy', 'align',
        # reference to align to
        '-r',
        reference_path,
        # outdirectory and outfile name
        '-o',
        path.join(outdir_docker, str(sample_id)),
        # sequence trimming options
        '--trimLeft', f'{cfg['tracy']['trim_left']}',
        '--trimRight', f'{cfg['tracy']['trim_right']}', 
        # .ab1 file to use
        ab1_abs_path
    ]

    logging.info('Running align: %s', ' '.join(docker_cmd))

    try:
        subprocess.run(docker_cmd, check=True)

    except subprocess.CalledProcessError as e:
        logging.error(
            'Error running container for %s: %s',
            str(sample_ref_pair.ab1_file), e
        )


# %% Run tracy assemble against the reference in docker container
# (for the analysis of overlapping reads)

# %%
# group data by group in sample sheet
# run tracy assemble in docker container

for group_name, group in samplesheet.groupby(by='group'):
    # Generate list of paths to files that get assembled
    # (paths in docker container)
    file_paths_list = [
        path.join(datadir_docker, row['ab1_file']) for _, row in group.iterrows()
    ]
    logging.debug('File paths for assembly: %s', file_paths_list)

    # Join sample ids that get assembled
    sample_id_joined = '_'.join(group['sample_id'].tolist())
    logging.info('Processing assembly group: %s', sample_id_joined)

    # Append file extension (.fa) for docker command
    # Use first reference since all in group should have same reference
    assert group['reference_id'].nunique() == 1, f'Group {group_name} has multiple reference IDs: {group['reference_id'].unique()}'
    reference_name = group['reference_id'].iloc[0] + '.fa'
    logging.debug('Reference name: %s', reference_name)

    docker_cmd_assemble = [
        'docker', 'run',
        # Remove the container
        '--rm',
        # Mount data volume (ro: read-only)
        '-v',
        f'{datadir_host}:{datadir_docker}:ro',
        # Mount outdir volume
        '-v',
        f'{outdir_host}:{outdir_docker}',
        # container name
        '--name', f'assemble_{sample_id_joined}', 
        # -i option lets the container actively run
        '-i',
        # platform (precede image!)
        '--platform', cfg['docker']['platform'],             
        # docker image and version to use
        f'{cfg['docker']['image']}:{cfg['docker']['version']}',
        # tracy assemble command for assembling traces against the reference
        'tracy',
        'assemble',
        # reference to align to
        '-r',
        path.join(datadir_docker, reference_name),
        # outdirectory and outfile name
        '-o',
        path.join(outdir_docker, sample_id_joined),
        # sequence trimming options
        # (only trimming stringency can be specified but not fixed values
        # using trimLeft and trimRight; default according to tracy assemble
        # --help: 4 --> set here explicitly ([0:9], 0: disable trimming))
        '-t',
        '4',
        # .ab1 files to assemble (passed here as a list; see also below)
        *file_paths_list
    ]

    logging.info('Running assemble: %s', ' '.join(docker_cmd_assemble))

    try:
        subprocess.run(docker_cmd_assemble, check=True)

    except subprocess.CalledProcessError as e:
        logging.error(
            'Error running container for group %s: %s',
            str(sample_id_joined), e
        )


# %% Run tracy decompose using the assembled traces
# against the reference for variant calling
# TO BE IMPLEMENTED if necessary
