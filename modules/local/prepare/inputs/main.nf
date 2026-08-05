process PREPARE_INPUTS {
    container 'python:3.12'

    input:
    path samplesheet_file
    path reference_fasta
    path data_dir

    output:
    path 'samples.tsv', emit: samples_tsv
    path 'assemblies.tsv', emit: assemblies_tsv
    path 'references/*.fa', emit: reference_files

    script:
    """
    prepare_tracy_inputs.py \
        --samplesheet ${samplesheet_file} \
        --reference-fasta ${reference_fasta} \
        --data-dir ${data_dir} \
        --samples-output samples.tsv \
        --assemblies-output assemblies.tsv \
        --reference-dir references
    """
}
