process VUEGEN_REPORT {

    container params.vuegen_image
    // Azure Batch's TaskContainerSettings validation rejects a per-process
    // containerOptions override outright (see TRACY_RENDER_VISUALISATIONS),
    // so leave platform pinning to the global docker.runOptions for local
    // (e.g. Apple Silicon) runs instead.
    //containerOptions "--platform ${params.container_platform}"

    input:
    path combined_csv
    path decompose_files
    path align_files
    path assemble_files

    output:
    path 'vuegen_report', emit: report

    script:
    """
    pip install --quiet --no-input --disable-pip-version-check \\
        vuegen==${params.vuegen_version}

    build_vuegen_report.py \\
        --combined ${combined_csv} \\
        --indir . \\
        --report-dir vuegen_report \\
        --report-type ${params.vuegen_report_type}
    """
}
