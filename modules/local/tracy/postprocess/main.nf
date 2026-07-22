process TRACY_POSTPROCESS {

    container 'python:3.12'

    publishDir "${params.outdir}", mode: 'copy', pattern: '*.csv'

    input:
    path json_files

    output:
    path '*.csv', emit: results
    path 'results_combined.csv', emit: combined

    script:
    """
    python ${projectDir}/scripts/tracy_postprocessing.py \\
        --json ${json_files} \\
        --outdir .
    """
}
