process VUEGEN_PREPARE_TREE {

    container 'python:3.12'

    input:
    path combined_csv
    path decompose_files
    path align_files
    path assemble_files

    output:
    path 'vuegen_report', emit: tree

    script:
    """
    build_vuegen_tree.py \\
        --combined ${combined_csv} \\
        --indir . \\
        --report-dir vuegen_report
    """
}
