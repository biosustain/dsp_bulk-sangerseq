process VUEGEN_PREPARE_TREE {

    container 'python:3.12'

    input:
    path combined_csv
    // Every viewer channel names its files after the sample, so each is staged
    // into a directory of its own to keep `<sample>.html` from the decompose,
    // align and assemble sections from colliding in the task directory.
    path decompose_viewers, stageAs: 'decompose_viewers/*'
    path align_viewers, stageAs: 'align_viewers/*'
    path assemble_viewers, stageAs: 'assemble_viewers/*'

    output:
    path 'vuegen_report', emit: tree

    script:
    """
    build_vuegen_tree.py \\
        --combined ${combined_csv} \\
        --decompose-viewers decompose_viewers \\
        --align-viewers align_viewers \\
        --assemble-viewers assemble_viewers \\
        --report-dir vuegen_report
    """
}
