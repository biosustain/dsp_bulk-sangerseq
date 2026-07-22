process PREPARE_INPUTS {
    container 'python:3.12'

    input:
    path samplesheet_file
    path reference_fasta

    output:
    path 'samples.tsv', emit: samples_tsv
    path 'assemblies.tsv', emit: assemblies_tsv
    path 'references/*.fa', emit: reference_files

    script:
    def data_dir_abs = file(params.data_dir).toRealPath().toString()
    """
    python ${projectDir}/scripts/prepare_tracy_inputs.py \
        --samplesheet ${samplesheet_file} \
        --reference-fasta ${reference_fasta} \
        --data-dir ${data_dir_abs} \
        --samples-output samples.tsv \
        --assemblies-output assemblies.tsv \
        --reference-dir references
    """
}
