# source: https://chatgpt.com/share/6842f7c0-29dc-8003-9574-048726a5893a
# Script uses a samplesheet as a way to couple each sample with a single reference file rto align to

#%%
import subprocess
import os
import yaml
import pandas as pd


# %% Read yaml configuration file
with open('./config.yaml', 'r') as file:
     cfg = yaml.safe_load(file)


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
        "docker",
        "compose",
        "-p",
        str(sample_id),
        "up"
    ]

    params = dict(
        REFERENCE_NAME=reference_name,
        SAMPLE_ID=sample_id,
        FILE_NAME=file_name,
        TRIM_LEFT=str(cfg["tracy"]["trim_left"]),
        TRIM_RIGHT=str(cfg["tracy"]["trim_right"]),
        DATA_HOST=os.path.abspath(cfg["paths"]["data_host"]),
        OUTDIR_HOST=os.path.abspath(cfg["paths"]["outdir_host"]),
    )

    print("Running:", " ".join(docker_cmd))
    print("With env params:\n", '\n'.join([f"\t{k}={v}" for k, v in params.items()]))

    try:
        subprocess.run(docker_cmd, check=True, env=dict(os.environ, **params))
    except subprocess.CalledProcessError as e:
        print(f"Error for {sample_ref_pair.ab1_1}: {e}")
    finally:
        # tear down the containers after run
        subprocess.run(['docker', 'compose', '-p', str(sample_id), 'down'])
