process TRACY_DECOMPOSE_POSTPROCESS {

    container 'python:3.12'

    input:
    path json_files
    val indigo_link_base

    output:
    path '*.csv', emit: results
    path 'results_combined.csv', emit: combined

    script:
    // Without a base URL the tables keep their original columns; with one they
    // gain a link from each mutation to its position in the Indigo viewer.
    def indigo_link_arg = indigo_link_base ? "--indigo-link-base '${indigo_link_base}'" : ''
    """
    tracy_postprocessing.py \\
        --json ${json_files} \\
        ${indigo_link_arg} \\
        --outdir .
    """
}
